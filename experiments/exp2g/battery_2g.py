# experiments/exp2g/battery_2g.py
"""The Exp 2g battery: rung sets, grid, pins and paths (design §4.1,
§5). Everything here is a committed value or a pure function of one;
every literal is re-asserted against its source at load."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2G = Path(__file__).resolve().parent
EXPERIMENTS = EXP2G.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402  (sets sys.path: exp2c wins `harness`, exp2b supplies `models`)
from experiments.exp2d import stats_2d as st  # noqa: E402

EXP2B, EXP2C = bt.EXP2B, bt.EXP2C
EXP2D = EXPERIMENTS / "exp2d"
EXP2F = EXPERIMENTS / "exp2f"
EXP3C = EXPERIMENTS / "exp3c"
EXP1 = EXPERIMENTS / "exp1"
RESULTS = EXP2G / "results"
CHECKPOINTS_PATH = EXP2G / "checkpoints_2g.json"
HUB_INVENTORY_PATH = EXP2G / "hub_inventory.json"
SEAL_TAG = "exp2g-predictor-sealed"
PREREG_TAG = "exp2g-preregistered"

N_ITEMS, N_SHOTS = bt.N_ITEMS, bt.N_SHOTS
PROBE_SIZES = bt.PROBE_SIZES                 # ("410m", "1b")
PRIMARY_SIZE, REPLICATION_SIZE = "1b", "410m"   # ruling b
MODES = ("trained", "untrained")
UNTRAINED_SEED = 0                           # 2b/2c/2f's twin
ADJUDICATING, REPLICATING = "2.8b", "12b"
SWEEP_SIZES = (ADJUDICATING, REPLICATING)
REPO_OF = {"2.8b": "EleutherAI/pythia-2.8b", "12b": "EleutherAI/pythia-12b"}
FINAL_STEP = 143000
ELIGIBILITY_MIN_POS = 20                     # ruling d

# §4.1 — from 2c's committed m4 counts under 2d's bar (check_rung_sets)
R_28 = ("antonym", "antonym6", "add_base8", "sub_base8", "add3_mid",
        "sub3_mid", "arith_next")
R_12B = ("antonym", "antonym6", "add_base8", "sub_base8", "add3_mid",
         "sub4_mid", "median5", "arith_next", "count_div13")
PREDICTOR_RUNGS = ("antonym", "antonym6", "add_base8", "sub_base8",
                   "add3_mid", "sub3_mid", "sub4_mid", "median5",
                   "arith_next", "count_div13", "odd6")

# §4 grid, ruling e, with build finding B applied (64000 excluded at 2.8b)
GRID = {
    "2.8b": (0, 1000, 2000, 4000, 8000, 10000, 16000, 20000, 30000, 32000,
             40000, 50000, 60000, 70000, 80000, 90000, 100000, 110000,
             120000, 130000, 140000, 143000),
    "12b": (1000, 4000, 16000, 32000, 64000, 100000, 130000, 143000),
}
EXCLUDED_GRID = {
    "2.8b": {64000: "the Hub's step64000 branch carries step143000's weight "
                    "files byte-for-byte (stale copy; build finding B)"},
    "12b": {},
}


def sweep_rungs(size: str) -> tuple:
    if size == ADJUDICATING:
        return tuple(bt.RUNGS)
    if size == REPLICATING:
        return PREDICTOR_RUNGS
    raise ValueError(f"{size!r} is not a sweep size")


def trained_steps(size: str) -> tuple:
    return tuple(s for s in GRID[size] if s != 0)


def n_trained(size: str) -> int:
    return len(trained_steps(size))


def revision_of(step: int) -> str:
    """The final grid point is 2c's pinned `main` commit, never the
    Hub's step143000 branch (build finding C)."""
    return "main" if step == FINAL_STEP else f"step{step}"


# ---------------------------------------------- 2c's committed m4 counts

