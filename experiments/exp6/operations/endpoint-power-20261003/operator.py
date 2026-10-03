"""Detached operator for the one production endpoint-stage power calculation."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import traceback

ROOT = Path('/Users/michaeljordan/emergence-paper')
OUT = Path('/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode/exp6-endpoint-power-20261003')
DEST = ROOT/'experiments/exp6/operations/endpoint-power-20261003'
PYTHON = '/Users/michaeljordan/emergence-lab/.venv/bin/python'
GIT = '/opt/homebrew/bin/git'
RUNG_SHA = '98750c96dc2affb0e50220610c7964deab672411a2581ed0ea4d72ac6f8fc260'
SEAL_SHA = '5dbe5f2f700b2d64b28cfb6f29c6334eb7c12978b7bbba6051c7e0f7d9508189'
THREAD_VARS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
               'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS')
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def git(*args):
    return subprocess.run([GIT, *args], cwd=ROOT, text=True, capture_output=True,
                          check=True, timeout=180).stdout.strip()

def write(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2)+'\n')
    tmp.replace(path)

def run():
    from experiments.exp6 import battery_6 as b6, power_6 as pw, records_6 as r6
    from experiments.exp6.run import _common_6 as cm, endpoint_6 as ep
    state = {'pid': os.getpid(), 'sid': os.getsid(0), 'started_utc': now(),
             'operator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    current = None
    began = time.monotonic()
    code = 1
    def save(**updates):
        state.update(updates)
        write(OUT/'status.json', state)
    def terminate(signum, frame):
        raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    save(stage='checking-inputs')
    try:
        assert not git('status', '--porcelain'), 'Checkout must be clean at launch'
        assert not r6.power_path(b6.EXP6).exists(), 'Power record already exists; never rerun'
        assert not (b6.EXP6/'results/sweep').exists(), 'Sweep already exists'
        cm.gates()
        seal = ep.require_predictor_seal(b6.EXP6)
        assert seal['sha256'] == SEAL_SHA
        assert r6.sha256_file(r6.rung_sets_path(b6.EXP6)) == RUNG_SHA
        env = {**os.environ, **{k: '1' for k in THREAD_VARS},
               'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUNBUFFERED': '1',
               'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1'}
        args = [PYTHON, '-u', '-m', 'experiments.exp6.power_6', '--jobs', '8']
        save(stage='computing', head=git('rev-parse', 'HEAD'), command=args,
             predictor_sha256=SEAL_SHA, rung_sets_sha256=RUNG_SHA,
             thread_limits={k: env[k] for k in THREAD_VARS}, jobs=8)
        with (OUT/'power.log').open('xb') as log:
            current = subprocess.Popen(args, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                       stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            save(child_pid=current.pid, child_sid=os.getsid(current.pid))
            while True:
                try:
                    rc = current.wait(timeout=180)
                    break
                except subprocess.TimeoutExpired:
                    save(last_alive_utc=now(), elapsed_seconds=time.monotonic()-began)
            current = None
        save(power_exit_code=rc, compute_ended_utc=now(), child_pid=None)
        assert rc == 0, f'Power exited {rc}; inspect power.log, no automatic retry'
        save(stage='validating-record')
        rec = r6.read_json(r6.power_path(b6.EXP6))
        inputs, _ = pw.real_inputs(b6.EXP6)
        bad = pw.claim_failures(rec, inputs)
        assert not bad, bad
        assert rec['predictor_sha256'] == SEAL_SHA
        assert rec['rung_sets_sha256'] == RUNG_SHA == r6.sha256_file(r6.rung_sets_path(b6.EXP6))
        assert rec['git_sha'] == state['head']
        cm.exit_gate(r6.endpoint_halt_path(b6.EXP6))
        summary = {**state, 'stage': 'validated', 'validated_utc': now(),
                   'power_file_sha256': r6.sha256_file(r6.power_path(b6.EXP6)),
                   'verification_failures': bad,
                   'tests': {name: {k: row[k] for k in ('declared_status', 'thin', 'rungs_simulated')}
                             for name, row in rec['tests'].items()},
                   'wall_seconds': time.monotonic()-began}
        write(OUT/'summary.json', summary)
        DEST.mkdir(parents=True, exist_ok=False)
        for name in ('summary.json', 'power.log'):
            shutil.copyfile(OUT/name, DEST/name)
        shutil.copyfile(__file__, DEST/'operator.py')
        paths = [str(r6.power_path(b6.EXP6).relative_to(ROOT))]
        paths += [str((DEST/name).relative_to(ROOT)) for name in ('summary.json', 'power.log', 'operator.py')]
        assert not git('diff', '--cached', '--name-only'), 'Unrelated staged work'
        git('add', '--', *paths)
        git('commit', '-m', 'exp6: record the one endpoint-stage power calculation',
            '-m', 'Production defaults on the real sealed predictors and endpoint rung sets; declarations, inputs and tree re-derived before publication. No sweep or verdict calculation.',
            '-m', 'Agent: OpenAI GPT-6 Astra (OpenCode)')
        git('push', 'origin', 'master')
        head = git('rev-parse', 'HEAD')
        assert git('ls-remote', 'origin', 'refs/heads/master').split()[0] == head
        code = 0
        save(stage='complete-awaiting-endpoint-tag', result_commit=head, summary=summary)
    except BaseException as exc:
        save(stage='error', error=f'{type(exc).__name__}: {exc}')
        traceback.print_exc()
    finally:
        if current is not None and current.poll() is None:
            os.killpg(current.pid, signal.SIGTERM)
            try:
                current.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(current.pid, signal.SIGKILL)
                current.wait()
        save(ended_utc=now(), exit_code=code, child_pid=None, wall_seconds=time.monotonic()-began)
        print(json.dumps(state, indent=2), flush=True)
    return code

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'status.json').exists(), 'Operator already has a run record; inspect it'
    raise SystemExit(run())
