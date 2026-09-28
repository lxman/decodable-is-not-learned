# experiments/exp6/tests/_world_6.py
"""Synthetic worlds for the analyzer, written by the REAL runners.

A world is a full-shape results tree: 93 predictor units, four families'
endpoint stage, the rung sets, a power record, four sweeps with their
per-host gate records. Nothing here writes a record by hand: the tree is
what `predict_6`, `seal_predictor_6`, `endpoint_6`, `seal_endpoint_6`
and `sweep_6` leave when they run against FAKE loaders and a FAKE
sampler (2d F-1: a verdict must be reachable from the tree the runner
leaves, so the worlds are the runner's trees).

The fakes decide only what a model would have said:
  - a predictor's draw on an item is the item's answer or a wrong
    string, by a designed count per item;
  - an outcome's continuation at a checkpoint is the answer from the
    item's designed first-correct step on;
  - on the anchors and the control, the committed streams and the Mac's
    committed records, verbatim, so every gate against a committed
    referent passes through the production path.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import families_6 as fm
from experiments.exp6 import pins_6 as p6
from experiments.exp6 import power_6 as pw6
from experiments.exp6 import records_6 as r6
from experiments.exp6 import referents_6 as rf
from experiments.exp6.run import _common_6 as cm
from experiments.exp6.run import endpoint_6 as ep
from experiments.exp6.run import predict_6 as pr
from experiments.exp6.run import seal_endpoint_6 as se
from experiments.exp6.run import seal_predictor_6 as sp
from experiments.exp6.run import sweep_6 as sw

WRONG = " qqq"
N = b6.N_ITEMS
STACK = {"torch": "2.12.1", "transformers": "5.13.0", "numpy": "2.4.6",
         "safetensors": "0.8.0", "tokenizers": "0.22.2", "huggingface_hub": "1.22.0"}
# three rungs of each type: enough for every test to be EVALUABLE
DEFAULT_R = ("modarith_add1", "modarith_mul1", "lcs", "unscramble_short", "sort3",
             "ascii_basic", "deduction3", "temporal", "unit_interp1")


# ------------------------------------------------------------- injections
class Unreached(dict):
    """A loader, a sampler or a table of loaders that must not be reached.
    It is EMPTY, and therefore falsy, on purpose: a runner that reads
    `loaders or real_loaders()` falls through it to the real loaders.
    The runners ask `is None`."""

    def __getitem__(self, k):
        raise AssertionError(f"the stage reached its loader {k!r}")

    def __call__(self, *a, **k):
        raise AssertionError("the stage reached its loader")


def no_real_loaders(monkeypatch) -> None:
    """Every door to a real model raises, and says which."""
    def real(*a, **k):
        raise AssertionError("the stage fell through to the REAL loaders")
    monkeypatch.setattr(ep, "real_loaders", real)
    monkeypatch.setattr(pr, "real_loader", real)
    monkeypatch.setattr(pr, "real_sampler", real)


def tag_exists(tag) -> bool:
    return True


def blob_sha(tag, rel):
    return p6.sha256_file(p6.REPO / rel)


def blobs_bound(tag, paths, *, repo_root=None) -> list:
    return []


INJECT = {"tag_exists": tag_exists, "blob_sha": blob_sha, "frozen_check": lambda: None}
INJECT_SEAL = dict(INJECT, blobs_bound=blobs_bound)
ANALYZE = dict(tag_exists=tag_exists, blob_sha=blob_sha, blobs_bound=blobs_bound,
               frozen_check=lambda: None, imports_pinned=False, referents_sha=False)


def host(node="box-1", device="cuda") -> dict:
    return cm.host_record(device, stack_=dict(STACK), gpu="NVIDIA A100 80GB PCIe",
                          cuda="13.0", node=node, python="3.11.9",
                          platform_="Linux-6.8.0-x86_64",
                          nvidia_smi="NVIDIA A100 80GB PCIe, 565.57.01, 81920 MiB")


# ------------------------------------------------------------ the design
def spec(*, rho=None, R=None, n_pos=300, seed=0, flat_pos=0, ipa_other=False) -> dict:
    """`rho[(test, family)]`: how strongly the family's order follows
    the predictor's latent (0 = not at all). `R[family]`: the rungs the
    family clears at its endpoint. `ipa_other`: every model writes its
    transcriptions under ANOTHER convention (no stress mark, the
    affricates as digraphs), right or wrong as the design says."""
    rho = dict(rho or {})
    return {"rho": {(t, f): float(rho.get((t, f), 0.0)) for t, f in pw6.TESTS_6},
            "R": {f: tuple((R or {}).get(f, DEFAULT_R)) for f in fm.FAMILIES_6},
            "n_pos": int(n_pos), "flat_pos": int(flat_pos), "seed": int(seed),
            "ipa_other": bool(ipa_other)}


def other_convention(ipa: str) -> str:
    for a, b in (("ˈ", ""), ("ˌ", ""), ("ʧ", "tʃ"), ("ʤ", "dʒ")):
        ipa = ipa.replace(a, b)
    return ipa


def general(strength=0.6) -> dict:
    return {(t, f): strength for t, f in pw6.TESTS_6}


class Design:
    """The latents and everything derived from them, for one spec."""

    def __init__(self, sp_: dict, battery: dict):
        self.spec, self.battery = sp_, battery
        rng = np.random.default_rng(sp_["seed"])
        self.z = {t: {r: rng.normal(size=N) for r in b6.RUNGS_6} for t in ("A", "B")}
        self.z["410m"] = {r: 0.8 * self.z["A"][r] + 0.6 * rng.normal(size=N)
                          for r in b6.RUNGS_6}
        self.pos = {}                  # (predictor, tier, rung) -> [k] bits per item
        self.first = {}                # (family, rung) -> first-correct index or None
        for f in fm.FAMILIES_6:
            n_steps = len(fm.grid(f))
            for r in b6.RUNGS_6:
                a, b = sp_["rho"][("A", f)], sp_["rho"][("B", f)]
                rest = max(0.0, 1.0 - a * a - b * b) ** 0.5
                w = a * self.z["A"][r] + b * self.z["B"][r] + rest * rng.normal(size=N)
                k = sp_["n_pos"] if r in sp_["R"][f] else sp_["flat_pos"]
                order = np.argsort(-w)
                first = [None] * N
                for rank, i in enumerate(order[:k]):
                    first[int(i)] = int(rank * n_steps / max(k, 1))
                self.first[(f, r)] = first
        self._rng = rng

    def said(self, rung, i) -> str:
        """The right answer as a model of this world writes it."""
        a = str(self.battery[rung]["eval_items"][i]["answer"])
        if rung == "ipa_word" and self.spec.get("ipa_other"):
            a = other_convention(a)
        return " " + a

    # ---- predictors
    def counts(self, predictor, tier, rung) -> np.ndarray:
        t = r6.tier_shape(predictor, tier)
        if t["mode"] == "untrained":
            return np.zeros(N, dtype=int)
        key = {"pythia_1b": "A", "olmo2_1b": "B", "pythia_410m": "410m"}[predictor]
        z = self.z[key][rung]
        p = 1.0 / (1.0 + np.exp(-(1.4 * z - 1.0)))
        return np.rint(p * t["k"]).astype(int)

    def bits(self, predictor, tier, rung) -> list:
        key = (predictor, tier, rung)
        if key not in self.pos:
            t = r6.tier_shape(predictor, tier)
            rng = np.random.default_rng(
                [self.spec["seed"], sorted(r6.PREDICTORS_6).index(predictor),
                 sorted(r6.TIERS_6).index(tier), b6.ALL_RUNGS_6.index(rung)])
            out = []
            for c in self.counts(predictor, tier, rung):
                row = np.zeros(t["k"], dtype=int)
                row[rng.permutation(t["k"])[:int(c)]] = 1
                out.append(row.tolist())
            self.pos[key] = out
        return self.pos[key]

    # ---- outcomes
    def continuations(self, family, key, rung) -> list:
        """`key`: a grid step, or "init"."""
        cap = self.battery[rung]
        if rung in b6.ANCHORS_6:       # the Mac's committed record, verbatim
            return list(r6.read_json(
                fm.committed_sweep_record(family, key, rung))["continuations"])
        if rung == b6.CONTROL_6:
            return [" " + str(it["answer"]) for it in cap["eval_items"]]
        if key == fm.INIT:
            return [WRONG] * N
        idx = list(fm.grid(family)).index(int(key))
        first = self.first[(family, rung)]
        return [self.said(rung, i) if (first[i] is not None and idx >= first[i])
                else WRONG for i in range(len(cap["eval_items"]))]


# ---------------------------------------------------------------- the fakes
class FakeTok:
    all_special_ids = (0,)


class FakeModel:
    device = "cpu"

    def __init__(self, family=None, key=None):
        self.family, self.key = family, key


def fake_predictor_loader(predictor, mode, device):
    pin = rf.model_pin(predictor)
    return FakeTok(), FakeModel(), {"repo": pin["repo"], "commit": pin["commit"],
                                    "model_sha": pin["model_sha"]}


def fake_sampler(design: Design, *, break_gate=None):
    committed = {}

    def sample_item(model, tok, prompt, *, rung, size, mode, item_idx, seeds,
                    draws_per_seed, max_new_tokens, terminal_ids):
        predictor = next(p for p, v in r6.PREDICTORS_6.items() if v["size"] == size)
        tier = next(t for t in r6.PREDICTOR_TIERS[predictor]
                    if r6.tier_shape(predictor, t)["mode"] == mode
                    and tuple(r6.tier_shape(predictor, t)["seeds"]) == tuple(seeds)
                    and r6.tier_shape(predictor, t)["dps"] == draws_per_seed
                    and rung in r6.tier_shape(predictor, t)["rungs"])
        unit = (predictor, tier, rung)
        if unit in rf.gated_units():
            if unit not in committed:
                committed[unit] = {r["item"]: r for r in rf.committed_rows(*unit)}
            out = {s: list(committed[unit][item_idx]["draws"][str(s)]) for s in seeds}
            if break_gate == unit and item_idx == 7:
                out[seeds[0]][0] = out[seeds[0]][0] + "!"
            return out
        row = design.bits(predictor, tier, rung)[item_idx]
        good = design.said(rung, item_idx)
        return {s: [good if row[j * draws_per_seed + d] else WRONG
                    for d in range(draws_per_seed)] for j, s in enumerate(seeds)}
    return sample_item


class FakeRunner:
    def __init__(self, design, family, key, *, perturb=None):
        self.design, self.family, self.key, self.perturb = design, family, key, perturb
        self.by_prompt = None

    def generate(self, prompts, max_new_tokens):
        if self.by_prompt is None:
            self.by_prompt = {pr.prompts_of(self.design.battery[r])[0]: r
                              for r in b6.ALL_RUNGS_6}
        rung = self.by_prompt[prompts[0]]
        out = self.design.continuations(self.family, self.key, rung)
        if self.perturb is not None:
            out = self.perturb(self.family, self.key, rung, list(out))
        return out[:len(prompts)]          # the preflight scores a prefix


def fake_loaders(design: Design, *, perturb=None, digest=None, nonfinite=None) -> dict:
    """`perturb(family, key, rung, continuations) -> continuations` and
    `digest(family, key, loader) -> str` let a world break one thing. A
    trained checkpoint's digest is the Mac's committed one (gate 1(d)); a
    seeded twin's is its own."""
    def the_macs(family, key, how):
        if key == fm.INIT and fm.INIT_KIND[family] == "twin":
            return f"digest:twin:{family}"
        return rf.mac_digest(family, key)

    def info_for(family, man, key, loader):
        e = fm.entry(family, man, key)
        d = (digest or the_macs)(family, key, loader)
        info = {"repo": fm.repo(family), "commit": e.get("commit"),
                "loading_info": {"missing_keys": 0, "unexpected_keys": 0,
                                 "mismatched_keys": 0},
                "tensor_digest": d}
        if e.get("kind") == "from_config":
            info.update({"revision": e["revision"], "seed": e["seed"]})
        elif loader == "checkpoint":
            info.update({"revision": e["revision"], "kind": e["kind"],
                         "sha256": dict(e["lfs_sha256"])})
        if fm.RENDER_6[family] == "bos":
            from experiments.exp2n import battery_2n as bn
            info.update({"config_eos_token_id": 2,
                         "generation_eos_token_id": bn.EOS_STOP_ID_2N})
        return info

    def thin(family, man, *, device):
        key = fm.endpoint_step(family)
        return FakeModel(family, key), FakeTok(), info_for(family, man, key, "thin")

    def init(family, man, *, device, cache_root=None):
        return FakeModel(family, fm.INIT), FakeTok(), info_for(family, man, fm.INIT,
                                                                "checkpoint")

    def checkpoint(family, man, step, *, device, cache_root=None):
        return FakeModel(family, int(step)), FakeTok(), info_for(family, man, step,
                                                                 "checkpoint")

    def runner(family, tok, model):
        return FakeRunner(design, model.family, model.key, perturb=perturb)

    return {"thin": thin, "init": init, "checkpoint": checkpoint, "runner": runner,
            "render_ids": lambda tok, text: [2, 52, 29] if text != "Q:" else [52, 29],
            "release": lambda model: None,
            "free": lambda family, man, step, cache_root=None: None,
            "nonfinite": nonfinite or (lambda model, tok, prompts: 0)}


