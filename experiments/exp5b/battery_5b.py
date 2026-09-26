# experiments/exp5b/battery_5b.py
"""The Exp 5b battery (design `experiment-5b-design.md` §3, §10 as ruled):
every input a committed value or a pin over Experiment 5's closed record.
Nothing here is a dial. Zero network: the checkpoint manifest is
Experiment 5's (`battery_5.load_manifest_5`, sha-pinned)."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

EXP5B = Path(__file__).resolve().parent
EXPERIMENTS = EXP5B.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401 — the BLAS pin, before numpy
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402

EXP5 = b5.EXP5
RESULTS_5B = EXP5B / "results"
PROJECTION_PATH_5B = EXP5B / "projection.md"

PREREG_TAG_5B = "exp5b-preregistered"
CLOSED_TAG_5B = "exp5b-closed"
INSTRUMENT_BLOBS_5B = (
    "experiments/exp5b/battery_5b.py", "experiments/exp5b/stats_5b.py",
    "experiments/exp5b/collect_5b.py", "experiments/exp5b/analyze_5b.py",
    "experiments/exp5b/power_5b.py", "experiments/exp5b/run/units_5b.py",
    "experiments/exp5b/results/power_5b.json",
)
EXP5_CLOSED_TAG_5B = "exp5-closed"
EXP5_VERDICT_REL_5B = "experiments/exp5/results/verdict.json"
# `shasum -a 256 experiments/exp5/results/verdict.json` at the build (Task 1, step 4)
EXP5_VERDICT_SHA256_5B = "50a6f57e8e4b204adf83d84890fb19cb78eec495a977861e0f6a4cca26d61f11"
# design §3.6 gate 2: the literal subset of Experiment 5's verdict
EXP5_VERDICT_PIN_5B = {
    "verdict": "NOT-MATCHED", "modifier": "MIXED", "T": 0.05349206349206348,
    "n_cells": 63, "n_rungs": 13, "rung_block_p": 0.0006103515625,
    "n_nonzero_blocks": 13, "pairs_kept": 21,
}

# ------------------------------------------------------- the small-side window
WINDOW_STEPS_5B = (142000, 141000, 140000)             # dial b
SIZE_ORDER_5B = ("6.9b", "2.8b", "1.4b", "1b", "410m", "160m")   # dial n
WHYS_5B = ("final", "member")


def small_sides_5b() -> tuple:
    """Read at call time — the synthetic worlds shrink `battery_5.SMALL_SIDES_5`."""
    return tuple(b5.SMALL_SIDES_5)


def unit_steps_5b() -> tuple:
    return (b5.FINAL_STEP_5,) + tuple(WINDOW_STEPS_5B)


def reread_steps_5b() -> tuple:
    """Gate 1's twelve: the final and the first member (Experiment 5's S11 step)."""
    return (b5.FINAL_STEP_5, WINDOW_STEPS_5B[0])


def expected_units_5b() -> set:
    return {(s, st) for s in small_sides_5b() for st in unit_steps_5b()}


# ------------------------------------------------------------ the statistic
PLACEBO_SIGN_5B = 1                                    # dial e: the two moves ADDED
SQRT2_5B = math.sqrt(2.0)
SIGMA_GRID_5B = (5, 10, 15, 20, 30, 45)                # dial h, items per read
SIGMA_BELIEF_5B = 15
ALPHA_CAL_5B = 0.05
LOSS_TOL_5B = 1e-4                                      # gate 1: |Δℓ| on a re-read
SPIKE_PAIR_5B = ("2.8b", "12b")                         # S9
T_BAR_5B = b5.T_BAR_5
ALPHA_5B = b5.ALPHA_5
MIN_LIVE_CELLS_5B = b5.MIN_LIVE_CELLS_5
MIN_NONZERO_BLOCKS_5B = b5.MIN_NONZERO_BLOCKS_5
WORLDS_5B = ("INSUFFICIENT_DATA", "UNDETERMINED", "SURVIVES", "NOT-SURVIVED")
SURVIVES_CELLS_5B = ("CALIBRATED", "INFLATED", "OFF-GRID")
NOT_SURVIVED_CELLS_5B = ("INSIDE", "SIGN-ONLY", "SIZE-ONLY")
# Experiment 5's post-verdict descriptives (results/retrospective.md), printed beside S1/S3/S9
EXP5_REFERENTS_5B = {"row_2p8b_mean_c": 0.117, "outside_2p8b_and_antonyms_T": 0.0112,
                     "outside_2p8b_and_antonyms_p": 0.084, "spike_excluded_T": 0.0417,
                     "spike_excluded_p": 0.00037, "P_mean_items": 12.4, "P_sd_items": 13.6,
                     "mean_R_items": 39.1, "T_exp5_items": 26.7}


# ------------------------------------------------------------------- paths

def units_root_5b(root) -> Path:
    return Path(root) / "results" / "units"


def unit_dir_5b(root, size: str, step: int) -> Path:
    return b5.unit_dir_5(root, size, step)


def unit5b_record_path_5b(root, size, step) -> Path:
    return unit_dir_5b(root, size, step) / "_unit_5b.json"


def host_record_path_5b(root) -> Path:
    return Path(root) / "results" / "host_5b.json"


def gate1_path_5b(root) -> Path:
    return Path(root) / "results" / "gate1_5b.json"


def power_path_5b(root) -> Path:
    return Path(root) / "results" / "power_5b.json"


def halt_marker_path_5b(root, size) -> Path:
    return b5.halt_marker_path_5(root, size)


def unit_complete_5b(root, size, step) -> bool:
    """Experiment 5's completeness (`_unit.json` present and every named
    file at its sha) AND 5b's attestation file, written after it."""
    return b5.unit_complete_5(root, size, step) and unit5b_record_path_5b(root, size, step).is_file()


