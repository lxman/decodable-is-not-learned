"""Tiered untrained inclusion screen (design §2, the promoted P1).

Tier 1 (candidate-design time): 2 seeds x both sizes x 500 permutations.
Reject a candidate if ANY fit lands at the add-one-x-Bonferroni floor with a
margin beyond the order-statistics bound for the max of 500 null draws
(stats_bounds.TIER1_BAR), or if ANY fit's classification goes past
"tolerated" (elevated / structural_abort). Tier 2 (pre-freeze, screen
survivors only): the identical frozen instrument config -- 5 seeds x both
sizes x 2,500 permutations. Design §2 declares tier-2's fits to BE the
campaign's untrained-gate fits (§4 gate 1); this module writes them in the
same campaign format exp2b's run_probes_2b.py used, under
results/probes/known_absent/, so no recomputation is needed at freeze.

Signature note (frozen `probe_starved`, experiments/exp2b/probe_starved.py):

    probe_starved(activations, labels, bases, *, split_params, checkpoint_id,
                  alpha=0.01, n_perm=2500, seed, split_labels=None) -> dict

`activations` is a dict[(layer, token_slot) -> ndarray[n, d]] (a whole
candidate FAMILY, not a single array); the split is NOT caller-supplied --
probe_starved builds it itself from `bases` + `split_params` via the frozen
`starving_split`. There is no "split=" bypass. `screen_arrays` below (the
model-free core the unit tests exercise) therefore fabricates a per-item
UNIQUE arity-1 basis when no real basis exists: starving_split's per-
component holdout on unique singleton values reduces exactly to a random
item split (no item can be "mixed" when its only basis component is unique
to it), which is the intended "no basis" behavior expressed through the
frozen split machinery rather than a nonexistent bypass parameter.
`screen_candidate` (the real, per-capability path) instead threads the
item file's actual bases and the capability's real SplitParams
(battery/gen_items.py's SPLIT_PLAN -- 2c's CapabilitySpec, unlike 2b's,
carries no split_params field of its own) through the same low-level
`_fit_and_classify` helper.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

try:  # `experiments.exp2c.run.screen` (pytest / absolute import)
    from .. import instrument
    from .. import stats_bounds as sb
except ImportError:  # pragma: no cover - `python -m run.screen` from exp2c/
    import instrument
    import stats_bounds as sb

FLOORS = instrument.FLOORS
N_PERM_FULL = instrument.N_PERM_FULL
N_PERM_SCREEN = instrument.N_PERM_SCREEN
SEEDS_FULL = instrument.SEEDS_FULL
SEEDS_SCREEN = instrument.SEEDS_SCREEN
SIZES = instrument.SIZES
probe_starved = instrument.probe_starved
SplitParams = instrument.splits.SplitParams

HERE = Path(__file__).resolve().parent.parent   # experiments/exp2c
RESULTS = HERE / "results"
ITEMS_DIR = HERE / "battery" / "items"

# ------------------------------------------------------------- core fit/gate

def _fit_and_classify(activations, y, bases, *, split_params, checkpoint_id,
                      n_perm, seed, split_labels=None):
    """One starved fit + screen classification. Returns (rec, raw) where
    `raw` is probe_starved's own return dict (used verbatim for campaign
    fit files) and `rec` is the screen's condensed per-fit record."""
    r = probe_starved(activations, y, bases, split_params=split_params,
                      checkpoint_id=checkpoint_id, n_perm=n_perm, seed=seed,
                      split_labels=split_labels)
    # add-one floor x Bonferroni family (probe_starved.py's own comment):
    # the theoretical minimum corrected p for THIS fit's family size and
    # permutation count -- generalizes instrument.FLOORS (which is this
    # same quantity, fixed at n_perm=N_PERM_FULL, for the two probe sizes;
    # cross-checked against it in screen_candidate for tier-2 fits).
    theoretical_floor = r["n_candidates"] / (n_perm + 1)
    at_floor = bool(r["null_p"] <= theoretical_floor * 1.0001)
    cls = sb.classify_fire(r["accuracy"], r["null_mean"], r["null_std"], at_floor)
    rec = {"seed": seed, "corrected_p": r["null_p"], "margin": r["margin"],
           "null_mean": r["null_mean"], "null_sd": r["null_std"],
           "at_floor": at_floor, "classification": cls}
    return rec, r


