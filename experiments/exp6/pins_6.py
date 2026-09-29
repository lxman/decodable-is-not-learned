# experiments/exp6/pins_6.py
"""Exp 6 pins: the frozen modules it imports, the blobs its tags bind,
and the git binding itself. No pin here is a convenience: each is a
verdict input (2j F-1, 4c F-1)."""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import records_6 as r6

REPO = b6.REPO
EXP6 = b6.EXP6

# the blobs `exp6-preregistered` binds: the analyzer, the battery and
# its tables, every runner, and the manifest of the item files
INSTRUMENT_BLOBS_6 = (
    "experiments/exp6/analyze_6.py",
    "experiments/exp6/battery_6.py",
    "experiments/exp6/families_6.py",
    "experiments/exp6/floors_6.py",
    "experiments/exp6/pins_6.py",
    "experiments/exp6/power_6.py",
    "experiments/exp6/records_6.py",
    "experiments/exp6/referents_6.py",
    "experiments/exp6/strata_6.py",
    "experiments/exp6/verify_6.py",
    "experiments/exp6/run/_common_6.py",
    "experiments/exp6/run/predict_6.py",
    "experiments/exp6/run/seal_predictor_6.py",
    "experiments/exp6/run/endpoint_6.py",
    "experiments/exp6/run/seal_endpoint_6.py",
    "experiments/exp6/run/sweep_6.py",
)
# the one file `check_imports_6` may be told to pass over
EXEMPT_6 = ("experiments/exp6/run/preflight_6.py",)
ITEM_BLOBS_6 = tuple(f"experiments/exp6/battery/items/{r}.json" for r in b6.RUNGS_6)

