"""Fixed experiment entry. Installed site JSON is independently enrolled data."""
import sys
import json
import hashlib
import re
from pathlib import Path

# Administrative pin, supplied by the independently enrolled launch command.
# It is not read from site_7.json or any environment variable.
if len(sys.argv) < 3 or sys.argv[1] != "--site-sha256" or not re.fullmatch("[0-9a-f]{64}", sys.argv[2]):
    raise RuntimeError("independent launch --site-sha256 required")
site_sha = sys.argv[2]
del sys.argv[1:3]
site_path = Path(__file__).with_name("site_7.json")
site_bytes = site_path.read_bytes()
if site_path.is_symlink() or hashlib.sha256(site_bytes).hexdigest() != site_sha:
    raise RuntimeError("independent launch site SHA mismatch")
site = json.loads(site_bytes)
config_bytes = Path(site["config_path"]).read_bytes()
if hashlib.sha256(config_bytes).hexdigest() != site["config_sha256"]:
    raise RuntimeError("deployment config SHA mismatch")
config = json.loads(config_bytes)
repo = Path(config["repo"]).resolve(strict=True)
root = Path(site["package_root"]).resolve(strict=True)
if root != repo/"experiments/exp7":
    raise RuntimeError("fixed pure package path")
for name, expected in config["source_pins"].items():
    path = Path(config["repo"])/name
    if not path.resolve().is_relative_to(Path(config["repo"]).resolve()) or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise RuntimeError("bootstrap source binding refused")
for package in ("exp7core", "exp7stats", "exp7ops", "exp7integration", "run"):
    folder = root/package
    if not folder.is_dir():
        raise RuntimeError("pure package absent")
    if any(folder.rglob("*.pyc")):
        raise RuntimeError("existing unpinned bytecode refused before imports")
    for path in folder.rglob("*.py"):
        if path.relative_to(Path(config["repo"])).as_posix() not in config["source_pins"]:
            raise RuntimeError("omitted executable source")
# Native leaves use frozen experiments.exp6/exp3/exp2g imports. The same
# independently enrolled source map must include their complete Python closure,
# including every executable initializer. Namespace ancestors are metadata only.
# This finder is installed before exposing repo; no predecessor is imported here.
from importlib.machinery import PathFinder
class _BoundRepositoryImports:
    def find_spec(self, fullname, path=None, target=None):
        spec = PathFinder.find_spec(fullname, path)
        if spec is None:
            return None
        native = fullname == "experiments" or fullname.startswith("experiments.")
        if spec.origin in (None, "namespace"):
            locations = list(spec.submodule_search_locations or ())
            inside = [Path(p).resolve() for p in locations if Path(p).resolve().is_relative_to(repo)]
            if native and (len(inside) != len(locations) or not inside):
                raise ImportError("repository namespace escaped bound root")
            for folder in inside:
                if not any((repo/n).is_relative_to(folder) and n.endswith(".py") for n in config["source_pins"]):
                    raise ImportError("repository namespace lacks pinned descendants")
            return spec if inside else None
        source = Path(spec.origin)
        inside = source.resolve().is_relative_to(repo)
        if native and not inside:
            raise ImportError("predecessor import outside bound repository")
        if inside:
            name = source.relative_to(repo).as_posix()
            expected = config["source_pins"].get(name)
            if source.suffix != ".py" or source.is_symlink() or expected is None or hashlib.sha256(source.read_bytes()).hexdigest() != expected:
                raise ImportError("unpinned repository executable")
            if spec.cached and Path(spec.cached).exists():
                raise ImportError("preexisting repository bytecode refused")
            return spec
        return None
sys.meta_path.insert(sys.meta_path.index(PathFinder), _BoundRepositoryImports())
sys.path.insert(0, str(repo))
sys.path.insert(0, str(root))
if Path(__file__).name == "calibration_7.py":
    # Install the delivered model/network guard before integration/statistical
    # imports. The fixed entry below closes stdin via the delivered v3 helper.
    import exp7stats.calibration_cli
from exp7integration.bootstrap import main
raise SystemExit(main(Path(__file__).name, sys.argv[1:], site_path, site_sha))
