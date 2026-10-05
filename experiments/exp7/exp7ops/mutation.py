"""Disposable-copy mutation with durable original/mutant/restored receipts."""
from pathlib import Path
import shutil
from .evidence import require, digest, once, snapshot, path_in, verify_files, canonical

def run_mutants(source, destination, mutants, evaluate):
    """evaluate(copy_root, task) runs only a guarded selected synthetic test task.

    A kill is an assertion failure, never an import/syntax/guard crash. Interrupts
    restore bytes in finally. A SIGKILL leaves a backup+intent record, and explicit
    recover_copy verifies them; neither function touches source bytes.
    """
    source, destination = Path(source).resolve(), Path(destination)
    approved = Path("/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode").resolve(strict=True)
    require(destination.resolve().is_relative_to(approved), "mutation copy must be in approved scratch")
    require(not destination.exists() and callable(evaluate), "fresh mutation destination")
    original = snapshot(source)
    require(original, "empty mutation source")
    destination.mkdir()
    work, logs, backups = (destination / n for n in ("copy", "logs", "backups"))
    shutil.copytree(source, work)
    logs.mkdir(); backups.mkdir()
    once(destination / "original-manifest.json", original)
    results = []
    for mutant in mutants:
        require(set(mutant) == {"id", "file", "old", "new", "task"}, "mutant schema")
        tag = mutant["id"]
        from .evidence import identifier
        identifier(tag)
        target = path_in(work, mutant["file"])
        before = target.read_bytes()
        old, new = mutant["old"].encode(), mutant["new"].encode()
        require(old != new and before.count(old) == 1, "mutant must target one exact original span")
        after = before.replace(old, new, 1)
        compile(after, str(target), "exec")
        once(backups / tag, before)
        once(logs / (tag + ".intent.json"), {**mutant, "original_sha256": digest(before), "mutant_sha256": digest(after)})
        baseline = evaluate(work, mutant["task"])
        once(logs / (tag + ".original.json"), baseline)
        require(clean(baseline), "mutation baseline not clean")
        result = {"id": tag, "status": "INTERRUPTED"}
        try:
            target.write_bytes(after)
            clear_bytecode(work)
            observed = evaluate(work, mutant["task"])
            once(logs / (tag + ".mutant.json"), observed)
            require(type(observed) is dict and set(observed) >= {"tests", "failures", "errors", "returncode"}, "mutation test receipt")
            killed = observed["tests"] > 0 and observed["failures"] > 0 and observed["errors"] == 0 and observed["returncode"] != 0
            result = {"id": tag, "status": "KILLED" if killed else "SURVIVED_OR_INVALID", "test": observed}
        finally:
            target.write_bytes(before)
            clear_bytecode(work)
            require(snapshot(work) == original, "restoration byte mismatch")
            restored = evaluate(work, mutant["task"])
            once(logs / (tag + ".restored.json"), {"test": restored, "tree": snapshot(work)})
            require(clean(restored), "restored suite not clean")
            once(logs / (tag + ".result.json"), result)
        results.append(result)
    require(snapshot(source) == original, "original source was changed")
    once(destination / "results.json", results)
    return results

def clean(result):
    return (type(result) is dict and result.get("tests", 0) > 0 and result.get("failures") == 0
            and result.get("errors") == 0 and result.get("returncode") == 0)

def clear_bytecode(root):
    for path in Path(root).rglob("__pycache__"):
        shutil.rmtree(path)
    for path in Path(root).rglob("*.pyc"):
        path.unlink()

def recover_copy(destination, mutant):
    from .evidence import strict, identifier
    identifier(mutant)
    destination = Path(destination)
    intent = strict((destination / "logs" / (mutant + ".intent.json")).read_bytes())
    data = (destination / "backups" / mutant).read_bytes()
    require(digest(data) == intent["original_sha256"], "backup mismatch")
    target = path_in(destination / "copy", intent["file"])
    require(digest(target.read_bytes()) in (intent["original_sha256"], intent["mutant_sha256"]), "unknown interrupted bytes")
    target.write_bytes(data)
    clear_bytecode(destination / "copy")
    original = strict((destination / "original-manifest.json").read_bytes())
    verify_files(destination / "copy", original, exact=True)
    once(destination / "logs" / (mutant + ".recovered.json"), {"tree": original, "suite_still_required": True})
    return original