def screen_arrays(X, y, n_perm, seed, *, split_params=None,
                  checkpoint_id="synthetic"):
    """Model-free core: one starved fit on caller-provided arrays via the
    frozen `probe_starved`, classified via stats_bounds.classify_fire. The
    unit tests call this directly (synthetic, single-candidate, no real
    basis); `screen_candidate` uses the lower-level `_fit_and_classify`
    with the real multi-candidate activation family instead."""
    y = np.asarray(y)
    X = np.asarray(X, dtype=np.float32)
    bases = [(str(i),) for i in range(len(y))]   # per-item unique -> random split
    sp = split_params or SplitParams(min_holdout_values=1, min_val_items=1)
    activations = {(0, 0): X}
    rec, _raw = _fit_and_classify(activations, y, bases, split_params=sp,
                                  checkpoint_id=checkpoint_id, n_perm=n_perm,
                                  seed=seed)
    return rec


def _tier1_margin_bar(rec: dict) -> float:
    """stats_bounds.TIER1_BAR is the max-of-500 order-stat quantile in null-
    SD units; converted to margin units (margin = (acc-null_mean)/(1-
    null_mean)) so it compares directly against a fit's own margin."""
    return sb.TIER1_BAR * rec["null_sd"] / max(1e-9, 1 - rec["null_mean"])


def _assert_floor_matches(size: str, n_perm: int, n_candidates: int) -> None:
    """instrument.FLOORS is the ledgered per-size floor for the canonical
    tier-2 config (design §3: 18/2501 at 410m, 14/2501 at 1b). A mismatch
    here means the thinned candidate family drifted from that ledgered
    count, which would silently invalidate every FLOORS-derived number in
    the design doc -- loud failure, not a warning."""
    if n_perm != N_PERM_FULL:
        return
    expected = round(FLOORS[size] * (N_PERM_FULL + 1))
    assert n_candidates == expected, (
        f"{size}: thinned candidate family is {n_candidates}, expected "
        f"{expected} from instrument.FLOORS[{size!r}]={FLOORS[size]!r}; "
        f"the ledgered candidate count (design §3) has drifted")


# ------------------------------------------------------------ real activations
# Adapted from experiments/exp2b/run/collect_activations.py + activations.py
# + models.py (frozen conventions; exp2c paths, exp2c items). Probe-side,
# UNTRAINED TWIN ONLY -- the two-stage lock forbids any eval-side model
# (2.8b/6.9b/12b) from being loaded or queried by any code in this module,
# so PYTHIA_SHAS below carries just the two probe sizes and nothing else
# ever names an eval-side SHA or repo id here. torch/transformers are
# imported lazily inside the functions that need them so importing this
# module (or running its unit tests) never touches either.

PYTHIA_SHAS = {
    "410m": "9879c9b5f8bea9051dcb0e68dff21493d67e9d4f",
    "1b": "f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2",
}
UNTRAINED_SEED = 0        # matches 2b's M1/M2 untrained-weights control seed
LAYER_STRIDE = 3          # every 3rd layer + final -> the Bonferroni family
_ANSWER_CUE = "\nA:"


def _load_item_file(name: str) -> dict:
    return json.loads((ITEMS_DIR / f"{name}.json").read_text())


