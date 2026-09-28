# experiments/exp6/tests/test_pins_6.py
"""The bindings: a tag binds an instrument, not a name (2h F-3); a seal
that cannot be checked is a failure line, never an exception."""
import pytest

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import pins_6 as p6
from experiments.exp6 import records_6 as r6


def _sha(tag, rel):
    return p6.sha256_file(p6.REPO / rel)


def test_the_blobs_the_preregistration_binds():
    assert len(p6.INSTRUMENT_BLOBS_6) == len(set(p6.INSTRUMENT_BLOBS_6)) == 16
    assert len(p6.ITEM_BLOBS_6) == 17
    for rel in ("experiments/exp6/analyze_6.py", "experiments/exp6/power_6.py",
                "experiments/exp6/run/predict_6.py", "experiments/exp6/run/sweep_6.py",
                "experiments/exp6/run/endpoint_6.py", "experiments/exp6/strata_6.py",
                "experiments/exp6/floors_6.py", "experiments/exp6/verify_6.py"):
        assert rel in p6.INSTRUMENT_BLOBS_6
    assert (r6.PREREG_TAG_6, r6.PREDICTOR_SEAL_TAG_6, r6.ENDPOINT_SEAL_TAG_6) == \
        ("exp6-preregistered", "exp6-predictor-sealed", "exp6-endpoint-sealed")


def test_require_tag(tmp_path):
    rels = ["experiments/exp6/battery_6.py", "experiments/exp6/verify_6.py"]
    ok = p6.require_tag("t", rels, tag_exists=lambda t: True, blob_sha=_sha)
    assert ok["n_bound"] == 2
    with pytest.raises(RuntimeError, match="does not exist"):
        p6.require_tag("t", rels, tag_exists=lambda t: False, blob_sha=_sha)
    with pytest.raises(RuntimeError, match="does not bind"):
        p6.require_tag("t", rels, tag_exists=lambda t: True,
                       blob_sha=lambda tag, rel: "0" * 64)
    with pytest.raises(RuntimeError, match="does not bind"):   # the tag lacks the path
        p6.require_tag("t", rels, tag_exists=lambda t: True,
                       blob_sha=lambda tag, rel: None)
    with pytest.raises(RuntimeError, match="not on disk"):
        p6.require_tag("t", ["experiments/exp6/nope.py"], tag_exists=lambda t: True,
                       blob_sha=_sha)


def test_the_real_binding_refuses_before_the_tag_is_cut():
    """On the real repository, before the tag exists: a refusal."""
    if p6.git_tag_exists(r6.PREREG_TAG_6):
        pytest.skip("the tag has been cut")
    with pytest.raises(RuntimeError, match="does not exist"):
        p6.require_prereg_6()


def test_seal_failures_never_raise():
    paths = [b6.EXP6 / "battery_6.py"]
    none = lambda tag, rel, repo_root=None: []                          # noqa: E731
    assert p6.seal_failures("t", paths, tag_exists=lambda t: True, blobs_bound=none) == []
    assert "does not exist" in p6.seal_failures(
        "t", paths, tag_exists=lambda t: False, blobs_bound=none)[0]
    drift = lambda tag, rel, repo_root=None: list(rel)                  # noqa: E731
    bad = p6.seal_failures("t", paths, tag_exists=lambda t: True, blobs_bound=drift)
    assert len(bad) == 1 and "does not bind 1 file" in bad[0]

    def boom(*a, **k):
        raise OSError("git is gone")
    assert "OSError" in p6.seal_failures("t", paths, tag_exists=boom,
                                         blobs_bound=none)[0]
    assert "OSError" in p6.seal_failures("t", paths, tag_exists=lambda t: True,
                                         blobs_bound=boom)[0]
    with pytest.raises(RuntimeError):
        p6.require_seal("t", paths, tag_exists=lambda t: False, blobs_bound=none)


def test_seal_failures_hand_git_paths_relative_to_the_repository():
    seen = []

    def bound(tag, rel, repo_root=None):
        seen.extend(rel)
        return []
    p6.seal_failures("t", [b6.EXP6 / "results" / "power_6.json"],
                     tag_exists=lambda t: True, blobs_bound=bound)
    assert seen == ["experiments/exp6/results/power_6.json"]


def test_the_import_surface_sees_what_the_interpreter_loaded():
    import experiments.exp6.analyze_6  # noqa: F401
    surf = p6.import_surface()
    assert "experiments/exp6/analyze_6.py" in surf
    assert not any("/tests/" in k for k in surf)
    assert all(len(v) == 64 for v in surf.values())


