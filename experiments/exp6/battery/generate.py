# experiments/exp6/battery/generate.py
"""Write the Exp 6 item files (design §3.1): one JSON per rung under
`items/`, 500 eval items and 2 shots, generated from the rung's seed,
the vendored word table and the collision index — nothing else.

    PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python \
        -m experiments.exp6.battery.generate all
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from . import audit_bbkeys_6 as au
from . import collisions_6 as c6
from . import gen_arith, gen_ascii, gen_logic, gen_shapes, gen_units, gen_words  # noqa: F401
from . import words_6 as w6
from .spec import SPECS_6, generate

ITEMS_DIR = Path(__file__).resolve().parent / "items"
RUNG_ORDER_6 = ("modarith_add1", "modarith_sub1", "modarith_mul1",
                "unscramble_short", "unscramble_long", "ipa_word",
                "sort3", "sort5", "deduction3", "deduction5",
                "ascii_bubble", "ascii_basic", "shapes", "temporal", "lcs",
                "unit_interp1", "unit_interp2")


def context() -> dict:
    ctx = {}
    ctx.update(gen_words.context())
    ctx.update(gen_ascii.context())
    return ctx


def payload(name: str, ctx: dict | None = None) -> dict:
    """One rung's items. REFUSES unless the collision keys of the
    generators on disk are the ones the committed audit measured: an item
    file is evidence of freshness only behind a gate that was checked."""
    if name not in SPECS_6:
        raise ValueError(f"{name!r} is not a rung: {sorted(SPECS_6)}")
    au.load_record()
    spec = SPECS_6[name]
    d = generate(spec, ctx if ctx is not None else context(),
                 collisions=c6.for_spec(spec))
    d["provenance"] = {"words_6_sha256": w6.WORDS_6_SHA256,
                       "bigbench_index_sha256": c6.INDEX_6_SHA256,
                       "bigbench_commit": c6.BIGBENCH_COMMIT,
                       "bbkey_audit_sha256": au.AUDIT_6_SHA256,
                       "pyfiglet": gen_ascii.PYFIGLET_VERSION}
    return d


def dumps(d: dict) -> str:
    return json.dumps(d, indent=1, ensure_ascii=False, sort_keys=True) + "\n"


def write(name: str, ctx: dict | None = None, out_dir: Path = ITEMS_DIR) -> dict:
    text = dumps(payload(name, ctx))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{name}.json"
    p.write_text(text, encoding="utf-8")
    return {"rung": name, "path": str(p),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if set(SPECS_6) != set(RUNG_ORDER_6):
        raise SystemExit(f"registry {sorted(SPECS_6)} != RUNG_ORDER_6")
    names = RUNG_ORDER_6 if argv == ["all"] else tuple(argv)
    ctx = context()
    for n in names:
        r = write(n, ctx)
        print(f'    "{r["rung"]}": "{r["sha256"]}",')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