# filled by tests/import_scan_6.py at the real-tree closure (Task 5 of
# the instrument plan); None means "not pinned", which the analyzer
# records as a failure.
FROZEN_SHA256_6 = {
    "experiments/exp1/signatures/stats.py":
        "ceab3eb7f6daf9346b9231f0e4af7e458b43ba4e7361556aef926e1abde2611f",
    "experiments/exp2b/models.py":
        "a4c5eed26cc92044aeb9ed7b68b177035de3ac2615dbba09a6d21eeb191a55a4",
    "experiments/exp2b/probe_starved.py":
        "e6c81df28e4a7e07db3a123e4b06d3c8a98a7d330cd726596d41b1136c4cd27b",
    "experiments/exp2b/splits.py":
        "49df4c62c3c3bd611b9cf49be46001c12220045a3611a39be5e2bc5b89ded6e0",
    "experiments/exp2c/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2c/battery/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2c/battery/base.py":
        "6d77c3c91c5ca0eb84e1a011ef64af0e04ade6fe8d1ad42d526be3a37fbacbb2",
    "experiments/exp2c/battery/family_map.py":
        "46477b37683c8ea0e1f2f219dce96858a0dcf91710b15cae45a8cf4c4c7ab375",
    "experiments/exp2c/battery/generators_controls.py":
        "baab6da475f90f8c07acb6d1eb317484bf36afeb40705684f43ecd5ec9fdade6",
    "experiments/exp2c/battery/generators_rescues.py":
        "d70215c89ffd58d3f18f9dcd99940c7e92655ba8185919f50b2090b7e900c257",
    "experiments/exp2c/battery/generators_rungs.py":
        "778bf30da104f71773c26aa909ef2fddcd81291676a2db5d30130581b8d162d0",
    "experiments/exp2c/battery/wordlists_2c.py":
        "f46c6092d6429a59b95531d1a58b1bbfc0576d692d1162b8dfd2b6daf051790f",
    "experiments/exp2c/harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    "experiments/exp2c/instrument.py":
        "c486213bfa4753a83593b5383e2c0c90a6379b156f59a236ceeac7d68961e052",
    "experiments/exp2c/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2c/run/power_table.py":
        "89816cf0e7e2418e748104dbc32fd50e12ded78988f2c2c04b05ff1a89c58da1",
    "experiments/exp2c/run/screen.py":
        "fef1814142955912066837fbd2119f5c2ae27fe31393ede890584313e2b06873",
    "experiments/exp2c/stats_bounds.py":
        "39057433f1d67cbbf803141dc25ee36cda9e96270b0634006c0fcab245ee49f8",
    "experiments/exp2d/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2d/analyze_2d.py":
        "01ee334db5fe273a8509cf4bf79757b52a40a123311acd42554ac1a82e40334a",
    "experiments/exp2d/battery_2d.py":
        "503a2c09ec320989223561291ff93c71d62d27ed20c5681f9b2d535b7708e81a",
    "experiments/exp2d/stats_2d.py":
        "86243932709013ea15b250e9bf15243ce6209e03e6bcf81af0f7ac3f92644b46",
    "experiments/exp2f/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2f/analyze_2f.py":
        "79018ff34b6f41bd2a5e8fa0f922a2de567861750057a5eca1a3dad6cf3f61d3",
    "experiments/exp2f/collect_eval_2f.py":
        "189e3738471185b7205f106fdac9bc5da1d564caafc60e39f4d6e3546915d071",
    "experiments/exp2f/labels_2f.py":
        "8dc31850e5c47b7a1cc171b0388521ebe01005ddc123954c0073734cf9aaac25",
    "experiments/exp2f/make_referents_2f.py":
        "c08eec5cea9f49a05c6754c84b81e1cb8560537881b002faee02bcf085af1c10",
    "experiments/exp2f/probe_2f.py":
        "63c714d6e899dd9d6d5610a3d54c9254ec0749d03f44a703790d4a4354854f62",
    "experiments/exp2g/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2g/analyze_2g.py":
        "eab7c5b91d57351ee2a7adb0e85d71cb92cb4d6ed15d0bb90150c95c2076050e",
    "experiments/exp2g/battery_2g.py":
        "aca79dd71ee7dead3c0ce065945bb38eaf1b0b72b5d5f40698dabb0f5a9cf3c1",
    "experiments/exp2g/checkpoints_2g.py":
        "155fee3ec3933db33930d7ddadb99c02604d893205a8f8c037016cc18609fb10",
    "experiments/exp2g/collect_eval_2g.py":
        "392ab84e2bac360bf041858a4b991824a3bda9ca414e34d0f84e44b22610efaf",
    "experiments/exp2g/labels_2g.py":
        "d86e7cdb4dcc10257986e8a85824365972a75ba993be5a8fde8a825d68e3077d",
    "experiments/exp2g/predictor_2g.py":
        "3381b43a34fd1fb1f7ef57eb9d02a6a9e9ec41b3ffcadea425c37b86c1e92a4e",
    "experiments/exp2g/probe_2g.py":
        "63abc9e6518ac1ab53e4a70e0c716bccd357a11ea3fc2733de52e2ec4e23d451",
    "experiments/exp2g/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2g/run/sweep_2g.py":
        "850db5831adeffc46a888ca185ef3f1ad819a8db104c9eafd1df69c470c91a87",
    "experiments/exp2g/stats_2g.py":
        "cf3c4c89c86fa43c5ba49d5c4be12eabad28ac65d9d12a43b1e31ef6e4bc195f",
    "experiments/exp2g/strata_2g.py":
        "ea0acbbdfde13655a6b89d3afcc981f348ee6312b4448b70d437f1e4d3f7f594",
    "experiments/exp2h/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2h/analyze_2h.py":
        "52733e8d4280fb41b76cda2dcac024299ce7dd61090f856ba3147c8098b871bf",
    "experiments/exp2h/battery_2h.py":
        "2d721cf85bbd85937f45a1135e8b5e102685ab424d8ab0dfada527bd8ab4e80a",
    "experiments/exp2i/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2i/analyze_2i.py":
        "85e482fea17e0706476243a0a98a7d2c32efebd6536c5255ae48e729b494c252",
    "experiments/exp2i/battery_2i.py":
        "e0a8d10cb4dde8a3af1a3e9b32447c407b43201513dc758d6cd9a8c38b5cdfcf",
    "experiments/exp2i/power_2i.py":
        "0e5e449ac420e40243ae86eb84e576256e857581ad3c7e000fcea5e08666119d",
    "experiments/exp2i/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2i/run/_common_2i.py":
        "5cc7c97f68b45656d6dbbb5fbf6d7d895d7b1d96e104df543f8c9f1691e5ad4f",
    "experiments/exp2j/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2j/analyze_2j.py":
        "976f1ff1f91affa2fc66d635e6b6d9a8aabfd21bdc7ccc38abfe87482ea09b13",
    "experiments/exp2j/functionals_2j.py":
        "39375f01de4b5bf06787175e25f7f85394844c005c3c4ea66f69954b1fe8bfce",
    "experiments/exp2k/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2k/analyze_2k.py":
        "27ea6f7b4dcf18894061363a7d7d64d2a63e867946797a5306a695c9d0e86f1a",
    "experiments/exp2k/battery_2k.py":
        "1066265d689573cc009c73df1b036a9453be7a807d79e153b53ccf52177eec0a",
    "experiments/exp2l/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2l/analyze_2l.py":
        "a76d26031abc73df0757c9fa20ac5b5254a06128d5fc6897c0cd5876106441b6",
    "experiments/exp2l/battery_2l.py":
        "c85726b9909dfe11dd6481b96e773ce27aa507d83ac05348e0125f79aae50b8b",
    "experiments/exp2m/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2m/analyze_2m.py":
        "034c8a7359a275a2835c31e31fcb27b7d37ffb7144b53d49cfcc3e95ceab275e",
    "experiments/exp2m/battery_2m.py":
        "0c5e1f07f8881c537304b496240605b95027306962ec2e4f389b42843323bffd",
    "experiments/exp2n/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2n/analyze_2n.py":
        "a860a4e7fe3d40cba923d72f89e84facbfcfdfb92567930f55427587cb90c80b",
    "experiments/exp2n/battery_2n.py":
        "e85165bd0ca1dd9f93eb07c89b74851ea2413d32f7ef9e694082ade49170a3e8",
    "experiments/exp2n/power_2n.py":
        "9c7d71b0a4d1133358f2c1d198af308caf6abb904549c8f27738798c68e9f58f",
    "experiments/exp2n/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp2n/run/endpoint_2n.py":
        "62d62959361e6591ea530dc2dbe3136e614c26ecd04a60ad6e173bedecc7002d",
    "experiments/exp3/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp3/analyze_3.py":
        "aa0cb2374fbdffde2f9eaae26cee1ce51f9f42c0b32fd89f4f8754c983a92274",
    "experiments/exp3/masses.py":
        "24385274e3007278e6289ed2fadbc7d4f539f2618982a6fe778571df6e962cf0",
    "experiments/exp3/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp3/run/run_cell.py":
        "5c018457d9eb999079b4b0426dc0ecadf10baed6339d32b5eb914f280da35b46",
    "experiments/exp3/sampler.py":
        "e33c50d3985b1d6205d886e53726860f364cce1c6cd943ec460524e9110a03ea",
}
IMPORTED_SHA256_6 = {
    "experiments/exp6/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp6/battery/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp6/battery/spec.py":
        "b344717695c400cdc1818b0f7d9e7f285d6c6b82383e160e216fa81242d16575",
    "experiments/exp6/make_referents_6.py":
        "6ae25bb863759ed33eef17dd4a9525689a72aae24e48a6a34856eaa01b349237",
    "experiments/exp6/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_tag_exists(tag: str) -> bool:
    out = subprocess.run(["git", "tag", "--list", tag], cwd=REPO,
                         capture_output=True, text=True)
    return tag in out.stdout.split()


def git_blob_sha256(tag: str, relpath: str):
    out = subprocess.run(["git", "show", f"{tag}:{relpath}"], cwd=REPO,
                         capture_output=True)
    if out.returncode != 0:
        return None
    return hashlib.sha256(out.stdout).hexdigest()


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                              capture_output=True, text=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def require_tag(tag: str, relpaths, *, tag_exists=None, blob_sha=None) -> dict:
    """The tag must exist and every named path's bytes on disk must be
    the bytes the tag carries (2k's blob binding; 2h F-3: a tag binds
    an instrument, not a name)."""
    tag_exists = tag_exists or git_tag_exists
    blob_sha = blob_sha or git_blob_sha256
    if not tag_exists(tag):
        raise RuntimeError(f"tag {tag} does not exist")
    bound = {}
    for rel in relpaths:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(tag, rel), sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {tag} does not bind {rel}: tag "
                               f"{str(want)[:12]} against disk {got[:12]}")
        bound[rel] = got
    return {"tag": tag, "n_bound": len(bound), "bound": bound}


