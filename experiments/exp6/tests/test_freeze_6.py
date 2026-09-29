# experiments/exp6/tests/test_freeze_6.py
"""The adversarial freeze's findings, each held by a test that failed at
the build HEAD (f3a9bf046) and passes after its closure. Every check runs
in a FRESH interpreter, as the campaign's processes do: a pytest session
has loaded every test module's imports, and the import surface of a
session is not the surface of a runner or of the analyzer.

F-1. The import pins were measured by importing the modules, not by
running them: the verdict path loads 2c's battery registry lazily
(`harness.answer_type_of`, through `battery_2d.load_item_file`, on every
battery load) and the Pythia predictor's loader loads exp2b's `models`
lazily; six files the pins did not name. On a complete campaign tree the
analyzer's exit check refused, and every runner's exit gate halted its
stage after the stage had done its work.

F-2. The import surface counted only the modules whose files lie under
this repository's `experiments/`. A second `experiments` directory
earlier on `sys.path` (a namespace portion merges) supplied a frozen
module from outside; the frozen pin hashed the repository's untouched
file, the surface check passed it over, and the verdict changed with
every pin active (freeze checklist, F-2: BATTERY-BOUND to GENERAL on a
null world).
"""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from experiments.exp6 import pins_6 as p6

REPO = p6.REPO


def _env(pythonpath=None, empty=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1"})
    if empty is not None:
        env.update({"HF_HOME": str(empty), "HF_HUB_CACHE": str(Path(empty) / "hub")})
    env["PYTHONPATH"] = os.pathsep.join(str(p) for p in (pythonpath or [REPO]))
    return env


def _py(code, *, cwd, pythonpath=None, empty=None, timeout=600):
    return subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=str(cwd),
                          env=_env(pythonpath, empty), capture_output=True, text=True,
                          timeout=timeout)


# ------------------------------------------------------------------ F-1
def test_f1_the_analyzers_lazy_path_is_pinned(tmp_path):
    """Loading the battery is on every verdict path (the analyzer, both
    seals, the power writer, every runner). What it loads is pinned."""
    got = _py("""
        from experiments.exp6 import analyze_6, battery_6 as b6, pins_6 as p6
        b6.load_battery_6()
        p6.check_imports_6()
        print("PINNED")
    """, cwd=REPO, empty=tmp_path)
    assert got.returncode == 0 and "PINNED" in got.stdout, got.stderr[-1500:]


def test_f1_the_pythia_loaders_import_path_is_pinned(tmp_path):
    """The Pythia predictor's real loader asserts exp3's module
    provenance, which imports exp2b's `models` by its bare name. No
    model is built: only the import is made."""
    got = _py("""
        from experiments.exp6.run import predict_6
        from experiments.exp6 import battery_6 as b6, pins_6 as p6
        from experiments.exp3.run.run_cell import _assert_module_provenance
        b6.load_battery_6()
        _assert_module_provenance()
        p6.check_imports_6()
        print("PINNED")
    """, cwd=REPO, empty=tmp_path)
    assert got.returncode == 0 and "PINNED" in got.stdout, got.stderr[-1500:]


def test_f1_the_import_scan_forces_both_lazy_paths():
    """The tool that owns the pins measures what the verdict path loads,
    not what an import loads."""
    from experiments.exp6.tools import import_scan_6 as sc
    assert "load_battery_6()" in sc.ANALYZER
    assert "_assert_module_provenance()" in sc.RUNNER
    for rel in ("experiments/exp2c/battery/base.py",
                "experiments/exp2c/battery/generators_controls.py",
                "experiments/exp2c/battery/generators_rescues.py",
                "experiments/exp2c/battery/generators_rungs.py",
                "experiments/exp2c/battery/wordlists_2c.py",
                "experiments/exp2b/models.py"):
        assert rel in p6.FROZEN_SHA256_6, rel