def _split_plan(name: str) -> "SplitParams":
    """2c's CapabilitySpec carries no split_params field (unlike 2b's);
    battery/gen_items.py's SPLIT_PLAN is the source task 6 actually checked
    feasible and used to generate the committed item files."""
    try:
        from ..battery import gen_items as _gen_items
    except ImportError:  # pragma: no cover - `python -m run.screen` from exp2c/
        # instrument (imported above) prepends experiments/exp2b to sys.path,
        # which ALSO has a battery/ package (its own gen_items.py, no
        # SPLIT_PLAN) -- an unqualified `import battery` here would silently
        # resolve to exp2b's, not exp2c's. Force exp2c's own directory ahead
        # of it and drop any stale caching before the plain import.
        import sys
        exp2c_dir = str(HERE)
        if exp2c_dir in sys.path:
            sys.path.remove(exp2c_dir)
        sys.path.insert(0, exp2c_dir)
        sys.modules.pop("battery", None)
        sys.modules.pop("battery.gen_items", None)
        from battery import gen_items as _gen_items
    split_params, _n_probe = _gen_items.SPLIT_PLAN[name]
    return split_params


def _render_prompt(question: str, shots) -> str:
    parts = [f"Q: {q}\nA: {a}" for q, a in shots or []]
    parts.append(f"Q: {question}\nA:")
    return "\n\n".join(parts)


def _question_end_char(prompt: str) -> int:
    idx = prompt.rfind(_ANSWER_CUE)
    if idx <= 0:
        raise ValueError("prompt does not end with the answer cue")
    return idx


def _position_indices(tok, prompt: str) -> tuple[int, int]:
    full = tok(prompt, add_special_tokens=False)["input_ids"]
    prefix = tok(prompt[: _question_end_char(prompt)],
                add_special_tokens=False)["input_ids"]
    return len(prefix) - 1, len(full) - 1


def _load_untrained_pythia(size: str):
    """The untrained twin only: seeded random init, NO pretrained weights.
    Adapted from experiments/exp2b/models.py's load_pythia(untrained=True)."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    repo = f"EleutherAI/pythia-{size}"
    tok = AutoTokenizer.from_pretrained(repo, revision=PYTHIA_SHAS[size])
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    cfg = AutoConfig.from_pretrained(repo, revision=PYTHIA_SHAS[size])
    torch.manual_seed(UNTRAINED_SEED)
    model = AutoModelForCausalLM.from_config(cfg).to(dtype=torch.float16)
    return tok, model.to("mps").eval()


def _collect_capability(model, tok, payload: dict, *, batch_size: int = 32,
                        device: str = "mps") -> dict:
    import torch

    items = payload["probe_items"]
    shots = [tuple(s) for s in payload["shots"]]
    prompts = [_render_prompt(it["question"], shots) for it in items]
    labels = [it["probe_label"] for it in items]

    old_side = tok.padding_side
    tok.padding_side = "right"  # forwards only; index by true (unpadded) length
    X_chunks = []
    try:
        for i in range(0, len(prompts), batch_size):
            chunk = prompts[i:i + batch_size]
            enc = tok(chunk, return_tensors="pt", padding=True,
                      add_special_tokens=False).to(device)
            with torch.no_grad():
                out = model(**enc, output_hidden_states=True)
            hs = torch.stack(out.hidden_states, dim=0)          # [n_layers, B, T, d]
            for b, prompt in enumerate(chunk):
                q_idx, p_idx = _position_indices(tok, prompt)
                sel = hs[:, b, [q_idx, p_idx], :]                # [n_layers, 2, d]
                X_chunks.append(sel.to(torch.float16).cpu().numpy())
    finally:
        tok.padding_side = old_side
    return {"X": np.stack(X_chunks), "y": np.array(labels, dtype=object)}


def _activations_path(size: str, name: str) -> Path:
    return RESULTS / "activations" / f"{size}_untrained" / f"{name}.npz"


def _save_activations(path: Path, arrays: dict, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, X=arrays["X"], y=arrays["y"].astype(str),
                        meta=json.dumps(meta))


def _load_activation_map(path: Path) -> tuple[dict, np.ndarray, dict]:
    z = np.load(path, allow_pickle=False)
    X, y = z["X"], z["y"]
    meta = json.loads(str(z["meta"]))
    act = {(layer, slot): X[:, layer, slot, :].astype(np.float32)
           for layer in range(X.shape[1]) for slot in range(X.shape[2])}
    return act, y, meta


def _thin_layers(act: dict) -> dict:
    """Every 3rd layer + final, x2 positions -- the same thinning
    run_probes_2b.py applies before fitting; instrument.FLOORS is ledgered
    against exactly the resulting counts (18 at 410m, 14 at 1b)."""
    n_layers = 1 + max(l for l, _ in act.keys())
    keep = set(range(0, n_layers, LAYER_STRIDE)) | {n_layers - 1}
    return {(l, s): X for (l, s), X in act.items() if l in keep}


def _load_untrained_activations(name: str, size: str):
    """(activations, labels, bases, meta) for one capability/size. Collects
    (untrained twin only) on first use and caches to the .npz thereafter --
    never executed by this task's tests; correctness gate is code review."""
    payload = _load_item_file(name)
    items = payload["probe_items"]
    bases = [tuple(it["basis"]) for it in items]
    path = _activations_path(size, name)
    if not path.exists():
        tok, model = _load_untrained_pythia(size)
        arrays = _collect_capability(model, tok, payload)
        meta = {"size": size, "mode": "untrained", "capability": name,
                "sha": PYTHIA_SHAS[size], "untrained_seed": UNTRAINED_SEED,
                "n_items": int(arrays["X"].shape[0]),
                "n_layers": int(arrays["X"].shape[1])}
        _save_activations(path, arrays, meta)
    act, y, meta = _load_activation_map(path)
    act = _thin_layers(act)
    assert len(y) == len(bases), f"{name}/{size}: activation/basis count mismatch"
    return act, y, bases, meta


