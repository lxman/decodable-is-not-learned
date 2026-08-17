"""Freeze-time referent battery (design §4; freeze-checklist line):
every committed value 3c's meaning depends on, re-verified executable
on the REAL trees. No model is loaded and no new quantity is computed
— everything here is a read of committed artifacts through the frozen
loaders.

    python -m experiments.exp3c.verify_referents_3c

Writes referent_check_3c.json and exits nonzero on any failure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from experiments.exp3 import analyze_3 as a3
from experiments.exp3c import analyze_3c as c
from experiments.exp3c import compute_power_3c as pw

EXP3C = Path(__file__).resolve().parent
OUT = EXP3C / "referent_check_3c.json"


def main() -> int:
    checks = []

    def check(name, fn):
        try:
            detail = fn()
            checks.append({"check": name, "ok": True,
                           **({"detail": detail} if detail else {})})
            print(f"ok   {name}")
        except Exception as e:  # noqa: BLE001 — the record IS the point
            checks.append({"check": name, "ok": False, "error": str(e)})
            print(f"FAIL {name}: {e}")

    check("frozen exp3 files match their sha pins",
          lambda: c.check_frozen_imports())
    check("stream_map_3c is the formula's output and continuous "
          "with exp3's committed map",
          lambda: {"entries": len(c.check_stream_map()["cells"])})

    state = {}

    def load_exp3_tree():
        verify_fn = a3.load_verify()
        state["verify_fn"] = verify_fn
        state["cells"] = a3.load_sampling_cells(a3.EXP3,
                                                verify_fn=verify_fn)
        return {"cells": len(state["cells"])}

    check("exp3's 16 sampling cells load; stored tallies equal the "
          "recompute from raw draws", load_exp3_tree)

    def fires_table():
        ref = c.load_exp3_referent()
        state["ref"] = ref
        for key in a3.SAMPLING_CELLS:
            rc = state["cells"][key]["recomputed"]
            want = ref["fires"][c._key(key)]
            got = {"full_string_total": rc["full_string_total"],
                   "n_draws": rc["n_draws_total"]}
            if got != want:
                raise ValueError(f"{c._key(key)}: {got} != {want}")
        return {"cells_checked": 16}

    check("recomputed fires table equals the sha-pinned committed "
          "verdict record, 16/16", fires_table)

    def addresses():
        got = c.extract_fire_addresses(a3.EXP3, state["cells"],
                                       verify_fn=state["verify_fn"])
        if got != c.EXP3_FIRE_ADDRESSES_PIN:
            raise ValueError(f"{got} != pin")
        ans = state["cells"][c.FIRED_CELL]["answers"][436]
        if len(ans) != 4:
            raise ValueError(f"fired answer {ans!r} length != 4")
        return {"fired": got["reverse_string/1b/trained"],
                "fired_answer": ans}

    check("fired-cell address re-extracts to the pin (item 436, "
          "seed 0, draw 6; length-4 answer)", addresses)

    def twins():
        for key in c.TWIN_CELLS:
            rc = state["cells"][key]["recomputed"]
            if rc["full_string_total"] != 0:
                raise ValueError(f"{c._key(key)} fires "
                                 f"{rc['full_string_total']}")
        rev = sum(state["cells"][(r, s, "untrained")]["recomputed"]
                  ["n_draws_total"] for r in c.REVERSAL_RUNGS
                  for s in c.PROBE_SIZES)
        ctrl = sum(state["cells"][(r, s, "untrained")]["recomputed"]
                   ["n_draws_total"]
                   for r in (a3.POSITIVE_CONTROL, a3.MATCHED_CONTROL)
                   for s in c.PROBE_SIZES)
        if (rev, ctrl) != (c.TWIN_REVERSAL_DRAWS, c.TWIN_CONTROL_DRAWS):
            raise ValueError(f"twin draws ({rev}, {ctrl}) != "
                             f"({c.TWIN_REVERSAL_DRAWS}, "
                             f"{c.TWIN_CONTROL_DRAWS})")
        return {"reversal_twin_draws": rev, "control_twin_draws": ctrl}

    check("standing twin record: 0 fires across all 8 twin cells; "
          "512,000 reversal + 64,000 control twin draws", twins)

    def pins():
        sha_refs = a3.items_sha_referents(a3.load_gate2_referents())
        state["sha_refs"] = sha_refs
        for key in c.SCORED_CELLS:
            rung = key[0]
            got = state["cells"][key]["items_sha256"]
            if got != sha_refs[rung]:
                raise ValueError(f"{c._key(key)}: {got} != "
                                 f"{sha_refs[rung]}")
        return {"rungs": sorted(set(k[0] for k in c.SCORED_CELLS))}

    check("exp3 scored cells carry the §4 item pins (3b's referents)",
          pins)

    def prompts():
        got = c.load_prompts()
        n = 0
        for rung in c.REVERSAL_RUNGS:
            answers = state["cells"][(rung, "1b", "trained")]["answers"]
            if len(got[rung]) != len(answers):
                raise ValueError(f"{rung}: {len(got[rung])} prompts "
                                 f"against {len(answers)} answers")
            for i, (ans, p) in enumerate(zip(answers, got[rung])):
                if str(ans).casefold() in p.casefold():
                    raise ValueError(
                        f"{rung} item {i}: answer occurs in its own "
                        f"prompt — the by-construction guarantee the "
                        f"leak gate leans on is broken")
                n += 1
        return {"items_scanned": n}

    check("no committed answer occurs in its own rendered prompt "
          "(1000 items scanned)", prompts)

    def power():
        committed = pw.OUT.read_text()
        rebuilt = json.dumps(pw.build(), indent=1, sort_keys=True) + "\n"
        if committed != rebuilt:
            raise ValueError("power_3c.json is not the frozen code's "
                             "output")
        q = pw.build()["doc_quotes_check"]
        bad = {k for k, v in q.items() if not v["agrees"]}
        want = {"luck_floor_26^-4_quoted_1.5e-6",
                "luck_gap_factor_quoted_13x",
                "lone_draw_one_in_three_at_1e-6"}
        if bad != want:
            raise ValueError(f"quote disagreements {sorted(bad)} != "
                             f"the three ledgered slips")
        return {"expected_disagreements": sorted(want)}

    check("power_3c.json equals the frozen code's output; quote check "
          "disagrees on exactly the three ledgered slips", power)

    def determinism_reference():
        p = a3.EXP3 / "determinism_reference.json"
        if not p.is_file():
            raise FileNotFoundError(f"no determinism reference at {p}")
        return {"path": str(p)}

    check("exp3's committed determinism reference exists (cold re-run "
          "is its own checklist line)", determinism_reference)

    n_fail = sum(1 for x in checks if not x["ok"])
    OUT.write_text(json.dumps(
        {"checks": checks, "n_checks": len(checks), "n_failed": n_fail},
        indent=1) + "\n")
    print(f"\n{len(checks) - n_fail}/{len(checks)} referent checks "
          f"pass; written {OUT}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