REREAD_KEYS_5B = ("digest_equal", "digest_here", "digest_committed", "loss_here", "loss_committed",
                  "loss_delta", "per_doc_diffs", "count_abs_diff_sum", "count_abs_diff_max",
                  "continuation_diffs_sum", "byte_identical", "tolerance_failures", "loss_within_tol")


def unit5b_record_failures_5b(rec: dict, *, size, step, host) -> list:
    bad = []
    label = f"{size}/step{int(step)}/_unit_5b"
    for k, v in (("size", size), ("step", int(step)), ("prereg_tag", PREREG_TAG_5B),
                 ("exp5_closed_tag", EXP5_CLOSED_TAG_5B)):
        if rec.get(k) != v:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {v!r}")
    if rec.get("why") not in WHYS_5B:
        bad.append(f"{label}: why {rec.get('why')!r} not in {WHYS_5B}")
    elif rec.get("why") != ("final" if int(step) == b5.FINAL_STEP_5 else "member"):
        # Freeze C-4 (Task 1's deferred minor): `why` is "final" iff the step is the final
        bad.append(f"{label}: why {rec.get('why')!r} does not match step {int(step)}")
    want_reread = int(step) in reread_steps_5b()
    if rec.get("reread") is not want_reread:
        bad.append(f"{label}: reread {rec.get('reread')!r}, expected {want_reread}")
    rr = rec.get("reread_record")
    if want_reread:
        if not isinstance(rr, dict) or any(k not in rr for k in REREAD_KEYS_5B):
            bad.append(f"{label}: reread_record missing or lacks {REREAD_KEYS_5B}")
    elif rr is not None:
        bad.append(f"{label}: reread_record present on a non-re-read unit")
    if rec.get("host_sha256") != host.get("sha256"):
        bad.append(f"{label}: host_sha256 is not the host record's")
    if not isinstance(rec.get("git_sha"), str) or not rec.get("git_sha"):
        bad.append(f"{label}: git_sha missing")
    return bad


def exp5_unit_record_5b(exp5_root, size, step, name: str) -> dict:
    """One of Experiment 5's committed unit files, read-only."""
    p = b5.unit_dir_5(exp5_root, size, step) / name
    if not p.is_file():
        raise FileNotFoundError(p)
    return json.loads(p.read_text())


# ---------------------------------------------------------------- bindings

