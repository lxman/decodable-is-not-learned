"""One descriptive run and saved-output audit; detached from the tool shell."""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone

ROOT = Path('/Users/michaeljordan/emergence-paper')
HERE = Path(__file__).resolve().parent
STATUS = HERE / 'status.json'
PYTHON = '/Users/michaeljordan/emergence-lab/.venv/bin/python'
GIT = '/opt/homebrew/bin/git'

def now():
    return datetime.now(timezone.utc).isoformat()

state = {'pid': os.getpid(), 'sid': os.getsid(0), 'started_utc': now(),
         'stage': 'waiting-for-monitor', 'analyzer_invocations': 0}
lock = threading.Lock()
stop = threading.Event()

def save():
    with lock:
        state['heartbeat_utc'] = now()
        temp = STATUS.with_suffix('.tmp')
        temp.write_text(json.dumps(state, indent=2) + '\n')
        temp.replace(STATUS)

def heartbeat():
    while not stop.wait(30):
        save()

with (HERE / 'started-once').open('x') as marker:
    marker.write(now() + '\n')
save()
thread = threading.Thread(target=heartbeat, daemon=True)
thread.start()
code = 1
try:
    deadline = time.monotonic() + 180
    while not (HERE / 'monitor-ready').exists():
        if time.monotonic() > deadline:
            raise RuntimeError('Monitor registration was not released within 180 seconds')
        time.sleep(.2)
    state['launch_commit'] = subprocess.check_output(
        [GIT, 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    state['stage'] = 'analysis'
    state['analyzer_invocations'] = 1
    state['analysis_started_utc'] = now()
    save()
    with (HERE / 'analysis.log').open('xb') as log:
        result = subprocess.run([PYTHON, 'analyses/matched-token/analyze.py'],
                                cwd=ROOT, stdin=subprocess.DEVNULL,
                                stdout=log, stderr=subprocess.STDOUT)
    state['analysis_exit_code'] = result.returncode
    state['analysis_finished_utc'] = now()
    if result.returncode:
        raise RuntimeError(f'Analysis refused/failed with exit {result.returncode}')
    state['stage'] = 'saved-output-verification'
    save()
    with (HERE / 'verification.log').open('xb') as log:
        result = subprocess.run([PYTHON, 'analyses/matched-token/verify_outputs.py'],
                                cwd=ROOT, stdin=subprocess.DEVNULL,
                                stdout=log, stderr=subprocess.STDOUT)
    state['verification_exit_code'] = result.returncode
    if result.returncode:
        raise RuntimeError(f'Saved-output verification failed with exit {result.returncode}')
    state['stage'] = 'complete'
    code = 0
except Exception as exc:
    state['stage'] = 'failed'
    state['error'] = str(exc)
finally:
    stop.set()
    thread.join()
    state['exit_code'] = code
    state['finished_utc'] = now()
    save()
sys.exit(code)
