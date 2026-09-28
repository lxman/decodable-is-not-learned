# experiments/exp6/referents_6.py
"""The committed records Exp 6 measures itself against (design §3.3,
§3.4): the anchors' predictor streams (2k, 2i), the control's (exp3),
and the four families' Mac records of the anchors on every grid point.
Read-only; every path listed here is in the referent manifest."""
from __future__ import annotations

from pathlib import Path

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import families_6 as fm
from experiments.exp6 import records_6 as r6

# 2b's pinned Pythia revisions (`experiments/exp2b/models.py`), as
# literals: that module imports torch at its top, and the analyzer loads
# no torch. A test holds the two tables equal.
PYTHIA_COMMIT_6 = {"410m": "9879c9b5f8bea9051dcb0e68dff21493d67e9d4f",
                   "1b": "f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2"}

# Exp 5's frozen cross-host tolerance (plan delta: the design said 8,
# the benchmark's observed maximum, which leaves no margin)
TOL_PER_RUNG_6 = 15
D_TOLERANCE_6 = 0.03               # S10: anchor D, new pipeline vs committed


# S9 / S10: the committed verdict records of the five experiments that
# read 2c's battery with these predictors (referents; never re-run)
VERDICT_RECORDS_6 = {x: b6.EXPERIMENTS / x / "results" / "verdict.json"
                     for x in ("exp2i", "exp2k", "exp2l", "exp2m", "exp2n")}
# (test, family) -> (experiment, the path of the test inside its verdict
# record, what that committed test conditioned on)
COMMITTED_TEST_6 = {
    ("A", "olmo7b"): ("exp2k", ("primary",), "unconditioned, 256 draws"),
    ("A", "olmo13b"): ("exp2l", ("tests", "A"), "unconditioned, 256 draws"),
    ("A", "smollm3_3b"): ("exp2m", ("tests", "A"), "unconditioned, 256 draws"),
    ("A", "comma_7b"): ("exp2n", ("tests", "A"), "unconditioned, 256 draws"),
    ("B", "olmo7b"): ("exp2i", ("secondaries", "within_alone"),
                      "unconditioned (2i's within-alone; its Test B conditioned "
                      "on x_A's zero cut)"),
    ("B", "olmo13b"): ("exp2l", ("secondaries", "S3 within alone"),
                       "unconditioned (2l's within-alone; its Test B conditioned "
                       "on x_A's median bucket)"),
    ("B", "smollm3_3b"): ("exp2m", ("tests", "B"), "unconditioned, 64 draws"),
    ("B", "comma_7b"): ("exp2n", ("tests", "B"), "unconditioned, 64 draws"),
}


def committed_test(test: str, family: str) -> dict:
    """The committed reading of (test, family) on 2c's battery: T, the
    rungs read, and the per-rung D of the anchors."""
    exp, path, note = COMMITTED_TEST_6[(test, family)]
    node = r6.read_json(VERDICT_RECORDS_6[exp])
    for k in path:
        node = node[k]
    return {"experiment": exp, "path": "/".join(path), "conditioning": note,
            "T": node["stratified"]["T"], "p": node["stratified"]["p"],
            "eligible": list(node["eligible"]),
            "per_rung_d": {r: node["per_rung"][r]["d"] for r in node["per_rung"]}}


def committed_draws_path(predictor: str, tier: str, rung: str) -> Path:
    e = b6.EXPERIMENTS
    size = r6.PREDICTORS_6[predictor]["size"]
    if tier == "control":
        if r6.PREDICTORS_6[predictor]["lineage"] != "pythia":
            raise ValueError(f"{predictor}: the control has no committed stream")
        return e / "exp3" / "results" / "sampling" / f"{size}_trained" / \
            f"{rung}.draws.jsonl.gz"
    if tier != "main" or rung not in b6.ANCHORS_6:
        raise ValueError(f"{predictor}/{tier}/{rung} has no committed stream")
    if r6.PREDICTORS_6[predictor]["lineage"] == "pythia":
        return e / "exp2k" / "results" / "k256" / f"{size}_trained" / \
            f"{rung}.draws.jsonl.gz"
    return e / "exp2i" / "results" / "predictor" / "olmo1b" / f"{rung}.draws.jsonl.gz"


def committed_record_path(predictor: str, tier: str, rung: str) -> Path:
    p = committed_draws_path(predictor, tier, rung)
    return p.with_name(p.name.replace(".draws.jsonl.gz", ".json"))


def gated_units() -> list:
    """The (predictor, tier, rung) units that reproduce a committed
    stream: gate 1-P's coverage."""
    out = []
    for p, t, r in r6.predictor_units():
        if (t == "main" and r in b6.ANCHORS_6) or t == "control":
            out.append((p, t, r))
    return out


def committed_rows(predictor: str, tier: str, rung: str) -> list:
    t = r6.tier_shape(predictor, tier)
    return r6.read_draws(committed_draws_path(predictor, tier, rung),
                         seeds=t["seeds"], dps=t["dps"])


def model_pin(predictor: str, tier: str = "main") -> dict:
    """What a predictor's loader must report. Pythia: the revision sha
    (exp3's loader returns it as the model sha). OLMo-2 1B: the commit
    of 2i's manifest and the tensor digest 2i's committed records carry
    — the loader must MEASURE that digest again."""
    if r6.PREDICTORS_6[predictor]["lineage"] == "pythia":
        size = r6.PREDICTORS_6[predictor]["size"]
        return {"repo": f"EleutherAI/pythia-{size}", "commit": PYTHIA_COMMIT_6[size],
                "model_sha": PYTHIA_COMMIT_6[size]}
    from experiments.exp2i import battery_2i as bi
    man = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    rec = r6.read_json(committed_record_path(predictor, "main", b6.ANCHORS_6[0]))
    return {"repo": bi.REPO_1B, "commit": bi.entry_1b_endpoint(man)["commit"],
            "model_sha": rec["model_sha"]}


