# experiments/exp6/tests/test_families_6.py
"""The four families: the grids are the committed ones, and every call
this module makes into a frozen loader BINDS to that loader's real
signature (no model is loaded: the loaders are replaced by recorders and
what was recorded is bound against the real function)."""
import inspect

import pytest

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import families_6 as fm


def test_the_grids_are_the_committed_ones():
    assert fm.FAMILIES_6 == ("smollm3_3b", "olmo7b", "olmo13b", "comma_7b")
    assert {f: len(fm.grid(f)) for f in fm.FAMILIES_6} == {
        "smollm3_3b": 26, "olmo7b": 21, "olmo13b": 16, "comma_7b": 24}
    assert sum(len(fm.grid(f)) for f in fm.FAMILIES_6) == 87
    assert {f: fm.endpoint_step(f) for f in fm.FAMILIES_6} == {
        "smollm3_3b": 3440000, "olmo7b": 928646, "olmo13b": 596057,
        "comma_7b": 460000}
    for f in fm.FAMILIES_6:
        g = list(fm.grid(f))
        assert g == sorted(g) and len(set(g)) == len(g) and g[-1] == fm.endpoint_step(f)
    assert fm.INIT_KIND == {"smollm3_3b": "twin", "olmo7b": "twin",
                            "olmo13b": "step0", "comma_7b": "twin"}
    assert fm.RENDER_6["comma_7b"] == "bos" and \
        [fm.RENDER_6[f] for f in fm.FAMILIES_6[:3]] == ["plain"] * 3
    with pytest.raises(ValueError):
        fm.grid("pythia_2.8b")


@pytest.mark.parametrize("family", fm.FAMILIES_6)
def test_every_grid_step_has_a_pinned_entry(family):
    man = fm.manifest(family)
    for step in fm.grid(family):
        e = fm.entry(family, man, step)
        assert e["commit"] and e["revision"] and e["lfs_sha256"], (family, step)
        assert e["kind"] != "from_config"
    init = fm.entry(family, man, fm.INIT)
    if fm.INIT_KIND[family] == "twin":
        assert init["kind"] == "from_config" and init["seed"] == 0
        assert init["config_commit"] == fm.entry(family, man,
                                                 fm.endpoint_step(family))["commit"]
    else:
        assert init["revision"].startswith("stage1-step0")
    with pytest.raises(ValueError, match="not on the grid"):
        fm.entry(family, man, 7)


@pytest.mark.parametrize("family", fm.FAMILIES_6)
def test_the_macs_committed_anchor_records_exist(family):
    for r in b6.ANCHORS_6:
        assert fm.committed_endpoint_record(family, r).is_file()
        assert fm.committed_sweep_record(family, fm.INIT, r).is_file()
        for s in fm.grid(family):
            assert fm.committed_sweep_record(family, s, r).is_file(), (family, s, r)


def _real(family):
    bi, bl, bm, bn = fm._mods()
    return {"smollm3_3b": (bm, "load_thin_3b", "load_checkpoint_3b", "load_twin_3b",
                           "load_tokenizer_3b", "free_checkpoint_3b"),
            "olmo7b": (bi, "load_thin", "load_checkpoint", "load_twin_7b",
                       "load_tokenizer", "free_checkpoint"),
            "olmo13b": (bl, "load_thin_13b", "load_checkpoint_13b", None,
                        "load_tokenizer_13b", "free_checkpoint_13b"),
            "comma_7b": (bn, "load_thin_comma", "load_checkpoint_comma",
                         "load_twin_comma", "load_tokenizer_comma",
                         "free_checkpoint_comma")}[family]