def require_prereg_5b(*, tag_exists=None, blob_sha=None, blobs=INSTRUMENT_BLOBS_5B) -> dict:
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(PREREG_TAG_5B):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_5B} does not exist")
    bound = {}
    for rel in blobs:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(PREREG_TAG_5B, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {PREREG_TAG_5B} does not bind {rel}: tag "
                               f"{str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    return {"tag": PREREG_TAG_5B, "instrument_blobs": bound}


def require_exp5_closed_5b(*, tag_exists=None, blob_sha=None, verdict_sha=None,
                           exp5_root=None) -> dict:
    """Design §3.6 gate 2: `exp5-closed` present, Experiment 5's thirteen
    instrument blobs at that tag equal to disk, and the committed
    verdict.json at its pin (`verdict_sha=False` skips the sha — the
    synthetic worlds' Experiment 5 tree)."""
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(EXP5_CLOSED_TAG_5B):
        raise RuntimeError(f"tag {EXP5_CLOSED_TAG_5B} does not exist")
    bound = {}
    for rel in b5.INSTRUMENT_BLOBS_5:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(EXP5_CLOSED_TAG_5B, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {EXP5_CLOSED_TAG_5B} does not bind {rel}: tag "
                               f"{str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    got_v = None
    if verdict_sha is not False:
        want_v = EXP5_VERDICT_SHA256_5B if verdict_sha is None else verdict_sha
        vp = (Path(exp5_root) / "results" / "verdict.json") if exp5_root is not None \
            else REPO / EXP5_VERDICT_REL_5B
        if not vp.is_file():
            raise RuntimeError(f"{vp}: Experiment 5's verdict.json is missing")
        got_v = hashlib.sha256(vp.read_bytes()).hexdigest()
        if got_v != want_v:
            raise RuntimeError(f"verdict.json hashes to {got_v[:12]}, pinned {str(want_v)[:12]}")
    return {"tag": EXP5_CLOSED_TAG_5B, "blobs": bound, "verdict_sha256": got_v}


def exp5_verdict_pin_failures_5b(v5: dict, pin=None) -> list:
    """The literal subset (design §3.6 gate 2); `pin=None` → the module's;
    the worlds pass their own or skip by setting the module pin to None."""
    pin = EXP5_VERDICT_PIN_5B if pin is None else pin
    if pin is None:
        return []
    bad = []
    prim = v5.get("primary") or {}
    rb = prim.get("rung_block") or {}
    checks = (("verdict", v5.get("verdict"), pin["verdict"]),
              ("modifier", (v5.get("tree") or {}).get("modifier"), pin["modifier"]),
              ("T", repr(prim.get("T")), repr(pin["T"])),
              ("n_cells", prim.get("n_cells"), pin["n_cells"]),
              ("n_rungs", prim.get("n_rungs"), pin["n_rungs"]),
              ("rung-block p", repr(rb.get("p")), repr(pin["rung_block_p"])),
              ("n_nonzero_blocks", prim.get("n_nonzero_blocks"), pin["n_nonzero_blocks"]),
              ("pairs_kept", (v5.get("gate4") or {}).get("pairs_kept"), pin["pairs_kept"]))
    for name, got, want in checks:
        if got != want:
            bad.append(f"exp5 verdict pin: {name} = {got!r}, pinned {want!r}")
    return bad


def _strip_volatile(v: dict) -> dict:
    out = dict(v)
    out.pop("meta", None)
    out.pop("pins_active", None)
    return out


def exp5_verdict_equal_failures_5b(rederived: dict, committed: dict) -> list:
    a, b = _strip_volatile(rederived), _strip_volatile(committed)
    if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True):
        return []
    for k in sorted(set(a) | set(b)):
        if json.dumps(a.get(k), sort_keys=True) != json.dumps(b.get(k), sort_keys=True):
            return [f"exp5 verdict: the re-derived record differs from the committed one at "
                    f"key {k!r} (meta and pins_active excluded)"]
    return ["exp5 verdict: the re-derived record differs from the committed one"]


# ------------------------------------------------------------ frozen pins
# Built by `tests/import_scan_5b.py` (run() on the real pre-campaign tree,
# every 5b stage tool pulled in by hand); pasted verbatim, never hand-edited.
FROZEN_SHA256_5B = {
    REPO / "experiments/exp1/signatures/stats.py":
        "ceab3eb7f6daf9346b9231f0e4af7e458b43ba4e7361556aef926e1abde2611f",
    REPO / "experiments/exp2b/models.py":
        "a4c5eed26cc92044aeb9ed7b68b177035de3ac2615dbba09a6d21eeb191a55a4",
    REPO / "experiments/exp2b/probe_starved.py":
        "e6c81df28e4a7e07db3a123e4b06d3c8a98a7d330cd726596d41b1136c4cd27b",
    REPO / "experiments/exp2b/splits.py":
        "49df4c62c3c3bd611b9cf49be46001c12220045a3611a39be5e2bc5b89ded6e0",
    REPO / "experiments/exp2c/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2c/battery/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2c/battery/base.py":
        "6d77c3c91c5ca0eb84e1a011ef64af0e04ade6fe8d1ad42d526be3a37fbacbb2",
    REPO / "experiments/exp2c/battery/family_map.py":
        "46477b37683c8ea0e1f2f219dce96858a0dcf91710b15cae45a8cf4c4c7ab375",
    REPO / "experiments/exp2c/battery/generators_controls.py":
        "baab6da475f90f8c07acb6d1eb317484bf36afeb40705684f43ecd5ec9fdade6",
    REPO / "experiments/exp2c/battery/generators_rescues.py":
        "d70215c89ffd58d3f18f9dcd99940c7e92655ba8185919f50b2090b7e900c257",
    REPO / "experiments/exp2c/battery/generators_rungs.py":
        "778bf30da104f71773c26aa909ef2fddcd81291676a2db5d30130581b8d162d0",
    REPO / "experiments/exp2c/battery/wordlists_2c.py":
        "f46c6092d6429a59b95531d1a58b1bbfc0576d692d1162b8dfd2b6daf051790f",
    REPO / "experiments/exp2c/harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    REPO / "experiments/exp2c/instrument.py":
        "c486213bfa4753a83593b5383e2c0c90a6379b156f59a236ceeac7d68961e052",
    REPO / "experiments/exp2c/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2c/run/power_table.py":
        "89816cf0e7e2418e748104dbc32fd50e12ded78988f2c2c04b05ff1a89c58da1",
    REPO / "experiments/exp2c/run/screen.py":
        "fef1814142955912066837fbd2119f5c2ae27fe31393ede890584313e2b06873",
    REPO / "experiments/exp2c/stats_bounds.py":
        "39057433f1d67cbbf803141dc25ee36cda9e96270b0634006c0fcab245ee49f8",
    REPO / "experiments/exp2d/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2d/analyze_2d.py":
        "01ee334db5fe273a8509cf4bf79757b52a40a123311acd42554ac1a82e40334a",
    REPO / "experiments/exp2d/battery_2d.py":
        "503a2c09ec320989223561291ff93c71d62d27ed20c5681f9b2d535b7708e81a",
    REPO / "experiments/exp2d/stats_2d.py":
        "86243932709013ea15b250e9bf15243ce6209e03e6bcf81af0f7ac3f92644b46",
    REPO / "experiments/exp2f/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2f/analyze_2f.py":
        "79018ff34b6f41bd2a5e8fa0f922a2de567861750057a5eca1a3dad6cf3f61d3",
    REPO / "experiments/exp2f/collect_eval_2f.py":
        "189e3738471185b7205f106fdac9bc5da1d564caafc60e39f4d6e3546915d071",
    REPO / "experiments/exp2f/labels_2f.py":
        "8dc31850e5c47b7a1cc171b0388521ebe01005ddc123954c0073734cf9aaac25",
    REPO / "experiments/exp2f/make_referents_2f.py":
        "c08eec5cea9f49a05c6754c84b81e1cb8560537881b002faee02bcf085af1c10",
    REPO / "experiments/exp2f/probe_2f.py":
        "63c714d6e899dd9d6d5610a3d54c9254ec0749d03f44a703790d4a4354854f62",
    REPO / "experiments/exp2g/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2g/analyze_2g.py":
        "eab7c5b91d57351ee2a7adb0e85d71cb92cb4d6ed15d0bb90150c95c2076050e",
    REPO / "experiments/exp2g/battery_2g.py":
        "aca79dd71ee7dead3c0ce065945bb38eaf1b0b72b5d5f40698dabb0f5a9cf3c1",
    REPO / "experiments/exp2g/checkpoints_2g.py":
        "155fee3ec3933db33930d7ddadb99c02604d893205a8f8c037016cc18609fb10",
    REPO / "experiments/exp2g/collect_eval_2g.py":
        "392ab84e2bac360bf041858a4b991824a3bda9ca414e34d0f84e44b22610efaf",
    REPO / "experiments/exp2g/labels_2g.py":
        "d86e7cdb4dcc10257986e8a85824365972a75ba993be5a8fde8a825d68e3077d",
    REPO / "experiments/exp2g/predictor_2g.py":
        "3381b43a34fd1fb1f7ef57eb9d02a6a9e9ec41b3ffcadea425c37b86c1e92a4e",
    REPO / "experiments/exp2g/probe_2g.py":
        "63abc9e6518ac1ab53e4a70e0c716bccd357a11ea3fc2733de52e2ec4e23d451",
    REPO / "experiments/exp2g/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2g/run/sweep_2g.py":
        "850db5831adeffc46a888ca185ef3f1ad819a8db104c9eafd1df69c470c91a87",
    REPO / "experiments/exp2g/stats_2g.py":
        "cf3c4c89c86fa43c5ba49d5c4be12eabad28ac65d9d12a43b1e31ef6e4bc195f",
    REPO / "experiments/exp2g/strata_2g.py":
        "ea0acbbdfde13655a6b89d3afcc981f348ee6312b4448b70d437f1e4d3f7f594",
    REPO / "experiments/exp2h/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2h/analyze_2h.py":
        "52733e8d4280fb41b76cda2dcac024299ce7dd61090f856ba3147c8098b871bf",
    REPO / "experiments/exp2h/battery_2h.py":
        "2d721cf85bbd85937f45a1135e8b5e102685ab424d8ab0dfada527bd8ab4e80a",
    REPO / "experiments/exp2i/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2i/analyze_2i.py":
        "85e482fea17e0706476243a0a98a7d2c32efebd6536c5255ae48e729b494c252",
    REPO / "experiments/exp2i/battery_2i.py":
        "e0a8d10cb4dde8a3af1a3e9b32447c407b43201513dc758d6cd9a8c38b5cdfcf",
    REPO / "experiments/exp3/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp3/analyze_3.py":
        "aa0cb2374fbdffde2f9eaae26cee1ce51f9f42c0b32fd89f4f8754c983a92274",
    REPO / "experiments/exp3/sampler.py":
        "e33c50d3985b1d6205d886e53726860f364cce1c6cd943ec460524e9110a03ea",
    REPO / "experiments/exp3c/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp3c/analyze_3c.py":
        "66b78ffbedb808625ed33019f29d2ef8ec9d0f31a1115eb7cb08ad3e67d42d84",
    REPO / "experiments/exp5/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp5/_threads_5.py":
        "d03346e66b09f005e56e4e2c0c7dabdfb36db3d44d3ed4c3c5f7ae6874d33447",
    REPO / "experiments/exp5/analyze_5.py":
        "8263ba54efa778faf07f73d45af75353083a4c8781ff88ac6722a89f57a2b338",
    REPO / "experiments/exp5/battery_5.py":
        "de22cb14485eaae4cce74e2db48407138484f6f04dcdd06c5b3618b3cfd5e582",
    REPO / "experiments/exp5/collect_5.py":
        "62cc4996b528aa5eeadccab3afc89745676e87ac847e3b856fcc67e5cc213024",
    REPO / "experiments/exp5/make_referents_5.py":
        "76d5d959197cfb8dabd97b6dbf0aaffdeba3c4324e957fd4a946c81c25a97a2c",
    REPO / "experiments/exp5/power_5.py":
        "f083429ec771c09f0660a0270149e2159e5d4a70f8718bf1648d1370ae7b2912",
    REPO / "experiments/exp5/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp5/run/preflight_5.py":
        "f32e8c36d9aad0ba05b64a17ac66f3d120b37fe9cb8e568c049ae65284990821",
    REPO / "experiments/exp5/search_5.py":
        "4b32e041b65a7359d9dda0a9c4ad17ee0f76e185a5aea7c07070d6b7fe6a66bf",
    REPO / "experiments/exp5/slice_5.py":
        "5b43b3d0c4a6b87f9ba710c692c2200f0894ce8db90d4eb66567641072cf8cb6",
    REPO / "experiments/exp5/stats_5.py":
        "3fc6f04f669d7fe106121e7f2cd38597c84dc2d88325bb25ec62291b63e08683",
    REPO / "experiments/exp5/verify_referents_5.py":
        "c7468181d347abbd9171536fe202f1267c56687e748496f822f908930c9c1550",
}

IMPORTED_SHA256_5B = {
    REPO / "experiments/exp5b/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp5b/make_referents_5b.py":
        "19013817873683ee916503de9b646020cc9a5d5d071f86fbe7a2939abb6aa013",
    REPO / "experiments/exp5b/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp5b/run/preflight_5b.py":
        "67b4c42083085d2282d8b1818b0709253bacd5643b7a1459762a3f8a24f79377",
    REPO / "experiments/exp5b/verify_referents_5b.py":
        "b1a8da4c0d56ccfd1da5c12bb76214b9f8eab53942026a1b86e1f6001b12f168",
}


def check_frozen_5b() -> None:
    if FROZEN_SHA256_5B is None:
        raise RuntimeError("FROZEN_SHA256_5B is None — not pinned (build incomplete)")
    bad = [f"{p}" for p, want in FROZEN_SHA256_5B.items()
           if not Path(p).is_file() or bg.sha256_file(p) != want]
    if bad:
        raise RuntimeError("5b: a frozen module drifted from its pin: " + "; ".join(bad))


def check_imports_5b() -> None:
    """Lesson 11 (2j F-1): every module under `experiments/` this process
    has imported (tests excluded) is pinned — `FROZEN_SHA256_5B`
    (drift-checked), an `INSTRUMENT_BLOBS_5B` file, or `IMPORTED_SHA256_5B`
    (drift-checked). Experiment 5's modules are in FROZEN_SHA256_5B."""
    if IMPORTED_SHA256_5B is None or FROZEN_SHA256_5B is None:
        raise RuntimeError("the import surface is not pinned (build incomplete)")
    pinned = {str(Path(p).resolve()): v for p, v in FROZEN_SHA256_5B.items()}
    pinned |= {str(Path(p).resolve()): v for p, v in IMPORTED_SHA256_5B.items()}
    covered = {str((REPO / rel).resolve()) for rel in INSTRUMENT_BLOBS_5B}
    drifted, unpinned = [], []
    for p, want in sorted(pinned.items()):
        pp = Path(p)
        if not pp.is_file() or bg.sha256_file(pp) != want:
            drifted.append(f"(pin) -> {p}")
    exp_root = str((REPO / "experiments").resolve())
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rp = Path(f).resolve()
        s = str(rp)
        if not s.startswith(exp_root + "/") or "tests" in rp.parts:
            continue
        if s in covered or s in pinned:
            continue
        unpinned.append(f"{name} -> {s}")
    if unpinned:
        raise RuntimeError("unpinned module on the import surface: " + "; ".join(sorted(unpinned)))
    if drifted:
        raise RuntimeError("imported module drifted from its pin: " + "; ".join(sorted(drifted)))


# ------------------------------------------------------------------- git

def git_sha_5b() -> str:
    return b5.git_sha_5()


def is_ancestor_5b(a: str, b: str) -> bool:
    return b5.is_ancestor_5(a, b)


def projection_commit_5b():
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--",
                          "experiments/exp5b/projection.md"], cwd=REPO,
                         capture_output=True, text=True)
    lines = [ln for ln in out.stdout.strip().splitlines() if ln]
    return lines[-1] if lines else None