FINAL_COUNT_PIN = {
    "2.8b": {
        "add4_mid": 2, "sub4_mid": 4, "add3_mid": 43, "sub3_mid": 264,
        "antonym6": 149, "antonym": 272, "arith_next": 137, "quad_next": 5,
        "base12_digitsum": 3, "base13": 1, "base7": 0, "oct2dec": 0,
        "caesar_len8": 0, "caesar": 0, "clock24_d999": 22, "clock24": 25,
        "collatz_step2": 77, "count_div13": 58, "count_div7": 28,
        "hamming12": 99, "isqrt_gap": 73, "median5": 113, "median7": 78,
        "mod13_comp": 27, "mod17": 26, "mod19": 28, "mod13": 46, "odd6": 61,
        "odd_one_out": 81, "rev_string7": 0, "reverse_string": 0,
        "roman_sum7": 79, "sub_base8": 91, "add_base8": 44,
    },
    "12b": {
        "antonym": 280, "antonym6": 199, "add_base8": 50, "sub_base8": 86,
        "add3_mid": 26, "sub3_mid": 11, "sub4_mid": 12, "median5": 131,
        "arith_next": 76, "count_div13": 102, "odd6": 94,
    },
}


def m4_path(size: str, rung: str) -> Path:
    return EXP2C / "results" / "m4" / f"{size}_trained" / f"{rung}.json"


def load_m4_counts(size: str, rungs=None) -> dict:
    """2c's committed correct counts for the sweep rungs, each
    re-asserted against the pin."""
    rungs = tuple(rungs) if rungs is not None else sweep_rungs(size)
    out = {}
    for r in rungs:
        rec = json.loads(m4_path(size, r).read_text())
        if rec.get("capability") != r or rec.get("n") != N_ITEMS or \
                rec.get("mode") != "trained" or rec.get("size") != size:
            raise ValueError(f"m4 record {size}/{r}: not the committed shape")
        if rec["correct"] != FINAL_COUNT_PIN[size][r]:
            raise ValueError(f"m4 {size}/{r}: correct {rec['correct']} against "
                             f"the pin {FINAL_COUNT_PIN[size][r]}")
        out[r] = int(rec["correct"])
    return out


def rising_by_bar(counts: dict, floors: dict) -> tuple:
    """2d's rule on one size: clears the floor by the one-sided exact
    binomial at α .01."""
    return tuple(r for r in counts
                 if st.binomial_bar(counts[r], N_ITEMS, floors[r])["significant"])


def check_rung_sets(floors: dict) -> dict:
    got28 = rising_by_bar(load_m4_counts("2.8b"), floors)
    got12 = rising_by_bar(load_m4_counts("12b"), floors)
    if set(got28) != set(R_28):
        raise ValueError(f"R_2.8b from m4 + bar is {got28}, pinned {R_28}")
    if set(got12) != set(R_12B):
        raise ValueError(f"R_12b from m4 + bar is {got12}, pinned {R_12B}")
    return {"2.8b": list(R_28), "12b": list(R_12B)}


# --------------------------------------------------------------- floors

FLOORS_VERDICT_2D_SHA256 = \
    "d5b1b28bf70f4be1a5acf73df8ad03d8c57349ce4acf15e26f690c6dc1347b61"


def load_floors(path=None, *, sha_pin=FLOORS_VERDICT_2D_SHA256) -> dict:
    """2d's frozen floors (max(majority share, 1/n_options)), read from
    2d's committed verdict, sha-pinned."""
    p = Path(path or EXP2D / "results" / "verdict.json")
    raw = p.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{p} hashes to {got}, pinned {sha_pin}")
    per = json.loads(raw)["per_rung"]
    if set(per) != set(bt.RUNGS):
        raise ValueError("2d's verdict does not carry the 34 rungs")
    return {r: float(per[r]["floor"]) for r in bt.RUNGS}


# ------------------------------------------------------- frozen imports

