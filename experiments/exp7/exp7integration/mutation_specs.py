"""Exact final-source mutation targets; full execution belongs to future freeze."""
from pathlib import Path
from exp7ops.mutants import MUTANTS as CORE
from exp7ops.evidence import require, digest

SPECS = (
    ("adapter-drop-claim-order", "adapter.py", "I-ADAPTER", 'claim == {"schema": SCHEMA, "stage": stage, "production": production}', 'True'),
    ("adapter-ignore-authority", "adapter.py", "I-ADAPTER", 'digest(raw) == self.authority_sha256', 'True'),
    ("adapter-model-none", "adapter.py", "I-ADAPTER", 'all(type(v) is str for v in values)', 'all(v is None or type(v) is str for v in values)'),
    ("adapter-abstention-lost", "adapter.py", "I-ADAPTER", '"abstained": {a: values[a] is None for a in ARMS}', '"abstained": {a: False for a in ARMS}'),
    ("adapter-drop-source-exit", "adapter.py", "I-ADAPTER", 'require(self._authority_read() == self._authority, "adapter authority changed at exit")', 'pass  # mutant: entry-only authority'),
    ("o8-unbound-site", "bootstrap.py", "O8-BOOTSTRAP", 'digest(raw) == pin(site_sha256)', 'True'),
    ("o8-no-cold-input-close", "bootstrap.py", "O8-BOOTSTRAP", 'close_cli_stdin(sys.stdin)', 'pass  # mutant: readable inherited stdin'),
    ("o8-stale-worker", "heartbeat_service.py", "O8-PORTS", 'type(age) in (int, float) and -5 <= age <= self.timeout', 'True'),
    ("o8-supervisor-in-campaign", "supervisor.py", "O8-DEPLOYMENT", 'not root.is_relative_to(repo) and not root.is_relative_to(campaign) and\n            not repo.is_relative_to(root) and not campaign.is_relative_to(root)', 'True'),
    ("runtime-unreviewed", "candidate_runtime.py", "I-RUNTIME-PREPARATION", 'digest(raw) == pin(expected)', 'True'),
    ("inventory-unknown-files", "inventory.py", "I-ADAPTER", 'files == expected', 'True'),
    ("inventory-transient-write", "inventory.py", "I-ADAPTER", 'require(not self.events, f"transient campaign mutation during power: {self.events}")', 'pass  # mutant: lost transient write latch'),
)
STATS = (
    {"id": "saved-power-unbound-geometry", "file": "exp7stats/power_validation.py", "task": "S-REVIEW-SR1-SR5",
     "old": 'record.get("geometry_sha256") == digest(geometry)', "new": 'True'},
    {"id": "cold-inherited-fd", "file": "exp7stats/read_boundary.py", "task": "S-REVIEW-SR1-R",
     "old": "type(observed['readable_fds']) in (list, tuple) and not observed['readable_fds']", "new": "True"},
    {"id": "cold-inherited-buffer", "file": "exp7stats/read_boundary.py", "task": "S-REVIEW-SR1-R",
     "old": "type(observed['readable_streams']) in (list, tuple) and not observed['readable_streams']", "new": "True"},
)
MUTANTS = CORE + STATS + tuple({"id": name, "file": "exp7integration/"+file, "task": task, "old": old, "new": new}
                      for name, file, task, old, new in SPECS)


def validate_targets(package, tasks):
    rows = []
    for spec in MUTANTS:
        require(spec["task"] in tasks, "mutation task missing")
        path = Path(package)/spec["file"]; raw = path.read_bytes()
        old, new = spec["old"].encode(), spec["new"].encode()
        require(old != new and raw.count(old) == 1, "final mutation span missing/nonunique: "+spec["id"])
        changed = raw.replace(old, new)
        compile(changed, str(path), "exec")
        rows.append({"id": spec["id"], "file": spec["file"], "source_sha256": digest(raw),
                     "mutant_sha256": digest(changed), "task": spec["task"]})
    return rows
