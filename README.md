# Decodable Is Not Learned — supporting record

Public supporting record for the paper "Decodable Is Not Learned:
Untrained-Weights Controls and Basis-Starved Splits for Linear
Probing" (Michael Jordan). This is a path-filtered extraction of the
private working repository, preserving full commit history, authorship
dates, and ordering for everything the paper relies on: the three
frozen preregistration documents, the experiments' code, campaign
ledgers, all committed probe fits (480 for Experiment 2, 770 for
Experiment 2b, and Experiment 2c's 220 untrained-gate fits), the
frozen reports and verdicts, the Experiment 2c screening record
(tier-1/tier-2 verdicts, ejections, and the M1 inclusion record the
paper's Section 7 reports), and the paper source with the scripts
that generate its figures, Table 1, and Appendix A.

Tags mark the preregistration and closeout commits:
`exp2-preregistered`, `exp2-closed`, `exp2b-preregistered`,
`exp2b-closed`, `exp2c-preregistered`. For Experiments 2 and 2b,
probe fits appear only in commits after the corresponding freeze tag
— the ordering the paper describes is checkable in this history.
Experiment 2c's untrained screening fits are frozen WITH its battery
by design (they are the inclusion screen, adjudicated at the freeze);
its trained-side fits appear only after the tag. Activation npz files
are not committed; their SHA-256 digests are
(`experiments/exp2b/results/activations_sha256.txt`).

Commit SHAs here differ from those quoted in the paper's ledgers
(extraction rewrites history); see PROVENANCE.md for the mapping and
the declared redactions.

## License

MIT for code, CC BY 4.0 for text and data; see LICENSE.md.
