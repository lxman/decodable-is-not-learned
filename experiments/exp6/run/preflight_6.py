# experiments/exp6/run/preflight_6.py
"""Exp 6 preflight (design §7, stage 0): SCRATCH ONLY. Nothing under
`root/results` may change; nothing a model writes is stored, and nothing
it writes on a rung of the new battery is printed or counted — the
preflight reports finiteness, identity, shape, seconds and memory, and no
score. The frozen modules and the import surface are checked. The
predictor stage checks no tag (4c's rule: it runs before the predictor
exists); the outcome stage runs after the predictor seal and refuses,
before it loads anything or builds a host record, unless the predictor
is sealed (final review C-1, ruling I-19).

    python -m experiments.exp6.run.preflight_6 --stage predictor --device mps
    python -m experiments.exp6.run.preflight_6 --stage outcome --device cuda

`predictor` (the Mac), each predictor once:
  - finiteness MEASURED on the longest prompts of the battery;
  - the REHEARSAL of gate 1-P: item 0 of an anchor at the main tier's
    shape against the committed stream, byte for byte (2k's rehearsal);
  - one item of each preflight rung sampled at the main tier's shape
    TWICE: identical draws required (the sampler is seeded per item);
  - seconds per item, scaled to the tier.
`outcome` (the box), each family:
  - the stage-1 endpoint through the thin loader and the FIRST grid step
    through the checkpoint loader (the step most likely to be non-finite
    at half precision: 4c's step 1000), finiteness measured on each;
  - forty items of each preflight rung scored and timed; peak memory;
  - where the family is rendered with a BOS prefix (Comma), both
    renders' ids and the stop ids the loader measured;
  - on the smallest family the endpoint through BOTH loaders: identical
    continuations on the preflight rungs and equal tensor digests (the
    rehearsal of gate 1(a));
  - on every read the two anchors (2c's base-8 pair) on all their items,
    each count held to the Mac's committed count of that checkpoint
    within the cross-host tolerance (the rehearsal of gate 1(c); final
    review M-4). The anchors' outcomes are committed: printing their
    counts discloses nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

EXP6 = Path(__file__).resolve().parents[1]
REPO = EXP6.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp6 import battery_6 as b6  # noqa: E402
from experiments.exp6 import families_6 as fm  # noqa: E402
from experiments.exp6 import pins_6 as p6  # noqa: E402
from experiments.exp6 import records_6 as r6  # noqa: E402
from experiments.exp6 import referents_6 as rf  # noqa: E402
from experiments.exp6 import verify_6 as v6  # noqa: E402
from experiments.exp6.run import _common_6 as cm  # noqa: E402
from experiments.exp6.run import endpoint_6 as ep  # noqa: E402
from experiments.exp6.run import predict_6 as pr  # noqa: E402

# the longest prompt (641 tokens), the longest budget (24), a number rung
PREFLIGHT_RUNGS_6 = ("temporal", "ipa_word", "modarith_mul1")
REHEARSAL_RUNG_6 = b6.ANCHORS_6[0]
TWICE_FAMILY_6 = fm.FAMILIES_6[0]            # the smallest: SmolLM3-3B
N_PROBE = 8
N_ITEMS_OUTCOME = 40                         # design §7: forty items, nothing stored
RENDER_PROBE = "Q:"


def results_snapshot(root) -> frozenset:
    """Every file under results/ with its sha256: the preflight's own
    proof that it wrote nothing there."""
    base = r6.results(root)
    if not base.exists():
        return frozenset()
    return frozenset((str(p.relative_to(base)), r6.sha256_file(p))
                     for p in sorted(base.rglob("*")) if p.is_file())


def peak_memory(device: str):
    try:
        import torch
        if device.startswith("cuda") and torch.cuda.is_available():
            return int(torch.cuda.max_memory_allocated())
        if device == "mps":
            return int(torch.mps.driver_allocated_memory())
    except Exception:  # noqa: BLE001
        return None
    return None


def shape_of(continuations, answer_type: str) -> dict:
    """What the continuations LOOK like, and nothing about whether they
    are right: how many normalize to the empty string, how many are one
    identical string."""
    def norm(c):
        try:
            return v6.normalize_6(c, answer_type)
        except IndexError:
            return ""
    n = [norm(c) for c in continuations]
    top = max((n.count(x) for x in set(n)), default=0)
    return {"n": len(n), "n_empty": int(sum(1 for x in n if not x)),
            "n_most_common": int(top)}


def n_nonfinite_each(model, tok, prompts) -> int:
    """Non-finite logits at the last position, one prompt at a time: a
    predictor's tokenizer need not have a pad token."""
    import torch
    n = 0
    for p in prompts:
        enc = tok(p, return_tensors="pt").to(model.device)
        with torch.no_grad():
            logits = model(**enc).logits[:, -1].float()
        n += int((~torch.isfinite(logits)).sum().item())
    return n