# ------------------------------------------------------------------ F-2
def _shadow_exp2i(root: Path) -> Path:
    """A second `experiments` directory whose exp2i is the repository's
    by symlink, except one file, which is a copy with a changed rule."""
    d = root / "experiments" / "exp2i"
    d.mkdir(parents=True)
    src = REPO / "experiments" / "exp2i"
    for p in src.iterdir():
        if p.name in ("analyze_2i.py", "__pycache__"):
            continue
        (d / p.name).symlink_to(p)
    text = (src / "analyze_2i.py").read_text()
    assert text.count("    return bool(p < ALPHA and T >= T_BAR)") == 1
    (d / "analyze_2i.py").write_text(text.replace(
        "    return bool(p < ALPHA and T >= T_BAR)",
        "    return bool(T > -1)   # a shadow: every defined test fires"))
    return root


def test_f2_a_frozen_module_from_a_second_experiments_directory(tmp_path):
    shadow = _shadow_exp2i(tmp_path / "shadow")
    got = _py("""
        import sys
        from experiments.exp6 import analyze_6, pins_6 as p6
        from experiments.exp2i import analyze_2i
        print("LOADED", analyze_2i.__file__)
        try:
            p6.check_imports_6()
            print("PASSED")
        except RuntimeError as e:
            print("REFUSED", e)
    """, cwd=tmp_path, pythonpath=[shadow, REPO], empty=tmp_path / "hf")
    assert got.returncode == 0, got.stderr[-1500:]
    assert f"LOADED {shadow}" in got.stdout          # the shadow was what ran
    assert "REFUSED" in got.stdout and "outside the repository" in got.stdout, got.stdout


def test_f2_a_namespace_portion_outside_the_repository(tmp_path):
    """The merge itself refuses: a portion that supplies no module today
    can supply one to the next lazy import."""
    (tmp_path / "shadow" / "experiments").mkdir(parents=True)
    got = _py("""
        from experiments.exp6 import pins_6 as p6
        import experiments
        print("PORTIONS", len(list(experiments.__path__)))
        try:
            p6.check_imports_6()
            print("PASSED")
        except RuntimeError as e:
            print("REFUSED", e)
    """, cwd=tmp_path, pythonpath=[tmp_path / "shadow", REPO], empty=tmp_path / "hf")
    assert got.returncode == 0, got.stderr[-1500:]
    assert "PORTIONS 2" in got.stdout and "REFUSED" in got.stdout, got.stdout


def test_f2_a_bare_named_module_from_outside(tmp_path):
    """2c's harness imports its battery registry by the BARE name
    `battery` (and exp3 imports `models`, 2g `splits` and
    `probe_starved`): where that name resolves is decided by sys.path.
    One that resolves outside the repository refuses."""
    b = tmp_path / "shadow" / "battery"
    b.mkdir(parents=True)
    (b / "__init__.py").write_text("")
    (b / "base.py").write_text("SPECS = {}\n")
    got = _py(f"""
        import sys
        from experiments.exp6 import pins_6 as p6
        sys.path.insert(0, {str(tmp_path / 'shadow')!r})
        import battery.base
        try:
            p6.check_imports_6()
            print("PASSED")
        except RuntimeError as e:
            print("REFUSED", e)
    """, cwd=tmp_path, empty=tmp_path / "hf")
    assert got.returncode == 0, got.stderr[-1500:]
    assert "REFUSED" in got.stdout and "battery" in got.stdout, got.stdout


def test_f2_the_repository_alone_passes(tmp_path):
    """The check refuses what is foreign and nothing else: the analyzer's
    own process, from the repository root, passes."""
    got = _py("""
        from experiments.exp6 import analyze_6, pins_6 as p6
        p6.check_imports_6()
        print("PINNED")
    """, cwd=REPO, empty=tmp_path)
    assert got.returncode == 0 and "PINNED" in got.stdout, got.stderr[-1500:]


