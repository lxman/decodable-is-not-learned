# Experiment 7 Pre-Tag Calibration — Independent Runtime Review

- **Audited Candidate Commit**: `2f081c1f1109922a1778a4fb4d70948606acf600`
- **Governing Specification**: `docs/superpowers/plans/2026-10-04-exp7-annex/integration-v3/RUNTIME-PREPARATION.md` (Sections 1–3)
- **Host / Interpreter**: Darwin arm64, `/Users/michaeljordan/emergence-lab/.venv/bin/python -I -B -X int_max_str_digits=5000` (CPython `3.11.15`, `/opt/homebrew/Cellar/python@3.11/3.11.15_3/Frameworks/Python.framework/Versions/3.11`)
- **Disposition**: `ACCEPT`

## 1. Audited Input Artifacts

| Artifact | Path | Bytes | SHA256 |
|---|---|---:|---|
| Synthetic Cases | `experiments/exp7/calibration/authority/synthetic-cases.json` | `3,945` | `21667d68e26ad0b2d8e329969c2c7d3eb9cccbb0f27ec268f88f69388210d773` |
| Runtime Selection | `experiments/exp7/calibration/authority/runtime-selection.json` | `91,527` | `ef6966cbce9c2bad39bebae34afe39003fc9b4af396dcf0e36175ead7e2996c9` |
| Runtime Proposal | `experiments/exp7/calibration/authority/runtime-proposal.json` | `145,742` | `20b3619f10cd08fbdb44a264b1d65b4c571bf0451dcf5e4655ea7731d42f9207` |

- `synthetic-cases.json` (`schema: "exp7.synthetic-cases.v1"`) was independently recomputed in a cold `-I -B` interpreter and verified byte-for-byte identical to `exp7stats.common.dumps(exp7stats.calibration.frozen_cases())`.
- `runtime-selection.json` (`schema: "exp7.runtime-selection.v1"`) and `runtime-proposal.json` (`schema: "exp7.runtime-proposal.v1"`, `authority: false`, `selection_sha256: ef6966cbce9c2bad39bebae34afe39003fc9b4af396dcf0e36175ead7e2996c9`, `runtime_sha256: 16718b298ca146366b2475235ef106bc1659ec7acdad77f8c2b3fb1ededc64fa`) pass strict JSON decoding without duplicate keys or non-finite constants.

## 2. Independent Runtime Reproduction

All three runtime sections (`files`, `frozen`, `generated`) were independently recomputed from disk and cold interpreter state under `/Users/michaeljordan/emergence-lab/.venv/bin/python -I -B -X int_max_str_digits=5000`:

1. **`roots` and `files` (`215` files total)**:
   - `stdlib` root: `/opt/homebrew/Cellar/python@3.11/3.11.15_3/Frameworks/Python.framework/Versions/3.11/lib/python3.11` (`116` files: `94` `.py` sources and `22` `.so` extension modules).
   - `numpy` root: `/Users/michaeljordan/emergence-lab/.venv/lib/python3.11/site-packages/numpy` (`98` files: `87` `.py` sources and `11` `.so` extension modules).
   - `helper` role: `1` file (`/Users/michaeljordan/emergence-lab/.venv/lib/python3.11/site-packages/_distutils_hack/__init__.py`, loaded by virtual-environment `site` startup).
   - Every selected path is a canonical (`str(Path(p).resolve()) == p`), non-symlink regular file, and every SHA256 digest recomputed from `Path(p).read_bytes()` matches `proposal["runtime"]["files"]` exactly.
   - Zero model, tokenizer, HuggingFace, or network packages (`torch`, `transformers`, `mlx`, `mlx_lm`, `huggingface_hub`, `tokenizers`, `safetensors`, `datasets`, `accelerate`, `socket`, `_socket`, `ssl`, `_ssl`, `http`, `requests`, `httpx`, `aiohttp`, `sentencepiece`, `hf_xet`, `ftplib`, `smtplib`, `websockets`, `boto3`, `botocore`, `paramiko`, `experiments`) appear anywhere in `files`.

2. **`frozen` (`18` modules total)**:
   - Verified `_imp.is_frozen(name)` is `True` and recomputed `exp7stats.candidate_audit.code_hash(_imp.get_frozen_object(name))` for all `18` modules (`_collections_abc`, `_frozen_importlib`, `_frozen_importlib_external`, `_sitebuiltins`, `abc`, `codecs`, `genericpath`, `importlib.machinery`, `importlib.util`, `io`, `ntpath`, `os`, `os.path`, `posixpath`, `runpy`, `site`, `stat`, `zipimport`).
   - Every frozen fingerprint matches `proposal["runtime"]["frozen"]` exactly.

