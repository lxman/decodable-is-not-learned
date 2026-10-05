"""Fixed remote evidence protocol. No arbitrary shell/program text enters it."""
from pathlib import Path
import base64
from .evidence import require, path_in, digest, once
from .operator import terminal

def unit_name(value):
    require(type(value) is str and value and all(c.isascii() and (c.isalnum() or c in "_-/") for c in value)
            and all(p for p in value.split("/")), "unit token")
    return value

def encode_payload(payload):
    require(type(payload) is dict and payload and all(type(x) is bytes for x in payload.values()), "wire bytes map")
    return {name: base64.b64encode(data).decode("ascii") for name, data in payload.items()}

def decode_payload(payload):
    require(type(payload) is dict and payload, "wire map")
    output = {}
    for name, value in payload.items():
        require(type(name) is str and type(value) is str, "wire types")
        output[name] = base64.b64decode(value, validate=True)
    return output

def decode(operation, reply):
    require(type(reply) is dict, "wire reply")
    if operation == "unit":
        return decode_payload(reply)
    if operation == "final-evidence":
        require(set(reply) == {"files", "payload", "terminal"}, "wire final schema")
        return {**reply, "payload": decode_payload(reply["payload"])}
    if operation == "stop-new-work":
        require(reply == {"stop_requested": True}, "wire stop confirmation")
    else:
        require(operation == "snapshot", "wire operation")
    return reply

def remote_main(argv, *, root, allowed_units, inventory, observe_terminal, stop_path, check_bindings):
    """Used by fixed /workspace/exp7_ops/remote_7.py deployment wrapper.

    allowed_units and inventory are independently bound path policies from the
    approved deployment; inventory() enumerates the FULL evidence tree, including
    failures. The local wrapper's path/source pins are checked on entry and exit.
    """
    require(check_bindings() is None, "remote binding check")
    require(type(argv) is list and argv and argv[0] in ("snapshot", "unit", "final-evidence", "stop-new-work"), "fixed remote operation")
    operation = argv[0]
    if operation == "unit":
        require(len(argv) == 2 and unit_name(argv[1]) in allowed_units, "unit outside approved inventory")
        folder = path_in(root, argv[1])
        require({p.name for p in folder.iterdir()} == {"raw.jsonl", "record.json", "DONE.json"}, "torn remote unit")
        payload = {n: path_in(folder, n).read_bytes() for n in ("raw.jsonl", "record.json", "DONE.json")}
        result = encode_payload(payload)
    else:
        require(len(argv) == 1, "no arbitrary remote arguments")
        if operation == "stop-new-work":
            if not Path(stop_path).exists():
                once(stop_path, {"stop_new_work": True})
            result = {"stop_requested": True}
        elif operation == "snapshot":
            complete = {}
            observation = observe_terminal()
            if observation is not None:
                terminal(observation)
            if observation is not None and (observation["exit_code"] != 0 or observation["kind"] != "complete"):
                # Terminal failure inventory is collected by final-evidence.
                # Parsing/admitting DONE directories first could conceal the
                # failure terminal behind the very malformed files it explains.
                require(check_bindings() is None, "remote exit bindings")
                return {"units": {}, "terminal": observation}
            for name in allowed_units:
                folder = path_in(root, name)
                done = folder / "DONE.json"
                if done.exists():
                    require({p.name for p in folder.iterdir()} == {"raw.jsonl", "record.json", "DONE.json"}, "extra complete-unit file")
                    complete[name] = digest(path_in(folder, "DONE.json").read_bytes())
            result = {"units": complete, "terminal": observation}
        else:
            observation = observe_terminal()
            terminal(observation)
            names = inventory()
            require(type(names) is tuple and names and len(set(names)) == len(names), "full remote inventory")
            payload = {n: path_in(root, n).read_bytes() for n in names}
            require(observe_terminal() == observation, "remote terminal drift")
            result = {"files": {n: digest(b) for n, b in payload.items()},
                      "payload": encode_payload(payload), "terminal": observation}
    require(check_bindings() is None, "remote exit bindings")
    return result
