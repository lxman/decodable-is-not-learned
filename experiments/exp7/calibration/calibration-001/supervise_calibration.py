"""Detached supervisor for Experiment 7 full-stage pre-tag synthetic calibration (calibration-001)."""
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

REPO = Path("/Users/michaeljordan/emergence-paper").resolve()
EXP7 = REPO / "experiments/exp7"
RUN_DIR = EXP7 / "calibration/calibration-001"
SCRATCH_BASE = Path("/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode/exp7-calibration-001")
SCRATCH_ROOT = SCRATCH_BASE / "root"
EMPTY_PYCACHE = SCRATCH_BASE / "empty-pycache"

PYTHON = "/Users/michaeljordan/emergence-lab/.venv/bin/python"
CLI_SCRIPT = str(EXP7 / "calibration/run_calibration_cli.py")
CANDIDATE_COMMIT = "501853e36e4937f0ec8f2307a81b2d3990b0333d"
MANIFEST_REL = "experiments/exp7/calibration/authority/calibration-candidate.json"
MANIFEST_SHA256 = "10a6389533c549443d1862fad7566d012777134aa2a86c9ca8008db1b778bbee"
WALL_TIMEOUT_SECONDS = 144000.0  # 40 hours safety bound (> ~28.1h profiled runtime)