FROZEN_IMPORT_SHA256_2G = {
    EXP2B / "models.py":
        "a4c5eed26cc92044aeb9ed7b68b177035de3ac2615dbba09a6d21eeb191a55a4",
    EXP2B / "probe_starved.py":
        "e6c81df28e4a7e07db3a123e4b06d3c8a98a7d330cd726596d41b1136c4cd27b",
    EXP2B / "splits.py":
        "49df4c62c3c3bd611b9cf49be46001c12220045a3611a39be5e2bc5b89ded6e0",
    EXP2C / "harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    EXP2C / "run" / "screen.py":
        "fef1814142955912066837fbd2119f5c2ae27fe31393ede890584313e2b06873",
    EXP2D / "battery_2d.py":
        "503a2c09ec320989223561291ff93c71d62d27ed20c5681f9b2d535b7708e81a",
    EXP2D / "stats_2d.py":
        "86243932709013ea15b250e9bf15243ce6209e03e6bcf81af0f7ac3f92644b46",
    EXP2D / "analyze_2d.py":
        "01ee334db5fe273a8509cf4bf79757b52a40a123311acd42554ac1a82e40334a",
    EXP2F / "probe_2f.py":
        "63c714d6e899dd9d6d5610a3d54c9254ec0749d03f44a703790d4a4354854f62",
    EXP2F / "labels_2f.py":
        "8dc31850e5c47b7a1cc171b0388521ebe01005ddc123954c0073734cf9aaac25",
    EXP2F / "collect_eval_2f.py":
        "189e3738471185b7205f106fdac9bc5da1d564caafc60e39f4d6e3546915d071",
    EXP2F / "analyze_2f.py":
        "79018ff34b6f41bd2a5e8fa0f922a2de567861750057a5eca1a3dad6cf3f61d3",
    EXP3C / "analyze_3c.py":
        "66b78ffbedb808625ed33019f29d2ef8ec9d0f31a1115eb7cb08ad3e67d42d84",
    EXP1 / "signatures" / "stats.py":
        "ceab3eb7f6daf9346b9231f0e4af7e458b43ba4e7361556aef926e1abde2611f",
}


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_frozen_imports_2g() -> None:
    for path, want in FROZEN_IMPORT_SHA256_2G.items():
        got = sha256_file(path)
        if got != want:
            raise ValueError(f"frozen file {path} has sha256 {got}, expected "
                             f"{want} — 2b/2c/2d/2f/3c are closed and their "
                             f"code is 2g's instrument")


# --------------------------------------------- probe-item activations