def test_f2_the_bare_names_are_the_ones_the_scan_measures():
    """`BARE_TOPS_6` is not a hand list that can fall behind: the scan
    reports every bare-named module it saw loaded from experiments/, and
    `--check` refuses a difference (asserted here on the table's shape;
    the cold battery runs the scan)."""
    assert set(p6.BARE_TOPS_6) == {"battery", "exp1_signatures_stats", "harness",
                                   "models", "probe_starved", "splits"}
    from experiments.exp6.tools import import_scan_6 as sc
    assert "bare_tops" in sc.TAIL


@pytest.mark.slow
def test_f1_f2_a_complete_world_under_every_real_pin(tmp_path):
    """A complete synthetic campaign (the REAL runners, fake loaders)
    analysed in a fresh process with the frozen-module pin, the import
    pin and the referent pin all REAL — only the git tag lookups are
    injected, since a synthetic tree has no tags. At f3a9bf046 this
    delivered INSUFFICIENT_DATA ('unpinned module on the import surface:
    experiments/exp2c/battery/base.py'); now it delivers a verdict, and
    nothing it loaded lies under a tests/ directory."""
    root = tmp_path / "w"
    build = _py(f"""
        from experiments.exp6.tests import _world_6 as W
        W.build_world({str(root)!r}, W.spec(rho=W.general(0.6)))
        print("BUILT")
    """, cwd=REPO, empty=tmp_path / "hf")
    assert build.returncode == 0 and "BUILT" in build.stdout, build.stderr[-1500:]
    got = _py(f"""
        import json, sys
        from experiments.exp6 import analyze_6 as an, pins_6 as p6
        v = an.run({str(root)!r}, n_perm=120, n_boot=10,
                   tag_exists=lambda t: True,
                   blob_sha=lambda tag, rel: p6.sha256_file(p6.REPO / rel),
                   blobs_bound=lambda tag, paths, repo_root=None: [])
        tests_loaded = sorted(str(p6._under_experiments(m.__file__))
                              for m in list(sys.modules.values())
                              if getattr(m, "__file__", None)
                              and p6._under_experiments(m.__file__) is not None
                              and "tests" in p6._under_experiments(m.__file__).parts)
        print(json.dumps({{"verdict": v["verdict"],
                          "failures": v["referents"]["failures"],
                          "pins": v["referents"]["pins_active"],
                          "tests_loaded": tests_loaded}}))
    """, cwd=REPO, empty=tmp_path / "hf", timeout=3600)
    assert got.returncode == 0, got.stderr[-1500:]
    out = json.loads(got.stdout.strip().splitlines()[-1])
    assert out["failures"] == [], out["failures"][:3]
    assert out["verdict"] != "INSUFFICIENT_DATA"
    assert out["pins"]["frozen_modules"] and out["pins"]["import_surface"] and \
        out["pins"]["referent_manifest"]
    assert out["tests_loaded"] == []


# ------------------------------------------------------------------ F-3
def test_f3_an_endpoint_load_is_not_resumed_across_hosts(tmp_path):
    """A load a killed box left half-written, resumed on another box: at
    f3a9bf046 the runner skipped the first box's records, wrote the rest
    and the load record under the second box, and COMPLETED into a tree
    the endpoint seal can never accept (every skipped record names the
    other host). It is refused before anything is loaded."""
    from experiments.exp6 import battery_6 as b6
    from experiments.exp6 import families_6 as fm
    from experiments.exp6 import records_6 as r6
    from experiments.exp6.run import endpoint_6 as ep
    from experiments.exp6.tests import _world_6 as W
    fam, which = fm.FAMILIES_6[0], "stage1_final"
    rung = b6.ALL_RUNGS_6[0]
    r6.write_json(r6.endpoint_record_path(tmp_path, fam, which, rung),
                  {"rung": rung, "host_sha256": "a" * 64})
    kw = dict(root=tmp_path, device="cpu", man=fm.manifest(fam),
              battery={r: {} for r in b6.ALL_RUNGS_6}, seal_sha="s" * 64,
              loaders=W.Unreached(), stack={}, git_sha="")
    with pytest.raises(RuntimeError, match="not resumed across hosts"):
        ep.run_which(fam, which, host={"sha256": "b" * 64}, **kw)
    # the same host resumes: past the check, to its loader
    with pytest.raises(AssertionError, match="reached its loader"):
        ep.run_which(fam, which, host={"sha256": "a" * 64}, **kw)