# -------------------------------------------------------------- the stages
def build_predictors(root, design, **kw) -> None:
    sampler = fake_sampler(design, break_gate=kw.get("break_gate"))
    for p in r6.PREDICTORS_6:
        pr.run(p, root=root, device="cpu", loader=fake_predictor_loader,
               sampler=sampler, **INJECT)


def seal_predictors(root) -> dict:
    return sp.seal(root, **INJECT)


def build_endpoints(root, design, *, host_rec=None, families=None, **kw) -> dict:
    h = host_rec or host("box-endpoint")
    r6.write_json(cm.hosts_dir(root) / f"{h['sha256'][:12]}.json", h)
    return ep.run(root=root, device="cuda", families=families,
                  loaders=fake_loaders(design, **kw), host=h, **INJECT_SEAL)


def seal_endpoints(root) -> dict:
    return se.seal(root, **INJECT_SEAL)


def fake_power_test(inp: dict, *, p15=0.9, false_fire=0.01) -> dict:
    """One test's power record with the numbers CHOSEN and everything
    else derived exactly as the real producer derives it."""
    from experiments.exp2i import analyze_2i as an2i
    from experiments.exp2i import power_2i as pw
    rungs = list(inp["rungs"])
    dropped = list(an2i._degenerate_rungs(inp["x"], inp["strata"], rungs))
    keep = [r for r in rungs if r not in dropped]
    rec = {"rungs": rungs, "dropped_degenerate": dropped, "rungs_simulated": keep,
           "n_pos_lower_bound": {r: int(inp["n_pos"][r]) for r in rungs},
           "n_trained_steps": inp["n_steps"], "bar": pw.BAR,
           "declare_at": pw.DECLARE_AT, "t_bar": an2i.T_BAR, "alpha": an2i.ALPHA,
           "n_sim": pw.N_SIM, "n_perm": pw.N_PERM_POWER, "thin": len(keep) < 3,
           "targets": {}}
    if not keep:
        rec.update({"declared_status": "THIN", "declaration": "nothing simulated"})
        return rec
    for d, p in (("0.1", max(0.0, p15 - 0.4)), ("0.15", p15), ("0.2", min(1.0, p15 + 0.05))):
        rec["targets"][d] = {"p_fires": float(p), "calibrated_rho": 0.3,
                             "mean_T": float(d), "sd_T": 0.01}
    rec["null"] = {"false_fire_rate": float(false_fire), "null_sd_T": 0.011,
                   "p_fires": float(false_fire)}
    rec["min_detectable_T"] = 0.027
    rec["declared_status"] = ("POWERED" if p15 >= pw.BAR
                              else "DECLARED UNDERPOWERED IN ADVANCE")
    rec["declaration"] = f"P(fires | D_true = {pw.DECLARE_AT}) = {p15:.3f}"
    return rec