def require_prereg_6(*, tag_exists=None, blob_sha=None) -> dict:
    return require_tag(r6.PREREG_TAG_6, INSTRUMENT_BLOBS_6 + ITEM_BLOBS_6,
                       tag_exists=tag_exists, blob_sha=blob_sha)


def seal_failures(tag: str, paths, *, tag_exists=None, blobs_bound=None) -> list:
    """A seal tag must exist and bind every path, byte for byte (2i's
    ruling 1). NEVER RAISES: a missing tag, a drifted file or an
    injected callable that raises all come back as failure lines."""
    from experiments.exp2i import battery_2i as bi
    tag_exists = tag_exists or git_tag_exists
    blobs_bound = blobs_bound or bi.blobs_bound
    try:
        if not tag_exists(tag):
            return [f"the tag {tag!r} does not exist"]
        rel = [os.path.relpath(str(p), str(REPO)) for p in paths]
        drift = blobs_bound(tag, rel, repo_root=REPO)
    except Exception as e:  # noqa: BLE001 — deliberately broad, never escapes
        return [f"binding {tag!r} raised {type(e).__name__}: {e}"]
    if drift:
        return [f"{tag!r} does not bind {len(drift)} file(s): {sorted(drift)[:3]}"]
    return []


def require_seal(tag: str, paths, *, tag_exists=None, blobs_bound=None) -> None:
    bad = seal_failures(tag, paths, tag_exists=tag_exists, blobs_bound=blobs_bound)
    if bad:
        raise RuntimeError("; ".join(bad))


