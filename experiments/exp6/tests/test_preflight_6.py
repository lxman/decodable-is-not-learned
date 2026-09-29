# experiments/exp6/tests/test_preflight_6.py
"""The preflight with fake models: what it passes, what it fails, and
that it writes no campaign record, prints no new-battery score, and checks
the anchors against their committed counts."""
import json

import pytest

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import families_6 as fm
from experiments.exp6 import records_6 as r6
from experiments.exp6 import referents_6 as rf
from experiments.exp6 import verify_6 as v6
from experiments.exp6.run import preflight_6 as pf
from experiments.exp6.run import seal_predictor_6 as sp
from experiments.exp6.tests import _world_6 as W

QUIET = dict(frozen_check=lambda: None, log=lambda *a: None)


@pytest.fixture(scope="module")
def battery():
    return b6.load_battery_6()


@pytest.fixture(scope="module")
def design(battery):
    return W.Design(W.spec(rho=W.general()), battery)


@pytest.fixture
def root(tmp_path):
    r6.write_json(r6.results(tmp_path) / "predictor" / "kept.json", {"kept": True})
    return tmp_path


def predictor(root, design, **kw):
    kw.setdefault("sampler", W.fake_sampler(design))
    kw.setdefault("nonfinite", lambda model, tok, prompts: 0)
    return pf.run_predictor(root=root, device="cpu", loader=W.fake_predictor_loader,
                            **QUIET, **kw)


SEALED = dict(tag_exists=W.tag_exists, blobs_bound=W.blobs_bound)


@pytest.fixture
def sealed(root):
    """The outcome preflight runs after the predictor seal (final review
    C-1, ruling I-19): the smallest tree a predictor seal describes."""
    files = sp.file_table(root)
    r6.write_json(r6.seal_path(root), {"files": files,
                                       "sha256": r6.composite_sha(files)})
    return root


def outcome(root, design, **kw):
    loaders = kw.pop("loaders", None) or W.fake_loaders(design, **kw)
    return pf.run_outcome(root=root, device="cuda", loaders=loaders, host=W.host(),
                          cache_root=root / "ckpt", **SEALED, **QUIET)


# ------------------------------------------------------------ the predictor
def test_the_predictor_preflight(root, design):
    before = pf.results_snapshot(root)
    out = predictor(root, design)
    assert out["pass"] and sorted(out["predictors"]) == sorted(r6.PREDICTORS_6)
    for p, row in out["predictors"].items():
        assert row["model_is_pinned"] and row["n_nonfinite_logits"] == 0
        assert row["rehearsal"] == {"rung": "add_base8", "item": 0,
                                    "k": r6.tier_shape(p, "main")["k"],
                                    "identical": True}
        assert tuple(row["rungs"]) == pf.PREFLIGHT_RUNGS_6
        for rung, r in row["rungs"].items():
            assert r["twice_identical"] and r["budget"] == b6.max_new_tokens_6(rung)
            assert r["shape"]["n"] == r6.tier_shape(p, "main")["k"]
    assert pf.results_snapshot(root) == before and len(before) == 1


def test_the_preflight_reports_no_score(root, design):
    """Shape, seconds, identity: nothing that says how many draws on a
    rung of the new battery are right."""
    said = []
    pf.run_predictor(root=root, device="cpu", loader=W.fake_predictor_loader,
                     sampler=W.fake_sampler(design),
                     nonfinite=lambda m, t, p: 0, frozen_check=lambda: None,
                     log=lambda *a: said.append(" ".join(map(str, a))))
    out = predictor(root, design)
    text = json.dumps(out, default=str) + " ".join(said)
    for word in ("correct", "verified", "bits", "draws\":", "continuations"):
        assert word not in text, word
    assert set(out["predictors"]["pythia_1b"]["rungs"]["temporal"]["shape"]) == \
        {"n", "n_empty", "n_most_common"}


def test_a_rehearsal_that_differs_fails(root, design):
    inner = W.fake_sampler(design)

    def sampler(model, tok, prompt, **kw):
        got = inner(model, tok, prompt, **kw)
        if kw["rung"] == "add_base8" and kw["size"] == "1b":
            got[kw["seeds"][0]][3] += "!"
        return got
    out = predictor(root, design, sampler=sampler)
    assert not out["pass"]
    assert out["predictors"]["pythia_1b"]["rehearsal"]["identical"] is False
    assert out["predictors"]["olmo2_1b"]["pass"]


def test_a_sampler_that_is_not_seeded_fails(root, design):
    inner, calls = W.fake_sampler(design), []

    def sampler(model, tok, prompt, **kw):
        got = inner(model, tok, prompt, **kw)
        calls.append(kw["rung"])
        if kw["rung"] == "ipa_word" and calls.count("ipa_word") % 2 == 0:
            got[kw["seeds"][0]][0] += " again"
        return got
    out = predictor(root, design, sampler=sampler, predictors=("pythia_410m",))
    row = out["predictors"]["pythia_410m"]
    assert not out["pass"] and not row["rungs"]["ipa_word"]["twice_identical"]
    assert row["rungs"]["temporal"]["twice_identical"]


