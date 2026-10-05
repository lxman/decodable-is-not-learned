"""Low-to-high ordinal merging; all nominal groups and ties retained."""
from collections import defaultdict
from .contract import integer, require


def merge_levels(nominal, ordinal, *, minimum=10):
    require(len(nominal) == len(ordinal) and len(nominal) > 0, "strata lengths")
    integer(minimum, 1, 1000000, "minimum block size")
    groups = defaultdict(lambda: defaultdict(list))
    for i, (n, o) in enumerate(zip(nominal, ordinal)):
        require(type(n) is str and n, "nominal key")
        integer(o, 0, 1000000, "ordinal level")
        groups[n][o].append(i)
    assigned, report = [None] * len(nominal), []
    for n in sorted(groups):
        chunks, levels, indices = [], [], []
        for o in sorted(groups[n]):
            levels.append(o)
            indices.extend(groups[n][o])
            if len(indices) >= minimum:
                chunks.append((levels, indices))
                levels, indices = [], []
        if indices:
            if chunks:
                chunks[-1][0].extend(levels)
                chunks[-1][1].extend(indices)
            else:
                chunks.append((levels, indices))
        for ls, ix in chunks:
            key = (n, tuple(ls))
            for i in ix:
                assigned[i] = key
            report.append({"key": key, "n": len(ix), "thin": len(ix) < minimum})
    require(all(s is not None for s in assigned), "lost pair")
    return tuple(assigned), tuple(report)


def availability_buckets(base, availability, *, parts=2):
    require(parts in (1, 2, 3), "bucket count")
    require(len(base) == len(availability) and len(base) > 0, "bucket lengths")
    groups = defaultdict(list)
    for i, (s, u) in enumerate(zip(base, availability)):
        require(0 <= u <= 1, "availability outside [0,1]")
        groups[s].append(i)
    result, report = [None] * len(base), []
    for s in sorted(groups, key=repr):
        ix = groups[s]
        values = sorted(availability[i] for i in ix)
        # Nearest-rank cutpoints; equality always stays in the lower bucket.
        cuts = sorted(set(values[(len(ix) * q + parts - 1) // parts - 1]
                          for q in range(1, parts)))
        counts = defaultdict(int)
        for i in ix:
            b = sum(availability[i] > c for c in cuts)
            result[i] = (s, b)
            counts[b] += 1
        report.append({"base": s, "cuts": tuple(cuts), "sizes": dict(counts),
                       "constant": len(set(values)) == 1,
                       "range": (values[0], values[-1])})
    return tuple(result), tuple(report)
