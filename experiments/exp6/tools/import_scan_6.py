# experiments/exp6/tools/import_scan_6.py
"""The import surface, measured in a FRESH interpreter (2j F-1: a read
sweep sees what an analyzer opens, not what the interpreter executes on
its behalf; 4c F-1: the runners have an import surface too).

Two interpreters, because the two surfaces differ in kind. The
ANALYZER's: the analyzer, the power module and the seals, with every
import they make lazily forced — and torch must not be among what loads.
The RUNNERS': the same plus the sampler and the loaders, where torch
loads and is meant to. Every file under experiments/ that either
interpreter loaded is listed. A file the preregistration tag binds is
bound there; every other file is printed as a pin: frozen modules of
earlier experiments under FROZEN_SHA256_6, Exp 6's own unbound modules
under IMPORTED_SHA256_6.

    python -m experiments.exp6.tools.import_scan_6           (prints the two tables)
    python -m experiments.exp6.tools.import_scan_6 --check   (against pins_6; exit 1 on drift)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

EXP6 = Path(__file__).resolve().parents[1]
REPO = EXP6.parent.parent
ANALYZER = r'''
import json, sys
sys.path.insert(0, %r)
from experiments.exp6 import analyze_6, power_6, make_referents_6      # noqa: F401
from experiments.exp6.run import (predict_6, seal_predictor_6, endpoint_6,   # noqa: F401
                                  seal_endpoint_6, sweep_6, _common_6)
# every import the analyzer's path makes lazily, forced
from experiments.exp6 import families_6, referents_6, verify_6, floors_6, strata_6
families_6._mods()
verify_6.harness_2c()
referents_6.model_pin("pythia_1b")
strata_6._sg()
floors_6.clears(1, 500, .1)
floors_6.floor_table_6({})
from experiments.exp2d import battery_2d                                # noqa: F401
from experiments.exp2i import battery_2i, power_2i                      # noqa: F401
from experiments.exp2n import power_2n                                  # noqa: F401
'''
RUNNER = ANALYZER + r'''
from experiments.exp3 import sampler                                    # noqa: F401
from experiments.exp3.run import run_cell                               # noqa: F401
from experiments.exp6.run import preflight_6                            # noqa: F401
'''
TAIL = r'''
from experiments.exp6 import pins_6
print(json.dumps({"surface": pins_6.import_surface(), "torch": "torch" in sys.modules,
                  "transformers": "transformers" in sys.modules}))
'''


def _run(code: str) -> dict:
    out = subprocess.run([sys.executable, "-c", (code + TAIL) % str(REPO)], cwd=REPO,
                         capture_output=True, text=True,
                         env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin",
                              "HOME": str(Path.home()),
                              "PYTHONPATH": ":".join(p for p in sys.path if p)})
    if out.returncode:
        raise RuntimeError(out.stderr[-2000:])
    return json.loads(out.stdout.strip().splitlines()[-1])


def scan() -> dict:
    a, r = _run(ANALYZER), _run(RUNNER)
    surface = dict(r["surface"])
    for k, v in a["surface"].items():
        if surface.setdefault(k, v) != v:
            raise RuntimeError(f"{k} hashed differently in the two interpreters")
    return {"surface": surface, "torch": a["torch"], "transformers": a["transformers"],
            "analyzer_only": sorted(a["surface"]),
            "runner_only": sorted(set(r["surface"]) - set(a["surface"]))}


def tables(surface: dict) -> tuple:
    from experiments.exp6 import pins_6 as p6
    bound = set(p6.INSTRUMENT_BLOBS_6)
    frozen = {k: v for k, v in surface.items()
              if not k.startswith("experiments/exp6/") and k != "experiments/__init__.py"}
    own = {k: v for k, v in surface.items()
           if (k.startswith("experiments/exp6/") or k == "experiments/__init__.py")
           and k not in bound and k not in p6.EXEMPT_6}
    return dict(sorted(frozen.items())), dict(sorted(own.items())), \
        sorted(k for k in surface if k in bound)


def literal(name: str, table: dict) -> str:
    rows = "".join(f'    "{k}":\n        "{v}",\n' for k, v in table.items())
    return f"{name} = {{\n{rows}}}"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    got = scan()
    frozen, own, bound = tables(got["surface"])
    if got["torch"] or got["transformers"]:
        print("the analyzer's imports load torch or transformers: they must not")
        return 1
    if "--check" in argv:
        from experiments.exp6 import pins_6 as p6
        bad = []
        if p6.FROZEN_SHA256_6 != frozen:
            bad.append("FROZEN_SHA256_6 is not the scan's table")
        if p6.IMPORTED_SHA256_6 != own:
            bad.append("IMPORTED_SHA256_6 is not the scan's table")
        for b in bad:
            print(b)
        print(f"{len(frozen)} frozen, {len(own)} own, {len(bound)} bound by the tag:",
              "DRIFT" if bad else "as pinned")
        return 1 if bad else 0
    print(literal("FROZEN_SHA256_6", frozen))
    print(literal("IMPORTED_SHA256_6", own))
    print(f"# {len(frozen)} frozen, {len(own)} own, {len(bound)} bound by the tag; "
          f"{len(got['runner_only'])} loaded by the runners alone: "
          f"{got['runner_only']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
