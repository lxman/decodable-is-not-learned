# experiments/exp6/verify_referents_6.py
"""The cold battery: every referent, pin and gate checked from a cold
start, in a fresh process, against the real tree. Run before the tag,
and again after EVERY stage lands (2i's lesson: a cold tool run only at
close-out carries the premises of the day it was written).

Each item prints PASS, FAIL or SKIP. SKIP is for a stage that has not
run; an item never skips because its check is inconvenient. No item
prints a statistic of any test: the battery reads gates, not results.

    python -m experiments.exp6.verify_referents_6 [root]
"""
from __future__ import annotations

import sys
from pathlib import Path

EXP6 = Path(__file__).resolve().parent
REPO = EXP6.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp6 import battery_6 as b6  # noqa: E402
from experiments.exp6 import families_6 as fm  # noqa: E402
from experiments.exp6 import floors_6 as fl  # noqa: E402
from experiments.exp6 import pins_6 as p6  # noqa: E402
from experiments.exp6 import records_6 as r6  # noqa: E402
from experiments.exp6 import referents_6 as rf  # noqa: E402
from experiments.exp6 import strata_6 as s6  # noqa: E402

SKIP = "SKIP"
COMMITTED_TALLY_6 = {
    ("pythia_1b", "main", "add_base8"): 644, ("pythia_1b", "main", "sub_base8"): 2799,
    ("pythia_1b", "control", "ctrl_copy"): 13460,
    ("pythia_410m", "main", "add_base8"): 964,
    ("pythia_410m", "main", "sub_base8"): 2689,
    ("pythia_410m", "control", "ctrl_copy"): 12787,
    ("olmo2_1b", "main", "add_base8"): 1554, ("olmo2_1b", "main", "sub_base8"): 4124,
}


def _items():
    bat = b6.load_battery_6()
    assert set(bat) == set(b6.ALL_RUNGS_6)
    return f"{len(bat)} item files under their pins"


def _tables():
    bat = b6.load_battery_6()
    fl.check_floor_pins_6(fl.floor_table_6(bat))
    table = s6.build_table_6(bat)
    s6.check_strata_pins_6(table)
    s6.check_structure_pins_6(s6.structure_table_6(bat, table))
    fl.check_heuristic_pins_6(fl.heuristic_table_6(bat))
    return "floors, strata, structure levels, heuristic floors: as pinned"


def _audit():
    from experiments.exp6.battery import audit_bbkeys_6 as au
    rec = au.load_record()
    return (f"the collision-key audit: {sum(r['n_identical'] for r in rec['files'].values())}"
            f" identical, 0 failed; {len(au.load_known())} known answers")


def _overlap():
    from experiments.exp6.battery import overlap_6 as ov
    rec = ov.load_record()
    asked = sum(row["items"].get("asks a pair BIG-bench prints on any line", 0)
                for row in rec["rungs"].values())
    if asked:
        raise ValueError(f"{asked} items ask a pair BIG-bench prints")
    return f"the content-overlap record: {len(rec['rungs'])} rungs, of the pinned items"


def _tokens():
    rec = r6.read_json(EXP6 / "battery" / "token_lengths_6.json")
    bat = b6.load_battery_6()
    for rung, row in rec["rungs"].items():
        if row["items_sha256"] != bat[rung]["items_sha256"]:
            raise ValueError(f"{rung}: the token record measured other items")
        if max(row["answer_tokens_max"].values()) + 2 > row["budget"] or \
                row["budget"] != b6.max_new_tokens_6(rung):
            raise ValueError(f"{rung}: budget {row['budget']}")
    return f"{len(rec['rungs'])} rungs' longest answers inside their budgets"


def _manifest():
    from experiments.exp6 import analyze_6 as an
    from experiments.exp6 import make_referents_6 as mkr
    bad = mkr.check_referents(mkr.PATH, sha_pin=an.REFERENTS_6_SHA256)
    if bad:
        raise ValueError("; ".join(bad[:3]))
    return f"{len(rf.referent_files())} referent files as listed"


def _tallies():
    for (p, t, r), want in COMMITTED_TALLY_6.items():
        shape = r6.tier_shape(p, t)
        bits = r6.bits_of(rf.committed_rows(p, t, r), b6.load_item_file_6(r),
                          seeds=shape["seeds"])
        got = sum(map(sum, bits))
        if got != want:
            raise ValueError(f"{p}/{t}/{r}: {got} verified against the committed {want}")
    return "the criterion reproduces all eight committed tallies exactly"


def _committed_tests():
    from experiments.exp6 import power_6 as pw6
    n = sum(1 for t, f in pw6.TESTS_6 if len(rf.committed_test(t, f)["eligible"]) == 9)
    if n != 8:
        raise ValueError(f"{n} of 8 committed tests readable")
    return "the eight committed readings on 2c's battery are readable"


