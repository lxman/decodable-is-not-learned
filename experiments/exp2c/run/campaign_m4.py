"""M4 eval campaign for 2c: argmax on the eval sizes, the scale-ascent
outcome (design §3 eval side, §6 M4).

Usage:
    python -m run.campaign_m4 <size> <trained|untrained> [capability ...]

size            2.8b | 6.9b | 12b  — the LOCKED side. M4 is the first
                time this program queries a 2.8b+ model, and it refuses
                to start unless the Stage 1 tag exists.
trained         pretrained weights at the ledgered SHA
untrained       seeded random init, same architecture — the EMPIRICAL
                chance floor the ascent score normalizes against
                (design §3: "empirical untrained floors"), seed 0

Scope differs from M1 deliberately. M1 measured the new pool only,
because the survivors' M1 record carries from 2b. M4 measures ALL 34
scored rungs: a survivor with no ascent score has no outcome, and the
primary statistic is a rank correlation over the whole battery.

The 12 carried survivors have no item file and no SPECS entry on the 2c
side — they live in exp2b's frozen tree. They are loaded through
`reuse_manifest.json` and sha-verified on every load, because the reuse
declaration ("survivor items verbatim from the 2b tagged record",
design §7) is what makes their carried probe fits comparable. Their
`answer_type` rides inside the 2b item file; 2c's own rungs take it
from the SPECS registry, via `harness.load_items`.

One result JSON per (size, mode, capability) under results/m4/;
existing results are skipped (process rule 7: durable + resumable).
Model loading goes through exp2b's pinned models.py via the instrument
sys.path shim — same SHAs, same fp16/MPS policy, no second loader to
drift. Scoring is `harness.evaluate_argmax`, i.e. 2b's prompt/normalize/
verify semantics verbatim, which is what makes 410m/1b/2.8b/6.9b/12b
numbers commensurable.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

# ORDER IS LOAD-BEARING in the bare-import branch: 2c's battery package
# must enter sys.modules BEFORE the instrument shim prepends exp2b to
# sys.path, or `battery` resolves to exp2b's (which has no family_map /
# generators_controls). The package-relative branch is immune — the
# dotted path pins which `battery` is meant — but keeps the same order
# so the two branches cannot drift.
try:  # experiments.exp2c.run.campaign_m4 (pytest / absolute import)
    from ..battery.family_map import (REUSED_FAMILIES,
                                      scored_battery_families)
    from ..harness import HFRunner, evaluate_to_file, load_items
    from .. import instrument  # noqa: F401  (puts exp2b on sys.path)
except ImportError:  # pragma: no cover - `python -m run.campaign_m4`
    from battery.family_map import REUSED_FAMILIES, scored_battery_families
    from harness import HFRunner, evaluate_to_file, load_items
    import instrument  # noqa: F401

import models  # exp2b's pinned loader, reached through the shim above

EXP_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = EXP_DIR.parent.parent
RESULTS = EXP_DIR / "results"

EVAL_SIZES = models.EVAL_SIZES
# Floor first, within each size: it is cheap (random init, no download)
# and every trained number is normalized against it, so a size whose
# floor is missing yields no ascent score. campaign_m4.sh executes this
# same order — the declared plan and the driver must not disagree.
MODES = ("untrained", "trained")
UNTRAINED_SEED = 0
STAGE1_TAG = "exp2c-stage1"


# -------------------------------------------------------- the two-stage lock

def _git_tag_exists(tag: str) -> bool:
    out = subprocess.run(["git", "tag", "--list", tag],
                         cwd=REPO_ROOT, capture_output=True, text=True)
    return tag in out.stdout.split()


def require_stage1_tag(tag_exists=_git_tag_exists) -> None:
    """The lock in code, not just in discipline.

    The design's commitment is that no eval-side model is queried before
    Stage 1 is committed AND tagged. Enforcing it here means the record
    shows the runner could not have been used early, rather than asking
    a reader to take that on trust."""
    if not tag_exists(STAGE1_TAG):
        raise RuntimeError(
            f"refusing to query an eval-side model: the Stage 1 tag "
            f"{STAGE1_TAG!r} does not exist. The two-stage lock requires "
            f"the predictor to be committed and tagged first.")


def check_size(size: str) -> None:
    assert size in EVAL_SIZES, \
        f"M4 runs eval sizes only {EVAL_SIZES}, not {size!r}"


# ------------------------------------------------------------ item loading

def eval_capability_names() -> list[str]:
    """Every scored rung — new pool AND carried survivors."""
    return sorted(scored_battery_families())


def _survivor_entry(name: str) -> dict:
    manifest = json.loads((RESULTS / "reuse_manifest.json").read_text())
    return manifest["survivors"][name]["item_file"]


def _load_survivor(name: str, entry: dict | None = None) -> dict:
    """Load a carried survivor's items from exp2b's frozen tree, verified
    against the manifest hash."""
    entry = entry or _survivor_entry(name)
    path = REPO_ROOT / entry["path"]
    raw = path.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != entry["sha256"]:
        raise RuntimeError(
            f"{name}: sha256 mismatch against the reuse manifest "
            f"({got[:12]} != {entry['sha256'][:12]}) — the 2b record this "
            f"rung's probe fits were carried from has changed")
    cap = json.loads(raw)
    cap.setdefault("name", name)
    return cap  # 2b item files carry answer_type inline


def load_capability(name: str) -> dict:
    """Survivor-aware item loading. 2c rungs take answer_type from the
    SPECS registry; survivors carry it in the file."""
    if name in REUSED_FAMILIES:
        return _load_survivor(name)
    return load_items(name)


# ------------------------------------------------------------- the plan

def result_path_for(size: str, mode: str, cap_name: str) -> Path:
    """results/m4/<size>_<mode>/<cap>.json — the durable, resumable unit."""
    return RESULTS / "m4" / f"{size}_{mode}" / f"{cap_name}.json"


def campaign_plan() -> list[tuple[str, str, str]]:
    """(size, mode, capability) for the whole campaign, cheapest size
    first so 2.8b and 6.9b land before 12b, the long pole, starts."""
    caps = eval_capability_names()
    return [(size, mode, cap)
            for size in EVAL_SIZES for mode in MODES for cap in caps]


def remaining(plan=None) -> list[tuple[str, str, str]]:
    plan = plan if plan is not None else campaign_plan()
    return [c for c in plan if not result_path_for(*c).exists()]


# ------------------------------------------------------------- running

def run(size: str, mode: str, caps: list[str] | None = None) -> None:
    require_stage1_tag()
    check_size(size)
    assert mode in MODES, f"mode must be one of {MODES}, not {mode!r}"
    caps = caps or eval_capability_names()

    runner = None

    def runner_factory():
        nonlocal runner
        if runner is None:
            tok, model = models.load_pythia(
                size, untrained=(mode == "untrained"), seed=UNTRAINED_SEED)
            runner = HFRunner(tok, model)
        return runner

    meta = {"size": size, "mode": mode, "sha": models.PYTHIA_SHAS[size],
            "untrained_seed": UNTRAINED_SEED if mode == "untrained" else None,
            "stage1_tag": STAGE1_TAG}
    for name in caps:
        r = evaluate_to_file(runner_factory, load_capability(name),
                             result_path_for(size, mode, name), meta)
        print(f"[m4] {size}/{mode}/{name}: acc={r['acc']:.4f} "
              f"cp95=({r['cp95'][0]:.4f},{r['cp95'][1]:.4f}) n={r['n']}",
              flush=True)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--plan":
        todo = remaining()
        print(f"[m4] {len(todo)} of {len(campaign_plan())} cells remaining")
        for size, mode, cap in todo[:20]:
            print(f"    {size}/{mode}/{cap}")
        if len(todo) > 20:
            print(f"    ... and {len(todo) - 20} more")
        return
    run(sys.argv[1], sys.argv[2], sys.argv[3:] or None)


if __name__ == "__main__":
    main()
