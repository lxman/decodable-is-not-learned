"""Matched-token Pythia size-ladder item-order analysis.

Tests whether committed small-model sampled output tails (`Pythia-1b` k=256 and
k=64, `Pythia-410m` k=256 and k=64, and cross-family `OLMo-2 1B` k=64), linear
probe margins (`probe_1b`, `probe_410m`), and wrong-answer emission priors
(`wrong_prior_1b`, `wrong_prior_olmo1b`) order which individual items resolve
across the larger Pythia parameter ladder (`1.4b, 2.8b, 6.9b, 12b`) at fixed
training tokens.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import csv
import datetime as dt
import hashlib
import importlib.abc
import importlib.machinery
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
RESULTS = HERE / "results"

SOURCE = "5154f8935dc79e478b0853cbe39a39d931f00177"
GIT_TIMEOUT_S = 30
TOKENS_PER_STEP = 2_097_152

SIZES = ("410m", "1b", "1.4b", "2.8b", "6.9b", "12b")
PREDICTOR_SIZES = ("410m", "1b")
OUTCOME_SIZES = ("1.4b", "2.8b", "6.9b", "12b")
NO28B_SIZES = ("1.4b", "6.9b", "12b")

STEPS = (1000, 2000, 4000, 5000, 6000, 8000, 16000, 32000, 100000, 143000)
SPINE_STEPS = (1000, 2000, 4000, 8000, 16000, 32000, 100000, 143000)
FINAL_STEP = 143000

N_ITEMS = 500
N_RUNGS = 34
MIN_OUTCOME_SIDE = 5
N_PERM = 10_000
N_BOOT = 1_000
PERM_SEED = 20261024
FAMILY_BOOT_B = 10_000
FAMILY_BOOT_SEED = 20261004

RCAP_PREDICTOR_ORDER = (
    "pythia_1b_k256",
    "olmo2_1b_k64",
    "pythia_1b_k64",
    "pythia_410m_k256",
    "pythia_410m_k64",
    "probe_1b",
    "probe_410m",
    "wrong_prior_1b",
    "wrong_prior_olmo1b",
)
RPRED11_PREDICTOR_ORDER = (
    "pythia_1b_k64",
    "pythia_410m_k64",
    "probe_1b",
    "probe_410m",
)

R_CAP = (
    "add3_mid",
    "add_base8",
    "antonym",
    "antonym6",
    "arith_next",
    "odd6",
    "sub3_mid",
    "sub4_mid",
    "sub_base8",
)
R_PRED11 = (
    "add3_mid",
    "add_base8",
    "antonym",
    "antonym6",
    "arith_next",
    "count_div13",
    "median5",
    "odd6",
    "sub3_mid",
    "sub4_mid",
    "sub_base8",
)

CODE_RELS = (
    "experiments/exp2c/__init__.py",
    "experiments/exp2c/harness.py",
    "experiments/exp2c/battery/__init__.py",
    "experiments/exp2c/battery/family_map.py",
    "experiments/exp2c/run/__init__.py",
    "experiments/exp2c/run/power_table.py",
    "experiments/exp2d/__init__.py",
    "experiments/exp2d/battery_2d.py",
    "experiments/exp2d/analyze_2d.py",
    "experiments/exp2d/stats_2d.py",
    "experiments/exp2g/__init__.py",
    "experiments/exp2g/battery_2g.py",
    "experiments/exp2g/checkpoints_2g.py",
    "experiments/exp2g/labels_2g.py",
    "experiments/exp2g/predictor_2g.py",
    "experiments/exp2g/stats_2g.py",
    "experiments/exp2g/strata_2g.py",
    "experiments/exp2g/analyze_2g.py",
    "experiments/exp2h/__init__.py",
    "experiments/exp2h/battery_2h.py",
    "experiments/exp2h/analyze_2h.py",
    "experiments/exp2i/__init__.py",
    "experiments/exp2i/battery_2i.py",
    "experiments/exp2j/__init__.py",
    "experiments/exp2j/functionals_2j.py",
    "experiments/exp2k/__init__.py",
    "experiments/exp2k/battery_2k.py",
    "experiments/exp3/__init__.py",
    "experiments/exp3/sampler.py",
    "experiments/exp3c/__init__.py",
    "experiments/exp3c/analyze_3c.py",
    "experiments/exp5/__init__.py",
    "experiments/exp5/battery_5.py",
)

STATIC_DATA_RELS = (
    "experiments/exp2d/results/verdict.json",
    "experiments/exp2g/results/predictor/predictor.json",
    "experiments/exp2g/results/predictor/predictor_sha256.txt",
    "experiments/exp2g/results/predictor/strata.json",
    "experiments/exp2i/results/predictor/predictor_2i.json",
    "experiments/exp5/checkpoints_5.json",
    "analyses/matched-token/results/counts.csv",
)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_path(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{path}: expected regular non-symlink file")
    return sha256_bytes(path.read_bytes())


class _PinnedFinder(importlib.abc.MetaPathFinder):
    def __init__(self, root: Path, allowed: set[str]):
        self.root = root.resolve()
        self.allowed = set(allowed)

    def find_spec(self, fullname: str, path=None, target=None):
        if fullname != "experiments" and not fullname.startswith("experiments."):
            return None
        parts = fullname.split(".")
        mod_rel = Path(*parts).with_suffix(".py")
        pkg_dir = self.root / Path(*parts)
        mod_file = self.root / mod_rel
        if mod_file.is_file():
            rel = mod_rel.as_posix()
            if rel not in self.allowed:
                raise ImportError(f"unpinned repository import refused: {rel}")
            return importlib.util.spec_from_file_location(fullname, mod_file)
        if pkg_dir.is_dir():
            init_py = pkg_dir / "__init__.py"
            if init_py.is_file():
                rel = init_py.relative_to(self.root).as_posix()
                if rel not in self.allowed:
                    raise ImportError(f"unpinned package __init__ refused: {rel}")
                return importlib.util.spec_from_file_location(
                    fullname,
                    init_py,
                    submodule_search_locations=[str(pkg_dir)],
                )
            spec = importlib.machinery.ModuleSpec(fullname, loader=None, is_package=True)
            spec.submodule_search_locations = [str(pkg_dir)]
            return spec
        raise ImportError(f"missing pinned module under {self.root}: {fullname}")


@contextmanager
def pinned_imports(root: Path, allowed_rels=CODE_RELS):
    finder = _PinnedFinder(root, set(allowed_rels))
    saved_modules = {
        k: v
        for k, v in sys.modules.items()
        if k == "experiments" or k.startswith("experiments.")
    }
    for k in list(saved_modules):
        sys.modules.pop(k, None)
    sys.meta_path.insert(0, finder)
    try:
        yield
    finally:
        if finder in sys.meta_path:
            sys.meta_path.remove(finder)
        for k in [
            m
            for m in list(sys.modules)
            if m == "experiments" or m.startswith("experiments.")
        ]:
            sys.modules.pop(k, None)
        sys.modules.update(saved_modules)


def _git_bytes(root: Path, args: list[str]) -> bytes:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            timeout=GIT_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError(
            f"git {' '.join(args)} timed out after {GIT_TIMEOUT_S}s"
        ) from exc
    if out.returncode != 0:
        err = out.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"git {' '.join(args)} failed: {err}")
    return out.stdout


class Bindings:
    """Verifies repository code and data files against pinned Git commit SOURCE."""

    def __init__(self, root: Path = REPO, source: str = SOURCE):
        self.root = Path(root).resolve()
        self.source = source
        self.expected_sha256: dict[str, str] = {}
        self.verified_files = 0
        self._load_tree()

    def _load_tree(self) -> None:
        cat = _git_bytes(self.root, ["cat-file", "-t", self.source]).decode().strip()
        if cat not in ("commit", "tag"):
            raise ValueError(f"source {self.source} is not a commit/tag ({cat})")
        raw = _git_bytes(
            self.root,
            [
                "ls-tree",
                "-r",
                "--full-tree",
                self.source,
                "--",
                "experiments",
                "analyses/matched-token",
            ],
        )
        blob_oids: dict[str, str] = {}
        for line in raw.decode("utf-8").splitlines():
            meta, rel = line.split("\t", 1)
            if rel.startswith("experiments/exp7/"):
                continue
            mode, kind, oid = meta.split(" ")
            if kind == "blob":
                if mode == "120000":
                    raise ValueError(f"symlink in source tree refused: {rel}")
                blob_oids[rel] = oid

        need_rels = set(CODE_RELS) | set(STATIC_DATA_RELS)
        for rel in blob_oids:
            if rel.startswith("experiments/") and rel.endswith(".py"):
                need_rels.add(rel)
            elif (
                rel.startswith("experiments/exp2c/battery/")
                and rel.endswith(".json")
            ):
                need_rels.add(rel)
            elif (
                rel.startswith("experiments/exp2d/results/main/")
                and (rel.endswith(".draws.jsonl.gz") or rel.endswith(".json"))
            ):
                need_rels.add(rel)
            elif (
                rel.startswith("experiments/exp2k/results/k256/")
                and (rel.endswith(".draws.jsonl.gz") or rel.endswith(".json"))
            ):
                need_rels.add(rel)
            elif (
                rel.startswith("experiments/exp2i/results/predictor/olmo1b/")
                and (rel.endswith(".draws.jsonl.gz") or rel.endswith(".json"))
            ):
                need_rels.add(rel)
            elif (
                rel.startswith("experiments/exp5/results/units/")
                and rel.endswith(".json")
            ):
                need_rels.add(rel)

        missing = sorted(need_rels - set(blob_oids))
        if missing:
            raise ValueError(f"missing blobs in {self.source}: {missing[:5]}")

        batch_in = "".join(f"{blob_oids[r]}\n" for r in sorted(need_rels)).encode(
            "ascii"
        )
        try:
            proc = subprocess.run(
                ["git", "cat-file", "--batch"],
                cwd=self.root,
                input=batch_in,
                capture_output=True,
                timeout=GIT_TIMEOUT_S * 2,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ValueError("git cat-file --batch timed out") from exc
        if proc.returncode != 0:
            raise ValueError("git cat-file --batch failed")

        buf = proc.stdout
        pos = 0
        for rel in sorted(need_rels):
            nl = buf.index(b"\n", pos)
            header = buf[pos:nl].decode("ascii").split(" ")
            oid, kind, size_s = header[0], header[1], int(header[2])
            if oid != blob_oids[rel] or kind != "blob":
                raise ValueError(f"unexpected batch header for {rel}: {header}")
            start = nl + 1
            end = start + size_s
            content = buf[start:end]
            if len(content) != size_s or buf[end : end + 1] != b"\n":
                raise ValueError(f"truncated batch content for {rel}")
            pos = end + 1
            self.expected_sha256[rel] = sha256_bytes(content)

    def verify_rel(self, rel: str) -> str:
        if rel not in self.expected_sha256:
            raise ValueError(f"unpinned relative path: {rel}")
        path = self.root / rel
        for parent in [path, *path.parents]:
            if parent == self.root:
                break
            if parent.is_symlink():
                raise ValueError(f"symlink component refused: {parent}")
        got = sha256_path(path)
        want = self.expected_sha256[rel]
        if got != want:
            raise ValueError(f"sha256 drift on {rel}: got {got}, expected {want}")
        self.verified_files += 1
        return got

    def verify_all(self) -> dict[str, str]:
        self.verified_files = 0
        out = {}
        for rel in sorted(self.expected_sha256):
            out[rel] = self.verify_rel(rel)
        return out


# --------------------------------------------------------- pure math / outcomes


def build_outcomes_for_rung(
    bits_by_step_size: dict[int, dict[str, list[int]]],
    *,
    outcome_sizes: tuple[str, ...] = OUTCOME_SIZES,
    no28b_sizes: tuple[str, ...] = NO28B_SIZES,
    predictor_sizes: tuple[str, ...] = PREDICTOR_SIZES,
    steps: tuple[int, ...] = STEPS,
    spine_steps: tuple[int, ...] = SPINE_STEPS,
    final_step: int = FINAL_STEP,
    n_items: int = N_ITEMS,
) -> dict:
    """Computes all planned item-level outcome vectors for a single rung from
    `bits_by_step_size[step][size] -> list[int]` of length `n_items`.
    """
    n_out = len(outcome_sizes)

    # 1. Primary size-ladder outcome at final_step: sum across outcome_sizes (0..4)
    y_143k_count = []
    # 2. Earliest-size emergence rank at final_step:
    #    1.4b -> 4, 2.8b -> 3, 6.9b -> 2, 12b -> 1, none -> 0
    y_143k_first_size = []
    # 3. 2.8b-excluded ladder at final_step: sum across (1.4b, 6.9b, 12b) (0..3)
    y_143k_no28b = []
    # 4. Individual larger sizes at final_step
    y_by_size = {s: [int(b) for b in bits_by_step_size[final_step][s]] for s in outcome_sizes}
    # 5. Greedy-zero indicator at final_step: 1 iff all predictor_sizes are 0 at final_step
    greedy_zero_keep = []
    # 6. Per-checkpoint 4-size sum y_step[t] (0..4)
    y_by_step = {t: [] for t in steps}
    # 7. 10-checkpoint x 4-size grid sum (0..40) and 8-checkpoint spine sum (0..32)
    y_grid_40 = []
    y_spine_32 = []

    for i in range(n_items):
        final_hits = [
            idx
            for idx, s in enumerate(outcome_sizes)
            if int(bits_by_step_size[final_step][s][i]) == 1
        ]
        y_143k_count.append(len(final_hits))
        y_143k_first_size.append((n_out - final_hits[0]) if final_hits else 0)
        y_143k_no28b.append(
            sum(int(bits_by_step_size[final_step][s][i]) for s in no28b_sizes)
        )
        gz = all(int(bits_by_step_size[final_step][ps][i]) == 0 for ps in predictor_sizes)
        greedy_zero_keep.append(bool(gz))

        grid_tot = 0
        spine_tot = 0
        for t in steps:
            c_t = sum(int(bits_by_step_size[t][s][i]) for s in outcome_sizes)
            y_by_step[t].append(c_t)
            grid_tot += c_t
            if t in spine_steps:
                spine_tot += c_t
        y_grid_40.append(grid_tot)
        y_spine_32.append(spine_tot)

    def _pack(vec: list[int], keep_mask: list[bool] | None = None) -> dict:
        if keep_mask is None:
            n_pos = sum(1 for v in vec if v > 0)
            return {"y": vec, "n_pos": int(n_pos), "n_items": len(vec)}
        filt = [v for v, k in zip(vec, keep_mask) if k]
        n_pos = sum(1 for v in filt if v > 0)
        return {
            "y": vec,
            "n_pos": int(n_pos),
            "n_items": len(filt),
            "keep": list(keep_mask),
        }

    return {
        "y_143k_count": _pack(y_143k_count),
        "y_143k_first_size": _pack(y_143k_first_size),
        "y_143k_no28b": _pack(y_143k_no28b),
        "y_143k_greedy_zero": _pack(y_143k_count, greedy_zero_keep),
        "by_size_143k": {s: _pack(y_by_size[s]) for s in outcome_sizes},
        "by_step": {t: _pack(y_by_step[t]) for t in steps},
        "y_grid_40": _pack(y_grid_40),
        "y_spine_32": _pack(y_spine_32),
        "greedy_zero_n": int(sum(greedy_zero_keep)),
        "counts_143k": {
            s: int(sum(bits_by_step_size[final_step][s]))
            for s in (*predictor_sizes, *outcome_sizes)
        },
    }


def composite_strata_zero_cut(base_strata: dict, cond_scores: dict, rungs) -> dict:
    """Conditions base difficulty strata on 1{cond > 0} (the Exp 2h/2i zero cut)."""
    return {
        r: {
            "strata": [
                f"{s}|{int(float(c) > 0.0)}"
                for s, c in zip(base_strata[r]["strata"], cond_scores[r])
            ]
        }
        for r in rungs
    }


def composite_strata_median_cut(base_strata: dict, cond_scores: dict, rungs) -> dict:
    """Conditions base difficulty strata on 1{cond > median(cond)}."""
    out = {}
    for r in rungs:
        arr = np.asarray(cond_scores[r], dtype=np.float64)
        med = float(np.median(arr))
        out[r] = {
            "strata": [
                f"{s}|{int(float(v) > med)}"
                for s, v in zip(base_strata[r]["strata"], arr)
            ]
        }
    return out


def family_bootstrap_t(
    per_rung_d: dict[str, float],
    family_of: dict[str, str],
    *,
    n_boot: int = FAMILY_BOOT_B,
    seed: int = FAMILY_BOOT_SEED,
) -> dict:
    """Cluster-bootstraps families with replacement (`n_boot` draws, `seed`).

    Returns point estimates and 95% percentile CIs for both:
    - `rung_mean`: equal-rung average over the sampled families' rungs
    - `family_mean`: equal-family average over the sampled families
    """
    rungs = [r for r, v in sorted(per_rung_d.items()) if v is not None and not math.isnan(v)]
    if not rungs:
        return {
            "n_rungs": 0,
            "n_families": 0,
            "rung_mean": None,
            "rung_mean_ci": [None, None],
            "family_mean": None,
            "family_mean_ci": [None, None],
        }
    fams: dict[str, list[float]] = {}
    for r in rungs:
        fams.setdefault(family_of[r], []).append(float(per_rung_d[r]))
    fam_names = sorted(fams)
    k_fams = len(fam_names)
    point_rung = float(np.mean([per_rung_d[r] for r in rungs]))
    point_fam = float(np.mean([np.mean(fams[f]) for f in fam_names]))

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, k_fams, size=(n_boot, k_fams))
    fam_means = np.array([float(np.mean(fams[f])) for f in fam_names], dtype=np.float64)
    fam_S = np.array([float(np.sum(fams[f])) for f in fam_names], dtype=np.float64)
    fam_C = np.array([len(fams[f]) for f in fam_names], dtype=np.float64)

    boot_fam = np.mean(fam_means[idx], axis=1)
    boot_rung = np.sum(fam_S[idx], axis=1) / np.sum(fam_C[idx], axis=1)

    return {
        "n_rungs": len(rungs),
        "n_families": k_fams,
        "families": {f: len(fams[f]) for f in fam_names},
        "rung_mean": point_rung,
        "rung_mean_ci": [
            float(np.quantile(boot_rung, 0.025)),
            float(np.quantile(boot_rung, 0.975)),
        ],
        "family_mean": point_fam,
        "family_mean_ci": [
            float(np.quantile(boot_fam, 0.025)),
            float(np.quantile(boot_fam, 0.975)),
        ],
    }


def evaluate_predictor_set(
    scores_by_rung: dict[str, list[float]],
    out_by_rung: dict[str, dict],
    strata_by_rung: dict[str, dict],
    rungs: tuple[str, ...],
    family_of: dict[str, str],
    st_mod,
    *,
    n_perm: int = N_PERM,
    perm_seed: int = PERM_SEED,
    n_boot: int = N_BOOT,
) -> dict:
    """Runs stratified and unstratified Somers' D + permutation + item bootstrap +
    family bootstrap across `rungs`, gracefully dropping any rung that is
    n_pos-thin (<5 positive or <5 zero items) or has no informative within-stratum
    outcome/predictor pair.
    """
    cells = []
    raw_cells = []
    thin = []
    dropped_degenerate = []

    for r in rungs:
        rec = out_by_rung[r]
        keep = rec.get("keep")
        y_full = np.asarray(rec["y"], dtype=np.float64)
        x_full = np.asarray(scores_by_rung[r], dtype=np.float64)
        s_full = list(strata_by_rung[r]["strata"])
        if keep is not None:
            mask = np.asarray(keep, dtype=bool)
            y = y_full[mask]
            x = x_full[mask]
            s = [sv for sv, kv in zip(s_full, keep) if kv]
        else:
            y = y_full
            x = x_full
            s = s_full

        n_pos = int(np.sum(y > 0))
        n_neg = int(len(y) - n_pos)
        if n_pos < MIN_OUTCOME_SIDE or n_neg < MIN_OUTCOME_SIDE:
            thin.append(r)
            continue

        # Check whether within-stratum Somers' D has at least one informative pair
        # AND whether predictor varies in at least one stratum with informative outcome pairs.
        strat_res = st_mod.somers_d_within(x, y, s)
        raw_res = st_mod.somers_d_within(x, y, ["all"] * len(y))
        if strat_res["n_pairs"] == 0 or math.isnan(strat_res["d"]):
            dropped_degenerate.append(r)
            continue

        # Also check whether predictor has variance inside at least one stratum that has outcome pairs
        has_var = False
        by_s: dict[str, list[int]] = {}
        for idx_i, sv in enumerate(s):
            by_s.setdefault(sv, []).append(idx_i)
        for idxs in by_s.values():
            if len(idxs) >= 2:
                ys = y[idxs]
                xs = x[idxs]
                if np.min(ys) != np.max(ys) and np.min(xs) != np.max(xs):
                    has_var = True
                    break
        if not has_var:
            dropped_degenerate.append(r)
            continue

        cells.append({"rung": r, "x": x, "y": y, "strata": s})
        raw_cells.append({"rung": r, "x": x, "y": y, "strata": ["all"] * len(y)})

    if not cells:
        return {
            "defined": False,
            "eligible": [],
            "thin": thin,
            "dropped_degenerate": dropped_degenerate,
            "stratified": {"T": None, "p": 1.0, "null_mean": None, "null_sd": None, "n_perm": 0},
            "raw": {"T": None, "p": 1.0, "null_mean": None, "null_sd": None, "n_perm": 0},
            "pooled_d": None,
            "raw_pooled_d": None,
            "family_bootstrap": family_bootstrap_t({}, family_of, n_boot=n_boot, seed=FAMILY_BOOT_SEED),
            "per_rung": {},
        }

    strat_perm = st_mod.perm_test(cells, n_perm=n_perm, seed=perm_seed)
    raw_perm = st_mod.perm_test(raw_cells, n_perm=n_perm, seed=perm_seed)
    pooled = st_mod.pooled_d(cells)
    raw_pooled = st_mod.pooled_d(raw_cells)

    per_rung = {}
    per_rung_d_map = {}
    for c, rc in zip(cells, raw_cells):
        r = c["rung"]
        ci = st_mod.bootstrap_d(c["x"], c["y"], c["strata"], n_boot=n_boot, seed=perm_seed)
        d_val = float(strat_perm["per_rung"][r]["d"])
        raw_d_val = float(raw_perm["per_rung"][r]["d"])
        per_rung_d_map[r] = d_val
        per_rung[r] = {
            "d": d_val,
            "n_pairs": int(strat_perm["per_rung"][r]["n_pairs"]),
            "n_strata_used": int(len(st_mod.precompute(c["y"], c["strata"]))),
            "ci_lo": float(ci["lo"]),
            "ci_hi": float(ci["hi"]),
            "raw_d": raw_d_val,
            "raw_n_pairs": int(raw_perm["per_rung"][r]["n_pairs"]),
            "n_items": int(len(c["y"])),
            "n_pos": int(np.sum(c["y"] > 0)),
        }

    fam_boot = family_bootstrap_t(per_rung_d_map, family_of)

    return {
        "defined": True,
        "eligible": [c["rung"] for c in cells],
        "thin": thin,
        "dropped_degenerate": dropped_degenerate,
        "stratified": {
            "T": float(strat_perm["T"]),
            "p": float(strat_perm["p"]),
            "n_ge": int(strat_perm["n_ge"]),
            "n_perm": int(strat_perm["n_perm"]),
            "null_mean": float(strat_perm["null_mean"]),
            "null_sd": float(strat_perm["null_sd"]),
        },
        "raw": {
            "T": float(raw_perm["T"]),
            "p": float(raw_perm["p"]),
            "n_ge": int(raw_perm["n_ge"]),
            "n_perm": int(raw_perm["n_perm"]),
            "null_mean": float(raw_perm["null_mean"]),
            "null_sd": float(raw_perm["null_sd"]),
        },
        "pooled_d": float(pooled),
        "raw_pooled_d": float(raw_pooled),
        "family_bootstrap": fam_boot,
        "per_rung": per_rung,
    }


def evaluate_all_rungs_unstratified(
    scores_by_rung: dict[str, list[float]],
    out_by_rung: dict[str, dict],
    all_rungs: tuple[str, ...],
    family_of: dict[str, str],
    st_mod,
) -> dict:
    """Computes unstratified Somers' D on all 34 rungs and summarizes across:
    - all informative rungs (0 < n_pos < 500 and predictor non-constant)
    - rungs with n_pos >= 20 (and n_neg >= 20)
    """
    rows = {}
    info_d = {}
    ge20_d = {}
    for r in all_rungs:
        y = np.asarray(out_by_rung[r]["y"], dtype=np.float64)
        x = np.asarray(scores_by_rung[r], dtype=np.float64)
        n_pos = int(np.sum(y > 0))
        n_neg = int(len(y) - n_pos)
        x_pos = int(np.sum(x > 0))
        res = st_mod.somers_d_within(x, y, ["all"] * len(y))
        d_val = None if (res["n_pairs"] == 0 or math.isnan(res["d"])) else float(res["d"])
        has_x_var = bool(np.min(x) != np.max(x))
        informative = bool(d_val is not None and has_x_var)
        ge20 = bool(informative and n_pos >= 20 and n_neg >= 20)
        if informative:
            info_d[r] = d_val
        if ge20:
            ge20_d[r] = d_val
        rows[r] = {
            "rung": r,
            "family": family_of[r],
            "n_pos": n_pos,
            "n_neg": n_neg,
            "x_pos": x_pos,
            "n_pairs": int(res["n_pairs"]),
            "raw_d": d_val,
            "informative": informative,
            "ge20": ge20,
        }
    return {
        "per_rung": rows,
        "informative_summary": family_bootstrap_t(info_d, family_of),
        "ge20_summary": family_bootstrap_t(ge20_d, family_of),
    }


# --------------------------------------------------------- data loading


def load_and_verify_all_inputs(bindings: Bindings):
    """Loads and byte-verifies all Exp 5 units and all committed predictors."""
    file_hashes = bindings.verify_all()
    py_rels = {r for r in bindings.expected_sha256 if r.endswith(".py")}

    with pinned_imports(bindings.root, allowed_rels=py_rels):
        from experiments.exp2c.battery import family_map as fm
        from experiments.exp2d import analyze_2d as a2d
        from experiments.exp2d import battery_2d as bt
        from experiments.exp2g import battery_2g as bg
        from experiments.exp2g import predictor_2g as pr
        from experiments.exp2g import stats_2g as st
        from experiments.exp2g import strata_2g as sg
        from experiments.exp2h import battery_2h as bh
        from experiments.exp2i import battery_2i as bi
        from experiments.exp2j import functionals_2j as fn2j
        from experiments.exp2k import battery_2k as bk

        battery = bg.load_battery()
        verify_fn = a2d.load_verify()
        all_rungs = tuple(bt.RUNGS)
        family_of = dict(bt.FAMILY_OF)

        if tuple(sorted(R_PRED11)) != tuple(sorted(bg.PREDICTOR_RUNGS)):
            raise ValueError("R_PRED11 does not match bg.PREDICTOR_RUNGS")

        # 1. Load and re-verify all 60 Exp 5 units x 34 rungs x 500 items
        # Also cross-check against analyses/matched-token/results/counts.csv
        mt_counts_path = bindings.root / "analyses/matched-token/results/counts.csv"
        mt_counts: dict[tuple[str, int, str], int] = {}
        with mt_counts_path.open("r", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                mt_counts[(row["size"], int(row["step"]), row["rung"])] = int(
                    row["correct"]
                )

        bits_by_rung: dict[str, dict[int, dict[str, list[int]]]] = {
            r: {t: {} for t in STEPS} for r in all_rungs
        }
        for s in SIZES:
            for t in STEPS:
                unit_dir = (
                    bindings.root
                    / "experiments"
                    / "exp5"
                    / "results"
                    / "units"
                    / s
                    / f"step{t}"
                )
                for r in all_rungs:
                    rec_path = unit_dir / f"{r}.json"
                    rec = json.loads(rec_path.read_text(encoding="utf-8"))
                    cap = battery[r]
                    if rec.get("size") != s or int(rec.get("step", -1)) != t or rec.get("rung") != r:
                        raise ValueError(f"unit header mismatch: {rec_path}")
                    if rec.get("items_sha256") != cap["items_sha256"]:
                        raise ValueError(f"items_sha256 mismatch: {rec_path}")
                    bits = [int(b) for b in rec["bits"]]
                    conts = rec["continuations"]
                    if len(bits) != N_ITEMS or len(conts) != N_ITEMS:
                        raise ValueError(f"length != {N_ITEMS}: {rec_path}")
                    rederived = [
                        int(bool(verify_fn(c, it["answer"], cap["answer_type"])))
                        for c, it in zip(conts, cap["eval_items"])
                    ]
                    if rederived != bits:
                        raise ValueError(f"bit re-derivation mismatch: {rec_path}")
                    c_sum = int(sum(bits))
                    if c_sum != int(rec["correct"]) or c_sum != mt_counts[(s, t, r)]:
                        raise ValueError(f"count mismatch against matched-token CSV: {rec_path}")
                    bits_by_rung[r][t][s] = bits

        # 2. Load 2g predictor & difficulty strata
        pred2g = pr.load_predictor(
            bindings.root / "experiments/exp2g/results/predictor/predictor.json",
            sha_pin=bh.PREDICTOR_2G_SHA,
        )
        strata = sg.from_json(pred2g["strata"])
        sg.check_strata_pins(strata)

        probe_1b = {
            r: [float(v) for v in pr.cell_scores(pred2g, r, "1b", "trained", rule="cv")]
            for r in R_PRED11
        }
        probe_410m = {
            r: [float(v) for v in pr.cell_scores(pred2g, r, "410m", "trained", rule="cv")]
            for r in R_PRED11
        }

        # 3. Load Pythia k=64 counts on all 34 rungs (exp2d main tier)
        pythia_1b_k64 = bh.sampler_counts("1b", all_rungs)
        pythia_410m_k64 = bh.sampler_counts("410m", all_rungs)

        # 4. Load Pythia k=256 counts on R_CAP (exp2k) and verify against k256 records + 2d seed0
        pythia_1b_k256 = {}
        pythia_410m_k256 = {}
        for r in R_CAP:
            cap = battery[r]
            for s, target in (("1b", pythia_1b_k256), ("410m", pythia_410m_k256)):
                rec_2k = json.loads(
                    bk.tier_record_path(bindings.root / "experiments/exp2k", s, r).read_text(
                        encoding="utf-8"
                    )
                )
                bad_2k = bk.tier_record_failures_2k(rec_2k, size=s, rung=r, cap=cap)
                if bad_2k:
                    raise ValueError(f"2k record failure on {s}/{r}: {bad_2k}")
                rows_2k = bk.read_rows_2k(
                    bk.tier_draws_path(bindings.root / "experiments/exp2k", s, r)
                )
                if bk.tallies_2k(rows_2k, cap, verify_fn) != rec_2k["per_seed_tallies"]:
                    raise ValueError(f"2k tallies mismatch on {s}/{r}")
                bits_2k = bk.bits_2k(rows_2k, cap, verify_fn)
                counts_2k = bk.counts_at_k(bits_2k, 256)
                # Check seed-0 block matches 2d k=64 counts
                seed0_counts = bk.counts_at_k(bits_2k, 64)
                ref_64 = pythia_1b_k64[r] if s == "1b" else pythia_410m_k64[r]
                if seed0_counts != [int(c) for c in ref_64]:
                    raise ValueError(f"2k seed-0 block mismatch against 2d on {s}/{r}")
                target[r] = [float(c) for c in counts_2k]

        # 5. Load OLMo-2 1B k=64 counts on R_CAP (exp2i)
        olmo_raw = bi.sampler_counts_olmo(
            R_CAP,
            root=bindings.root / "experiments/exp2i",
            battery=battery,
            verify_fn=verify_fn,
        )
        olmo2_1b_k64 = {r: [float(c) for c in olmo_raw[r]] for r in R_CAP}

        # 6. Compute wrong-answer emission priors on R_CAP (exp2j functionals)
        wrong_prior_1b = {}
        wrong_prior_olmo1b = {}
        for r in R_CAP:
            cap = battery[r]
            rows_1b = fn2j.draw_rows_2d("1b", r)
            rows_olmo = fn2j.draw_rows_2i(bindings.root / "experiments/exp2i", r)
            wp_1b = fn2j.wrong_target_propensity(rows_1b, cap)
            wp_olmo = fn2j.wrong_target_propensity(rows_olmo, cap)
            wrong_prior_1b[r] = [float(v) for v in wp_1b]
            wrong_prior_olmo1b[r] = [float(v) for v in wp_olmo]

        predictors = {
            "pythia_1b_k256": pythia_1b_k256,
            "pythia_410m_k256": pythia_410m_k256,
            "olmo2_1b_k64": olmo2_1b_k64,
            "pythia_1b_k64": {r: [float(c) for c in pythia_1b_k64[r]] for r in all_rungs},
            "pythia_410m_k64": {r: [float(c) for c in pythia_410m_k64[r]] for r in all_rungs},
            "probe_1b": probe_1b,
            "probe_410m": probe_410m,
            "wrong_prior_1b": wrong_prior_1b,
            "wrong_prior_olmo1b": wrong_prior_olmo1b,
        }

        return {
            "file_hashes": file_hashes,
            "py_rels": py_rels,
            "all_rungs": all_rungs,
            "family_of": family_of,
            "bits_by_rung": bits_by_rung,
            "strata": strata,
            "predictors": predictors,
        }


# --------------------------------------------------------- full analysis


def run_analysis(loaded: dict, *, n_perm: int = N_PERM, n_boot: int = N_BOOT) -> dict:
    with pinned_imports(REPO, allowed_rels=loaded["py_rels"]):
        from experiments.exp2g import stats_2g as st

        all_rungs = loaded["all_rungs"]
        family_of = loaded["family_of"]
        bits_by_rung = loaded["bits_by_rung"]
        strata = loaded["strata"]
        preds = loaded["predictors"]

        # Build outcomes for all 34 rungs
        outcomes_by_rung = {
            r: build_outcomes_for_rung(bits_by_rung[r]) for r in all_rungs
        }

        def _out_slice(rungs, key, subkey=None):
            if subkey is None:
                return {r: outcomes_by_rung[r][key] for r in rungs}
            return {r: outcomes_by_rung[r][key][subkey] for r in rungs}

        # 1. Primary y_143k_count on R_CAP (9 rungs)
        rcap_out_143k = _out_slice(R_CAP, "y_143k_count")
        rcap_predictors = (
            "pythia_1b_k256",
            "olmo2_1b_k64",
            "pythia_1b_k64",
            "pythia_410m_k256",
            "pythia_410m_k64",
            "probe_1b",
            "probe_410m",
            "wrong_prior_1b",
            "wrong_prior_olmo1b",
        )
        primary_rcap = {}
        for pname in rcap_predictors:
            primary_rcap[pname] = evaluate_predictor_set(
                preds[pname],
                rcap_out_143k,
                strata,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )

        # 2. Primary y_143k_count on R_PRED11 (11 rungs)
        rpred11_out_143k = _out_slice(R_PRED11, "y_143k_count")
        rpred11_predictors = (
            "pythia_1b_k64",
            "pythia_410m_k64",
            "probe_1b",
            "probe_410m",
        )
        primary_rpred11 = {}
        for pname in rpred11_predictors:
            primary_rpred11[pname] = evaluate_predictor_set(
                preds[pname],
                rpred11_out_143k,
                strata,
                R_PRED11,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )

        # 3. Earliest-size emergence rank y_143k_first_size on R_CAP and R_PRED11
        rcap_first = _out_slice(R_CAP, "y_143k_first_size")
        rpred11_first = _out_slice(R_PRED11, "y_143k_first_size")
        first_size_rcap = {
            pname: evaluate_predictor_set(
                preds[pname],
                rcap_first,
                strata,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )
            for pname in ("pythia_1b_k256", "olmo2_1b_k64", "pythia_1b_k64", "pythia_410m_k256", "probe_1b")
        }
        first_size_rpred11 = {
            pname: evaluate_predictor_set(
                preds[pname],
                rpred11_first,
                strata,
                R_PRED11,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )
            for pname in ("pythia_1b_k64", "pythia_410m_k64", "probe_1b")
        }

        # 4. Greedy-zero restriction at step143000 (410m == 0 and 1b == 0)
        rcap_gz = _out_slice(R_CAP, "y_143k_greedy_zero")
        rpred11_gz = _out_slice(R_PRED11, "y_143k_greedy_zero")
        greedy_zero_rcap = {
            pname: evaluate_predictor_set(
                preds[pname],
                rcap_gz,
                strata,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )
            for pname in ("pythia_1b_k256", "olmo2_1b_k64", "pythia_1b_k64", "pythia_410m_k256", "probe_1b")
        }
        greedy_zero_rpred11 = {
            pname: evaluate_predictor_set(
                preds[pname],
                rpred11_gz,
                strata,
                R_PRED11,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )
            for pname in ("pythia_1b_k64", "pythia_410m_k64", "probe_1b")
        }

        # 5. Individual larger sizes at step143000 (1.4b, 2.8b, 6.9b, 12b) and 2.8b-excluded ladder
        by_size_rcap = {}
        by_size_rpred11 = {}
        for s in OUTCOME_SIZES:
            out_s_cap = _out_slice(R_CAP, "by_size_143k", s)
            by_size_rcap[s] = {
                pname: evaluate_predictor_set(
                    preds[pname],
                    out_s_cap,
                    strata,
                    R_CAP,
                    family_of,
                    st,
                    n_perm=n_perm,
                    n_boot=n_boot,
                )
                for pname in ("pythia_1b_k256", "olmo2_1b_k64", "pythia_1b_k64", "probe_1b")
            }
            out_s_11 = _out_slice(R_PRED11, "by_size_143k", s)
            by_size_rpred11[s] = {
                pname: evaluate_predictor_set(
                    preds[pname],
                    out_s_11,
                    strata,
                    R_PRED11,
                    family_of,
                    st,
                    n_perm=n_perm,
                    n_boot=n_boot,
                )
                for pname in ("pythia_1b_k64", "probe_1b")
            }

        rcap_no28b = _out_slice(R_CAP, "y_143k_no28b")
        rpred11_no28b = _out_slice(R_PRED11, "y_143k_no28b")
        no28b_rcap = {
            pname: evaluate_predictor_set(
                preds[pname],
                rcap_no28b,
                strata,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )
            for pname in ("pythia_1b_k256", "olmo2_1b_k64", "pythia_1b_k64", "pythia_410m_k256", "probe_1b")
        }
        no28b_rpred11 = {
            pname: evaluate_predictor_set(
                preds[pname],
                rpred11_no28b,
                strata,
                R_PRED11,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )
            for pname in ("pythia_1b_k64", "pythia_410m_k64", "probe_1b")
        }

        # 6. Per-checkpoint size-ladder curve (all 10 steps) + 40-cell grid + 32-cell spine
        checkpoint_curve = {}
        for t in STEPS:
            out_t_cap = _out_slice(R_CAP, "by_step", t)
            out_t_11 = _out_slice(R_PRED11, "by_step", t)
            checkpoint_curve[str(int(t))] = {
                "step": int(t),
                "tokens": int(t * TOKENS_PER_STEP),
                "rcap": {
                    pname: evaluate_predictor_set(
                        preds[pname],
                        out_t_cap,
                        strata,
                        R_CAP,
                        family_of,
                        st,
                        n_perm=n_perm,
                        n_boot=n_boot,
                    )
                    for pname in ("pythia_1b_k256", "olmo2_1b_k64", "pythia_1b_k64", "probe_1b")
                },
                "rpred11": {
                    pname: evaluate_predictor_set(
                        preds[pname],
                        out_t_11,
                        strata,
                        R_PRED11,
                        family_of,
                        st,
                        n_perm=n_perm,
                        n_boot=n_boot,
                    )
                    for pname in ("pythia_1b_k64", "probe_1b")
                },
            }

        grid_40_rcap = {
            pname: evaluate_predictor_set(
                preds[pname],
                _out_slice(R_CAP, "y_grid_40"),
                strata,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )
            for pname in ("pythia_1b_k256", "olmo2_1b_k64", "pythia_1b_k64", "pythia_410m_k256", "probe_1b")
        }
        grid_40_rpred11 = {
            pname: evaluate_predictor_set(
                preds[pname],
                _out_slice(R_PRED11, "y_grid_40"),
                strata,
                R_PRED11,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )
            for pname in ("pythia_1b_k64", "pythia_410m_k64", "probe_1b")
        }
        spine_32_rcap = {
            pname: evaluate_predictor_set(
                preds[pname],
                _out_slice(R_CAP, "y_spine_32"),
                strata,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )
            for pname in ("pythia_1b_k256", "olmo2_1b_k64", "pythia_1b_k64", "pythia_410m_k256", "probe_1b")
        }
        spine_32_rpred11 = {
            pname: evaluate_predictor_set(
                preds[pname],
                _out_slice(R_PRED11, "y_spine_32"),
                strata,
                R_PRED11,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            )
            for pname in ("pythia_1b_k64", "pythia_410m_k64", "probe_1b")
        }

        # 7. Composite-stratum conditioning at step143000
        #    a) probe_1b | pythia_1b_k256 (zero cut, R_CAP)
        #    b) pythia_1b_k256 | probe_1b (median cut, R_CAP)
        #    c) probe_1b | pythia_1b_k64 (zero cut, R_PRED11)
        #    d) pythia_1b_k64 | probe_1b (median cut, R_PRED11)
        #    e) pythia_1b_k256 | olmo2_1b_k64 (zero cut and median cut, R_CAP)
        #    f) olmo2_1b_k64 | pythia_1b_k256 (zero cut and median cut, R_CAP)
        strata_k256_zero = composite_strata_zero_cut(strata, preds["pythia_1b_k256"], R_CAP)
        strata_k256_med = composite_strata_median_cut(strata, preds["pythia_1b_k256"], R_CAP)
        strata_probe_cap_med = composite_strata_median_cut(strata, preds["probe_1b"], R_CAP)
        strata_k64_11_zero = composite_strata_zero_cut(strata, preds["pythia_1b_k64"], R_PRED11)
        strata_probe_11_med = composite_strata_median_cut(strata, preds["probe_1b"], R_PRED11)
        strata_olmo_zero = composite_strata_zero_cut(strata, preds["olmo2_1b_k64"], R_CAP)
        strata_olmo_med = composite_strata_median_cut(strata, preds["olmo2_1b_k64"], R_CAP)

        conditioning_143k = {
            "probe_1b_beyond_pythia_1b_k256_rcap": evaluate_predictor_set(
                preds["probe_1b"],
                rcap_out_143k,
                strata_k256_zero,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            ),
            "pythia_1b_k256_beyond_probe_1b_rcap": evaluate_predictor_set(
                preds["pythia_1b_k256"],
                rcap_out_143k,
                strata_probe_cap_med,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            ),
            "probe_1b_beyond_pythia_1b_k64_rpred11": evaluate_predictor_set(
                preds["probe_1b"],
                rpred11_out_143k,
                strata_k64_11_zero,
                R_PRED11,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            ),
            "pythia_1b_k64_beyond_probe_1b_rpred11": evaluate_predictor_set(
                preds["pythia_1b_k64"],
                rpred11_out_143k,
                strata_probe_11_med,
                R_PRED11,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            ),
            "pythia_1b_k256_beyond_olmo2_1b_k64_zero_rcap": evaluate_predictor_set(
                preds["pythia_1b_k256"],
                rcap_out_143k,
                strata_olmo_zero,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            ),
            "pythia_1b_k256_beyond_olmo2_1b_k64_median_rcap": evaluate_predictor_set(
                preds["pythia_1b_k256"],
                rcap_out_143k,
                strata_olmo_med,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            ),
            "olmo2_1b_k64_beyond_pythia_1b_k256_zero_rcap": evaluate_predictor_set(
                preds["olmo2_1b_k64"],
                rcap_out_143k,
                strata_k256_zero,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            ),
            "olmo2_1b_k64_beyond_pythia_1b_k256_median_rcap": evaluate_predictor_set(
                preds["olmo2_1b_k64"],
                rcap_out_143k,
                strata_k256_med,
                R_CAP,
                family_of,
                st,
                n_perm=n_perm,
                n_boot=n_boot,
            ),
        }

        # 8. Unstratified 34-rung reading at step143000
        all34_out_143k = _out_slice(all_rungs, "y_143k_count")
        all_rungs_143k = {
            "pythia_1b_k64": evaluate_all_rungs_unstratified(
                preds["pythia_1b_k64"], all34_out_143k, all_rungs, family_of, st
            ),
            "pythia_410m_k64": evaluate_all_rungs_unstratified(
                preds["pythia_410m_k64"], all34_out_143k, all_rungs, family_of, st
            ),
        }

        # Rung metadata summary on R_PRED11
        rung_meta_143k = {}
        for r in R_PRED11:
            ro = outcomes_by_rung[r]
            rung_meta_143k[r] = {
                "rung": r,
                "family": family_of[r],
                "in_r_cap": r in R_CAP,
                "n_pos_143k": int(ro["y_143k_count"]["n_pos"]),
                "greedy_zero_n": int(ro["greedy_zero_n"]),
                "greedy_zero_n_pos": int(ro["y_143k_greedy_zero"]["n_pos"]),
                "counts_143k": dict(ro["counts_143k"]),
            }

        return {
            "source_commit": SOURCE,
            "parameters": {
                "sizes": list(SIZES),
                "predictor_sizes": list(PREDICTOR_SIZES),
                "outcome_sizes": list(OUTCOME_SIZES),
                "no28b_sizes": list(NO28B_SIZES),
                "steps": list(STEPS),
                "spine_steps": list(SPINE_STEPS),
                "final_step": FINAL_STEP,
                "tokens_per_step": TOKENS_PER_STEP,
                "r_cap": list(R_CAP),
                "r_pred11": list(R_PRED11),
                "n_items": N_ITEMS,
                "n_perm": n_perm,
                "perm_seed": PERM_SEED,
                "n_boot": n_boot,
                "family_boot_b": FAMILY_BOOT_B,
                "family_boot_seed": FAMILY_BOOT_SEED,
            },
            "rung_meta_143k": rung_meta_143k,
            "primary_rcap_143k": primary_rcap,
            "primary_rpred11_143k": primary_rpred11,
            "first_size_rcap_143k": first_size_rcap,
            "first_size_rpred11_143k": first_size_rpred11,
            "greedy_zero_rcap_143k": greedy_zero_rcap,
            "greedy_zero_rpred11_143k": greedy_zero_rpred11,
            "by_size_rcap_143k": by_size_rcap,
            "by_size_rpred11_143k": by_size_rpred11,
            "no28b_rcap_143k": no28b_rcap,
            "no28b_rpred11_143k": no28b_rpred11,
            "checkpoint_curve": checkpoint_curve,
            "grid_40_rcap": grid_40_rcap,
            "grid_40_rpred11": grid_40_rpred11,
            "spine_32_rcap": spine_32_rcap,
            "spine_32_rpred11": spine_32_rpred11,
            "conditioning_143k": conditioning_143k,
            "all_rungs_143k": all_rungs_143k,
        }


# --------------------------------------------------------- writers & report


def _fmt(val, digits: int = 3, signed: bool = True) -> str:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "—"
    fmt = f"{{:{'+' if signed else ''}.{digits}f}}"
    return fmt.format(float(val))


def _fmt_p(p) -> str:
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return "—"
    p = float(p)
    if p < 0.0002:
        return f"{p:.4f} (1/{int(round(1.0 / p))})"
    return f"{p:.4f}"


def write_per_rung_csv(path: Path, summary: dict) -> None:
    fieldnames = [
        "rung_set",
        "outcome",
        "predictor",
        "rung",
        "family",
        "n_items",
        "n_pos",
        "d",
        "ci_lo",
        "ci_hi",
        "n_pairs",
        "n_strata_used",
        "raw_d",
        "raw_n_pairs",
    ]
    rows = []

    def _collect_block(rung_set_label: str, outcome_label: str, block: dict):
        for pname, res in block.items():
            for r, pr_row in res.get("per_rung", {}).items():
                rows.append(
                    {
                        "rung_set": rung_set_label,
                        "outcome": outcome_label,
                        "predictor": pname,
                        "rung": r,
                        "family": summary["rung_meta_143k"][r]["family"],
                        "n_items": pr_row["n_items"],
                        "n_pos": pr_row["n_pos"],
                        "d": f"{pr_row['d']:.6f}",
                        "ci_lo": f"{pr_row['ci_lo']:.6f}",
                        "ci_hi": f"{pr_row['ci_hi']:.6f}",
                        "n_pairs": pr_row["n_pairs"],
                        "n_strata_used": pr_row["n_strata_used"],
                        "raw_d": f"{pr_row['raw_d']:.6f}",
                        "raw_n_pairs": pr_row["raw_n_pairs"],
                    }
                )

    _collect_block("R_CAP", "y_143k_count", summary["primary_rcap_143k"])
    _collect_block("R_PRED11", "y_143k_count", summary["primary_rpred11_143k"])
    _collect_block("R_CAP", "y_143k_first_size", summary["first_size_rcap_143k"])
    _collect_block("R_PRED11", "y_143k_first_size", summary["first_size_rpred11_143k"])
    _collect_block("R_CAP", "y_143k_greedy_zero", summary["greedy_zero_rcap_143k"])
    _collect_block("R_PRED11", "y_143k_greedy_zero", summary["greedy_zero_rpred11_143k"])
    _collect_block("R_CAP", "y_143k_no28b", summary["no28b_rcap_143k"])
    _collect_block("R_PRED11", "y_143k_no28b", summary["no28b_rpred11_143k"])
    _collect_block("R_CAP", "y_grid_40", summary["grid_40_rcap"])
    _collect_block("R_PRED11", "y_grid_40", summary["grid_40_rpred11"])
    for s in OUTCOME_SIZES:
        _collect_block("R_CAP", f"size_{s}_143k", summary["by_size_rcap_143k"][s])
        _collect_block("R_PRED11", f"size_{s}_143k", summary["by_size_rpred11_143k"][s])

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_checkpoint_curve_csv(path: Path, summary: dict) -> None:
    fieldnames = [
        "step",
        "tokens",
        "rung_set",
        "predictor",
        "n_eligible",
        "T_strat",
        "p_strat",
        "T_raw",
        "pooled_d",
        "fam_boot_lo",
        "fam_boot_hi",
    ]
    rows = []
    for t in STEPS:
        rec = summary["checkpoint_curve"][str(int(t))]
        for rset_key, rset_label in (("rcap", "R_CAP"), ("rpred11", "R_PRED11")):
            for pname, pres in rec[rset_key].items():
                fb = pres["family_bootstrap"]
                rows.append(
                    {
                        "step": int(t),
                        "tokens": int(rec["tokens"]),
                        "rung_set": rset_label,
                        "predictor": pname,
                        "n_eligible": len(pres["eligible"]),
                        "T_strat": "" if pres["stratified"]["T"] is None else f"{pres['stratified']['T']:.6f}",
                        "p_strat": f"{pres['stratified']['p']:.6f}",
                        "T_raw": "" if pres["raw"]["T"] is None else f"{pres['raw']['T']:.6f}",
                        "pooled_d": "" if pres["pooled_d"] is None else f"{pres['pooled_d']:.6f}",
                        "fam_boot_lo": "" if fb["rung_mean_ci"][0] is None else f"{fb['rung_mean_ci'][0]:.6f}",
                        "fam_boot_hi": "" if fb["rung_mean_ci"][1] is None else f"{fb['rung_mean_ci'][1]:.6f}",
                    }
                )
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_all_rungs_143k_csv(path: Path, summary: dict) -> None:
    fieldnames = [
        "rung",
        "family",
        "n_pos_143k",
        "n_neg_143k",
        "pythia_1b_k64_xpos",
        "pythia_1b_k64_d",
        "pythia_1b_k64_informative",
        "pythia_410m_k64_xpos",
        "pythia_410m_k64_d",
        "pythia_410m_k64_informative",
        "ge20",
    ]
    rows = []
    r1b = summary["all_rungs_143k"]["pythia_1b_k64"]["per_rung"]
    r410 = summary["all_rungs_143k"]["pythia_410m_k64"]["per_rung"]
    for r in sorted(r1b):
        a = r1b[r]
        b = r410[r]
        rows.append(
            {
                "rung": r,
                "family": a["family"],
                "n_pos_143k": a["n_pos"],
                "n_neg_143k": a["n_neg"],
                "pythia_1b_k64_xpos": a["x_pos"],
                "pythia_1b_k64_d": "" if a["raw_d"] is None else f"{a['raw_d']:.6f}",
                "pythia_1b_k64_informative": int(bool(a["informative"])),
                "pythia_410m_k64_xpos": b["x_pos"],
                "pythia_410m_k64_d": "" if b["raw_d"] is None else f"{b['raw_d']:.6f}",
                "pythia_410m_k64_informative": int(bool(b["informative"])),
                "ge20": int(bool(a["ge20"])),
            }
        )
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_report(summary: dict) -> str:
    lines = []
    lines.append("# Matched-Token Pythia Size-Ladder Item-Order Report")
    lines.append("")
    lines.append(
        f"- **Source tree pinned and verified:** `{summary['source_commit']}` (`exp7-closed`)"
    )
    lines.append(
        "- **Outcome ladder:** `OUTCOME_SIZES = ('1.4b', '2.8b', '6.9b', '12b')` at matched training checkpoints (`410m` and `1b` excluded from all outcome vectors so predictor and outcome never share a model size)."
    )
    lines.append(
        f"- **Permutations:** `{summary['parameters']['n_perm']}` (`seed = {summary['parameters']['perm_seed']}`); per-rung bootstrap: `{summary['parameters']['n_boot']}`; family-cluster bootstrap: `{summary['parameters']['family_boot_b']}` (`seed = {summary['parameters']['family_boot_seed']}`)."
    )
    lines.append("")

    # Table 1: Primary y_143k_count on R_CAP (9 rungs) and R_PRED11 (11 rungs)
    lines.append("## 1. Primary Size-Ladder Outcome at `step143000` (`y_143k_count` across `1.4b, 2.8b, 6.9b, 12b`)")
    lines.append("")
    lines.append("| Rung set | Predictor | Eligible rungs | Stratified $T$ | Perm $p$ | Null SD | Family-boot 95% CI | Equal-family mean | Unstratified $T$ | Pooled $D$ |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    for rset_label, block, p_order in (
        ("`R_CAP` (9)", summary["primary_rcap_143k"], RCAP_PREDICTOR_ORDER),
        ("`R_PRED11` (11)", summary["primary_rpred11_143k"], RPRED11_PREDICTOR_ORDER),
    ):
        for pname in p_order:
            res = block[pname]
            fb = res["family_bootstrap"]
            ci_str = f"[{_fmt(fb['rung_mean_ci'][0])}, {_fmt(fb['rung_mean_ci'][1])}]"
            lines.append(
                f"| {rset_label} | `{pname}` | {len(res['eligible'])} | "
                f"**{_fmt(res['stratified']['T'])}** | {_fmt_p(res['stratified']['p'])} | "
                f"{_fmt(res['stratified']['null_sd'], signed=False)} | {ci_str} | "
                f"{_fmt(fb['family_mean'])} | {_fmt(res['raw']['T'])} | {_fmt(res['pooled_d'])} |"
            )
    lines.append("")

    # Table 2: Per-rung breakdown at step143000 on R_PRED11
    lines.append("## 2. Per-Rung Stratified Somers' $D$ at `step143000` (`y_143k_count`)")
    lines.append("")
    lines.append("| Rung | Family | $n_{\\text{pos}}$ (`1.4b..12b`) | Greedy-0 ($n$ / $n_{\\text{pos}}$) | `pythia_1b_k256` $D$ [95% CI] | `olmo2_1b_k64` $D$ [95% CI] | `pythia_1b_k64` $D$ [95% CI] | `pythia_410m_k256` $D$ | `probe_1b` $D$ | `wrong_prior_1b` $D$ |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    p_cap = summary["primary_rcap_143k"]
    p_11 = summary["primary_rpred11_143k"]
    for r in R_PRED11:
        meta = summary["rung_meta_143k"][r]
        fam = meta["family"]
        npos = meta["n_pos_143k"]
        gz_str = f"{meta['greedy_zero_n']} / {meta['greedy_zero_n_pos']}"

        def _cell(block, pname, with_ci=False):
            if pname not in block or r not in block[pname]["per_rung"]:
                return "—"
            pr_r = block[pname]["per_rung"][r]
            if with_ci:
                return f"{_fmt(pr_r['d'])} [{_fmt(pr_r['ci_lo'])}, {_fmt(pr_r['ci_hi'])}]"
            return _fmt(pr_r["d"])

        c_k256 = _cell(p_cap, "pythia_1b_k256", with_ci=True) if r in R_CAP else "—"
        c_olmo = _cell(p_cap, "olmo2_1b_k64", with_ci=True) if r in R_CAP else "—"
        c_k64 = _cell(p_11, "pythia_1b_k64", with_ci=True)
        c_410_256 = _cell(p_cap, "pythia_410m_k256") if r in R_CAP else "—"
        c_probe = _cell(p_11, "probe_1b")
        c_wp = _cell(p_cap, "wrong_prior_1b") if r in R_CAP else "—"
        lines.append(
            f"| `{r}` | `{fam}` | {npos} | {gz_str} | {c_k256} | {c_olmo} | {c_k64} | {c_410_256} | {c_probe} | {c_wp} |"
        )
    lines.append("")

    # Table 3: Alternative outcomes at step143000 & across the grid
    lines.append("## 3. Alternative Size-Ladder Outcomes (`first_size`, Greedy-Zero Restriction, `2.8b`-Excluded, and Multi-Checkpoint Grid)")
    lines.append("")
    lines.append("| Outcome | Rung set | `pythia_1b_k256` $T$ ($p$) | `olmo2_1b_k64` $T$ ($p$) | `pythia_1b_k64` $T$ ($p$) | `pythia_410m_k256` $T$ ($p$) | `probe_1b` $T$ ($p$) |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")

    alt_rows = [
        ("Primary count `y_143k_count` (`1.4b..12b`)", "`R_CAP` (9)", summary["primary_rcap_143k"]),
        ("Primary count `y_143k_count` (`1.4b..12b`)", "`R_PRED11` (11)", summary["primary_rpred11_143k"]),
        ("Earliest size `y_143k_first_size` (`1.4b=4..12b=1`)", "`R_CAP` (9)", summary["first_size_rcap_143k"]),
        ("Earliest size `y_143k_first_size` (`1.4b=4..12b=1`)", "`R_PRED11` (11)", summary["first_size_rpred11_143k"]),
        ("Greedy-zero `410m=0 & 1b=0` at `step143000`", "`R_CAP`", summary["greedy_zero_rcap_143k"]),
        ("Greedy-zero `410m=0 & 1b=0` at `step143000`", "`R_PRED11`", summary["greedy_zero_rpred11_143k"]),
        ("`2.8b`-excluded ladder (`1.4b, 6.9b, 12b`)", "`R_CAP` (9)", summary["no28b_rcap_143k"]),
        ("`2.8b`-excluded ladder (`1.4b, 6.9b, 12b`)", "`R_PRED11` (11)", summary["no28b_rpred11_143k"]),
        ("10-checkpoint × 4-size grid sum (`y_grid_40`)", "`R_CAP` (9)", summary["grid_40_rcap"]),
        ("10-checkpoint × 4-size grid sum (`y_grid_40`)", "`R_PRED11` (11)", summary["grid_40_rpred11"]),
        ("8-checkpoint spine × 4-size sum (`y_spine_32`)", "`R_CAP` (9)", summary["spine_32_rcap"]),
        ("8-checkpoint spine × 4-size sum (`y_spine_32`)", "`R_PRED11` (11)", summary["spine_32_rpred11"]),
    ]
    for label, rset, block in alt_rows:
        def _t_cell(pname):
            if pname not in block:
                return "—"
            res = block[pname]
            n_el = len(res["eligible"])
            return f"{_fmt(res['stratified']['T'])} (p={res['stratified']['p']:.4f}, m={n_el})"

        lines.append(
            f"| {label} | {rset} | {_t_cell('pythia_1b_k256')} | {_t_cell('olmo2_1b_k64')} | "
            f"{_t_cell('pythia_1b_k64')} | {_t_cell('pythia_410m_k256')} | {_t_cell('probe_1b')} |"
        )
    lines.append("")

    # Table 4: Individual larger sizes at step143000
    lines.append("## 4. Individual Larger Model Sizes at `step143000` (`1.4b`, `2.8b`, `6.9b`, `12b`)")
    lines.append("")
    lines.append("| Outcome size at `step143000` | Rung set | Eligible rungs | `pythia_1b_k256` $T$ ($p$) | `olmo2_1b_k64` $T$ ($p$) | `pythia_1b_k64` $T$ ($p$) | `probe_1b` $T$ ($p$) |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for s in OUTCOME_SIZES:
        b_cap = summary["by_size_rcap_143k"][s]
        n_el_cap = len(b_cap["pythia_1b_k64"]["eligible"])
        lines.append(
            f"| `{s}` | `R_CAP` | {n_el_cap} | "
            f"{_fmt(b_cap['pythia_1b_k256']['stratified']['T'])} ({b_cap['pythia_1b_k256']['stratified']['p']:.4f}) | "
            f"{_fmt(b_cap['olmo2_1b_k64']['stratified']['T'])} ({b_cap['olmo2_1b_k64']['stratified']['p']:.4f}) | "
            f"{_fmt(b_cap['pythia_1b_k64']['stratified']['T'])} ({b_cap['pythia_1b_k64']['stratified']['p']:.4f}) | "
            f"{_fmt(b_cap['probe_1b']['stratified']['T'])} ({b_cap['probe_1b']['stratified']['p']:.4f}) |"
        )
        b_11 = summary["by_size_rpred11_143k"][s]
        n_el_11 = len(b_11["pythia_1b_k64"]["eligible"])
        lines.append(
            f"| `{s}` | `R_PRED11` | {n_el_11} | — | — | "
            f"{_fmt(b_11['pythia_1b_k64']['stratified']['T'])} ({b_11['pythia_1b_k64']['stratified']['p']:.4f}) | "
            f"{_fmt(b_11['probe_1b']['stratified']['T'])} ({b_11['probe_1b']['stratified']['p']:.4f}) |"
        )
    lines.append("")

    # Table 5: Per-checkpoint size-ladder curve across the 10 shared checkpoints
    lines.append("## 5. Size-Ladder Item Concordance Across All 10 Shared Checkpoints")
    lines.append("")
    lines.append("| Step | Tokens (B) | `R_CAP` $m$ | `pythia_1b_k256` $T$ | `olmo2_1b_k64` $T$ | `pythia_1b_k64` $T$ (`R_CAP`) | `probe_1b` $T$ (`R_CAP`) | `R_PRED11` $m$ | `pythia_1b_k64` $T$ (`R_PRED11`) | `probe_1b` $T$ (`R_PRED11`) |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for t in STEPS:
        rec = summary["checkpoint_curve"][str(int(t))]
        tok_b = rec["tokens"] / 1e9
        rc = rec["rcap"]
        r11 = rec["rpred11"]
        m_cap = len(rc["pythia_1b_k64"]["eligible"])
        m_11 = len(r11["pythia_1b_k64"]["eligible"])
        lines.append(
            f"| `{t}` | {tok_b:.3f} | {m_cap} | "
            f"{_fmt(rc['pythia_1b_k256']['stratified']['T'])} | "
            f"{_fmt(rc['olmo2_1b_k64']['stratified']['T'])} | "
            f"{_fmt(rc['pythia_1b_k64']['stratified']['T'])} | "
            f"{_fmt(rc['probe_1b']['stratified']['T'])} | "
            f"{m_11} | "
            f"{_fmt(r11['pythia_1b_k64']['stratified']['T'])} | "
            f"{_fmt(r11['probe_1b']['stratified']['T'])} |"
        )
    lines.append("")

    # Table 6: Composite-stratum conditioning
    lines.append("## 6. Composite-Stratum Conditioning at `step143000` (`y_143k_count`)")
    lines.append("")
    lines.append("| Conditioning test | Rung set | Eligible rungs | Stratified $T$ | Perm $p$ | Family-boot 95% CI |")
    lines.append("|---|---|---:|---:|---:|---:|")
    cond_rows = [
        ("`probe_1b | pythia_1b_k256 > 0` (probe beyond sampler)", "`R_CAP`", "probe_1b_beyond_pythia_1b_k256_rcap"),
        ("`pythia_1b_k256 | probe_1b > median` (sampler beyond probe)", "`R_CAP`", "pythia_1b_k256_beyond_probe_1b_rcap"),
        ("`probe_1b | pythia_1b_k64 > 0` (probe beyond sampler)", "`R_PRED11`", "probe_1b_beyond_pythia_1b_k64_rpred11"),
        ("`pythia_1b_k64 | probe_1b > median` (sampler beyond probe)", "`R_PRED11`", "pythia_1b_k64_beyond_probe_1b_rpred11"),
        ("`pythia_1b_k256 | olmo2_1b_k64 > 0` (lineage beyond cross-family, zero cut)", "`R_CAP`", "pythia_1b_k256_beyond_olmo2_1b_k64_zero_rcap"),
        ("`pythia_1b_k256 | olmo2_1b_k64 > median` (lineage beyond cross-family, median cut)", "`R_CAP`", "pythia_1b_k256_beyond_olmo2_1b_k64_median_rcap"),
        ("`olmo2_1b_k64 | pythia_1b_k256 > 0` (cross-family beyond lineage, zero cut)", "`R_CAP`", "olmo2_1b_k64_beyond_pythia_1b_k256_zero_rcap"),
        ("`olmo2_1b_k64 | pythia_1b_k256 > median` (cross-family beyond lineage, median cut)", "`R_CAP`", "olmo2_1b_k64_beyond_pythia_1b_k256_median_rcap"),
    ]
    for label, rset, key in cond_rows:
        res = summary["conditioning_143k"][key]
        fb = res["family_bootstrap"]
        ci_str = f"[{_fmt(fb['rung_mean_ci'][0])}, {_fmt(fb['rung_mean_ci'][1])}]"
        lines.append(
            f"| {label} | {rset} | {len(res['eligible'])} | "
            f"**{_fmt(res['stratified']['T'])}** | {_fmt_p(res['stratified']['p'])} | {ci_str} |"
        )
    lines.append("")

    # Table 7: All 34 rungs unstratified summary
    lines.append("## 7. Unstratified 34-Rung Battery Summary at `step143000` (`y_143k_count`)")
    lines.append("")
    lines.append("| Predictor | Subset | Rungs ($m$) | Families ($G$) | Equal-rung mean $D$ [95% family-boot CI] | Equal-family mean $D$ [95% family-boot CI] |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for pname in ("pythia_1b_k64", "pythia_410m_k64"):
        for sub_key, sub_label in (
            ("informative_summary", "All informative rungs ($0 < n_{\\text{pos}} < 500$, non-constant $x$)"),
            ("ge20_summary", "Rungs with $n_{\\text{pos}} \\ge 20$ and $n_{\\text{neg}} \\ge 20$"),
        ):
            fb = summary["all_rungs_143k"][pname][sub_key]
            r_ci = f"{_fmt(fb['rung_mean'])} [{_fmt(fb['rung_mean_ci'][0])}, {_fmt(fb['rung_mean_ci'][1])}]"
            f_ci = f"{_fmt(fb['family_mean'])} [{_fmt(fb['family_mean_ci'][0])}, {_fmt(fb['family_mean_ci'][1])}]"
            lines.append(
                f"| `{pname}` | {sub_label} | {fb['n_rungs']} | {fb['n_families']} | {r_ci} | {f_ci} |"
            )
    lines.append("")
    return "\n".join(lines) + "\n"


def write_results_atomic(results_dir: Path, summary: dict, file_hashes: dict[str, str]) -> None:
    if results_dir.exists():
        raise FileExistsError(
            f"refusing to overwrite existing results directory: {results_dir}"
        )
    parent = results_dir.parent
    tmp_dir = Path(tempfile.mkdtemp(prefix=".tmp_results_", dir=parent))
    try:
        summary_path = tmp_dir / "summary.json"
        per_rung_path = tmp_dir / "per_rung.csv"
        curve_path = tmp_dir / "checkpoint_curve.csv"
        all34_path = tmp_dir / "all_rungs_143k.csv"
        report_path = tmp_dir / "REPORT.md"
        prov_path = tmp_dir / "provenance.json"

        summary_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        write_per_rung_csv(per_rung_path, summary)
        write_checkpoint_curve_csv(curve_path, summary)
        write_all_rungs_143k_csv(all34_path, summary)
        report_path.write_text(render_report(summary), encoding="utf-8")

        outputs_sha = {
            p.name: sha256_path(p)
            for p in (summary_path, per_rung_path, curve_path, all34_path, report_path)
        }
        prov = {
            "source_commit": SOURCE,
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "numpy_version": np.__version__,
            "verified_file_count": len(file_hashes),
            "input_files_sha256_digest": sha256_bytes(
                json.dumps(file_hashes, sort_keys=True).encode("utf-8")
            ),
            "outputs_sha256": outputs_sha,
        }
        prov_path.write_text(
            json.dumps(prov, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp_dir, results_dir)
    except Exception:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Verify all pinned code/data files and re-derive all bits without computing concordance or writing results.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS,
        help="Output results directory (must not exist).",
    )
    args = parser.parse_args(argv)

    bindings = Bindings(REPO, SOURCE)
    loaded = load_and_verify_all_inputs(bindings)
    if args.validate_only:
        bindings.verify_all()
        print(
            f"[matched-token-item-order] validate-only OK: verified {bindings.verified_files} files against {SOURCE}, "
            f"re-derived 60x34x500 = 1,020,000 Exp 5 bits and all predictor streams."
        )
        return 0

    if args.results_dir.exists():
        raise FileExistsError(
            f"refusing to run: {args.results_dir} already exists (write-once policy)"
        )

    summary = run_analysis(loaded)
    # Re-verify all input files at exit before committing results to disk
    file_hashes_after = bindings.verify_all()
    if file_hashes_after != loaded["file_hashes"]:
        raise RuntimeError("input file hashes changed during analysis run")

    write_results_atomic(args.results_dir, summary, file_hashes_after)
    print(f"[matched-token-item-order] wrote results to {args.results_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