def _write_campaign_fit(name: str, size: str, seed: int, r: dict) -> None:
    """Tier-2 fits ARE the campaign's untrained-gate fits (design §2); write
    them in exp2b's run_probes_2b.py fit-file format so no recomputation is
    needed at freeze."""
    import socket
    d = {"stage": "known_absent", "size": size, "capability": name,
         "host": socket.gethostname(), **r}
    dest = RESULTS / "probes" / "known_absent"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{size}_{name}_seed{seed}.json").write_text(json.dumps(d, indent=1))


# -------------------------------------------------------------------- runner

def screen_candidate(name: str, tier: int) -> dict:
    if tier not in (1, 2):
        raise ValueError(f"tier must be 1 or 2, got {tier!r}")
    n_perm = N_PERM_SCREEN if tier == 1 else N_PERM_FULL
    seeds = SEEDS_SCREEN if tier == 1 else SEEDS_FULL
    split_params = _split_plan(name)

    fits, reject = [], False
    for size in SIZES:
        act, y, bases, meta = _load_untrained_activations(name, size)
        checkpoint_id = f"pythia-{size}:{meta['sha'][:8]}:untrained"
        for s in seeds:
            rec, r = _fit_and_classify(act, y, bases, split_params=split_params,
                                       checkpoint_id=checkpoint_id,
                                       n_perm=n_perm, seed=s)
            rec["size"] = size
            fits.append(rec)
            if rec["classification"] not in ("not_fire", "tolerated"):
                reject = True
            if tier == 1 and rec["at_floor"] and \
               rec["margin"] > _tier1_margin_bar(rec):
                reject = True
            if tier == 2:
                _assert_floor_matches(size, n_perm, r["n_candidates"])
                _write_campaign_fit(name, size, s, r)

    out = {"name": name, "tier": tier, "fits": fits,
           "verdict": "reject" if reject else "pass"}
    dest = RESULTS / "screen" / f"tier{tier}"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{name}.json").write_text(json.dumps(out, indent=1))
    return out


def main(argv=None) -> None:
    import argparse
    p = argparse.ArgumentParser(description="Tiered untrained inclusion screen")
    p.add_argument("name")
    p.add_argument("--tier", type=int, choices=(1, 2), required=True)
    args = p.parse_args(argv)
    out = screen_candidate(args.name, args.tier)
    print(f"[screen] {args.name} tier{args.tier}: {out['verdict']} "
          f"({len(out['fits'])} fits)", flush=True)


if __name__ == "__main__":
    main()