PROBE_NPZ_SHA_PIN = {
    ("antonym", "410m", "trained"): "b8cb848d562afb16052d94e210e0bceb8445fabd95e914874013d5c03ec83310",
    ("antonym6", "410m", "trained"): "ad187783cd98edf5deff2f68a628b3279b524dcbd2b21a59fa724a9257a45781",
    ("add_base8", "410m", "trained"): "c662fc21affc940c483edb1a564b560408fac4846dd22768b41f3f7b8cdea725",
    ("sub_base8", "410m", "trained"): "17b5c0d1950a7b14bfdf65a62dac69dbd1803243be594ca11f7d8094b89dfc9b",
    ("add3_mid", "410m", "trained"): "03b27c6ef35df17a00c35569825f0de6010043f055cf10f52a4f993cb12a053b",
    ("sub3_mid", "410m", "trained"): "a43d9754bc516b54da1bde921d5c517e877ef6b653045c0887b6ab4f09461d9e",
    ("sub4_mid", "410m", "trained"): "2682a52bf51d185ec0e8019b0cd558307a675cbf8a68ac3a5ddac1a6281c61b3",
    ("median5", "410m", "trained"): "d6514ac512e6d5bd023498cf3bceef55d24968f48d61831cb6a37b59c0c18ff2",
    ("arith_next", "410m", "trained"): "cbc399352cc1b8f99b20373e70783cdb2c46b39d4ffcf34e4bc7394473bcdcbc",
    ("count_div13", "410m", "trained"): "128d951926beceaba0fcff82dc917f2b6c46e51e7193e65ed7c8ebaae0553dbe",
    ("odd6", "410m", "trained"): "f275d4101b42e5d3df80eeb9d3cda84d5c501dc51660034c26cc6f4377a02da8",
    ("antonym", "410m", "untrained"): "aa09fe44abacd3b1ba07be72bce5164de84c14f1df4223ed5c6490b44292b54c",
    ("antonym6", "410m", "untrained"): "9b6ae92d2d367d078a617274d99d06c1d3d118639eecb4af1eeb7c5c7ec9dacc",
    ("add_base8", "410m", "untrained"): "013c9d1ca6c5e444772fad1ebfcdce5933219ac424223bd8ba9a1800950b5642",
    ("sub_base8", "410m", "untrained"): "9529be7048f54b9dc171d496ebd9106b50c79329d544651f60b0978b7693c30d",
    ("add3_mid", "410m", "untrained"): "8a792d36fe692b334a00112ecc3c058d4e721a96cbd3b28ab68c756db563b26a",
    ("sub3_mid", "410m", "untrained"): "fb742dde155eab487406d096a8c29c86e2e9df2c98f8c57430654da301fbb56d",
    ("sub4_mid", "410m", "untrained"): "a774123e10ecd5c6bdfdde7bf988a2dd45079dba691ce2e66922e5f0fadb0bd8",
    ("median5", "410m", "untrained"): "c261695f850621e9c78151d133beaef21085096ac697f6f3cbf3ed73ba0f146f",
    ("arith_next", "410m", "untrained"): "ce2395b6ca05d70fa455dc79eceaab8c4ebbf3dd1508fbaf5a1f0f68c8336c7d",
    ("count_div13", "410m", "untrained"): "5b8957f4a9a66653bd839985070f4fb543dfd0e2df6170788b657e6d83d73464",
    ("odd6", "410m", "untrained"): "b2b3738d8e4b3a00d78051e819260e5f1e9391ed2bb8c6fa3172013626eafd04",
    ("antonym", "1b", "trained"): "1846cd4d458e501afb2b8e429887880cf36cbb754977874d8d89c19f1a07c619",
    ("antonym6", "1b", "trained"): "11b931d23d5abcd29a2afda11df869819b4fb7e206ea2626906b9a0855d5935b",
    ("add_base8", "1b", "trained"): "844a3f72b98e28ca66362a08a9e1aa9af0191fa15372df5b03ea04742a3a8f99",
    ("sub_base8", "1b", "trained"): "fc1c989e74fcc637aa4e95f1af46c4dd46c65c03d1da4e8815cbc8872aa0cf06",
    ("add3_mid", "1b", "trained"): "98b3d8bd79735581a6f357b25201219c40b7f498b398660dc5729f6d006516d0",
    ("sub3_mid", "1b", "trained"): "77c60f38472b13974f40f231f59b0a5cdc64dcd4e48cd54de73c2b0291402dc3",
    ("sub4_mid", "1b", "trained"): "42076f3d448384d65ddc4af531873f53e8a6213e3d45a21ffab94b15a6c7119a",
    ("median5", "1b", "trained"): "16f3e15ef23d4eca3335f026099dd27f598706c356a6dd22b7145369806c0383",
    ("arith_next", "1b", "trained"): "e14dc60e065c89f01b3fa2d05ef91d2d6114324e7c1af423bbcc95a81042f4d4",
    ("count_div13", "1b", "trained"): "79cc86f6e7804d3b09a65014a7cca0c0bbf506a085cab8d0bb708b66583bd305",
    ("odd6", "1b", "trained"): "aebb72adce205fe151e7253c6abb4ddba174005b3715e8899b11057be03422f6",
    ("antonym", "1b", "untrained"): "fc2f28b0c5e7e062b102c0025efd84dca33c4e1cabce974138c12c26100e4a8b",
    ("antonym6", "1b", "untrained"): "51d9906f71f48487a33ed114ee166c57173d7fc29535b9419683d2c5c6b84433",
    ("add_base8", "1b", "untrained"): "8f6444edbeef3083a51c42fcecd8c73f070841cad322e373a08440d5b5422f4b",
    ("sub_base8", "1b", "untrained"): "5bd292c648901c892c66b47d51ed4412ff43882c8678f61fe78b1dd78300f780",
    ("add3_mid", "1b", "untrained"): "ba4284174d5801933bdd9dad98d183ca6ced6a389a9548aaaae8844351fd965f",
    ("sub3_mid", "1b", "untrained"): "feddbe0e0830bbd84affc6ce077bff1933b59ab0507201eca8a32877b709117b",
    ("sub4_mid", "1b", "untrained"): "0d5cc9152602e8d4ddca4114a7e5cca9aff05709fa754067c8f03a53d902ed4b",
    ("median5", "1b", "untrained"): "a4637cf738ca10b67317e80f3325d74b8b89f603b71478480f0a517326154fa6",
    ("arith_next", "1b", "untrained"): "30140ffad82ccabf21b8d3493f94612d3a009d99310272ff28d5acbfe5fa9246",
    ("count_div13", "1b", "untrained"): "c64a8840418b1b10aa87f278517cb663d082e2d243545ca27e0072c1f81d30b1",
    ("odd6", "1b", "untrained"): "15abeb316cc52353044bd06369c4216ea6b8819d1762e0c76fe694ef329f456c",
}
DIGEST_LIST_SHA256 = {
    "exp2b": "05ac5d7b785d07c952c9c8af564f4980a83fb946d1dd1b4c8ba7dcfc054e1476",
    "exp2c": "9ad881a62566ccd3c9881665258b945abf78df86ce0d81ef7e70f3ecca063811",
}