def frozen_from_disk(paths) -> dict:
    return {str(Path(p).resolve().relative_to(REPO)): sha256_file(p) for p in paths}


def check_frozen_6() -> None:
    if not FROZEN_SHA256_6:
        raise RuntimeError("FROZEN_SHA256_6 is empty — not pinned (build incomplete)")
    for rel, want in FROZEN_SHA256_6.items():
        got = sha256_file(REPO / rel)
        if got != want:
            raise RuntimeError(f"frozen module drifted: {rel} ({got[:12]} != "
                               f"{want[:12]})")


_LINKED_6 = {}


def _linked_6() -> dict:
    """{resolved target: experiments/<name>} for every directory of
    experiments/ that is a LINK. None in the repository; every sibling of
    exp6 in the mutation harness's private trees. A frozen module that
    resolves its own path before it extends sys.path (2b, 2c, 2d, 2g, 2i
    do) puts the link's target on sys.path, and a module imported through
    it must still be read as the experiment it is (freeze F-2)."""
    key = str(REPO)
    if key not in _LINKED_6:
        out = {}
        try:
            for c in (REPO / "experiments").iterdir():
                if c.is_symlink():
                    out[c.resolve()] = Path("experiments") / c.name
        except OSError:
            pass
        _LINKED_6[key] = out
    return _LINKED_6[key]


def _under_experiments(f):
    """The path of a loaded file relative to the repository if it lies
    under experiments/, else None. Tried as given and then resolved: a
    module reached through a symlinked directory is still that module;
    and one reached through the link's TARGET is too (freeze F-2)."""
    root = REPO / "experiments"
    for p in (Path(f), Path(f).resolve()):
        for base in (root, root.resolve()):
            try:
                return Path("experiments") / p.relative_to(base)
            except ValueError:
                continue
    rp = Path(f).resolve()
    for target, name in _linked_6().items():
        try:
            return name / rp.relative_to(target)
        except ValueError:
            continue
    return None


def import_surface() -> dict:
    """Every file under experiments/ (tests excluded) that the
    interpreter has loaded, with its sha — what a read sweep cannot
    see."""
    import sys
    out = {}
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        rel = _under_experiments(f)
        if rel is None or "tests" in rel.parts:
            continue
        out[str(rel)] = sha256_file(f)
    return out


# Freeze F-2: the modules the frozen code imports by a BARE name, which
# sys.path resolves (2c's harness imports `battery`, exp3 `harness` and
# `models`, 2g `splits` and `probe_starved`, exp1's stats is loaded as
# `exp1_signatures_stats`). `tools/import_scan_6.py --check` refuses a
# difference between this table and what the scan measures.
BARE_TOPS_6 = ("battery", "exp1_signatures_stats", "harness", "models",
               "probe_starved", "splits")


def foreign_modules() -> list:
    """Freeze F-2: the loaded modules that answer to this repository's
    names and were NOT loaded from it — a portion of the `experiments`
    namespace outside `REPO/experiments`, an `experiments.*` module or a
    bare-named one (`BARE_TOPS_6`) whose file lies outside it. The
    surface check below keys on where a file lies, so a module supplied
    from a second `experiments` directory earlier on sys.path was passed
    over while the frozen pin hashed the repository's untouched copy."""
    import sys
    home = (REPO / "experiments").resolve()
    # the directory the links of experiments/ point into, where there are
    # links (the harness's trees): every module found through it is
    # itself held to the repository below, one by one
    homes = {home} | {t.parent for t in _linked_6()}
    bad = []
    for name, m in sorted(list(sys.modules.items()), key=lambda kv: kv[0]):
        top = name.split(".")[0]
        if top != "experiments" and top not in BARE_TOPS_6:
            continue
        f = getattr(m, "__file__", None)
        if name == "experiments":
            for portion in list(getattr(m, "__path__", None) or []):
                if Path(portion).resolve() not in homes:
                    bad.append(f"experiments (namespace portion {portion})")
            if f and _under_experiments(f) is None:
                bad.append(f"experiments ({f})")
            continue
        if f:
            if _under_experiments(f) is None:
                bad.append(f"{name} ({f})")
            continue
        for portion in list(getattr(m, "__path__", None) or []):
            if _under_experiments(portion) is None:
                bad.append(f"{name} (portion {portion})")
    return bad


