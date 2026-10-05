"""Small fail-closed evidence primitives; no network/process/model imports."""
from pathlib import Path
from hashlib import sha256
import json
import os
import re
import math
import tempfile

class Refusal(ValueError):
    """An operational refusal requiring preserved evidence and operator attention."""

def require(ok, message):
    if not ok:
        raise Refusal(message)

def digest(data):
    return sha256(data).hexdigest()

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()

def strict(data):
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def invalid(value):
        raise Refusal("nonfinite JSON")
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)

def pin(value):
    require(type(value) is str and re.fullmatch("[0-9a-f]{64}", value)
            and value != "0" * 64, "invalid SHA256")
    return value

def commit(value):
    require(type(value) is str and re.fullmatch("[0-9a-f]{40}", value)
            and value != "0" * 40, "invalid git identity")
    return value

def identifier(value):
    require(type(value) is str and re.fullmatch("[a-zA-Z0-9_-]{1,100}", value), "unsafe identifier")
    return value

def number(value, label):
    require(type(value) in (int, float) and math.isfinite(value) and value >= 0, label)
    return value

def path_in(root, relative):
    root = Path(root).resolve(strict=True)
    require(type(relative) is str and re.fullmatch(r"[a-zA-Z0-9_./-]+", relative), "unsafe path")
    require(not relative.startswith("/") and all(p not in ("", ".", "..") for p in relative.split("/")), "relative path")
    target = root
    for part in relative.split("/"):
        target = target / part
        require(not target.is_symlink(), "symlink refused")
    require(target.resolve().is_relative_to(root), "path escape")
    return target

def fsync_dir(directory):
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def once(path, value):
    data = value if type(value) is bytes else canonical(value)
    path = Path(path)
    require(not path.is_symlink(), "output symlink")
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    fsync_dir(path.parent)

def state(path, value):
    """Replace only a heartbeat/status, never scientific outputs or claims."""
    path = Path(path)
    require(not path.is_symlink(), "status symlink")
    # Unique staging names prevent unrelated heartbeat/progress writers from
    # colliding on a shared .next slot. Status ownership is separately enforced.
    fd, name = tempfile.mkstemp(prefix=path.name + ".next-", dir=path.parent)
    temporary = Path(name)
    with os.fdopen(fd, "wb") as stream:
        stream.write(canonical(value))
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)
    fsync_dir(path.parent)

def snapshot(root):
    root = Path(root)
    result = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), "tree symlink")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    return result

def verify_files(root, files, *, exact=False):
    require(type(files) is dict and files, "empty file manifest")
    for name, want in files.items():
        require(digest(path_in(root, name).read_bytes()) == pin(want), "file mismatch: " + name)
    if exact:
        require(snapshot(root) == files, "extra/missing tree file")

def selected_instances(response):
    """Successful-list envelope only; transport success is also mandatory upstream.

    Accept exactly instances, or success:true plus instances. Explicit errors,
    false/nonboolean success and unknown top-level fields are not absence.
    """
    require(type(response) is dict and set(response) in ({"instances"}, {"instances", "success"})
            and response.get("success", True) is True and type(response.get("instances")) is list,
            "unsuccessful or malformed instance-list envelope")
    rows, seen = [], set()
    for raw in response["instances"]:
        require(type(raw) is dict, "instance row")
        row = {k: raw.get(k) for k in ("id", "machine_id", "label", "actual_status")}
        require(all(type(row[k]) is int and row[k] > 0 for k in ("id", "machine_id")), "instance identity")
        require(row["id"] not in seen, "duplicate instance")
        require(type(row["label"]) is str and type(row["actual_status"]) is str
                and bool(row["actual_status"]), "instance status metadata")
        seen.add(row["id"])
        rows.append(row)
    return rows  # deliberately excludes every credential, key, IP and unknown field

def successful_instance_response(status_code, response):
    """Provider binding calls after successful transport + strict JSON decoding."""
    require(type(status_code) is int and 200 <= status_code < 300, "instance-list HTTP failure")
    return {"success": True, "instances": selected_instances(response)}

def selected_credit(response):
    require(type(response) is dict and "credit" in response, "malformed credit response")
    return number(response["credit"], "invalid account credit")