def probe_npz_path(size, mode, rung, *, probe_root=None) -> Path:
    """2b's tree for the carried survivors, 2c's otherwise; a world's
    own tree when `probe_root` is given."""
    if probe_root is not None:
        return (Path(probe_root) / "results" / "activations_probe"
                / f"{size}_{mode}" / f"{rung}.npz")
    exp = EXP2B if rung in bt.REUSED else EXP2C
    return exp / "results" / "activations" / f"{size}_{mode}" / f"{rung}.npz"


def load_probe_acts(path, cap, *, sha_pin):
    """The committed probe-item activations, thinned to 2f's site
    family; y == the committed probe_label list (the gate)."""
    from experiments.exp2c.run.screen import _load_activation_map
    from experiments.exp2f import probe_2f as pb
    got = sha256_file(path)
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"activation file {path} hashes to {got}, pinned "
                         f"{sha_pin} — not the committed probe-item activations")
    act, y, meta = _load_activation_map(Path(path))
    items = cap["probe_items"]
    y = [str(v) for v in y]
    if len(y) != len(items) or y != [str(it["probe_label"]) for it in items]:
        raise ValueError(f"{path}: labels are not the committed probe_labels")
    if meta.get("capability") != cap.get("name"):
        raise ValueError(f"{path}: capability {meta.get('capability')!r}")
    return pb.thin(act), y, meta


def load_battery(rungs=None) -> dict:
    rungs = tuple(rungs) if rungs is not None else tuple(bt.RUNGS)
    return {r: bt.load_item_file(r) for r in rungs}


# ----------------------------------------------------------------- paths

def sweep_dir(root, size) -> Path:
    return Path(root) / "results" / "sweep" / size


def record_path(root, size, step, rung) -> Path:
    return sweep_dir(root, size) / f"step{int(step)}" / f"{rung}.json"


def checkpoint_record_path(root, size, step) -> Path:
    return sweep_dir(root, size) / f"step{int(step)}" / "_checkpoint.json"


def gate1_path(root, size) -> Path:
    return sweep_dir(root, size) / "gate1.json"


def halt_marker_path(root, size) -> Path:
    return sweep_dir(root, size) / "HALTED"


def predictor_path(root) -> Path:
    return Path(root) / "results" / "predictor" / "predictor.json"


def predictor_sha_path(root) -> Path:
    return Path(root) / "results" / "predictor" / "predictor_sha256.txt"


def strata_path(root) -> Path:
    return Path(root) / "results" / "predictor" / "strata.json"


def eval_npz_path(root, size, mode, rung) -> Path:
    return (Path(root) / "results" / "activations_eval" / f"{size}_{mode}"
            / f"{rung}.npz")


def continuity_path(root, size, mode) -> Path:
    return Path(root) / "results" / "continuity" / f"{size}_{mode}.json"


if __name__ == "__main__":
    check_frozen_imports_2g()
    print(json.dumps(check_rung_sets(load_floors())))
    for size in SWEEP_SIZES:
        print(size, "trained steps", trained_steps(size), "excluded",
              EXCLUDED_GRID[size])