def _digest(strings) -> str:
    h = hashlib.sha256()
    for s in strings:
        h.update(str(s).encode("utf-8") + b"\x00")
    return h.hexdigest()


def _guard(root, frozen_check):
    (frozen_check or p6.check_frozen_6)()
    if frozen_check is None:
        p6.check_imports_6(exempt=p6.EXEMPT_6)
    return results_snapshot(root)


def _unchanged(root, before) -> None:
    after = results_snapshot(root)
    if after != before:
        moved = sorted(x[0] for x in after ^ before)
        raise RuntimeError(f"the preflight wrote under {r6.results(root)}: {moved[:5]}")


# ------------------------------------------------------------- the predictor
def predictor_preflight(predictor: str, *, device, loader, sampler, battery,
                        nonfinite=n_nonfinite_each, rungs=PREFLIGHT_RUNGS_6,
                        log=print) -> dict:
    t = r6.tier_shape(predictor, "main")
    size = r6.PREDICTORS_6[predictor]["size"]
    tok, model, model_rec = loader(predictor, "trained", device)
    out = {"predictor": predictor, "model": model_rec, "rungs": {}}
    try:
        pin = rf.model_pin(predictor)
        out["model_is_pinned"] = (model_rec["commit"] == pin["commit"]
                                  and model_rec["model_sha"] == pin["model_sha"])
        probe = sorted(pr.prompts_of(battery[rungs[0]]), key=len)[-N_PROBE:]
        out["n_nonfinite_logits"] = int(nonfinite(model, tok, probe))
        terminal = tuple(sorted(set(tok.all_special_ids)))

        def draw(rung, i):
            prompt = pr.prompts_of(battery[rung])[i]
            got = sampler(model, tok, prompt, rung=rung, size=size, mode="trained",
                          item_idx=i, seeds=t["seeds"], draws_per_seed=t["dps"],
                          max_new_tokens=b6.max_new_tokens_6(rung),
                          terminal_ids=terminal)
            return {str(s): [str(x) for x in got[s]] for s in t["seeds"]}

        # the rehearsal of gate 1-P: a committed stream, item 0
        if (predictor, "main", REHEARSAL_RUNG_6) in rf.gated_units():
            want = rf.committed_rows(predictor, "main", REHEARSAL_RUNG_6)[0]["draws"]
            got = draw(REHEARSAL_RUNG_6, 0)
            out["rehearsal"] = {"rung": REHEARSAL_RUNG_6, "item": 0, "k": t["k"],
                                "identical": got == {s: list(want[s]) for s in got}}
            log(f"[6 preflight] {predictor}: {REHEARSAL_RUNG_6} item 0, {t['k']} draws "
                f"against the committed stream: "
                f"{'IDENTICAL' if out['rehearsal']['identical'] else 'DIFFERS'}")
        for rung in rungs:
            t0 = time.time()
            a = draw(rung, 0)
            seconds = time.time() - t0
            b = draw(rung, 0)
            flat = [d for s in sorted(a) for d in a[s]]
            out["rungs"][rung] = {
                "twice_identical": a == b, "seconds_per_item": seconds,
                "hours_per_rung": seconds * b6.N_ITEMS / 3600.0,
                "shape": shape_of(flat, battery[rung]["answer_type"]),
                "budget": b6.max_new_tokens_6(rung)}
            log(f"[6 preflight] {predictor}/{rung}: item 0 sampled twice "
                f"{'IDENTICAL' if a == b else 'DIFFERS'}; {seconds:.1f} s an item, "
                f"{seconds * b6.N_ITEMS / 3600.0:.2f} h a rung; shape "
                f"{out['rungs'][rung]['shape']}")
        out["peak_memory_bytes"] = peak_memory(device)
    finally:
        fm.release(model)
    out["pass"] = bool(out["model_is_pinned"] and out["n_nonfinite_logits"] == 0
                       and out.get("rehearsal", {"identical": True})["identical"]
                       and all(r["twice_identical"] for r in out["rungs"].values()))
    return out