def test_unpinned_builds_refuse(monkeypatch):
    """Whether the build has filled its pins or not: an empty table
    refuses (a test that needs the pins EMPTY stops running the day they
    are filled, which is the day it matters)."""
    monkeypatch.setattr(p6, "FROZEN_SHA256_6", None)
    monkeypatch.setattr(p6, "IMPORTED_SHA256_6", None)
    with pytest.raises(RuntimeError, match="not pinned"):
        p6.check_frozen_6()
    with pytest.raises(RuntimeError, match="not pinned"):
        p6.check_imports_6()


# ------------------------------------------------ the pins, when they are filled
@pytest.fixture
def pinned(monkeypatch):
    """The import surface as it stands, pinned as the closure pins it:
    earlier experiments' files frozen, Exp 6's unbound files imported."""
    import experiments.exp6.analyze_6  # noqa: F401
    surf = p6.import_surface()
    bound = set(p6.INSTRUMENT_BLOBS_6)
    frozen = {k: v for k, v in surf.items() if not k.startswith("experiments/exp6/")}
    own = {k: v for k, v in surf.items()
           if k.startswith("experiments/exp6/") and k not in bound}
    assert frozen and own and bound & set(surf)
    monkeypatch.setattr(p6, "FROZEN_SHA256_6", dict(frozen))
    monkeypatch.setattr(p6, "IMPORTED_SHA256_6", dict(own))
    return frozen, own


def test_the_pinned_surface_passes(pinned):
    p6.check_frozen_6()
    p6.check_imports_6()


def test_a_frozen_module_that_drifted_is_refused(pinned, monkeypatch):
    frozen, _ = pinned
    rel = sorted(frozen)[0]
    monkeypatch.setattr(p6, "FROZEN_SHA256_6", dict(frozen, **{rel: "0" * 64}))
    with pytest.raises(RuntimeError, match=f"frozen module drifted: {rel}"):
        p6.check_frozen_6()
    with pytest.raises(RuntimeError, match=f"imported module drifted: {rel}"):
        p6.check_imports_6()


def test_an_imported_module_that_drifted_or_is_unpinned_is_refused(pinned, monkeypatch):
    _, own = pinned
    rel = sorted(own)[0]
    monkeypatch.setattr(p6, "IMPORTED_SHA256_6", dict(own, **{rel: "0" * 64}))
    with pytest.raises(RuntimeError, match=f"imported module drifted: {rel}"):
        p6.check_imports_6()
    monkeypatch.setattr(p6, "IMPORTED_SHA256_6",
                        {k: v for k, v in own.items() if k != rel})
    with pytest.raises(RuntimeError, match=f"unpinned module on the import surface: "
                                           f"{rel}"):
        p6.check_imports_6()


def test_a_file_the_tag_binds_is_not_pinned_twice(pinned):
    """The analyzer is loaded and is in neither table: the tag binds it."""
    assert "experiments/exp6/analyze_6.py" in p6.import_surface()
    assert "experiments/exp6/analyze_6.py" not in p6.IMPORTED_SHA256_6
    p6.check_imports_6()


def test_only_the_preflight_may_be_exempted(pinned, monkeypatch):
    _, own = pinned
    import experiments.exp6.run.preflight_6  # noqa: F401
    rel = "experiments/exp6/run/preflight_6.py"
    assert p6.EXEMPT_6 == (rel,) and rel not in p6.INSTRUMENT_BLOBS_6
    monkeypatch.setattr(p6, "IMPORTED_SHA256_6",
                        {k: v for k, v in p6.import_surface().items()
                         if k.startswith("experiments/exp6/") and k != rel
                         and k not in p6.INSTRUMENT_BLOBS_6})
    with pytest.raises(RuntimeError, match="unpinned module on the import surface"):
        p6.check_imports_6()
    p6.check_imports_6(exempt=p6.EXEMPT_6)
    with pytest.raises(RuntimeError, match="not exemptible"):
        p6.check_imports_6(exempt=("experiments/exp6/analyze_6.py",))
    with pytest.raises(RuntimeError, match="not exemptible"):
        p6.check_imports_6(exempt=p6.EXEMPT_6 + ("experiments/exp6/records_6.py",))


def test_the_tag_binds_the_item_files(monkeypatch):
    seen = []

    def blob(tag, rel):
        seen.append(rel)
        return p6.sha256_file(p6.REPO / rel)
    got = p6.require_prereg_6(tag_exists=lambda t: True, blob_sha=blob)
    assert got["n_bound"] == 16 + 17 and set(p6.ITEM_BLOBS_6) <= set(seen)
    with pytest.raises(RuntimeError, match="does not bind experiments/exp6/battery/"
                                           "items/lcs.json"):
        p6.require_prereg_6(tag_exists=lambda t: True, blob_sha=lambda tag, rel: (
            "0" * 64 if rel.endswith("items/lcs.json") else p6.sha256_file(p6.REPO / rel)))
