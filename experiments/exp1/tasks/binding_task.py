"""Phase-A task: compositional binding via in-context associative recall.

Design doc §2 (staged build): "Phase A -- own simple task (pipeline debug). A minimal
compositional-binding task with a percolation threshold we can compute in closed form.
Cheap; single size, single seed. Its only job is to shake out the three signature
functions end-to-end before the expensive runs."

SCOPE (also in PROGRESS.md): Phase A is pipeline-grade, NOT part of the scored truth
table. Its transition is the in-context-retrieval (induction) circuit forming over
training -- sharp on the argmax curve, with a smooth precursor the probe can read
early, which is exactly what exercises S1/S2/S3. The credibility-grade percolation
task is Phase B (Lubana). The closed-form threshold below is the Erdos-Renyi bipartite
giant-component threshold of the key->value association graph; for the debug run we
sit ABOVE it so the task is learnable.

Sequence format, length n_ctx = 2*n_pairs + 2:
    k1 v1 k2 v2 ... km vm  QUERY  kq        target (next token) = the value bound to kq
Keys and values are disjoint token ranges; QUERY is a single marker token. The value
bound to kq is present in context, so the capability is in-context retrieval; the
graph constrains which (key, value) pairs are legal.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import torch


@dataclass
class BindingTaskConfig:
    n_keys: int = 16
    n_values: int = 16
    edge_prob: float = 0.6      # kept above the giant-component threshold for the debug run
    n_pairs: int = 6            # (key, value) pairs shown in context per example
    seed: int = 0

    @property
    def n_ctx(self) -> int:
        return 2 * self.n_pairs + 2

    @property
    def vocab_size(self) -> int:
        # keys | values | QUERY marker
        return self.n_keys + self.n_values + 1

    @property
    def query_token(self) -> int:
        return self.n_keys + self.n_values  # last id

    def key_token(self, k: int) -> int:
        return k

    def value_token(self, v: int) -> int:
        return self.n_keys + v


class BindingTask:
    """Associative-recall dataset generator with a graph-constrained legal-pair set."""

    def __init__(self, cfg: BindingTaskConfig):
        self.cfg = cfg
        rng = np.random.default_rng(cfg.seed)
        # Bipartite Erdos-Renyi graph keys x values.
        self.adj = rng.random((cfg.n_keys, cfg.n_values)) < cfg.edge_prob
        # Ensure every key has >= 1 legal value so examples are always constructible.
        for k in range(cfg.n_keys):
            if not self.adj[k].any():
                self.adj[k, rng.integers(cfg.n_values)] = True
        self._legal_values = [np.flatnonzero(self.adj[k]) for k in range(cfg.n_keys)]

    def percolation_threshold(self) -> float:
        """Closed-form Erdos-Renyi bipartite giant-component threshold.

        For a random bipartite graph on n_keys x n_values with edge prob p, a giant
        component appears at p_c = 1 / sqrt((n_keys - 1) * (n_values - 1)). Below p_c
        the association graph is fragmented into isolated components.
        """
        return 1.0 / math.sqrt((self.cfg.n_keys - 1) * (self.cfg.n_values - 1))

    def make_dataset(self, n: int, seed: int):
        """Return (input_ids[N, n_ctx] long, value_labels[N] long, target_tokens[N] long).

        value_labels are the value CLASS (0..n_values-1) for the probe; target_tokens
        are the vocab id of the correct next token for verification.
        """
        cfg = self.cfg
        rng = np.random.default_rng(seed)
        ids = np.empty((n, cfg.n_ctx), dtype=np.int64)
        value_labels = np.empty(n, dtype=np.int64)
        for i in range(n):
            keys = rng.permutation(cfg.n_keys)[: cfg.n_pairs]
            vals = np.array([rng.choice(self._legal_values[k]) for k in keys])
            seq = []
            for k, v in zip(keys, vals):
                seq.append(cfg.key_token(int(k)))
                seq.append(cfg.value_token(int(v)))
            q = rng.integers(cfg.n_pairs)  # query one of the shown keys
            seq.append(cfg.query_token)
            seq.append(cfg.key_token(int(keys[q])))
            ids[i] = seq
            value_labels[i] = int(vals[q])
        target_tokens = value_labels + cfg.n_keys
        return (
            torch.from_numpy(ids),
            torch.from_numpy(value_labels),
            torch.from_numpy(target_tokens),
        )

    @property
    def chance(self) -> float:
        return 1.0 / self.cfg.n_values

    def value_class_of_token(self, token: int) -> int:
        """Inverse of value_token: map a predicted vocab id back to a value class.

        Returns -1 if the token is not in the value range (a malformed prediction).
        """
        v = token - self.cfg.n_keys
        return int(v) if 0 <= v < self.cfg.n_values else -1
