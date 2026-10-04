"""Offline source metadata inventory; never imports predecessor instruments."""
import collections
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
SNAPSHOT = "2d14da44ad882139bc95264697b03d45fe109354"
GIT = "/opt/homebrew/bin/git"
WORDS = "experiments/exp6/battery/data/words_6.tsv"
BB = "experiments/exp6/battery/data/bigbench_index_6.json"


def main():
    paths = subprocess.check_output([GIT, "ls-tree", "-r", "--name-only", SNAPSHOT], cwd=ROOT).decode().splitlines()
    items = sorted(p for p in paths if p.startswith("experiments/") and "/items/" in p
                   and p.endswith(".json") and not p.endswith("scored_battery.json"))
    pins = {}
    for p in items + [WORDS, BB]:
        raw = (ROOT / p).read_bytes()
        committed = subprocess.check_output([GIT, "show", f"{SNAPSHOT}:{p}"], cwd=ROOT)
        assert raw == committed, p
        pins[p] = hashlib.sha256(raw).hexdigest()
    rows = [line.split("\t") for line in (ROOT / WORDS).read_text().splitlines()[1:]]
    sig = collections.Counter("".join(sorted(r[1])) for r in rows)
    profiles = collections.Counter((len(w), min((int(rank)-1)//3333, 2),
                    tuple(sorted(collections.Counter(w).values(), reverse=True)))
            for rank, w, _, _ in rows if int(rank) <= 10000 and 4 <= len(w) <= 8
            and sig["".join(sorted(w))] == 1)
    capacities = {f"{n}:{t}": sum(v//2 for (nn, tt, _), v in profiles.items() if (nn, tt) == (n, t))
                  for n in range(4, 9) for t in range(3)}
    unit_support = collections.Counter()
    import math
    for n in range(2, 31):
        for p in range(n+1, 31):
            for m in range(2, 13):
                q = math.lcm(n, p)*m
                a, b = q*p//n, q*n//p
                if q <= 5000 and max(a, b) <= 9999:
                    unit_support[":".join(map(str, sorted((len(str(a)), len(str(b))))))] += 1
    record = {"snapshot": SNAPSHOT, "pins": pins, "item_files": items,
              "excluded": "scored_battery.json: aggregate scores, not item inputs; no model outputs read",
              "word_rows": len(rows), "word_pair_capacity": capacities,
              "unit_enumeration_capacity_before_old_collisions": dict(sorted(unit_support.items())),
              "computations": "Source hashes/schema reads, lexicon signature/profile counts, integer parameter-range enumeration only; no generated pair or baseline inspected."}
    with (HERE / "source_inventory.json").open("x") as f:
        json.dump(record, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({k: v for k, v in record.items() if k not in {"pins", "item_files"}}, indent=2))
    print("pinned item files:", len(items))


if __name__ == "__main__":
    main()
