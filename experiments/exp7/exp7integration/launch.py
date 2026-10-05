"""Fixed detached launcher with independently enrolled site and monitor pins."""
from pathlib import Path
from exp7ops.evidence import require, digest, pin, verify_files
from exp7ops.operator import detached_launch, stage_argv
from exp7ops.runtime import SystemProcess


class SiteBoundProcess:
    def __init__(self, process, deployment, stage, contract):
        self.process, self.deployment = process, deployment
        self.expected = stage_argv(deployment.data["python"], deployment.repo, stage, contract)

    def __getattr__(self, name):
        return getattr(self.process, name)

    def spawn(self, argv, **kwargs):
        require(argv == self.expected, "fixed detached stage command")
        bound = argv[:4]+["--site-sha256", pin(self.deployment.site_sha256)]+argv[4:]
        self.deployment.check_sources()
        require(digest(self.deployment.site_path.read_bytes()) == self.deployment.site_sha256, "launch site drift")
        return self.process.spawn(bound, **kwargs)


def launch_stage(deployment, stage, *, process=None):
    require(stage in deployment.data["stages"], "fixed launch stage")
    plan = deployment.data["stages"][stage]
    approval = deployment.authenticate(stage, Path(plan["contract_path"]).read_bytes())
    process = SiteBoundProcess(SystemProcess() if process is None else process, deployment, stage, plan["contract_path"])
    def monitor_pin():
        deployment.check_sources()
        require("tools/experiment_monitor.py" in deployment.data["monitor_sources"], "durable monitor source binding")
        verify_files(deployment.repo, deployment.data["monitor_sources"])
    result = detached_launch(process, python=deployment.data["python"], repo=deployment.repo,
                             contract=plan["contract_path"], stage=stage, out=plan["output"],
                             job=plan["job"], session=plan["session"], approval=approval, check_monitor_pin=monitor_pin)
    deployment.check_sources()
    return result