def mac_count(family: str, step, rung: str) -> int:
    return int(r6.read_json(fm.committed_sweep_record(family, step, rung))["correct"])


def mac_bits(family: str, step, rung: str) -> list:
    rec = r6.read_json(fm.committed_sweep_record(family, step, rung))
    if len(rec["bits"]) != b6.N_ITEMS:
        raise ValueError(f"{family}/{step}/{rung}: committed bits are not 500 long")
    return [int(b) for b in rec["bits"]]


def mac_endpoint_count(family: str, rung: str) -> int:
    return int(r6.read_json(fm.committed_endpoint_record(family, rung))["correct"])


# ---- gate 1(d): the weights are the ones the Mac ran (plan delta N-14)
def mac_digest(family: str, step) -> str:
    """The tensor digest the Mac measured when it ran this checkpoint in
    the family's own experiment (`weight_sha256` of the anchors'
    committed records; the two must carry one digest). It hashes the
    state dict on the CPU in the campaign's dtype: a property of the
    weights, not of the host."""
    got = {str(r6.read_json(fm.committed_sweep_record(family, step, r))
               .get("weight_sha256") or "") for r in b6.ANCHORS_6}
    if len(got) != 1 or "" in got:
        raise ValueError(f"{family}/{step}: the committed records carry no one "
                         f"tensor digest")
    return got.pop()


def digest_step(family: str, key):
    """The checkpoint a load's key names: the endpoint for the endpoint
    stage's read and for both gate reads of a sweep host, the init
    referent, or a grid step."""
    if key in ("stage1_final", r6.SWEEP_THIN, r6.SWEEP_CAND):
        return fm.endpoint_step(family)
    if key in ("init", fm.INIT):
        return fm.INIT
    return int(key)


def digest_failures(load: dict, family: str, key, *, label: str) -> list:
    """The load's MEASURED digest against the Mac's committed one. A
    seeded `from_config` twin is outside the gate: it is built, not
    loaded, and it is descriptive."""
    step = digest_step(family, key)
    if step == fm.INIT and fm.INIT_KIND[family] == "twin":
        return []
    want = mac_digest(family, step)
    if load.get("digest") != want:
        return [f"{label}: tensor digest {str(load.get('digest'))[:12]} is not the "
                f"Mac's committed {want[:12]}"]
    return []


def anchor_tolerance(counts: dict, referent: dict, *, label: str) -> list:
    """|Δ| per anchor against the Mac's committed count."""
    bad = []
    for r in b6.ANCHORS_6:
        if r not in counts or r not in referent:
            bad.append(f"{label}/{r}: count missing on one side")
            continue
        d = abs(int(counts[r]) - int(referent[r]))
        if d > TOL_PER_RUNG_6:
            bad.append(f"{label}/{r}: |Δ| {d} > {TOL_PER_RUNG_6} ({counts[r]} "
                       f"against the Mac's {referent[r]})")
    return bad


def gate1b_record(counts: dict) -> dict:
    """Gate 1(b) as a pure function of the box's anchor counts:
    `counts[family][which][rung]`, `which` in (stage1_final, init). One
    implementation — the endpoint runner writes it, the seal and the
    analyzer re-derive it from the records."""
    fam, bad = {}, []
    for f in fm.FAMILIES_6:
        if f not in counts:
            continue
        got, got0 = counts[f]["stage1_final"], counts[f]["init"]
        mac = {r: mac_endpoint_count(f, r) for r in b6.ANCHORS_6}
        mac0 = {r: mac_count(f, fm.INIT, r) for r in b6.ANCHORS_6}
        fails = anchor_tolerance(got, mac, label=f"6 gate 1(b) {f}/stage1_final")
        fails += anchor_tolerance(got0, mac0, label=f"6 gate 1(b) {f}/init")
        fam[f] = {"stage1_final": {"box": {r: int(got[r]) for r in b6.ANCHORS_6},
                                   "mac": mac},
                  "init": {"box": {r: int(got0[r]) for r in b6.ANCHORS_6},
                           "mac": mac0}, "failures": fails}
        bad += fails
    return {"families": fam, "tolerance_per_rung": TOL_PER_RUNG_6,
            "pass": not bad, "failures": bad}


def referent_files() -> list:
    """Every committed file outside exp6 that the analyzer reads."""
    out = set()
    for p, t, r in gated_units():
        out.add(committed_draws_path(p, t, r))
        out.add(committed_record_path(p, t, r))
    for f in fm.FAMILIES_6:
        for r in b6.ANCHORS_6:
            out.add(fm.committed_endpoint_record(f, r))
            out.add(fm.committed_sweep_record(f, fm.INIT, r))
            for s in fm.grid(f):
                out.add(fm.committed_sweep_record(f, s, r))
    e = b6.EXPERIMENTS
    out |= set(VERDICT_RECORDS_6.values())
    out |= {e / "exp2g" / "results" / "predictor" / "strata.json",
            e / "exp2c" / "battery" / "items" / "ctrl_copy.json",
            e / "exp2b" / "battery" / "items" / "add_base8.json",
            e / "exp2c" / "battery" / "items" / "sub_base8.json",
            e / "exp2i" / "checkpoints_2i.json", e / "exp2l" / "checkpoints_2l.json",
            e / "exp2m" / "checkpoints_2m.json", e / "exp2n" / "checkpoints_2n.json"}
    return sorted(out)
