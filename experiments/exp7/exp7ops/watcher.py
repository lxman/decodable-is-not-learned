"""Complete-unit landing/publication and evidence-first finalization."""
from pathlib import Path
from typing import Protocol
from .evidence import (require, pin, digest, once, state, canonical, strict,
                       path_in, verify_files, snapshot, identifier)
from .operator import land_unit, cost_guard, terminal
from .wire import unit_name

class Transport(Protocol):
    def snapshot(self): ...
    def unit(self, unit_id): ...
    def final_evidence(self): ...
    def stop_new_work(self): ...

def validate_snapshot(value, expected_units):
    require(type(value) is dict and set(value) == {"units", "terminal"}, "snapshot schema")
    require(type(value["units"]) is dict, "snapshot unit map")
    require(set(value["units"]) <= set(expected_units), "unexpected unit")
    for unit, want in value["units"].items():
        unit_name(unit); pin(want)
    if value["terminal"] is not None:
        terminal(value["terminal"])
    return value

class Watcher:
    def __init__(self, *, approval, transport, provider, composition, root, out,
                 expected_units, publish, independently_secure, release_secured,
                 forecast_remaining, reserve, now):
        require(expected_units and len(set(expected_units)) == len(expected_units), "exact unit inventory")
        self.units = tuple(unit_name(u) for u in expected_units)
        for fn in (publish, independently_secure, release_secured, forecast_remaining, now):
            require(callable(fn), "missing watcher capability")
        self.approval, self.transport, self.provider, self.composition = approval, transport, provider, composition
        self.root, self.out = Path(root), Path(out)
        self.publish, self.secure, self.release = publish, independently_secure, release_secured
        self.forecast, self.reserve, self.now = forecast_remaining, reserve, now

    def tick(self):
        """One iteration; scheduler calls every 300 seconds, heartbeat at <=60s."""
        require(not (self.out / "final.CLAIM").exists(), "finalization already claimed; reconcile")
        snap = validate_snapshot(self.transport.snapshot(), self.units)
        paths, unit_failures = [], []
        for unit in sorted(snap["units"]):
            try:
                payload = self.transport.unit(unit)
                require(type(payload) is dict and type(payload.get("DONE.json")) is bytes,
                        "missing completion marker")
                require(digest(payload["DONE.json"]) == snap["units"][unit], "snapshot drift")
                names = land_unit(self.root, unit, payload,
                    verify=lambda u, p: self.composition.verify_unit(self.approval.stage, u, p))
                paths.extend((self.root / unit / n) for n in names)
            except Exception as exc:
                if snap["terminal"] is None:
                    raise
                # Failed or claimed-success terminals both retain the bytes for
                # independent diagnosis. No malformed unit is admitted as valid.
                unit_failures.append({"unit": unit, "phase": "unit-validation", "error_type": type(exc).__name__})
        # Revalidate even previously published complete units against independent
        # expectations; existence alone never certifies a recovered unit.
        if paths:
            try:
                self.publish(tuple(paths))
            except Exception as exc:
                if snap["terminal"] is None:
                    raise
                unit_failures.append({"phase": "unit-publication", "error_type": type(exc).__name__})
        status = {"completed": len(paths) // 3, "total": len(self.units), "heartbeat_utc": self.now()}
        state(self.out / "watch-state.json", status)
        if snap["terminal"] is None:
            try:
                status["cost"] = cost_guard(self.approval, self.provider.credit(),
                    forecast_remaining=self.forecast(len(snap["units"])), reserve=self.reserve)
            except Exception:
                # A bounded, authenticated STOP request is not permission to delete
                # an instance or overwrite a once-only scientific stage.
                once(self.out / "cost-stop.CLAIM", {"stage": self.approval.stage})
                self.transport.stop_new_work()
                raise
            return {"terminal": False, **status}
        once(self.out / "final.CLAIM", {"terminal": snap["terminal"]})
        once(self.out / "terminal-unit-failures.json", unit_failures)
        evidence = self.transport.final_evidence()
        require(type(evidence) is dict and set(evidence) == {"files", "payload", "terminal"}, "final evidence schema")
        require(evidence["terminal"] == snap["terminal"], "terminal changed")
        require(type(evidence["files"]) is dict and evidence["files"], "empty final evidence")
        require(type(evidence["payload"]) is dict and set(evidence["payload"]) == set(evidence["files"]), "partial archive transfer")
        archive = self.out / "preserved-final"
        archive.mkdir()
        # This deliberately preserves failed/torn units and logs as evidence.
        # The independent verifier checks the remote inventory's scope/coverage.
        for name, want in evidence["files"].items():
            data = evidence["payload"][name]
            require(type(data) is bytes and digest(data) == pin(want), "final transfer mismatch")
            target = path_in(archive, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            once(target, data)
        verify_files(archive, evidence["files"], exact=True)
        try:
            verification = self.composition.verify_final(archive, snap["terminal"])
            require(type(verification) is dict and set(verification) == {"scientific_state", "failures", "inventory_sha256"}, "final verifier schema")
            require(verification["scientific_state"] in ("COMPLETE", "INSUFFICIENT_DATA"), "final scientific state")
            pin(verification["inventory_sha256"])
            require(type(verification["failures"]) is list, "final failure list")
        except Exception as exc:
            verification = {"scientific_state": "INSUFFICIENT_DATA",
                "failures": [{"phase": "final-verification", "error_type": type(exc).__name__}],
                "inventory_sha256": digest(canonical(evidence["files"]))}
        if unit_failures:
            verification = {**verification, "scientific_state": "INSUFFICIENT_DATA",
                            "failures": verification["failures"] + unit_failures}
        once(self.out / "final-verification.json", verification)
        if snap["terminal"]["exit_code"] == 0 and snap["terminal"]["kind"] == "complete":
            require(set(snap["units"]) == set(self.units) and verification["scientific_state"] == "COMPLETE"
                    and not verification["failures"], "success claims incomplete/invalid campaign")
        # A failed completed campaign can be released after its ENTIRE failure
        # evidence is secured; its scientific refusal remains a refusal.
        receipt_path = self.secure(archive, evidence["files"], snap["terminal"], verification)
        require(Path(receipt_path).is_file(), "independent secured receipt missing")
        result = self.release(receipt_path)
        once(self.out / "watch.COMPLETE.json", result)
        return {"terminal": True, "release": result, **status}

def heartbeat_loop(*, tick, heartbeat, clock, wait, interval=300):
    """Work scheduler under an already-started independent heartbeat session."""
    require(interval == 300, "fixed watcher interval")
    require(callable(getattr(heartbeat, "check", None)), "started independent heartbeat required")
    heartbeat.check()
    due = clock()
    while True:
        heartbeat.check()
        if clock() >= due:
            result = tick()
            heartbeat.check()
            if result["terminal"]:
                return result
            due = clock() + interval
        wait(min(60, max(0, due - clock())))
