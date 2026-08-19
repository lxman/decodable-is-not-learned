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

- **Experiments 2, 2b, 2c** — the probing-hygiene arc the paper is
  about: standard splits and what an untrained network decodes; the
  basis-starved re-run; the screened battery and its inclusion-time
  untrained gate (the paper's Section 7).
- **Experiments 3a, 3b, 3, 3c, 3d** — the successor generation arc the
  paper's Section 6 draws its calibration lessons from: a verdict that
  crashed on a valueless input (3a), the same-weights probe/emission
  dissociation (3b), sampling elicitation (3), staged deepening (3c),
  and item-grain rank prediction (3d, whose power table mis-specified
  its alternative's shape — the sixth lesson).

Every experiment whose record ships here carries both its
preregistration and its closeout tag:
`exp2-preregistered` / `exp2-closed`,
`exp2b-preregistered` / `exp2b-closed`,
`exp2c-preregistered` / `exp2c-closed`,
`exp3a-preregistered` / `exp3a-closed`,
`exp3b-preregistered` / `exp3b-closed`,
`exp3-preregistered` / `exp3-closed`,
`exp3c-preregistered` / `exp3c-closed`,
`exp3d-preregistered` / `exp3d-closed`.
Interim stage tags exist only in the private repository. `v1.0` and
`v1.1` anchor the Zenodo-archived snapshots and deliberately point
outside the current line, so each deposit remains exactly what was
deposited.

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