def test_a_predictor_with_non_finite_logits_fails(root, design):
    out = predictor(root, design, nonfinite=lambda m, t, p: 3,
                    predictors=("olmo2_1b",))
    assert not out["pass"] and out["predictors"]["olmo2_1b"]["n_nonfinite_logits"] == 3


def test_a_loader_off_its_pin_fails(root, design):
    def loader(predictor, mode, device):
        tok, model, rec = W.fake_predictor_loader(predictor, mode, device)
        return tok, model, dict(rec, model_sha="0" * 40)
    out = pf.run_predictor(root=root, device="cpu", loader=loader,
                           sampler=W.fake_sampler(design),
                           nonfinite=lambda m, t, p: 0, predictors=("pythia_1b",),
                           **QUIET)
    assert not out["pass"] and not out["predictors"]["pythia_1b"]["model_is_pinned"]


def test_a_preflight_that_writes_under_results_is_refused(root, design):
    def loader(predictor, mode, device):
        r6.write_json(r6.results(root) / "predictor" / "leak.json", {})
        return W.fake_predictor_loader(predictor, mode, device)
    with pytest.raises(RuntimeError, match="the preflight wrote under"):
        pf.run_predictor(root=root, device="cpu", loader=loader,
                         sampler=W.fake_sampler(design),
                         nonfinite=lambda m, t, p: 0, predictors=("pythia_1b",),
                         **QUIET)


def test_the_frozen_modules_are_checked_first(root, design):
    def moved():
        raise RuntimeError("a frozen module moved")
    with pytest.raises(RuntimeError, match="a frozen module moved"):
        pf.run_predictor(root=root, device="cpu", loader=W.fake_predictor_loader,
                         sampler=W.fake_sampler(design), frozen_check=moved)


# -------------------------------------------------------------- the outcome
def test_the_outcome_preflight(sealed, design):
    root = sealed
    before = pf.results_snapshot(root)
    out = outcome(root, design)
    assert out["pass"] and tuple(out["families"]) == fm.FAMILIES_6
    for f, row in out["families"].items():
        names = ["endpoint, thin loader", "first grid step, checkpoint loader"]
        if f == pf.TWICE_FAMILY_6:
            names.append("endpoint, checkpoint loader")
            assert row["two_loaders"] == {"digests_equal": True,
                                          "continuations_identical": True}
        else:
            assert "two_loaders" not in row
        assert list(row["reads"]) == names
        assert row["reads"][names[0]]["step"] == fm.endpoint_step(f)
        assert row["reads"][names[1]]["step"] == fm.grid(f)[0]
        for read in row["reads"].values():
            assert read["digest_is_the_macs"] is True       # gate 1(d), rehearsed
            assert tuple(read["rungs"]) == pf.PREFLIGHT_RUNGS_6
            assert all(v["shape"]["n"] == v["n_items"] == pf.N_ITEMS_OUTCOME == 40
                       for v in read["rungs"].values())
            if fm.RENDER_6[f] == "bos":
                assert read["renders"]["plain"] == [52, 29]
                assert read["renders"]["bos"] == [2, 52, 29]
                assert read["renders"]["generation_eos_token_id"] == \
                    read["renders"]["stop_id_pinned"] == 3
                assert read["renders"]["config_eos_token_id"] == 2
            else:
                assert "renders" not in read
        assert row["hours_for_the_grid"] >= 0
    assert pf.results_snapshot(root) == before
    text = json.dumps(out, default=str)
    for word in ("correct", "bits", "continuations\":"):
        assert word not in text, word


def test_two_loaders_that_disagree_fail(sealed, design):
    root = sealed
    out = outcome(root, design, digest=lambda f, k, how: f"{f}:{k}:{how}")
    row = out["families"][pf.TWICE_FAMILY_6]
    assert not out["pass"] and row["two_loaders"]["digests_equal"] is False
    assert row["two_loaders"]["continuations_identical"] is True
    assert not any(r["digest_is_the_macs"] for f in out["families"].values()
                   for r in f["reads"].values())
    # two loaders that agree with each other and not with the Mac: no pass either
    out = outcome(root, design, digest=lambda f, k, how: f"{f}:{k}")
    assert out["families"][pf.TWICE_FAMILY_6]["two_loaders"]["digests_equal"] is True
    assert not out["pass"] and not any(f["pass"] for f in out["families"].values())
    seen = []

    def perturb(family, key, rung, conts):
        seen.append((family, key, rung))
        if family == pf.TWICE_FAMILY_6 and rung == "temporal" and \
                seen.count((family, key, rung)) == 2:
            conts[11] = " another"
        return conts
    out = outcome(root, design, perturb=perturb)
    row = out["families"][pf.TWICE_FAMILY_6]
    assert not out["pass"] and row["two_loaders"] == {
        "digests_equal": True, "continuations_identical": False}


