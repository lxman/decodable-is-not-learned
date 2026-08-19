"""The Exp 3d referent battery: every §4 referent, re-asserted
EXECUTABLE against the real committed trees — run at build, re-run
cold at the freeze, and equivalent in content to what run() enforces
on the way to a verdict (the checks live in the frozen loaders; this
battery exists so they can be exercised without a tranche on disk).

Numbered checks, all-or-nothing:
 1  frozen-import pins byte-identical (exp3 ×4, 3c ×3, 2c harness)
 2  item files: sha pins + the strata pin (194/155/151)
 3  3b-derived sha_refs == the §4 literal pins (two sources, one value)
 4  the 13 committed fires re-extracted from raw bytes == the pin
 5  3c verdict record (sha-pinned): fires table == the recompute
 6  the twin record: 0 fires / 512,000 + 64,000 draws, from raw bytes
 7  functional_selection_3d.json reproduces from the item file
 8  power_3d.json: m_min == recompute from the frozen ranks
 9  ctrl_copy sampled-rate pins == exp3's sha-pinned verdict entries
10  the verify wrapper: 3c's committed crasher draw scores False;
    answer-side crash stays a hard error (criterion totality, stop #1)
11  span_validation_3d.json reproduces from committed bytes
12  stream_map_3d.json == the frozen formula + both overlap laws
13  3c committed draws files == their §4 literal shas
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP3D = Path(__file__).resolve().parent
if str(EXP3D.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP3D.parent.parent))
for _p in (EXP3D.parent / "exp2b", EXP3D.parent / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from experiments.exp3 import analyze_3 as a3  # noqa: E402
from experiments.exp3c import analyze_3c as c  # noqa: E402
from experiments.exp3d import analyze_3d as d  # noqa: E402
from experiments.exp3d import span_validation_3d as sv  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn):
        CHECKS.append((n, name, fn))
        return fn
    return deco


@check(1, "frozen-import pins")
def _c1(ctx):
    d.check_frozen_imports_3d()


@check(2, "item files: sha pins + strata pin")
def _c2(ctx):
    ctx["items"] = d.load_item_file("reverse_string")
    d.load_item_file("ctrl_copy")


@check(3, "3b-derived sha_refs == §4 literal pins")
def _c3(ctx):
    gate2 = a3.load_gate2_referents()
    sha_refs = a3.items_sha_referents(gate2)
    ctx["sha_refs"] = sha_refs
    for rung in d.SCORING_RUNGS:
        if sha_refs.get(rung) != d.ITEMS_SHA_PIN[rung]:
            raise AssertionError(
                f"{rung}: 3b-derived {sha_refs.get(rung)} != literal "
                f"pin {d.ITEMS_SHA_PIN[rung]}")


@check(4, "13 committed fires re-extracted from raw bytes == pin")
def _c4(ctx):
    verify_fn = c.load_verify_3c()
    ctx["verify_fn"] = verify_fn
    exp3_cells = a3.load_sampling_cells(d.EXP3, verify_fn=verify_fn)
    ctx["exp3_cells"] = exp3_cells
    addresses = c.extract_fire_addresses(d.EXP3, exp3_cells,
                                         verify_fn=verify_fn)
    c3_cells = c.load_new_cells(d.EXP3C, verify_fn=verify_fn)
    ctx["c3_cells"] = c3_cells
    c3_verdict = json.loads(
        (d.EXP3C / "results" / "verdict.json").read_text())
    ctx["c3_verdict"] = c3_verdict
    ctx["base"] = d.build_committed_base(
        exp3_cells, c3_cells, addresses,
        c3_referent_fires=c3_verdict["fires"])


@check(5, "3c verdict record fires table == recompute")
def _c5(ctx):
    pass   # asserted inside build_committed_base (check 4); a separate
           # failure there names this check's referent in its message


@check(6, "twin record: 0 fires / 512k + 64k from raw bytes")
def _c6(ctx):
    t = ctx["base"]["twin"]
    if (t["fires"], t["reversal_twin_draws"],
            t["control_twin_draws"]) != \
            (0, d.TWIN_REVERSAL_DRAWS, d.TWIN_CONTROL_DRAWS):
        raise AssertionError(f"twin record {t}")


@check(7, "functional selection record reproduces")
def _c7(ctx):
    ctx["selection"] = d.load_selection(ctx["items"]["answers"])


@check(8, "power record m_min == recompute from frozen ranks")
def _c8(ctx):
    ctx["power"] = d.load_power_pin(ctx["selection"])


@check(9, "ctrl_copy sampled-rate pins == exp3 verdict entries")
def _c9(ctx):
    raw = (d.EXP3 / "results" / "verdict.json").read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    want = d.FROZEN_IMPORT_SHA256_3D[d.EXP3 / "results" / "verdict.json"]
    if got != want:
        raise AssertionError(f"exp3 verdict sha {got} != pin {want}")
    fires = json.loads(raw)["fires"]
    for size in d.SIZES_3D:
        e = fires[f"ctrl_copy/{size}/trained"]
        pin = d.CTRL_SAMPLED_RATE_PIN[size]
        if (e["full_string_total"], e["n_draws"]) != \
                (pin["count"], pin["n_draws"]):
            raise AssertionError(
                f"ctrl_copy/{size}: verdict {e['full_string_total']}/"
                f"{e['n_draws']} != pin {pin['count']}/{pin['n_draws']}")


@check(10, "verify wrapper totality: crasher False, answer-side hard")
def _c10(ctx):
    verify_fn = ctx["verify_fn"]
    # 3c stop #1's committed crasher address: reverse_string/410m,
    # item 395, seed 12, draw 22 — re-read from raw bytes and re-score
    import gzip
    gz = (d.EXP3C / "results" / "sampling" / "410m_trained"
          / "reverse_string.draws.jsonl.gz")
    text = None
    with gzip.open(gz, "rt") as f:
        for line in f:
            row = json.loads(line)
            if row["item"] == 395:
                text = row["draws"]["12"][22]
                break
    if text is None:
        raise AssertionError("crasher draw not found at its committed "
                             "address")
    answers = ctx["items"]["answers"]
    if verify_fn(text, answers[395], "word") is not False:
        raise AssertionError(
            f"the committed crasher draw {text!r} did not score False "
            f"through the total wrapper")
    try:
        verify_fn("anything", '"\t"', "word")
        raise AssertionError(
            "a crashing ANSWER was silently absorbed — the answer side "
            "must stay a hard error (stop #1's ratified boundary)")
    except IndexError:
        pass


@check(11, "span validation record reproduces")
def _c11(ctx):
    rec = sv.build()
    committed = json.loads(sv.OUT.read_text())
    if json.loads(json.dumps(rec, sort_keys=True)) != committed:
        raise AssertionError(
            "span_validation_3d.json does not reproduce from committed "
            "bytes")


@check(12, "stream map 3d == formula + overlap laws")
def _c12(ctx):
    d.check_stream_map_3d()
    c.check_stream_map()


@check(13, "3c committed draws files == §4 literal shas")
def _c13(ctx):
    for size in d.SIZES_3D:
        gz = (d.EXP3C / "results" / "sampling" / f"{size}_trained"
              / f"{d.RUNG}.draws.jsonl.gz")
        got = hashlib.sha256(gz.read_bytes()).hexdigest()
        if got != d.COMMITTED_3C_DRAWS_SHA256[size]:
            raise AssertionError(
                f"{gz}: {got} != pin "
                f"{d.COMMITTED_3C_DRAWS_SHA256[size]}")


def main() -> int:
    ctx = {}
    passed = 0
    for n, name, fn in CHECKS:
        try:
            fn(ctx)
        except Exception as e:   # noqa: BLE001 — the battery reports
            print(f"  {n:2d} FAIL {name}: {e}")
            print(f"[3d referents] {passed}/{len(CHECKS)} passed before "
                  f"the failure — the battery stops here")
            return 1
        passed += 1
        print(f"  {n:2d} ok   {name}", flush=True)
    print(f"[3d referents] {passed}/{len(CHECKS)} PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
