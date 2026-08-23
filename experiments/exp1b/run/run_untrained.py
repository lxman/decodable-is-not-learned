"""Exp 1b's untrained control: the probe, run on a randomly initialized network.

An untrained twin per trained cell — same architecture, same size, same seed, same
probe data and labels, no training. If S1 fires here, the probe is reading the
random expansion (a reservoir), not structure the training put there, and the
trained row's S1 means nothing. Exp 2's whole battery died this way; Exp 2b's
untrained control caught surface-statistics leaks in 13 of 25 capabilities. This
runner is that control, wired into 1b before any trained data exists.

Nothing under experiments/exp1/ is modified. The three exp1 calls a trained run
makes — construct, build probe data, probe — are made here MINUS the training
call, by importing exp1's own helpers.

INTERFACES, read from the frozen exp1 source at 9aad2b7 and recorded here because
reproducing them from memory is how a wrong `chance` gets baked into a frozen
instrument (Exp 1's units failure, Exp 2c's chance-floor defect):

  grokking  (run/run_grokking.py:42-88)
    config  grokking_config_for(size)            configs/grokking.py:75
    model   DecoderTransformer(TransformerConfig(vocab_size=task.vocab_size,
              n_ctx=task.n_ctx, d_model=cfg.d_model, n_layers=cfg.n_layers,
              n_heads=cfg.n_heads, seed=seed))
    data    n_probe = min(cfg.probe_n, data["test_ids"].shape[0])
            acts   = _collect_acts(model, probe_ids, device)   run_phaseA.py:43
            labels = data["test_labels"][:n_probe].numpy()
    chance  task.chance == 1.0 / cfg.p           tasks/modular_arith.py:60
    bucket  cfg.size_bucket

  lubana    (run/run_lubana.py:121-156)
    config  LubanaRunConfig(setting=, model_size=, scale="paper")
    lang    LubanaLanguage(LubanaConfig(seed=seed, **cfg.lang_kwargs))
    pool    lang.singleton_entities() if setting == "below" else None
    model   _make_model(lang, cfg, seed)                       run_lubana.py:80
    data    _entity_probe_data(lang, device, model, pool=pool) run_lubana.py:64
    chance  lang.chance == 1.0 / cfg.n_classes   tasks/lubana_lang.py:455
    bucket  _size_bucket(model.num_params())                   run_lubana.py:59

  both      probe_below_threshold(acts, labels, chance=, checkpoint_id=,
              below_threshold=, alpha=cfg.alpha, n_perm=cfg.n_perm, seed=seed)
            — everything after `labels` is keyword-only; `seed` has no default.
                                                        signatures/probe.py:89

Two facts that are easy to get wrong and are therefore asserted, not assumed:

1. exp1's runners use absolute imports (`from configs.lubana import ...`), so
   experiments/exp1 must be on sys.path for them to import at all. Putting it
   there makes `signatures` importable under TWO names — `signatures.schema` and
   `experiments.exp1.signatures.schema` — whose ProbeResult classes are distinct
   objects. `probe_below_threshold` is therefore imported through the
   `experiments.exp1.` path, so the ProbeResult it returns is the one
   records.py's `_build` reconstructs.
2. lubana's MODEL_SIZE_TARGETS has NO "10M" key (configs/lubana.py:39). The 10M
   row is the base model at scale="paper" — model_size=None, 12,870,144 params,
   bucket "10M" (results/lubana_above/10M/seed0.json). Only the 1M row passes a
   model_size. The computed bucket is cross-checked against the requested size.
"""

from __future__ import annotations

import sys
from pathlib import Path

EXP1B_DIR = Path(__file__).resolve().parents[1]
EXP1_DIR = EXP1B_DIR.parent / "exp1"

# exp1's runners import their own package absolutely; this is the only integration
# step needed and it modifies nothing under experiments/exp1/.
if str(EXP1_DIR) not in sys.path:
    sys.path.insert(0, str(EXP1_DIR))

from experiments.exp1.run.provenance import git_sha  # noqa: E402
from experiments.exp1.run.run_grokking import (  # noqa: E402
    DecoderTransformer,
    ModArithConfig,
    ModArithTask,
    TransformerConfig,
    grokking_config_for,
    resolve_device,
)
from experiments.exp1.run.run_lubana import (  # noqa: E402
    LubanaConfig,
    LubanaLanguage,
    LubanaRunConfig,
    _entity_probe_data,
    _make_model,
    _size_bucket,
)
from experiments.exp1.run.run_phaseA import _collect_acts  # noqa: E402
# Through experiments.exp1.* so the returned ProbeResult is records.py's class,
# not the duplicate reached via the bare `signatures` name (see note 1 above).
from experiments.exp1.signatures.probe import probe_below_threshold  # noqa: E402

