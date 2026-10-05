"""Fixed CLI programs; independently enrolled site constants are data only."""
from pathlib import Path
import sys
import os
from exp7ops.evidence import require, once, strict, digest, canonical
from exp7ops.operator import stage_main
from exp7ops.dispatch import FixedComposition
from exp7stats import power, analyzer, calibration
from exp7stats.calibration_context import CalibrationContext
from .deployment import FixedStageDeployment
from .heartbeat_service import OSHeartbeatService, run_bound_heartbeat, utc


def write_site_binding(path, *, config_path, config_sha256, package_root, expected_binding_sha256):
    """Future installation uses actual reviewed values; no default/trust guessing.

    Caller independently pins the exact resulting JSON in administrative launch
    evidence. This administrative data is never loaded as executable Python.
    """
    from exp7ops.evidence import pin
    value = {"schema": "exp7.site-binding.v1", "config_path": str(Path(config_path).absolute()),
             "config_sha256": pin(config_sha256), "package_root": str(Path(package_root).absolute())}
    raw = canonical(value)
    require(digest(raw) == pin(expected_binding_sha256), "independent site binding SHA")
    once(path, raw)
    return digest(raw)


def load_bound(site_path, site_sha256):
    # site_path is a literal sibling filename supplied by each fixed bootstrap,
    # not a CLI/env/user-selected module or configuration path.
    from exp7ops.evidence import pin
    raw = Path(site_path).read_bytes()
    require(digest(raw) == pin(site_sha256), "independent launch site SHA")
    value = strict(raw)
    require(set(value) == {"schema", "config_path", "config_sha256", "package_root"} and
            value["schema"] == "exp7.site-binding.v1", "fixed site binding schema")
    require(Path(__file__).resolve().parent.parent == Path(value["package_root"]).resolve(), "fixed pure package root")
    deployment = FixedStageDeployment(value["config_path"], value["config_sha256"])
    deployment.site_path, deployment.site_sha256 = Path(site_path), pin(site_sha256)
    return deployment


def stage_entry(argv, deployment):
    require(type(argv) is list and argv and argv[0] in deployment.data["stages"], "fixed stage CLI")
    name = argv[0]
    plan = deployment.data["stages"][name]
    service = OSHeartbeatService(config_path=Path(plan["output"])/"heartbeat-config.json",
                                  python=deployment.data["python"],
                                  bootstrap=deployment.repo/"experiments/exp7/run/heartbeat_7.py",
                                  fixed_stage=name, source_root=deployment.repo,
                                  source_pins=deployment.data["source_pins"], site_sha256=deployment.site_sha256)
    from .supervisor import OperationalComposition
    composition = OperationalComposition(deployment, power_run=power.run, analyzer_run=analyzer.run)
    return stage_main(argv, composition=composition, contract_path=Path(plan["contract_path"]),
                      output=plan["output"], pid=os.getpid(), now=utc, heartbeat_service=service)


def heartbeat_entry(argv, deployment):
    require(type(argv) is list and len(argv) == 1 and argv[0] in deployment.data["stages"], "fixed heartbeat stage")
    plan = deployment.data["stages"][argv[0]]
    return run_bound_heartbeat(Path(plan["output"])/"heartbeat-config.json", source_root=deployment.repo,
                               source_pins=deployment.data["source_pins"])


def secured_entry(argv, deployment):
    require(argv == [], "secured verifier accepts no arbitrary arguments")
    from .security import independent_secure_main
    plan = deployment.data["stages"]["watch"]
    approval = deployment.authenticate("watch", Path(plan["contract_path"]).read_bytes())
    return independent_secure_main(deployment, approval)


def baseline_entry(argv, deployment):
    require(argv == [], "baseline fixed stage accepts no arguments")
    plan = deployment.data["digest_baseline"]
    return deployment.predictor_digest_baseline(trust_path=plan["trust_path"], trust_sha256=plan["trust_sha256"])


def calibration_entry(argv, deployment):
    require(argv == [], "calibration fixed stage accepts no arguments")
    plan = deployment.data["calibration"]
    from exp7stats.read_boundary import close_cli_stdin
    close_cli_stdin(sys.stdin)
    # Independent candidate context BEFORE any prereg/projection/seal. Never
    # construct a live collection Campaign for pre-tag calibration.
    context = CalibrationContext(plan["output"], deployment.repo,
                                 candidate_commit=plan["candidate_commit"], manifest_path=plan["manifest_path"],
                                 manifest_sha256=plan["manifest_sha256"])
    return calibration.run(context)


def remote_entry(argv, deployment):
    from exp7ops.wire import remote_main
    from .security import TerminalObserver
    plan = deployment.data["remote"]
    require("heartbeat_identity_sha256" in plan and not {"token", "heartbeat_token"} & set(plan), "remote heartbeat identity schema")
    observer = TerminalObserver(identity=plan["parent_identity"], group=plan["process_group"],
                                 status_path=plan["status_path"], heartbeat_identity_sha256=plan["heartbeat_identity_sha256"])
    if argv == ["final-evidence"]:
        from .remote_evidence import final_evidence
        return final_evidence(deployment, observer)
    from exp7ops.evidence import snapshot
    root = Path(plan["evidence_root"])
    return remote_main(argv, root=root, allowed_units=tuple(plan["allowed_units"]),
                       inventory=lambda: tuple(snapshot(root)), observe_terminal=observer,
                       stop_path=root/"STOP_NEW_WORK.json", check_bindings=deployment.check_sources)


def metadata_entry(argv, deployment):
    require(argv == [], "metadata program accepts no arbitrary path")
    from .metadata_transport import metadata_reply
    return metadata_reply(deployment)


def launch_entry(argv, deployment):
    require(len(argv) == 1 and argv[0] in deployment.data["stages"], "fixed launch stage only")
    from .launch import launch_stage
    return launch_stage(deployment, argv[0])


ENTRIES = {"stage_7.py": stage_entry, "heartbeat_7.py": heartbeat_entry,
           "secured_7.py": secured_entry, "remote_7.py": remote_entry,
           "digest_baseline_7.py": baseline_entry, "calibration_7.py": calibration_entry,
           "metadata_7.py": metadata_entry, "launch_7.py": launch_entry}


def main(program, argv, site_path, site_sha256):
    require(program in ENTRIES, "fixed bootstrap program")
    deployment = load_bound(site_path, site_sha256)
    result = ENTRIES[program](argv, deployment)
    deployment.check_sources()
    require(digest(Path(site_path).read_bytes()) == site_sha256, "site binding exit drift")
    # Only selected result types are emitted. Provider replies never reach this.
    from exp7stats.common import dumps
    print(dumps(result).decode(), end="")
    accepted = "NO-DETECTED-CALIBRATION-DEFECT" if program == "calibration_7.py" else "COMPLETE"
    return 0 if not isinstance(result, dict) or result.get("state", accepted) == accepted else 1