@pytest.mark.parametrize("family", fm.FAMILIES_6)
def test_every_call_into_a_frozen_loader_binds(family, monkeypatch, tmp_path):
    mod, *names = _real(family)
    calls = []

    def recorder(name, returns):
        real = getattr(mod, name)

        def fake(*a, **k):
            b = inspect.signature(real).bind(*a, **k)   # raises TypeError if it cannot
            b.apply_defaults()
            calls.append(name)
            seen.setdefault(name, []).append(dict(b.arguments))
            return returns
        return fake
    seen = {}
    thin, ckpt, twin, tok, free = names
    monkeypatch.setattr(mod, thin, recorder(thin, ("M", "T", {"i": 1})))
    monkeypatch.setattr(mod, ckpt, recorder(ckpt, ("M", {"i": 1})))
    monkeypatch.setattr(mod, tok, recorder(tok, "T"))
    monkeypatch.setattr(mod, free, recorder(free, None))
    if twin:
        monkeypatch.setattr(mod, twin, recorder(twin, ("M", {"i": 1})))
    man = fm.manifest(family)
    assert fm.load_thin(family, man, device="cuda") == ("M", "T", {"i": 1})
    assert fm.load_checkpoint(family, man, fm.grid(family)[0], device="cuda",
                              cache_root=tmp_path) == ("M", "T", {"i": 1})
    assert fm.load_init(family, man, device="cuda", cache_root=tmp_path) == \
        ("M", "T", {"i": 1})
    fm.free(family, man, fm.grid(family)[0], cache_root=tmp_path)
    fm.free(family, man, fm.INIT, cache_root=tmp_path)
    want = {thin, ckpt, tok, free} | ({twin} if twin else set())
    assert set(calls) == want
    # and WHAT each loader was handed: the family's own repository, the
    # pinned commit or entry, the campaign's dtype, the caller's device
    end = fm.entry(family, man, fm.endpoint_step(family))
    first = fm.entry(family, man, fm.grid(family)[0])
    for name, args_list in seen.items():
        for args in args_list:
            assert args.get("repo", fm.repo(family)) == fm.repo(family), (name, args)
            if name in (thin, ckpt, twin):
                assert args["device"] == "cuda" and args["dtype"] == fm.DTYPE_6, name
    assert end["commit"] in seen[thin][0].values()
    assert first in seen[ckpt][0].values()
    assert set(seen[tok][0].values()) & {first["commit"], end["commit"]}
    if fm.INIT_KIND[family] == "twin":
        with pytest.raises(ValueError, match="is a twin"):
            fm.load_checkpoint(family, man, fm.INIT, device="cuda")


def test_every_frozen_loader_takes_the_device_as_an_argument():
    """The sweeps run on a rented GPU: no loader may hold the Mac's
    device as anything but a default."""
    for family in fm.FAMILIES_6:
        mod, thin, ckpt, twin, _, _ = _real(family)
        for name in (thin, ckpt, twin):
            if name:
                assert "device" in inspect.signature(getattr(mod, name)).parameters


def test_comma_is_scored_through_the_bos_runner(monkeypatch):
    from experiments.exp6 import verify_6 as v6
    h = v6.harness_2c()
    made = []
    monkeypatch.setattr(h, "HFRunner", lambda tok, model, bs: made.append(bs) or "inner")
    _, _, _, bn = fm._mods()
    monkeypatch.setattr(bn, "BosRunner", lambda inner: ("bos", inner))
    assert fm.runner("olmo7b", "T", "M") == "inner"
    assert fm.runner("comma_7b", "T", "M") == ("bos", "inner")
    assert made == [16, 16] and fm.BATCH_SIZE_6 == 16 and fm.DTYPE_6 == "float16"


def test_a_release_that_fails_says_so(monkeypatch, capsys):
    import gc

    def broken():
        raise RuntimeError("the allocator would not let go")
    monkeypatch.setattr(gc, "collect", broken)
    fm.release(object())                                   # does not raise
    assert "families_6.release: RuntimeError: the allocator would not let go" in \
        capsys.readouterr().err
    fm.release(None)
    assert capsys.readouterr().err == ""