from experiments.exp1b.records import (  # noqa: E402
    SIZE_BUCKETS,
    UNTRAINED_SYSTEMS,
    UntrainedRecord,
)

# The scored exp1 campaigns ran lubana at the paper scale, never the "reduced"
# default (run/campaign_m5.sh:33, run/campaign_m6.sh). The twin must match the
# cell it controls.
LUBANA_SCALE = "paper"
LUBANA_MODEL_SIZE = {"1M": "1M", "10M": None}

# An untrained network is trivially below any transition — it has not been trained
# at all — so the below-threshold condition is vacuously satisfied rather than
# measured. There is no checkpoint to read an argmax accuracy from, and no
# training history to place one against. Passing False instead would force
# `present` to False by construction and the control could never fire, which
# would make the gate decorative.
BELOW_THRESHOLD = True
CHECKPOINT_ID = "init"


def record_path(out_root: str | Path, system: str, size: str, seed: int) -> Path:
    """Durable unit: one JSON per untrained cell.

    Held under results/untrained/ so it cannot collide with the trained rows,
    which exp1's runners write to results/<system>/<size>/seed<N>.json.
    """
    return (Path(out_root) / "results" / "untrained" / system / size
            / f"seed{seed}.json")


def _grokking_cell(size: str, seed: int):
    cfg = grokking_config_for(size)
    device = resolve_device(cfg.device)
    task = ModArithTask(ModArithConfig(p=cfg.p, op=cfg.op,
                                       train_frac=cfg.train_frac, seed=seed))
    data = task.make_split(seed)
    model = DecoderTransformer(TransformerConfig(
        vocab_size=task.vocab_size, n_ctx=task.n_ctx,
        d_model=cfg.d_model, n_layers=cfg.n_layers, n_heads=cfg.n_heads,
        seed=seed,
    ))
    model.to(device)                       # <- no train(...) call: that is the point

    n_probe = min(cfg.probe_n, data["test_ids"].shape[0])
    acts = _collect_acts(model, data["test_ids"][:n_probe], device)
    labels = data["test_labels"][:n_probe].numpy()
    return cfg, model, acts, labels, task.chance, cfg.size_bucket


def _lubana_cell(setting: str, size: str, seed: int):
    cfg = LubanaRunConfig(setting=setting, scale=LUBANA_SCALE,
                          model_size=LUBANA_MODEL_SIZE[size])
    device = resolve_device(cfg.device)
    lang = LubanaLanguage(LubanaConfig(seed=seed, **cfg.lang_kwargs))
    # Below row: singleton components only, as the trained row (run_lubana.py:133).
    pool = lang.singleton_entities() if setting == "below" else None
    model = _make_model(lang, cfg, seed)
    model.to(device)                       # <- no _train_setting(...) call

    acts, labels = _entity_probe_data(lang, device, model, pool=pool)
    return cfg, model, acts, labels, lang.chance, _size_bucket(model.num_params())


def run_untrained(system: str, size: str, seed: int,
                  out_root: str | Path) -> UntrainedRecord:
    """Probe a randomly initialized twin of one trained cell. Saves and returns."""
    if system not in UNTRAINED_SYSTEMS:
        raise ValueError(f"system must be one of {UNTRAINED_SYSTEMS}, got {system!r}")
    if size not in SIZE_BUCKETS:
        raise ValueError(f"size must be one of {SIZE_BUCKETS}, got {size!r}")

    if system == "grokking":
        cfg, _model, acts, labels, chance, bucket = _grokking_cell(size, seed)
    else:
        setting = "below" if system == "lubana_below" else "above"
        cfg, _model, acts, labels, chance, bucket = _lubana_cell(setting, size, seed)

    if bucket != size:
        raise ValueError(
            f"{system}/{size}: model landed in bucket {bucket!r} — the size-to-config "
            f"mapping does not reproduce the trained cell, so this is not its twin")

    s1 = probe_below_threshold(
        acts, labels, chance=chance,
        checkpoint_id=CHECKPOINT_ID, below_threshold=BELOW_THRESHOLD,
        alpha=cfg.alpha, n_perm=cfg.n_perm, seed=seed,
    )

    rec = UntrainedRecord(system=system, size_bucket=bucket, seed=seed,
                          git_sha=git_sha(EXP1B_DIR), s1=s1, config=cfg.as_dict())
    rec.save(record_path(out_root, system, size, seed))
    return rec


if __name__ == "__main__":
    system, size, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    out_root = Path(sys.argv[4]) if len(sys.argv) > 4 else EXP1B_DIR
    rec = run_untrained(system, size, seed, out_root)
    print(f"[untrained {system}/{size} seed {seed}] "
          f"S1 present={rec.s1.present} acc={rec.s1.accuracy:.4f} "
          f"(chance {rec.s1.chance:.4f}) p={rec.s1.null_p:.4g} "
          f"@ {rec.s1.checkpoint_id}")