def test_a_non_finite_endpoint_fails_and_a_non_finite_first_step_is_reported(
        sealed, design):
    root = sealed
    end = {f: fm.endpoint_step(f) for f in fm.FAMILIES_6}
    out = outcome(root, design, nonfinite=lambda model, tok, prompts: (
        5 if (model.family == "olmo13b" and model.key == end["olmo13b"]) else 0))
    assert not out["pass"] and not out["families"]["olmo13b"]["pass"]
    assert out["families"]["olmo7b"]["pass"]
    out = outcome(root, design, nonfinite=lambda model, tok, prompts: (
        9 if model.key == fm.grid(model.family)[0] else 0))
    assert out["pass"]
    for row in out["families"].values():
        assert row["reads"]["first grid step, checkpoint loader"][
            "n_nonfinite_logits"] == 9


def test_a_stop_id_that_was_not_overridden_fails(sealed, design):
    root = sealed
    """Comma's config names its BOS as the stop id; the loaders override
    it, and the preflight holds what the loader MEASURED to the pin."""
    loaders = W.fake_loaders(design)
    inner = loaders["thin"]

    def thin(family, man, *, device):
        model, tok, info = inner(family, man, device=device)
        if family == "comma_7b":
            info = dict(info, generation_eos_token_id=2)
        return model, tok, info
    loaders["thin"] = thin
    out = outcome(root, design, loaders=loaders)
    assert not out["pass"] and not out["families"]["comma_7b"]["pass"]
    assert out["families"]["olmo7b"]["pass"]


def test_a_host_off_the_stack_pin_is_refused(sealed, design):
    root = sealed
    h = W.host()
    h["stack"] = dict(h["stack"], torch="2.11.0")
    with pytest.raises(RuntimeError, match="host record"):
        pf.run_outcome(root=root, device="cuda", loaders=W.fake_loaders(design),
                       host=h, cache_root=root / "ckpt", **SEALED, **QUIET)


def test_the_outcome_preflight_runs_after_the_predictor_seal(root, sealed, monkeypatch):
    """Final review C-1 (ruling I-19): the outcome preflight loads each
    family's endpoint and first grid step, so it runs after the predictor
    seal; it refuses before it loads anything and before it builds a host
    record. The predictor preflight is unchanged."""
    from experiments.exp6.run import _common_6 as cm
    W.no_real_loaders(monkeypatch)

    def no_host(*a, **k):
        raise AssertionError("the preflight built a host record")
    monkeypatch.setattr(cm, "host_record", no_host)
    r6.seal_path(root).unlink()                        # not sealed
    before = pf.results_snapshot(root)
    with pytest.raises(RuntimeError, match="after the predictor seal"):
        pf.run_outcome(root=root, device="cuda", loaders=W.Unreached(), host=None,
                       cache_root=root / "ckpt", **SEALED, **QUIET)
    assert pf.results_snapshot(root) == before
    sealed_ = dict(SEALED)
    files = sp.file_table(root)
    r6.write_json(r6.seal_path(root), {"files": files, "sha256": r6.composite_sha(files)})
    # the tag is not there
    with pytest.raises(RuntimeError, match="after the predictor seal.*does not exist"):
        pf.run_outcome(root=root, device="cuda", loaders=W.Unreached(), host=None,
                       cache_root=root / "ckpt",
                       **dict(sealed_, tag_exists=lambda t: False), **QUIET)
    # a file the seal does not describe
    r6.write_json(r6.results(root) / "predictor" / "late.json", {})
    with pytest.raises(RuntimeError, match="does not describe the files on disk"):
        pf.run_outcome(root=root, device="cuda", loaders=W.Unreached(), host=None,
                       cache_root=root / "ckpt", **SEALED, **QUIET)
    # the injections default to the real tag lookups; main() passes none
    import inspect
    sig = inspect.signature(pf.run_outcome).parameters
    assert sig["tag_exists"].default is None and sig["blobs_bound"].default is None