def _frozen():
    p6.check_frozen_6()
    from experiments.exp6.tools import import_scan_6 as sc
    got = sc.scan()
    frozen, own, bound = sc.tables(got["surface"])
    if got["torch"] or got["transformers"]:
        raise ValueError("the analyzer's imports load torch")
    if p6.FROZEN_SHA256_6 != frozen or p6.IMPORTED_SHA256_6 != own:
        raise ValueError("the import surface is not the pinned one")
    if set(p6.BARE_TOPS_6) != set(got["bare_tops"]) or got["foreign"]:
        raise ValueError(f"bare names {got['bare_tops']} against {p6.BARE_TOPS_6}, "
                         f"or modules from outside the repository {got['foreign'][:3]}")
    return f"{len(frozen)} frozen and {len(own)} own modules as pinned; no torch"


def _prereg():
    if not p6.git_tag_exists(r6.PREREG_TAG_6):
        return SKIP
    out = p6.require_prereg_6()
    return f"{r6.PREREG_TAG_6} binds {out['n_bound']} files"


def _predictor(root):
    from experiments.exp6.run import seal_predictor_6 as sp
    if not (r6.results(root) / "predictor").exists():
        return SKIP
    bad, units = sp.collect(root)
    gb, _ = sp.gate1p(root, units)
    bad += gb
    if not r6.seal_path(root).is_file():
        bad.append("not sealed")
    else:
        seal = r6.read_json(r6.seal_path(root))
        if seal.get("files") != sp.file_table(root):
            bad.append("the seal does not describe the files on disk")
        bad += p6.seal_failures(r6.PREDICTOR_SEAL_TAG_6,
                                [Path(root) / rel for rel in seal["files"]]
                                + [r6.seal_path(root)])
    if bad:
        raise ValueError(f"{len(bad)} failure(s): {bad[:3]}")
    return f"{len(units)} predictor units; gate 1-P byte-identical on eight; sealed"


def _endpoint(root):
    from experiments.exp6.run import seal_endpoint_6 as se
    if not (r6.results(root) / "endpoint").exists():
        return SKIP
    bat = b6.load_battery_6()
    seal = r6.read_json(r6.seal_path(root))
    bad, ep, hosts = se.collect(root, battery=bat, seal_sha256=seal["sha256"])
    bad += se.gate1b_failures(root, ep, hosts)
    if not r6.rung_sets_path(root).is_file():
        bad.append("the rung sets are not written")
    elif not bad:
        bad += se.rung_sets_failures(r6.read_json(r6.rung_sets_path(root)), ep,
                                     fl.floor_table_6(bat), fl.heuristic_table_6(bat),
                                     root)
        if r6.power_path(root).is_file():
            bad += p6.seal_failures(r6.ENDPOINT_SEAL_TAG_6, se.seal_paths(root))
        else:
            bad.append("the power record is not written")
    if bad:
        raise ValueError(f"{len(bad)} failure(s): {bad[:3]}")
    return f"{len(ep)} families' endpoints; gate 1(b) within {rf.TOL_PER_RUNG_6}; sealed"


def _sweeps(root):
    done = [f for f in fm.FAMILIES_6 if r6.sweep_dir(root, f).exists()]
    if not done:
        return SKIP
    steps = {f: sum(1 for s in fm.grid(f) if r6.checkpoint_path(root, f, s).is_file())
             for f in done}
    marks = r6.halt_markers(root)
    if marks:
        raise ValueError(f"halt marker(s): {[str(m) for m in marks[:3]]}")
    return "steps complete: " + ", ".join(
        f"{f} {steps[f]}/{len(fm.grid(f))}" for f in done)


def _read_sweep(root):
    from experiments.exp6.tools import read_sweep_6 as rs
    out = rs.sweep(root)
    if out["UNPINNED"] or out["outside_unexplained"]:
        raise ValueError(f"unpinned reads: "
                         f"{(out['UNPINNED'] + out['outside_unexplained'])[:3]}")
    return f"{out['n_reads']} reads, 0 unpinned"


def battery(root=EXP6) -> list:
    items = [("item files", _items), ("tables", _tables), ("collision audit", _audit),
             ("content overlap", _overlap), ("token record", _tokens), ("referent manifest", _manifest),
             ("committed tallies", _tallies), ("committed tests", _committed_tests),
             ("frozen and imported modules", _frozen), ("preregistration tag", _prereg),
             ("predictor stage", lambda: _predictor(root)),
             ("endpoint stage", lambda: _endpoint(root)),
             ("sweeps", lambda: _sweeps(root)),
             ("read sweep", lambda: _read_sweep(root))]
    out = []
    for name, thunk in items:
        try:
            got = thunk()
            out.append((name, SKIP if got == SKIP else "PASS",
                        "" if got == SKIP else got))
        except Exception as e:  # noqa: BLE001 — the battery reports, it does not stop
            out.append((name, "FAIL", f"{type(e).__name__}: {e}"))
    return out


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    rows = battery(Path(argv[0]) if argv else EXP6)
    for name, status, note in rows:
        print(f"{status:4s}  {name:30s} {note}")
    n = {s: sum(1 for _, x, _ in rows if x == s) for s in ("PASS", "FAIL", SKIP)}
    print(f"{n['PASS']}/{len(rows)} PASS, {n['FAIL']} FAIL, {n[SKIP]} SKIP")
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
