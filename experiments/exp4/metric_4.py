# experiments/exp4/metric_4.py
"""Experiment 4's metric layer (design §3.2, §3.3, dial d): pure numpy,
no torch, no I/O. Mutual k-NN alignment (Huh et al. 2024, App. A; the
released code's `mutual_knn` with topk 10 on normalised features) as a
deterministic function of activation bytes; the per-item overlap kept;
unbiased linear CKA (Song et al. 2012, as Huh's `unbiased_cka`) for S9;
2f's site family; depth-matched site pairing; the planted-structure
generator behind the committed calibration fixture.

`planted_pair` shares ONE random projection between its two outputs
(task-1 resolution 3): X and Y differ only in their independent noise
draw, so at signal 1 they are identical and at signal 0 they are
independent."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

EXP4 = Path(__file__).resolve().parent
if str(EXP4.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP4.parent.parent))

from experiments.exp2f import probe_2f  # noqa: E402

K_4 = 10
SITE_COUNT_PIN_4 = {7: 3, 13: 5, 17: 7, 25: 9, 33: 12, 37: 13}


def chance_4(n: int, k: int = K_4) -> float:
    """Expected mutual-k-NN overlap fraction between two INDEPENDENT
    rankings over n items: k / (n - 1)."""
    return k / (n - 1)


def sites_4(n_hidden: int) -> list:
    """The candidate depth family for a model with n_hidden layers:
    2f/2c's site family (every LAYER_STRIDE-th layer + the final layer,
    × 2 positions), collapsed to the sorted distinct layer indices."""
    return sorted({l for l, _ in probe_2f.site_family(int(n_hidden))})


def depth_pairs(sites_m, n_hidden_m, sites_q, n_hidden_q) -> list:
    """For each site h in sites_m, the site in sites_q whose relative
    depth h/(n_hidden_m-1) is closest to q/(n_hidden_q-1), ties broken
    to the SMALLER q. Returns a list the same length as sites_m."""
    out = []
    dm, dq = float(n_hidden_m - 1), float(n_hidden_q - 1)
    for h in sites_m:
        best = min(sites_q, key=lambda q: (abs(h / dm - q / dq), q))
        out.append(int(best))
    return out


def _unit_rows(X) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    if X.ndim != 2 or X.shape[0] < 2:
        raise ValueError(f"knn_sets: need a 2-D [n >= 2, d] array, got {X.shape}")
    norms = np.linalg.norm(X, axis=1)
    if not np.all(np.isfinite(X)) or np.any(norms == 0):
        raise ValueError("knn_sets: non-finite or zero rows")
    return X / norms[:, None]


def knn_sets(X, k: int = K_4) -> np.ndarray:
    """The k nearest neighbours (by cosine similarity, self excluded)
    of every row of X, as an ascending-sorted [n, k] uint16 array. Ties
    (equal similarity) break by ascending column index via a stable
    sort of -similarity. Deterministic: a pure function of X's bytes."""
    Xn = _unit_rows(X)
    n = Xn.shape[0]
    if not 1 <= k < n:
        raise ValueError(f"knn_sets: k {k} against n {n}")
    sims = Xn @ Xn.T
    np.fill_diagonal(sims, -np.inf)
    order = np.argsort(-sims, axis=1, kind="stable")[:, :k]
    order.sort(axis=1)
    if n > np.iinfo(np.uint16).max:
        raise ValueError("knn_sets: n exceeds uint16")
    return order.astype(np.uint16)


def overlap_counts(A, B) -> np.ndarray:
    """|A_i ∩ B_i| per row, as uint8 (0..k)."""
    A, B = np.asarray(A), np.asarray(B)
    if A.shape != B.shape or A.ndim != 2:
        raise ValueError(f"overlap_counts: shapes {A.shape} vs {B.shape}")
    out = np.zeros(A.shape[0], dtype=np.uint8)
    for i in range(A.shape[0]):
        out[i] = len(set(A[i].tolist()) & set(B[i].tolist()))
    return out


def mutual_knn_from_sets(A, B) -> dict:
    """The overlap fraction per item and its mean, from two [n, k]
    neighbour-set arrays (Huh et al.'s mutual_knn, precomputed sets)."""
    A = np.asarray(A)
    k = int(A.shape[1])
    per = overlap_counts(A, B).astype(np.float64) / k
    return {"per_item": per, "mean": float(per.mean()), "k": k, "n": int(A.shape[0])}


def _hsic_unbiased(K, L) -> float:
    n = K.shape[0]
    K = K.copy(); L = L.copy()
    np.fill_diagonal(K, 0.0); np.fill_diagonal(L, 0.0)
    ones = np.ones(n)
    t1 = float(np.sum(K * L))
    t2 = float(ones @ K @ ones) * float(ones @ L @ ones) / ((n - 1) * (n - 2))
    t3 = 2.0 * float(ones @ K @ L @ ones) / (n - 2)
    return (t1 + t2 - t3) / (n * (n - 3))


def linear_cka_unbiased(X, Y) -> float:
    """Unbiased linear CKA (Song et al. 2012; Huh et al.'s unbiased_cka)
    between two [n, d] activation matrices with the same n >= 4."""
    X = np.asarray(X, dtype=np.float64); Y = np.asarray(Y, dtype=np.float64)
    if X.shape[0] != Y.shape[0] or X.shape[0] < 4:
        raise ValueError(f"linear_cka_unbiased: rows {X.shape[0]} vs {Y.shape[0]} (need >= 4)")
    K, L = X @ X.T, Y @ Y.T
    num = _hsic_unbiased(K, L)
    den = np.sqrt(_hsic_unbiased(K, K) * _hsic_unbiased(L, L))
    if not np.isfinite(den) or den == 0:
        raise ValueError("linear_cka_unbiased: degenerate kernel")
    return float(num / den)


def planted_pair(n: int, d: int, signal: float, seed: int, d_latent: int = 8):
    """A synthetic pair (X, Y), float32 [n, d], sharing a d_latent-
    dimensional planted structure at strength `signal` in [0, 1] through
    ONE shared random projection A: X = s*(Z@A)/sqrt(d_latent) + (1-s)*N1,
    Y = s*(Z@A)/sqrt(d_latent) + (1-s)*N2. X and Y differ only in their
    independent noise draw — at signal 1 they are identical, at signal 0
    independent."""
    rng = np.random.default_rng(int(seed))
    Z = rng.standard_normal((n, d_latent))
    A = rng.standard_normal((d_latent, d))
    N1, N2 = rng.standard_normal((n, d)), rng.standard_normal((n, d))
    s = float(signal)
    base = s * (Z @ A) / np.sqrt(d_latent)
    X = base + (1.0 - s) * N1
    Y = base + (1.0 - s) * N2
    return X.astype(np.float32), Y.astype(np.float32)