def run_predictor(*, root=EXP6, device="mps", predictors=None, loader=None,
                  sampler=None, nonfinite=None, frozen_check=None, log=print) -> dict:
    before = _guard(root, frozen_check)
    battery = b6.load_battery_6()
    loader = pr.real_loader if loader is None else loader
    sampler = pr.real_sampler() if sampler is None else sampler
    res = {p: predictor_preflight(p, device=device, loader=loader, sampler=sampler,
                                  battery=battery, log=log,
                                  nonfinite=n_nonfinite_each if nonfinite is None
                                  else nonfinite)
           for p in (predictors or sorted(r6.PREDICTORS_6))}
    _unchanged(root, before)
    log("[6 preflight] predictor stage complete: nothing written under results/")
    return {"stage": "predictor", "predictors": res,
            "pass": all(r["pass"] for r in res.values())}


# --------------------------------------------------------------- the outcome
def _score(runner, cap) -> dict:
    cap = dict(cap, eval_items=list(cap["eval_items"][:N_ITEMS_OUTCOME]))
    t0 = time.time()
    ev = r6.evaluate_items_6(runner, cap)
    return {"seconds": time.time() - t0, "n_items": len(cap["eval_items"]),
            "shape": shape_of(ev["continuations"], cap["answer_type"]),
            "digest": _digest(ev["continuations"])}


def _anchors(runner, battery, family, step, name, log) -> dict:
    """Gate 1(c), rehearsed: each anchor on all its items through the
    runner, against the Mac's committed count of this checkpoint."""
    counts = {r: int(r6.evaluate_items_6(runner, battery[r])["correct"])
              for r in b6.ANCHORS_6}
    mac = {r: rf.mac_count(family, step, r) for r in b6.ANCHORS_6}
    label = f"6 preflight gate 1(c) {family}/{name}"
    bad = rf.anchor_tolerance(counts, mac, label=label)
    out = {r: {"count": counts[r], "mac": mac[r],
               "within": not any(m.startswith(f"{label}/{r}:") for m in bad)}
           for r in b6.ANCHORS_6}
    log(f"[6 preflight] {family}, {name} (step {step}): anchors "
        + ", ".join(f"{r} {v['count']} against the Mac's {v['mac']}"
                    f"{'' if v['within'] else ' OUTSIDE'}" for r, v in out.items())
        + f" (tolerance {rf.TOL_PER_RUNG_6})")
    return out