def projection_edits_5b(adding_commit: str, *, repo=None) -> list:
    """Experiment 5's F-5, for 5b's projection: every commit after the
    adding commit that touches it, plus a working-tree drift."""
    repo = REPO if repo is None else Path(repo)
    rel = "experiments/exp5b/projection.md"
    out = []
    later = subprocess.run(["git", "log", "--format=%H", f"{adding_commit}..HEAD", "--", rel],
                           cwd=repo, capture_output=True, text=True)
    if later.returncode != 0:
        return [f"projection: git log {adding_commit}..HEAD failed: {later.stderr.strip()[:120]}"]
    out += [f"projection: commit {c} modifies {rel} after its adding commit {adding_commit}"
            for c in later.stdout.split() if c]
    want = subprocess.run(["git", "rev-parse", f"{adding_commit}:{rel}"], cwd=repo,
                          capture_output=True, text=True).stdout.strip()
    got = subprocess.run(["git", "hash-object", str(repo / rel)], cwd=repo,
                         capture_output=True, text=True)
    if got.returncode != 0 or not want or got.stdout.strip() != want:
        out.append(f"projection: the working-tree {rel} ({got.stdout.strip()[:12] or 'missing'}) "
                   f"is not the blob its adding commit added ({want[:12] or 'none'})")
    return out


def prereg_tag_commit_5b():
    out = subprocess.run(["git", "rev-list", "-n", "1", PREREG_TAG_5B], cwd=REPO,
                         capture_output=True, text=True)
    sha = out.stdout.strip()
    return sha or None
