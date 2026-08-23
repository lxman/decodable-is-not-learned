# Decodable Is Not Learned — supporting record

Public supporting record for the paper "Decodable Is Not Learned:
Untrained-Weights Controls and Basis-Starved Splits for Linear
Probing" (Michael Jordan). This is a path-filtered extraction of the
private working repository, preserving full commit history, authorship
dates, and ordering for everything the paper relies on: the frozen
preregistration documents, the experiments' code, campaign ledgers,
all committed probe fits (480 for Experiment 2, 770 for Experiment 2b,
and Experiment 2c's 220 untrained-gate fits), every raw sampled draw
from the generation experiments, the frozen reports, verdicts and
retrospectives, and the paper source with the scripts that generate
its figures, Table 1, and Appendix A.

## What is here

- **Experiments 1, 1b, 1c** (added 2026-08-23) — the synthetic
  calibration of the three-signature instrument, reported in the
  companion essay rather than the paper: small transformers trained
  from scratch on a Lubana-style formal language (percolation, no
  structure below threshold by construction) and a modular-arithmetic
  grokking task (latent structure before the transition). Experiment 1
  closed FAIL on an S1 criterion later found to compare raw probe
  accuracy across incommensurable class counts; Experiment 1b re-tested
  the probe leg under an untrained-twin floor and closed PASS (grokking
  9/10, Lubana above threshold 10/10, below 0/10); Experiment 1c swept
  sub-critical graph density and closed FAIL with 0 of 320 trained and
  0 of 480 untrained sites firing, declared underpowered in advance.
  These records live on a separately filtered line merged into this
  history (see PROVENANCE.md); their code is self-contained under
  `experiments/exp1*`.
- **Experiments 2, 2b, 2c** — the probing-hygiene arc the paper is
  about: standard splits and what an untrained network decodes; the
  basis-starved re-run; the screened battery and its inclusion-time
  untrained gate (the paper's Section 7).
- **Experiment 2d** — the probe ladder's prediction re-tested with the
  sampling instrument on Experiment 2c's battery and known outcome:
  a model-free format floor applied to both sides, a pilot-driven
  power declaration (underpowered in advance), gate 1 on the
  production path, and a FAIL read as "not detected at this
  resolution".
- **Experiment 2e** — Experiment 2d's committed draws re-read with the
  format floor as a covariate instead of a threshold (analysis-only,
  zero model contact): a FAIL at a point estimate of .61, which
  settles that 2d's null was not its threshold's.
- **Experiment 2f** — ladder order on the two rungs Experiment 2c's
  probe had read as silent: one label per rung read by probe,
  sampling and argmax on the same weights and items (a LADDER — the
  probe reads the answer's digit in every cell where the generators
  do not; the earlier silence was the label and the split).
- **Experiments 3a, 3b, 3, 3c, 3d, 3e** — the successor generation arc the
  paper's Section 6 draws its calibration lessons from: a verdict that
  crashed on a valueless input (3a), the same-weights probe/emission
  dissociation (3b), sampling elicitation (3), staged deepening (3c),
  item-grain rank prediction (3d, whose power table mis-specified
  its alternative's shape — the sixth lesson), and the shortcut test
  that closed 3d's named alternative (3e, whose freeze found that an
  exclusion rule's conservative direction is test-relative — the
  seventh lesson).

Every experiment whose record ships here carries both its
preregistration and its closeout tag:
`exp1-analysis-frozen` (Experiment 1 predates the `-preregistered` /
`-closed` convention; its closeout is the 2026-07-14 commit that
recorded `experiments/exp1/results/analysis_verdict.txt`),
`exp1b-preregistered` / `exp1b-closed`,
`exp1c-preregistered` / `exp1c-closed` (plus `exp1c-stage-a`, the
power declaration made in advance — the one interim stage tag carried
here; see PROVENANCE.md),
`exp2-preregistered` / `exp2-closed`,
`exp2b-preregistered` / `exp2b-closed`,
`exp2c-preregistered` / `exp2c-closed`,
`exp2d-preregistered` / `exp2d-closed`,
`exp2e-preregistered` / `exp2e-closed`,
`exp2f-preregistered` / `exp2f-closed`,
`exp3a-preregistered` / `exp3a-closed`,
`exp3b-preregistered` / `exp3b-closed`,
`exp3-preregistered` / `exp3-closed`,
`exp3c-preregistered` / `exp3c-closed`,
`exp3d-preregistered` / `exp3d-closed`,
`exp3e-preregistered` / `exp3e-closed`.
Other interim stage tags exist only in the private repository. `v1.0`,
`v1.1`, `v1.2`, `v1.3`, `v1.4`, `v1.5`, `v1.6` and `v1.7` anchor the Zenodo-archived snapshots
(concept DOI 10.5281/zenodo.21830421) and deliberately point outside
the current line, so each deposit remains exactly what was deposited.

For Experiments 2 and 2b, probe fits appear only in commits after the
corresponding freeze tag — the ordering the paper describes is
checkable in this history. Experiment 2c's untrained screening fits
are frozen WITH its battery by design (they are the inclusion screen,
adjudicated at the freeze); its trained-side fits appear only after
the tag. The generation experiments' committed draws likewise post-date
their freezes. Activation npz files are not committed; their SHA-256
digests are (`experiments/exp2b/results/activations_sha256.txt`).

Commit SHAs here differ from those quoted in the paper's ledgers
(extraction rewrites history); see PROVENANCE.md for the mapping and
the declared redactions.

## License

MIT for code, CC BY 4.0 for text and data; see LICENSE.md.