def write_power(root, *, p15=0.9, overrides=None) -> dict:
    """The power record over the REAL inputs of the sealed tree."""
    from experiments.exp6 import analyze_6 as an
    ctx, bad = an.load_sealed_stages(root, tag_exists=tag_exists,
                                     blobs_bound=blobs_bound)
    assert not bad, bad[:5]
    inputs = an.test_inputs(ctx)
    tests = {}
    for t, f in pw6.TESTS_6:
        name = pw6.test_name(t, f)
        rec = fake_power_test(inputs[(t, f)], p15=(overrides or {}).get(name, p15))
        rec.update({"test": t, "family": f, "predictor": r6.TEST_PREDICTOR[t]})
        tests[name] = rec
    rec = {"tests": tests, "tree": pw6.tree_level(tests), "note": pw6.NOTE_6,
           "predictor_sha256": ctx["seal"]["sha256"],
           "rung_sets_sha256": r6.sha256_file(r6.rung_sets_path(root)),
           "calibration_note": an.CALIBRATION_SENTENCE_6,
           "prereg_tag": r6.PREREG_TAG_6, "git_sha": ""}
    r6.write_json(r6.power_path(root), rec)
    return rec


def build_sweep(root, design, family, *, host_rec=None, stop_after=None, **kw) -> dict:
    h = host_rec or host("box-sweep")
    r6.write_json(cm.hosts_dir(root) / f"{h['sha256'][:12]}.json", h)
    loaders = fake_loaders(design, **kw)
    if stop_after is not None:
        inner, seen = loaders["checkpoint"], []

        def checkpoint(family_, man, step, *, device, cache_root=None):
            if len(seen) >= stop_after:
                raise KeyboardInterrupt("the box died")
            seen.append(step)
            return inner(family_, man, step, device=device, cache_root=cache_root)
        loaders["checkpoint"] = checkpoint
    return sw.run(family, root=root, device="cuda", loaders=loaders, host=h,
                  cache_root=Path(root) / "ckpt", **INJECT_SEAL)


def build_world(root, sp_: dict, *, battery=None, stages=("predictor", "endpoint",
                                                          "power", "sweep"),
                p15=0.9) -> Design:
    root = Path(root)
    battery = battery or b6.load_battery_6()
    design = Design(sp_, battery)
    if "predictor" in stages:
        build_predictors(root, design)
        seal_predictors(root)
    if "endpoint" in stages:
        build_endpoints(root, design)
        seal_endpoints(root)
    if "power" in stages:
        write_power(root, p15=p15)
    if "sweep" in stages:
        for f in fm.FAMILIES_6:
            build_sweep(root, design, f)
    return design


def clone(src, dst) -> Path:
    """A world copied for one mutation (the base tree is never touched)."""
    shutil.copytree(src, dst)
    return Path(dst)