# ------------------------------------------------------------------ F-4
def _tree_with_pyc(tmp_path, mode):
    """A private tree (the mutation harness's own layout) whose
    `records_6` has a .pyc compiled from ANOTHER source; the source on
    disk untouched. `mode`: an unchecked-hash .pyc (Python never looks
    at the source), or a timestamp .pyc from a source of the same size
    and mtime (Python finds it valid)."""
    import py_compile
    import shutil
    from experiments.exp6.tests import mutation_check_6 as mc
    tree = mc.make_tree(tmp_path / "t")
    src = tree / "experiments/exp6/records_6.py"
    text = src.read_text()
    old = "span/sequence; first token for ipa"
    assert text.count(old) == 1
    alt = tmp_path / "alt" / "records_6.py"
    alt.parent.mkdir()
    alt.write_text(text.replace(old, "spam/sequence; first token for ipa"))
    assert alt.stat().st_size == src.stat().st_size
    shutil.copystat(src, alt)
    cache = src.parent / "__pycache__"
    cache.mkdir(exist_ok=True)
    inv = (py_compile.PycInvalidationMode.UNCHECKED_HASH
           if mode in ("unchecked", "carries_the_sources_hash")
           else py_compile.PycInvalidationMode.TIMESTAMP)
    pyc = cache / "records_6.cpython-311.pyc"
    py_compile.compile(str(alt), cfile=str(pyc), dfile=str(src), invalidation_mode=inv,
                       doraise=True)
    if mode == "carries_the_sources_hash":
        # final review I-3: the header names the TRUE source's hash, the
        # code is the other source's; Python never reads an unchecked header
        import importlib.util
        data = pyc.read_bytes()
        pyc.write_bytes(data[:8] + importlib.util.source_hash(src.read_bytes())
                        + data[16:])
    return tree


@pytest.mark.parametrize("mode", ["unchecked", "timestamp", "carries_the_sources_hash"])
def test_f4_bytecode_that_is_not_the_hashed_source(tmp_path, mode):
    """The pins hash SOURCE files; the interpreter runs a .pyc when it
    finds one valid. At f3a9bf046 a .pyc compiled from another source ran
    with check_frozen_6, check_imports_6 and the tag binding all passing.
    The bytecode that ran is now held to the source that was hashed."""
    tree = _tree_with_pyc(tmp_path, mode)
    env = _env([tree], tmp_path / "hf")
    env.pop("PYTHONDONTWRITEBYTECODE")
    got = subprocess.run([sys.executable, "-c", textwrap.dedent("""
        from experiments.exp6 import analyze_6, records_6 as r6, pins_6 as p6
        print("RAN", "spam" in r6.VERIFY_NOTE)
        try:
            p6.check_frozen_6(); p6.check_imports_6()
            print("PASSED")
        except RuntimeError as e:
            print("REFUSED", e)
    """)], cwd=str(tree), env=env, capture_output=True, text=True, timeout=600)
    assert got.returncode == 0, got.stderr[-1500:]
    assert "RAN True" in got.stdout                   # the other source is what ran
    assert "REFUSED" in got.stdout and "bytecode" in got.stdout, got.stdout