def family_preflight(family: str, *, device, loaders, battery, cache_root,
                     rungs=PREFLIGHT_RUNGS_6, twice=False, log=print) -> dict:
    man = fm.manifest(family)
    end, first = fm.endpoint_step(family), fm.grid(family)[0]
    probe = sorted(pr.prompts_of(battery[rungs[0]]), key=len)[-N_PROBE:]
    reads = [("endpoint, thin loader", end,
              lambda: loaders["thin"](family, man, device=device)),
             ("first grid step, checkpoint loader", first,
              lambda: loaders["checkpoint"](family, man, first, device=device,
                                            cache_root=cache_root))]
    if twice:
        reads.append(("endpoint, checkpoint loader", end,
                      lambda: loaders["checkpoint"](family, man, end, device=device,
                                                    cache_root=cache_root)))
    out = {"family": family, "reads": {}}
    for name, step, load_fn in reads:
        t0 = time.time()
        model, tok, info = load_fn()
        try:
            row = {"step": int(step), "load_seconds": time.time() - t0,
                   "tensor_digest": info.get("tensor_digest"),
                   # gate 1(d), rehearsed: on this host, are these the Mac's weights?
                   "digest_is_the_macs":
                       info.get("tensor_digest") == rf.mac_digest(family, step),
                   "n_nonfinite_logits": int(loaders["nonfinite"](model, tok, probe)),
                   "rungs": {}}
            if fm.RENDER_6[family] == "bos":
                from experiments.exp2n import battery_2n as bn
                ids = loaders.get("render_ids") or (
                    lambda tok_, text: list(tok_(text)["input_ids"]))
                row["renders"] = {
                    "plain": ids(tok, RENDER_PROBE),
                    "bos": ids(tok, bn.BOS_TOKEN_2N + RENDER_PROBE),
                    "config_eos_token_id": info.get("config_eos_token_id"),
                    "generation_eos_token_id": info.get("generation_eos_token_id"),
                    "stop_id_pinned": bn.EOS_STOP_ID_2N}
                log(f"[6 preflight] {family}, {name}: renders {row['renders']}")
            runner = loaders["runner"](family, tok, model)
            for rung in rungs:
                row["rungs"][rung] = _score(runner, battery[rung])
            row["anchors"] = _anchors(runner, battery, family, step, name, log)
            row["peak_memory_bytes"] = peak_memory(device)
        finally:
            loaders["release"](model)
        out["reads"][name] = row
        log(f"[6 preflight] {family}, {name} (step {step}): non-finite "
            f"{row['n_nonfinite_logits']}, load {row['load_seconds']:.0f} s, "
            + ", ".join(f"{r} {v['seconds']:.0f} s" for r, v in row["rungs"].items())
            + f", peak {row['peak_memory_bytes']}")
    if twice:
        a, b = out["reads"]["endpoint, thin loader"], \
            out["reads"]["endpoint, checkpoint loader"]
        out["two_loaders"] = {
            "digests_equal": a["tensor_digest"] == b["tensor_digest"]
            and a["tensor_digest"] is not None,
            "continuations_identical": all(
                a["rungs"][r]["digest"] == b["rungs"][r]["digest"] for r in rungs)}
        log(f"[6 preflight] {family}: the endpoint through both loaders: "
            f"{out['two_loaders']}")
        loaders["free"](family, man, end, cache_root=cache_root)
    loaders["free"](family, man, first, cache_root=cache_root)
    per_step = sum(v["seconds"] for v in
                   out["reads"]["first grid step, checkpoint loader"]["rungs"].values())
    out["seconds_per_rung_mean"] = (per_step / len(rungs)
                                    * b6.N_ITEMS / N_ITEMS_OUTCOME)
    out["hours_for_the_grid"] = (out["seconds_per_rung_mean"] * len(b6.ALL_RUNGS_6)
                                 * len(fm.grid(family)) / 3600.0)
    # the endpoint must be finite; a non-finite FIRST step is reported and
    # is the sweep's to refuse (it writes the unit and the analyzer reads
    # the count of non-finite units), not the preflight's
    out["pass"] = bool(
        out["reads"]["endpoint, thin loader"]["n_nonfinite_logits"] == 0
        and all(r["digest_is_the_macs"] for r in out["reads"].values())
        and all(r.get("renders", {}).get("generation_eos_token_id")
                == r.get("renders", {}).get("stop_id_pinned")
                for r in out["reads"].values())
        and all(a["within"] for r in out["reads"].values()
                for a in r["anchors"].values())
        and (not twice or all(out["two_loaders"].values())))
    return out


def run_outcome(*, root=EXP6, device="cuda", families=None, loaders=None,
                cache_root=None, frozen_check=None, host=None, tag_exists=None,
                blobs_bound=None, log=print) -> dict:
    before = _guard(root, frozen_check)
    try:        # after the predictor seal: before any load and any host record
        ep.require_predictor_seal(root, tag_exists=tag_exists, blobs_bound=blobs_bound)
    except Exception as e:  # noqa: BLE001 — every way of not being sealed refuses
        raise RuntimeError(f"the outcome preflight runs after the predictor seal: "
                           f"{type(e).__name__}: {e}") from e
    host = host or cm.host_record(device)
    bad = cm.host_failures(host)
    if bad:
        raise RuntimeError(f"host record: {bad}")
    battery = b6.load_battery_6()
    loaders = ep.real_loaders() if loaders is None else loaders
    cache_root = cache_root if cache_root is not None else fm.CKPT_CACHE_6
    res = {f: family_preflight(f, device=device, loaders=loaders, battery=battery,
                               cache_root=cache_root, twice=(f == TWICE_FAMILY_6),
                               log=log)
           for f in (families or fm.FAMILIES_6)}
    _unchanged(root, before)
    log("[6 preflight] outcome stage complete: nothing written under results/")
    return {"stage": "outcome", "host": host, "families": res,
            "pass": all(r["pass"] for r in res.values())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 6 preflight (scratch only)")
    ap.add_argument("--stage", required=True, choices=("predictor", "outcome"))
    ap.add_argument("--root", default=str(EXP6))
    ap.add_argument("--device", default=None)
    ap.add_argument("--predictor", action="append", choices=sorted(r6.PREDICTORS_6))
    ap.add_argument("--family", action="append", choices=fm.FAMILIES_6)
    a = ap.parse_args(argv)
    if a.stage == "predictor":
        out = run_predictor(root=Path(a.root), device=a.device or "mps",
                            predictors=a.predictor)
    else:
        out = run_outcome(root=Path(a.root), device=a.device or "cuda",
                          families=a.family)
    print(f"[6 preflight] {a.stage}: {'PASS' if out['pass'] else 'FAIL'}")
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
