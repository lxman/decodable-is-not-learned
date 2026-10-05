"""Fixed future-freeze orchestration. Every process effect uses a supplied port.

The controller is not a synthetic worker: only workers import the hard guard.
Planning tests supply a recorder port; no real subprocess starts in those tests.
"""
from pathlib import Path
import shutil
from exp7ops.evidence import require, once, strict, digest, snapshot, verify_files
from exp7ops.mutation import run_mutants
from .mutation_specs import MUTANTS, validate_targets


def deterministic_twice(process, *, python, package, fixture, fixture_sha256, output):
    output = Path(output); output.mkdir()
    worker = Path(package)/"numerical_worker.py"
    values = []
    for name in ("first", "second"):
        target = output/(name+".json")
        process.run([str(python), "-I", "-B", str(worker), "--fixture", str(fixture),
                     "--fixture-sha256", fixture_sha256, "--output", str(target)],
                    cwd=str(package), shell=False, timeout=86400)
        values.append(target.read_bytes())
    require(values[0] == values[1], "two independent workers differ")
    receipt = {"invocations": 2, "sha256": digest(values[0]), "byte_identical": True}
    once(output/"determinism.json", receipt)
    return receipt


def full_freeze(process, *, python, package, package_pins, fixture, fixture_sha256, output):
    """Caller enrolls reviewed source/export pins and registers detached controller.

    Full-default worlds, scans and two numerical workers execute only on exported
    fake producer bytes. Production runtime dispatch never imports this module.
    """
    from task_registry import TASKS
    package, output = Path(package), Path(output)
    require(digest(Path(fixture).read_bytes()) == fixture_sha256, "independent fixture pin")
    verify_files(package, package_pins, exact=True)
    require(output.resolve().is_relative_to(Path("/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode")), "freeze scratch only")
    require(not output.exists(), "fresh freeze output")
    output.mkdir()
    copy = output/"package"; shutil.copytree(package, copy)
    once(copy/"DISPOSABLE-SYNTHETIC-SOURCE.json", {"synthetic_only": True})
    validate_targets(copy, TASKS)
    counter = [0]
    def evaluate(work, task):
        require(task in TASKS or task == "all", "literal synthetic task only")
        counter[0] += 1
        path = output/f"task-{counter[0]:04d}.json"
        result = process.run([str(python), "-I", "-B", str(Path(work)/"run_task_tests.py"),
                              "--task", task, "--receipt", str(path)], cwd=str(work), shell=False, timeout=86400)
        # The port returns an exit code even on assertion failure. Import/syntax
        # crashes lacking a receipt cannot count as a mutation kill.
        require(type(result) is dict and type(result.get("returncode")) is int, "guarded process returncode required")
        receipt = strict(path.read_bytes())
        require(receipt["forbidden_loaded"] == [], "worker guard failed")
        return {**receipt, "returncode": result["returncode"]}
    before = evaluate(copy, "all")
    require(before["failures"] == before["errors"] == before["returncode"] == 0, "cold baseline failed")
    for task in ("worlds", "import-scan", "read-scan"):
        target = output/(task+".json")
        process.run([str(python), "-I", "-B", str(copy/"freeze_worker.py"), "--task", task,
                     "--fixture", str(fixture), "--fixture-sha256", fixture_sha256, "--output", str(target)],
                    cwd=str(copy), shell=False, timeout=86400)
        require(strict(target.read_bytes())["state"] == "COMPLETE", "freeze worker failed: "+task)
    deterministic_twice(process, python=python, package=copy, fixture=fixture, fixture_sha256=fixture_sha256, output=output/"determinism")
    mutations = run_mutants(copy, output/"mutations", MUTANTS, evaluate)
    require(all(v["status"] == "KILLED" for v in mutations), "unresolved mutation; explicit review required")
    after = evaluate(copy, "all")
    require(after["failures"] == after["errors"] == after["returncode"] == 0, "restored cold battery failed")
    verify_files(package, package_pins, exact=True)
    receipt = {"state": "COMPLETE", "synthetic_only": True, "before": before, "after": after,
               "mutations": len(mutations), "fixture_sha256": fixture_sha256}
    once(output/"COMPLETE.json", receipt)
    return receipt


class GuardedWorkerProcess:
    """Native controller leaf: only fixed guarded workers under one copied package.

    Instantiate only in a future authorized, detached, durably monitored freeze.
    The worker's guard forbids nested subprocesses, network and model imports.
    """
    def __init__(self, python, scratch):
        require(Path(python).is_absolute(), "absolute venv interpreter path")
        self.python, self.scratch = str(Path(python).absolute()), Path(scratch).resolve()
        require(self.scratch.is_relative_to(Path("/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode")), "worker scratch")
    def run(self, argv, *, cwd, shell, timeout):
        require(shell is False and argv[:3] == [self.python, "-I", "-B"], "fixed guarded Python invocation")
        script = Path(argv[3]).resolve()
        require(script.is_relative_to(self.scratch) and script.name in ("run_task_tests.py", "freeze_worker.py", "numerical_worker.py"), "fixed worker entry")
        require(Path(cwd).resolve() == script.parent and timeout == 86400, "fixed worker location/bound")
        import subprocess
        result = subprocess.run(argv, cwd=cwd, shell=False, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        log = self.scratch/("process-"+digest(result.stdout+str(argv).encode())+".log")
        once(log, result.stdout)
        return {"returncode": result.returncode, "log": str(log)}