3. **`generated` (`352` `CodeType` fingerprints total)**:
   - Installed `sys.addaudithook` on `"exec"` prior to importing the standard-library, NumPy, and `exp7*` calibration/bootstrap closure, and traversed `code_tree` across all audited `exec` code objects and loaded class `__mro__` methods.
   - Independently reproduced all `352` generated `CodeType` witnesses and verified their pinned Python producers:
     - `/opt/homebrew/Cellar/python@3.11/3.11.15_3/Frameworks/Python.framework/Versions/3.11/lib/python3.11/dataclasses.py`: `297` fingerprints
     - `/opt/homebrew/Cellar/python@3.11/3.11.15_3/Frameworks/Python.framework/Versions/3.11/lib/python3.11/collections/__init__.py`: `54` fingerprints
     - `/opt/homebrew/Cellar/python@3.11/3.11.15_3/Frameworks/Python.framework/Versions/3.11/lib/python3.11/functools.py`: `1` fingerprint
   - Confirmed `reproduced_generated == proposal["runtime"]["generated"]`.

4. **Canonical Runtime Digest**:
   - `digest(canonical(reproduced_runtime)) == "16718b298ca146366b2475235ef106bc1659ec7acdad77f8c2b3fb1ededc64fa" == proposal["runtime_sha256"]`.

## 3. Source Call and Read-Surface Audit

Inspected the calibration and bootstrap call/read surfaces per `RUNTIME-PREPARATION.md` Sections 1 & 3:
- `experiments/exp7/exp7stats/read_boundary.py`: `close_cli_stdin` verifies `stream.fileno() == 0`, closes the stream wrapper, and closes OS descriptor `0` (`EBADF`-safe). `ReadBoundary.cold()` enforces `_thread._count() == 0`, zero inherited readable file descriptors via `/dev/fd` (`fcntl.F_GETFL`), and zero GC-visible OS-backed readable `io.IOBase` streams. All read opens go through `snapshot_bytes` (`O_RDONLY | O_CLOEXEC | O_NOFOLLOW`, `fstat`/`stat` inode/device/size/timestamp identity verification before and after reading, and exact expected SHA256 check) wrapped in `ReadOnlySnapshot`. `native_call` blocks raw descriptor reads (`os.read`, `os.pread`, `os.readv`, `os.preadv`, `os.sendfile`, `os.splice`, `os.copy_file_range`) and `numpy.fromfile`.
- `experiments/exp7/exp7stats/candidate_audit.py`: `CandidateAudit` enforces exact SHA256 pins across all candidate and runtime files, verifies loaded modules and frozen objects, compiles pinned `.py` sources on demand to populate `allowed_codes`, blocks `sys.setprofile` replacement, blocks `subprocess.Popen` / `os.system` / `os.posix_spawn` / `os.fork` / `mmap.__new__` inside the audited block, and rejects any existing `.pyc` bytecode cache files.
- `experiments/exp7/exp7stats/calibration_context.py`: `CalibrationContext` enforces absence of `refs/tags/exp7-preregistered`, requires the calibration output root to be outside the repository, verifies every file in `exp7.calibration-candidate.v1` against both the working tree and committed Git blobs via `/opt/homebrew/bin/git -C <repo> show <commit>:<path>`, checks full source closure across `exp7stats` and `exp7core`, and wraps execution in `CandidateAudit`.
- `experiments/exp7/exp7stats/calibration_cli.py`: Blocks model/network/`experiments` imports at module load via `builtins.__import__`, `sys.meta_path`, and `sys.addaudithook` (allowing only read-only `/opt/homebrew/bin/git` `show`/`rev-parse` subprocesses outside `CandidateAudit`), sets `sys.dont_write_bytecode = True`, and closes `sys.stdin` via `close_cli_stdin` prior to constructing `CalibrationContext`.
- `experiments/exp7/exp7integration/bootstrap.py` & `experiments/exp7/run/calibration_7.py`: `calibration_7.py` requires an explicit `--site-sha256` CLI argument, verifies `site_7.json`, `config_path`, and all `source_pins` before exposing the repository on `sys.path`, installs `_BoundRepositoryImports` on `sys.meta_path`, imports `exp7stats.calibration_cli` before integration modules, and dispatches to `bootstrap.calibration_entry`, which closes `sys.stdin` via `close_cli_stdin` and constructs the default real `CalibrationContext`.

## 4. Disposition

`ACCEPT` — The runtime proposal `20b3619f10cd08fbdb44a264b1d65b4c571bf0451dcf5e4655ea7731d42f9207` (`runtime_sha256: 16718b298ca146366b2475235ef106bc1659ec7acdad77f8c2b3fb1ededc64fa`) is independently reproduced and approved for immutable runtime materialization via `accept_reviewed_runtime`.