STRIPPED_ENV = {
    "HOME": "/Users/michaeljordan",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
    "PYTHONHASHSEED": "0",
    "PYTHONIOENCODING": "utf-8",
    "PYTHONNOUSERSITE": "1",
    "PYTHONUNBUFFERED": "1",
    "TMPDIR": "/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T",
    "TZ": "UTC",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json_atomic(path: Path, data: dict):
    raw = (json.dumps(data, sort_keys=True, indent=2) + "\n").encode("utf-8")
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    with tmp.open("wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)
    dfd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def sample_rss(sup_pid: int, child_pid: int):
    try:
        res = subprocess.run(
            ["/bin/ps", "-o", "pid=,rss=,etime=,time=", "-p", f"{sup_pid},{child_pid}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        )
        sup_rss = 0
        child_rss = 0
        child_time = ""
        for line in res.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                pid = int(parts[0])
                rss_bytes = int(parts[1]) * 1024
                if pid == sup_pid:
                    sup_rss = rss_bytes
                elif pid == child_pid:
                    child_rss = rss_bytes
                    if len(parts) >= 4:
                        child_time = parts[3]
        return sup_rss, child_rss, sup_rss + child_rss, child_time
    except Exception:
        return 0, 0, 0, ""


def main():
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    if SCRATCH_BASE.exists():
        shutil.rmtree(SCRATCH_BASE)
    SCRATCH_ROOT.mkdir(parents=True)
    EMPTY_PYCACHE.mkdir(parents=True)

    argv = [
        PYTHON,
        "-I",
        "-B",
        "-X",
        f"pycache_prefix={EMPTY_PYCACHE}",
        "-X",
        "int_max_str_digits=5000",
        CLI_SCRIPT,
        "--root",
        str(SCRATCH_ROOT),
        "--repo",
        str(REPO),
        "--candidate-commit",
        CANDIDATE_COMMIT,
        "--manifest",
        MANIFEST_REL,
        "--manifest-sha256",
        MANIFEST_SHA256,
    ]

    stdout_path = RUN_DIR / "produce.stdout"
    stderr_path = RUN_DIR / "produce.stderr"
    sup_pid = os.getpid()
    sup_sid = os.getsid(0)
    started_utc = utc_now()
    t0 = time.monotonic()

    with stdout_path.open("wb") as out_f, stderr_path.open("wb") as err_f:
        proc = subprocess.Popen(
            argv,
            cwd=str(REPO),
            env=STRIPPED_ENV,
            stdin=subprocess.DEVNULL,
            stdout=out_f,
            stderr=err_f,
            start_new_session=True,
        )
        child_pid = proc.pid
        child_pgid = os.getpgid(child_pid)

        launch_info = {
            "schema": "exp7.calibration-launch.v1",
            "run_id": "calibration-001",
            "started_utc": started_utc,
            "supervisor_pid": sup_pid,
            "supervisor_sid": sup_sid,
            "child_pid": child_pid,
            "child_pgid": child_pgid,
            "argv": argv,
            "env": STRIPPED_ENV,
            "scratch_root": str(SCRATCH_ROOT),
            "empty_pycache": str(EMPTY_PYCACHE),
            "candidate_commit": CANDIDATE_COMMIT,
            "manifest_path": MANIFEST_REL,
            "manifest_sha256": MANIFEST_SHA256,
            "wall_timeout_seconds": WALL_TIMEOUT_SECONDS,
        }
        write_json_atomic(RUN_DIR / "produce.launch.json", launch_info)

        peak_sup_rss = 0
        peak_child_rss = 0
        peak_agg_rss = 0
        samples = 0
        last_status_write = 0.0
        timed_out = False

        while True:
            rc = proc.poll()
            elapsed = time.monotonic() - t0
            sup_rss, child_rss, agg_rss, child_cpu_str = sample_rss(sup_pid, child_pid)
            if agg_rss > 0:
                samples += 1
                peak_sup_rss = max(peak_sup_rss, sup_rss)
                peak_child_rss = max(peak_child_rss, child_rss)
                peak_agg_rss = max(peak_agg_rss, agg_rss)

            if rc is not None:
                break

            if elapsed > WALL_TIMEOUT_SECONDS:
                timed_out = True
                try:
                    os.killpg(child_pgid, signal.SIGTERM)
                except OSError:
                    pass
                time.sleep(2.0)
                if proc.poll() is None:
                    try:
                        os.killpg(child_pgid, signal.SIGKILL)
                    except OSError:
                        pass
                rc = proc.wait()
                break

            if elapsed - last_status_write >= 60.0 or samples <= 2:
                cal_dir = SCRATCH_ROOT / "statistics/calibration"
                status = {
                    "schema": "exp7.calibration-live-status.v1",
                    "run_id": "calibration-001",
                    "state": "RUNNING",
                    "updated_utc": utc_now(),
                    "elapsed_wall_seconds": round(elapsed, 3),
                    "elapsed_hours": round(elapsed / 3600.0, 4),
                    "supervisor_pid": sup_pid,
                    "child_pid": child_pid,
                    "child_cpu_time": child_cpu_str,
                    "current_child_rss_bytes": child_rss,
                    "peak_child_rss_bytes": peak_child_rss,
                    "peak_supervisor_rss_bytes": peak_sup_rss,
                    "peak_aggregate_rss_bytes": peak_agg_rss,
                    "ps_samples": samples,
                    "claim_exists": (cal_dir / "CLAIM.json").exists(),
                    "complete_exists": (cal_dir / "COMPLETE.json").exists(),
                    "refused_exists": (cal_dir / "REFUSED.json").exists(),
                    "halted_exists": (SCRATCH_ROOT / "statistics/HALTED.json").exists(),
                }
                write_json_atomic(RUN_DIR / "status.json", status)
                last_status_write = elapsed

            time.sleep(5.0)

    elapsed_total = time.monotonic() - t0
    ended_utc = utc_now()
    rusage_children = resource.getrusage(resource.RUSAGE_CHILDREN)

    cal_dir = SCRATCH_ROOT / "statistics/calibration"
    out_copy_dir = RUN_DIR / "output"
    copied_files = {}
    if cal_dir.exists():
        if out_copy_dir.exists():
            shutil.rmtree(out_copy_dir)
        out_copy_dir.mkdir(parents=True)
        import hashlib
        for item in sorted(cal_dir.iterdir()):
            if item.is_file():
                dst = out_copy_dir / item.name
                shutil.copy2(item, dst)
                copied_files[item.name] = {
                    "bytes": dst.stat().st_size,
                    "sha256": hashlib.sha256(dst.read_bytes()).hexdigest(),
                }

    # If calibration.json was produced and COMPLETE.json exists, run independent cold verify_calibration_semantics
    verify_result = None
    if rc == 0 and (cal_dir / "COMPLETE.json").exists() and (cal_dir / "calibration.json").exists():
        verify_t0 = time.monotonic()
        verify_code = f"""import sys, json
from pathlib import Path
sys.path.insert(0, {str(REPO)!r})
sys.path.insert(0, {str(EXP7)!r})
from exp7core.records import strict_json
from exp7stats.common import decode, digest
from exp7stats.calibration import verify_calibration_semantics
raw = Path({str(cal_dir / 'calibration.json')!r}).read_bytes()
record = decode(strict_json(raw))
verify_calibration_semantics(record)
print(json.dumps({{"verified": True, "state": record["state"], "calibration_sha256": digest(raw)}}))
"""
        vres = subprocess.run(
            [PYTHON, "-I", "-B", "-X", "int_max_str_digits=5000", "-c", verify_code],
            cwd=str(REPO),
            env=STRIPPED_ENV,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        verify_elapsed = time.monotonic() - verify_t0
        verify_result = {
            "returncode": vres.returncode,
            "elapsed_wall_seconds": round(verify_elapsed, 4),
            "stdout": vres.stdout.strip(),
            "stderr": vres.stderr.strip(),
        }
        write_json_atomic(RUN_DIR / "verify.result.json", verify_result)

    summary = {
        "schema": "exp7.calibration-supervisor-summary.v1",
        "run_id": "calibration-001",
        "state": "COMPLETE" if (rc == 0 and verify_result and verify_result["returncode"] == 0) else "FAILED",
        "started_utc": started_utc,
        "ended_utc": ended_utc,
        "elapsed_wall_seconds": round(elapsed_total, 4),
        "elapsed_hours": round(elapsed_total / 3600.0, 4),
        "timed_out": timed_out,
        "returncode": rc,
        "supervisor_pid": sup_pid,
        "child_pid": child_pid,
        "rusage_children_maxrss_bytes": int(rusage_children.ru_maxrss),
        "rusage_children_utime_seconds": round(float(rusage_children.ru_utime), 4),
        "rusage_children_stime_seconds": round(float(rusage_children.ru_stime), 4),
        "peak_child_rss_bytes": peak_child_rss,
        "peak_supervisor_rss_bytes": peak_sup_rss,
        "peak_aggregate_rss_bytes": peak_agg_rss,
        "ps_samples": samples,
        "copied_files": copied_files,
        "verify_result": verify_result,
    }
    write_json_atomic(RUN_DIR / "produce.supervisor.json", summary)
    write_json_atomic(RUN_DIR / "status.json", summary)
    return 0 if summary["state"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