def test_f4_bytecode_of_the_true_source_is_accepted(tmp_path):
    """The closure refuses what is not the source's code and nothing else:
    the repository's own timestamp caches (a first run writes them under a
    private prefix, a second loads them), and hash-based caches of every
    exp6 module compiled from its own source, pass."""
    import py_compile
    prefix = tmp_path / "prefix"
    code = """
        from experiments.exp6 import analyze_6, battery_6 as b6, pins_6 as p6
        b6.load_battery_6()
        print("STALE", p6.bytecode_failures())
        p6.check_imports_6()
        print("PINNED")
    """
    for _ in range(2):
        env = _env([REPO], tmp_path / "hf")
        env.pop("PYTHONDONTWRITEBYTECODE")
        env["PYTHONPYCACHEPREFIX"] = str(prefix)
        got = subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=str(REPO),
                             env=env, capture_output=True, text=True, timeout=600)
        assert got.returncode == 0 and "PINNED" in got.stdout, got.stderr[-1500:]
        assert "STALE []" in got.stdout, got.stdout
    assert list(prefix.rglob("*.pyc"))                    # the second run read caches
    from experiments.exp6.tests import mutation_check_6 as mc
    tree = mc.make_tree(tmp_path / "t")
    n = 0
    for src in (tree / "experiments" / "exp6").rglob("*.py"):
        if "tests" in src.relative_to(tree).parts:
            continue
        cfile = src.parent / "__pycache__" / f"{src.stem}.cpython-311.pyc"
        py_compile.compile(str(src), cfile=str(cfile), dfile=str(src), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
        n += 1
    assert n > 10
    env = _env([tree], tmp_path / "hf")
    got = subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=str(tree),
                         env=env, capture_output=True, text=True, timeout=600)
    assert got.returncode == 0 and "PINNED" in got.stdout, got.stderr[-1500:]
    assert "STALE []" in got.stdout, got.stdout


@pytest.mark.parametrize("body", ["other_code", "unreadable"])
def test_f4_a_hash_based_pyc_is_held_to_its_code(tmp_path, monkeypatch, body):
    """Final review I-3 at the function: a hash-based .pyc whose header
    carries the true source's hash is held to the code its source
    compiles to; one whose code cannot be read is refused (an unchecked
    one would run without Python looking). The module is a stand-in in
    `sys.modules` over the repository's own source; nothing is written
    in the repository."""
    import importlib.util
    import marshal
    import types
    src_path = REPO / "experiments" / "exp6" / "records_6.py"
    src = src_path.read_bytes()
    if body == "other_code":
        code = marshal.dumps(compile(src.replace(b"span/sequence", b"spam/sequence"),
                                     str(src_path), "exec", dont_inherit=True))
    else:
        code = b"\x00not marshal data"
    pyc = tmp_path / "records_6.cpython-311.pyc"
    flags = (0b01).to_bytes(4, "little")                    # hash-based, unchecked
    pyc.write_bytes(importlib.util.MAGIC_NUMBER + flags
                    + importlib.util.source_hash(src) + code)
    m = types.ModuleType("_exp6_f4_stand_in")
    m.__file__, m.__cached__ = str(src_path), str(pyc)
    monkeypatch.setitem(sys.modules, "_exp6_f4_stand_in", m)
    got = [x for x in p6.bytecode_failures() if x.startswith("_exp6_f4_stand_in:")]
    want = ("is not the code its source compiles to" if body == "other_code"
            else "is hash-based and unreadable")
    assert len(got) == 1 and want in got[0], got
    # the same header over the source's own code passes
    pyc.write_bytes(importlib.util.MAGIC_NUMBER + flags + importlib.util.source_hash(src)
                    + marshal.dumps(compile(src, str(src_path), "exec",
                                            dont_inherit=True)))
    assert not [x for x in p6.bytecode_failures() if x.startswith("_exp6_f4_stand_in:")]
    # and a header that is not this source's hash is refused even over the
    # source's own code (the header check stands beside the code check)
    pyc.write_bytes(importlib.util.MAGIC_NUMBER + flags + b"\x00" * 8
                    + marshal.dumps(compile(src, str(src_path), "exec",
                                            dont_inherit=True)))
    got = [x for x in p6.bytecode_failures() if x.startswith("_exp6_f4_stand_in:")]
    assert len(got) == 1 and "is hash-based and not this source's" in got[0], got