def test_the_outcome_preflight_rehearses_gate_1c(sealed, design):
    """Final review M-4 (ruling I-22): each read scores the two anchors on
    all their items and holds each count to the Mac's committed count of
    that checkpoint within the cross-host tolerance. The anchors are 2c's
    items, whose outcomes are committed."""
    out = outcome(sealed, design)
    assert out["pass"]
    for f, row in out["families"].items():
        for name, read in row["reads"].items():
            assert set(read["anchors"]) == set(b6.ANCHORS_6), (f, name)
            for r, a in read["anchors"].items():
                assert a == {"count": rf.mac_count(f, read["step"], r),
                             "mac": rf.mac_count(f, read["step"], r),
                             "within": True}, (f, name, r)
    # one anchor of one read moved past the tolerance: that family fails
    end = fm.endpoint_step("olmo7b")
    mac = rf.mac_count("olmo7b", end, "sub_base8")
    assert mac > rf.TOL_PER_RUNG_6

    def perturb(family, key, rung, conts):
        if family == "olmo7b" and key == end and rung == "sub_base8":
            return [W.WRONG] * len(conts)
        return conts
    out = outcome(sealed, design, perturb=perturb)
    assert not out["pass"] and not out["families"]["olmo7b"]["pass"]
    assert out["families"]["olmo7b"]["reads"]["endpoint, thin loader"]["anchors"][
        "sub_base8"] == {"count": 0, "mac": mac, "within": False}
    assert out["families"]["olmo7b"]["reads"]["endpoint, thin loader"]["anchors"][
        "add_base8"]["within"] is True
    assert all(out["families"][f]["pass"] for f in fm.FAMILIES_6 if f != "olmo7b")
    # inside the tolerance is within: fifteen items moved still pass
    moved = {"n": 0}

    def fifteen(family, key, rung, conts):
        if family == "olmo7b" and key == end and rung == "sub_base8":
            conts = list(conts)
            cap = design.battery[rung]
            for i, c in enumerate(conts):
                if moved["n"] < rf.TOL_PER_RUNG_6 and v6.verify_6(
                        c, cap["eval_items"][i]["answer"], cap["answer_type"]):
                    conts[i] = W.WRONG
                    moved["n"] += 1
        return conts
    out = outcome(sealed, design, perturb=fifteen)
    got = out["families"]["olmo7b"]["reads"]["endpoint, thin loader"]["anchors"][
        "sub_base8"]
    assert moved["n"] == rf.TOL_PER_RUNG_6
    assert got == {"count": mac - rf.TOL_PER_RUNG_6, "mac": mac, "within": True}
    assert out["families"]["olmo7b"]["pass"]


# ----------------------------------------------------------------- the parts
def test_the_shape_of_a_set_of_continuations():
    s = pf.shape_of([" 12", " 12\nQ:", "", " \r", " x", " 7"], "number")
    assert s == {"n": 6, "n_empty": 2, "n_most_common": 2}
    assert pf.shape_of([" \r", "\n"], "word") == {"n": 2, "n_empty": 2,
                                                  "n_most_common": 2}
    assert pf.shape_of([], "ipa") == {"n": 0, "n_empty": 0, "n_most_common": 0}


def test_the_snapshot_sees_a_changed_byte(tmp_path):
    assert pf.results_snapshot(tmp_path) == frozenset()
    p = r6.results(tmp_path) / "a" / "b.json"
    r6.write_json(p, {"x": 1})
    one = pf.results_snapshot(tmp_path)
    r6.write_json(p, {"x": 2})
    assert pf.results_snapshot(tmp_path) != one and len(one) == 1


def test_the_preflight_rungs_are_the_extremes(battery):
    rec = json.loads((b6.EXP6 / "battery" / "token_lengths_6.json").read_text())["rungs"]
    longest = max(b6.RUNGS_6, key=lambda r: max(rec[r]["prompt_tokens_max"].values()))
    budget = max(b6.RUNGS_6, key=lambda r: rec[r]["budget"])
    assert longest == "temporal" and budget == "ipa_word"
    assert {longest, budget} <= set(pf.PREFLIGHT_RUNGS_6)


def test_the_preflight_uses_the_loaders_it_is_handed(sealed, monkeypatch):
    """What a caller hands in is used, falsy or not (see the same test of
    the endpoint stage and the sweep)."""
    root = sealed
    W.no_real_loaders(monkeypatch)
    with pytest.raises(AssertionError, match="reached its loader$"):
        pf.run_predictor(root=root, device="cpu", loader=W.Unreached(),
                         sampler=W.Unreached(), nonfinite=lambda m, t, p: 0, **QUIET)
    with pytest.raises(AssertionError, match="reached its loader '"):
        pf.run_outcome(root=root, device="cuda", loaders=W.Unreached(), host=W.host(),
                       cache_root=root / "ckpt", **SEALED, **QUIET)


def test_the_finiteness_probe_that_is_handed_in_is_the_one_used(root, design):
    seen = []

    class Falsy:
        def __bool__(self):
            return False

        def __call__(self, model, tok, prompts):
            seen.append(len(prompts))
            return 0
    out = predictor(root, design, nonfinite=Falsy())
    assert out["pass"] and len(seen) >= len(r6.PREDICTORS_6)