def bytecode_failures() -> list:
    """Freeze F-4: the pins hash SOURCE files, and the interpreter runs a
    module's cached .pyc whenever it finds it valid — a timestamp .pyc
    whose recorded mtime and size match the source, or a hash-based one
    (an UNCHECKED one is never compared with the source at all). For
    every loaded module under experiments/ whose .pyc Python would have
    accepted, the code in the .pyc must be the code the source compiles
    to; a hash-based .pyc must carry the source's own hash AND that code
    (an unchecked one's header is never read by Python, so a header can
    carry the true source's hash over other code; final review I-3). An
    unreadable hash-based .pyc is a failure: Python would run an
    unchecked one without looking."""
    import importlib.util
    import marshal
    import sys
    bad = []
    for name, m in sorted(list(sys.modules.items()), key=lambda kv: kv[0]):
        # read from the module's own namespace: a lazy module (transformers')
        # imports on a missing attribute, and nothing here may import
        ns = vars(m) if hasattr(m, "__dict__") else {}
        f, cached = ns.get("__file__"), ns.get("__cached__")
        if not f or not cached or _under_experiments(f) is None:
            continue
        pyc = Path(cached)
        if not pyc.is_file() or not str(f).endswith(".py"):
            continue
        data, src = pyc.read_bytes(), Path(f).read_bytes()
        flags = int.from_bytes(data[4:8], "little")
        if flags & 0b1:                                  # hash-based
            if data[8:16] != importlib.util.source_hash(src):
                bad.append(f"{name}: {pyc.name} is hash-based and not this source's")
                continue
            try:
                ran = marshal.loads(data[16:])
            except Exception:  # noqa: BLE001 — an unchecked one would run unread
                bad.append(f"{name}: {pyc.name} is hash-based and unreadable")
                continue
            if compile(src, str(f), "exec", dont_inherit=True) != ran:
                bad.append(f"{name}: {pyc.name} is not the code its source compiles to")
            continue
        st = os.stat(f)
        if int.from_bytes(data[8:12], "little") != (int(st.st_mtime) & 0xFFFFFFFF) or \
                int.from_bytes(data[12:16], "little") != (st.st_size & 0xFFFFFFFF):
            continue                                     # stale: Python compiled the source
        try:
            ran = marshal.loads(data[16:])
        except Exception:  # noqa: BLE001 — an unreadable .pyc Python would reject
            continue
        if ran != compile(src, str(f), "exec", dont_inherit=True):
            bad.append(f"{name}: {pyc.name} is not the code its source compiles to")
    return bad


def check_imports_6(exempt=()) -> None:
    """Every file under experiments/ the interpreter has loaded is bound
    by the preregistration tag or pinned here. `exempt`: the preflight's
    own file and nothing else — scratch tooling that writes no record
    and prints no new-battery score (it checks the anchors), so that a fix
    to it re-cuts no tag; everything
    it imports is held to the pins like any other module. And nothing
    that answers to this repository's module names was loaded from
    anywhere else (freeze F-2)."""
    if IMPORTED_SHA256_6 is None or not FROZEN_SHA256_6:
        raise RuntimeError("the import surface is not pinned (build incomplete)")
    if set(exempt) - set(EXEMPT_6):
        raise RuntimeError(f"not exemptible: {sorted(set(exempt) - set(EXEMPT_6))}")
    foreign = foreign_modules()
    if foreign:
        raise RuntimeError(f"a module loaded from outside the repository: "
                           f"{foreign[:3]}")
    stale = bytecode_failures()
    if stale:
        raise RuntimeError(f"bytecode that is not the pinned source ran: {stale[:3]}")
    pinned = dict(FROZEN_SHA256_6)
    pinned.update(IMPORTED_SHA256_6)
    bound = set(INSTRUMENT_BLOBS_6)
    for rel, got in import_surface().items():
        if rel in bound or rel in exempt:
            continue                       # bound by the preregistration tag
        want = pinned.get(rel)
        if want is None:
            raise RuntimeError(f"unpinned module on the import surface: {rel}")
        if want != got:
            raise RuntimeError(f"imported module drifted: {rel}")
