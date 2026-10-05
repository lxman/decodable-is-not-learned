"""Terminal archive includes the disjoint, bound supervisor evidence trees."""
from pathlib import Path
from exp7ops.evidence import require, snapshot, digest, path_in, canonical, strict, pin
from exp7ops.operator import terminal
from exp7ops.wire import encode_payload
from .supervisor import check_supervisor

INVENTORY = "supervisor-inventory.json"


def bound_supervisors(deployment):
    """Only independently configured roots, including absent/empty roots."""
    stages = deployment.data["stages"]
    plan = deployment.data["remote"]
    roots = plan.get("supervisor_roots", {name: row["output"] for name, row in stages.items()})
    require(type(roots) is dict and set(roots) == set(stages), "complete bound remote supervisor roots")
    require(all(type(p) is str and Path(p).is_absolute() and ".." not in Path(p).parts for p in roots.values()), "absolute remote supervisor roots")
    require(len(set(roots.values())) == len(roots), "distinct bound supervisor roots")
    names = plan["supervisor_stages"]
    require(type(names) is list and names and len(names) == len(set(names)) and set(names) <= set(roots), "bound remote supervisors")
    return roots, set(names)


def supervisor_inventory(deployment):
    roots, admitted = bound_supervisors(deployment)
    rows = {}
    for name, bound in roots.items():
        root = Path(bound)
        require(root.resolve() == Path(deployment.data["stages"][name]["output"]).resolve(), "remote supervisor deployment mismatch")
        check_supervisor(root, repo=deployment.repo, campaign=deployment.root, stage=name)
        exists = root.exists()
        require(not exists or name in admitted, "existing bound supervisor omitted: "+name)
        rows[name] = {"root": bound, "exists": exists, "files": snapshot(root) if exists else {}}
    return {"schema": "exp7.remote-supervisor-inventory.v1", "roots": rows}


def verify_supervisor_archive(deployment, payload):
    """Independently check scope, existence declarations and every archived byte.

    Remote paths are administrative pins, not local filesystem discovery. Their
    current existence/file maps come from the independently re-observed fixed
    remote program, which enumerates ALL these roots on every request.
    """
    roots, admitted = bound_supervisors(deployment)
    require(INVENTORY in payload, "missing complete remote supervisor inventory")
    record = strict(payload[INVENTORY])
    require(type(record) is dict and set(record) == {"schema", "roots"} and record["schema"] == "exp7.remote-supervisor-inventory.v1" and set(record["roots"]) == set(roots), "remote supervisor inventory scope")
    expected = {}
    for name, row in record["roots"].items():
        require(type(row) is dict and set(row) == {"root", "exists", "files"} and row["root"] == roots[name] and type(row["exists"]) is bool and type(row["files"]) is dict, "remote supervisor inventory binding")
        require(not row["exists"] or name in admitted, "existing bound supervisor omitted: "+name)
        require(row["exists"] or not row["files"], "absent supervisor has archived files")
        for relative, sha in row["files"].items():
            require(type(relative) is str and len(Path(relative).parts) == 1 and relative not in ("", ".", "..") and not Path(relative).is_absolute(), "supervisor archive relative path")
            expected[f"supervisors/{name}/{relative}"] = pin(sha)
    actual = {n: digest(raw) for n, raw in payload.items() if n.startswith("supervisors/")}
    require(actual == expected, "incomplete bound supervisor archive bytes")
    return record


def final_evidence(deployment, observe_terminal):
    deployment.check_sources()
    plan = deployment.data["remote"]
    require(Path(plan["evidence_root"]).resolve() == deployment.root.resolve(), "canonical remote campaign root")
    observation = observe_terminal(); terminal(observation)
    require(not (deployment.root/"supervisors").exists() and not (deployment.root/INVENTORY).exists(), "reserved archive namespace inside campaign")
    def inventory():
        sources = {"": deployment.root}
        record = supervisor_inventory(deployment)
        for name, row in record["roots"].items():
            if row["exists"]:
                sources["supervisors/"+name+"/"] = Path(row["root"])
        return ({prefix+n: (root, n, sha) for prefix, root in sources.items() for n, sha in snapshot(root).items()}, record)
    before, supervisors = inventory()
    payload = {n: path_in(root, relative).read_bytes() for n, (root, relative, _) in before.items()}
    require(all(digest(payload[n]) == row[2] for n, row in before.items()), "terminal evidence changed during read")
    require(inventory() == (before, supervisors) and observe_terminal() == observation, "terminal full inventory drift")
    payload[INVENTORY] = canonical(supervisors)
    verify_supervisor_archive(deployment, payload)
    deployment.check_sources()
    return {"files": {n: digest(raw) for n, raw in payload.items()}, "payload": encode_payload(payload), "terminal": observation}
