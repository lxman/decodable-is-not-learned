"""Install independently accepted pre-tag calibration bytes before power.

This is a file-binding producer, not a calibration runner. The separately fixed
file map must come from the accepted committed calibration archive. Statistical
semantics are checked again by exp7stats.power.run; acceptance is never inferred
from a self-pinned directory or a boolean supplied by a collection Campaign.
"""
from pathlib import Path
import os
from exp7core.records import strict_json
from exp7stats.common import digest, require, pin, write_once, require_preoutcome
from .inventory import safe


def copy_accepted_calibration(source, campaign_root, *, accepted_files):
    require(type(accepted_files) is dict and set(accepted_files) == {
        "CLAIM.json", "calibration.json", "REPORT.md", "COMPLETE.json"}, "exact accepted calibration inventory")
    source, root = Path(source), Path(campaign_root)
    require_preoutcome(root)
    require(not (root / "statistics/power").exists(), "install calibration before power CLAIM")
    require(source.is_dir() and not source.is_symlink(), "calibration source directory")
    require({p.name for p in source.iterdir()} == set(accepted_files), "calibration archive inventory")
    payloads = {name: safe(source, name).read_bytes() for name in accepted_files}
    for name, raw in payloads.items():
        require(digest(raw) == pin(accepted_files[name]), f"accepted calibration binding: {name}")
    marker = strict_json(payloads["COMPLETE.json"])
    require(marker == {"files": {name: accepted_files[name] for name in ("calibration.json", "REPORT.md")}},
            "calibration completion marker binding")
    record = strict_json(payloads["calibration.json"])
    require(record.get("state") == "NO-DETECTED-CALIBRATION-DEFECT" and record.get("production") is True,
            "accepted production calibration required")
    stats = root / "statistics"
    require(not stats.is_symlink(), "statistics symlink")
    stats.mkdir(exist_ok=True)
    target = stats / "calibration"
    target.mkdir()  # any prior directory, including torn import, refuses
    for name, raw in payloads.items():
        write_once(target / name, raw)
        os.chmod(target / name, 0o444)
    for name in accepted_files:
        require(digest(safe(source, name).read_bytes()) == accepted_files[name] and
                digest(safe(target, name).read_bytes()) == accepted_files[name], "calibration copy entry/exit drift")
    return dict(accepted_files)
