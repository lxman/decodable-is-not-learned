# Provenance

Extracted 2026-07-28; re-extracted 2026-08-06 to add the Experiment 2c
record; re-extracted 2026-08-15 to add the Experiment 3a and 3b
records; re-extracted 2026-08-18 to add the Experiment 3 and 3c
records; re-extracted 2026-08-19 to add the Experiment 3d record;
re-extracted 2026-08-21 to add the Experiment 3e record;
re-extracted 2026-08-22 to add the Experiment 2d record, again the
same day to add the Experiment 2e record, and a third time that day
to add the Experiment 2f record. All
extractions from the private working repository with
`git filter-repo`, retaining the paths: `experiments/exp2`,
`experiments/exp2b`, `experiments/exp2c`, `experiments/exp2d`,
`experiments/exp2e`, `experiments/exp2f`, `experiments/exp3a`,
`experiments/exp3b`, `experiments/exp3`, `experiments/exp3c`,
`experiments/exp3d`, `experiments/exp3e`, `experiment-2-design.md`,
`experiment-2b-design.md`,
`experiment-2c-design.md`, `experiment-2d-design.md`,
`experiment-2e-design.md`, `experiment-2f-design.md`,
`experiment-3a-design.md`,
`experiment-3b-design.md`, `experiment-3-design.md`,
`experiment-3c-design.md`, `experiment-3d-design.md`,
`experiment-3e-design.md`, `paper`,
`.gitignore`; and, from 2026-08-23, `experiments/exp1`,
`experiments/exp1b`, `experiments/exp1c`, `experiment-1-design.md`,
`experiment-1b-design.md`, `experiment-1c-design.md` (see the next
paragraph for how those six were added). Each re-extraction reproduces the previous one exactly
on the previously retained paths —
the twenty-two earlier tag anchors below are unchanged, verified at
re-extraction — and the third 2026-08-22 round added the Experiment
2f record (closed LADDER: the ladder-order design on the
probe-flat-but-rising pair — one label per rung read by probe,
sampling and argmax on the same weights and items; the label
functions with their known-answer gates against 2c's committed
probe labels; 2b's probe at 2c's site family with the twin void
rule; the 34-file referent manifest; the machinery gate reproducing
2c's m3 records exactly; the continuity gate records (IDENTICAL on
all eight comparisons) and the sha256 digests of the eval-item
activations (the arrays themselves are not committed, as 2b/2c's
were not); the adversarial freeze record; the projection sealed
before analysis; verdict record and retrospective) at its
`-preregistered` and `-closed` tags. The second 2026-08-22 round
added the Experiment 2e record (closed FAIL; the floor-as-covariate re-read of Experiment
2d's committed draws, analysis-only with zero model contact: the
functional family fixed in advance with one primary and three printed
comparators, the 273-file referent manifest over 2d's tree, the
per-cell tally table by literal, the comparison gate that reproduces
2d's primary exactly from the same cells, the adversarial freeze
record with its ratified boundary finding, the projection sealed
before analysis under a full disclosure that every input was known to
the designer, verdict record, and retrospective) at its
`-preregistered` and `-closed` tags. The first 2026-08-22 round added
the Experiment 2d record
(closed FAIL under a declared-underpowered-in-advance status: the
sampling-ladder design, the 34-rung battery pinned to Experiment 2c's
committed items and outcome, the model-free format-floor rule with its
option-listing re-derivation, the AUC primary under 2c's family-block
null, the pilot-driven power procedure with both the ratified Tobit
and the symmetric rule the freeze ruled declaring, the adversarial
freeze record with its closed findings, all 1,224,000 raw pilot and
main draws, the four gate-1 production-path comparison records, the
68 argmax records, the projection sealed before analysis, verdict
record, and retrospective) at its `-preregistered` and `-closed`
tags. The 2026-08-21 round added the Experiment 3e record
(closed NO-SHORTCUT; the shortcut-or-reversal design, the frozen
partition of the 45-item repeat class with its printed variants, the
exact hypergeometric primary and the two exact DP nulls, the
class-level power record with the freeze's shape-rule sensitivity and
the declared-underpowered ruling, the adversarial freeze record with
its three closed findings, the scorer known-answer gate record, gate-1
byte re-derivation records on the production subset path, all 552,960
new raw draws in twelve block shards, the projection sealed before
analysis, verdict record, and retrospective) at its `-preregistered`
and `-closed` tags. The 2026-08-19 round added the Experiment 3d
record in the same way. Author
dates and commit
ordering are preserved. File contents at every retained path are
byte-identical to the private repository, with the following declared
exceptions:

1. `experiments/exp2b/run/sync_workers.sh`: two `user@LAN-IP`
   literals replaced, throughout history, with `<user>@<llmbox-lan-ip>`
   and `<user>@<devbox-lan-ip>`.
2. Commit and tag author/committer identities rewritten, throughout
   history, from a personal email address to the author's GitHub
   noreply address. Author dates are unchanged.
3. `paper/_build.html` (a PDF-build intermediate committed and deleted
   in the private history) is dropped entirely.
4. `README.md` and `LICENSE.md` are authored for this public record and
   have no private counterpart. Both were present in the `v1.0`
   snapshot but had been absent from the working line since a prior
   re-extraction restored only the provenance apparatus; the
   2026-08-19 round restores them. `LICENSE.md` is carried forward
   verbatim from `v1.0`; `README.md` is rewritten, because the `v1.0`
   text described only the Experiment 2/2b/2c scope and listed five
   tags, and reproducing it unchanged would have misdescribed the
   repository.

Nothing else is altered: no prose, no data, no code beyond the two
literals above.

On 2026-08-23 the Experiment 1, 1b and 1c records — the synthetic
instrument calibration the essay's empirical section reports: the
original three-signature instrument test (Experiment 1, closed FAIL on
a criterion later found misspecified), the corrected probe-leg test
with the untrained-twin floor (Experiment 1b, closed PASS) and the
sub-critical structure sweep (Experiment 1c, closed FAIL, declared
underpowered in advance) — were added by a different route, chosen so
that nothing already public would move. Their commits are interleaved
with the Experiment 2–3 history from 2026-07-03 to 2026-08-15, so
re-filtering the whole history with the exp1 paths added would have
changed the SHA of every public commit after 2026-07-03, including all
twenty-four tag anchors, and would have required a force-push. Instead
the six exp1 paths were filtered from a fresh clone of the private
repository into their own 138-commit line (`git filter-repo`, the same
mailmap as every prior round, no other rewrite) and that line was
merged into this repository's master with `--allow-unrelated-histories`
(merge commit 63f1b4e), a fast-forward on the remote. Every commit and
tag on the previously extracted line is unchanged; the exp1 line's
commits carry only the six exp1 paths in their trees. Verified at
extraction: each carried exp1 tag's tree is entry-for-entry identical
(blob hashes) to the private tag's tree restricted to the six paths,
and the merged tree is exactly the prior public tree plus the exp1
tree (3,915 entries). Experiment 1's freeze tag is named
`exp1-analysis-frozen` rather than `-preregistered`, as it was in the
private repository; `exp1c-stage-a` is an interim stage tag and
would ordinarily stay private like the others, but it marks the
commit in which Experiment 1c's power table was finalised against the
measured variance and the experiment declared underpowered before any
sweep cell was probed — the declaration the essay's calibration
paragraph cites — so it is carried here as the one exception to the
stage-tag rule, pushed 2026-08-23 on the author's word. The exp1 line's old→new commit map is
appended to `provenance/commit-map.txt`. The private exp1 trees carry
one hard-coded working-tree path (`experiments/exp1c/tests/mutation_check.py`),
left as is like the home-path literals tolerated in earlier rounds;
no LAN or credential literal occurs anywhere in the line.

On 2026-08-23, after the v1.7 release, the paper was carried onto this
line directly: one commit replaces `paper/` with the private
repository's `paper/` at its commit 3db6839 (byte-identical, verified
at the carry; `_build.html` is not tracked), bringing the v1.7 DOI
into the paper's own version list, the exp1 records into its
repository inventory, and Section 6's ninth lesson with checklist
item 23. No filter pass was run and nothing already on this line
moved. Paper-only updates will take this route from now on; the
filter-repo re-extraction remains the route for experiment records.

Between 2026-08-06 and the 2026-08-15 re-extraction, seven commits
existed only in this public repository (the paper's §7 addition and
approval, the AI-disclosure section, the Zenodo DOI paragraph, and the
provenance apparatus); their paper content has been carried in the
private paper history since that round. The 2026-08-18 round has no
public-only content beyond this provenance apparatus. The `v1.0` tag
continues to anchor the Zenodo-archived line
(DOI 10.5281/zenodo.21830422) unchanged, so the archived release
remains exactly what was deposited; the 2026-08-21 round and all
three 2026-08-22 rounds likewise have no public-only content beyond
this provenance apparatus, and `v1.1`, `v1.2`, `v1.3`, `v1.4`, `v1.5`,
`v1.6` and `v1.7` anchor their deposits off the current line (`v1.7`,
cut 2026-08-23 at the commit that recorded the exp1 graft, is the
first deposit to include the Experiment 1, 1b and 1c records).

The ledgers (`experiments/*/PROGRESS.md`) and closeout artifacts quote
private-repository SHAs, and reference a few working files that are
outside this extraction's scope (`experiments.md`, `environment.md`,
`CLAUDE.md`, essay drafts). The complete old→new commit map is
committed at `provenance/commit-map.txt`. Every experiment whose
record ships here carries both its preregistration and closeout tags;
interim stage tags (e.g. `exp2c-stage1`) exist only in the private
repository, with the one exception of `exp1c-stage-a` explained
above. Tag anchors:

| tag | private | public |
|---|---|---|
| exp2-preregistered | 5f48567 | b21f44c |
| exp2-closed | fc7ba9a | 20d6c5b |
| exp2b-preregistered | 7293ff7 | d692504 |
| exp2b-closed | 8375631 | 503ffb0 |
| exp2c-preregistered | 84e6da8 | d8e261d |
| exp2c-closed | 4381ea9 | cc0e279 |
| exp3a-preregistered | 718541c | 68825dd |
| exp3a-closed | 2377fa3 | b69d322 |
| exp3b-preregistered | eaa78dd | 15813e6 |
| exp3b-closed | 04c7e04 | 6db3077 |
| exp3-preregistered | ae82394 | 1661381 |
| exp3-closed | 6008331 | f44c072 |
| exp3c-preregistered | 97788eb | 012576c |
| exp3c-closed | 3fe176b | 8169976 |
| exp3d-preregistered | 8b2f1b0 | 20d514a |
| exp3d-closed | 2613a2f | b65d103 |
| exp3e-preregistered | d1031a6 | e5cba1f |
| exp3e-closed | 244a0e9 | c393617 |
| exp2d-preregistered | c617e81 | d84ec03 |
| exp2d-closed | 2ce1f5c | b4ba3de |
| exp2e-preregistered | a50c4a8 | 8dce446 |
| exp2e-closed | 92b258a | 81eac91 |
| exp2f-preregistered | 09b0c5e | b1b3ca1 |
| exp2f-closed | 6b1fef8 | 0dd378e |
| exp1-analysis-frozen | 8f7198d | 91567d9 |
| exp1b-preregistered | 2dbbc77 | 794298c |
| exp1b-closed | fb9537a | 4be999d |
| exp1c-preregistered | ba3ffd3 | a790cbf |
| exp1c-stage-a | 62a583b | be6c69b |
| exp1c-closed | 185be34 | 06dea62 |

The private repository — full history, including the referenced
out-of-scope files — is available to editors and reviewers on request.

Archived at Zenodo under concept DOI 10.5281/zenodo.21830421: release
v1.0 (10.5281/zenodo.21830422, the arXiv-v1 snapshot), release v1.1
(10.5281/zenodo.21998671, adding the Experiment 3 and 3c records) and
release v1.2 (10.5281/zenodo.22011547, adding the Experiment 3d
record), release v1.3 (10.5281/zenodo.22045940, adding the Experiment 3e
record), release v1.4 (10.5281/zenodo.22056230, adding the
Experiment 2d record), release v1.5 (10.5281/zenodo.22059612,
adding the Experiment 2e record), release v1.6
(10.5281/zenodo.22063906, adding the Experiment 2f record) and release
v1.7 (10.5281/zenodo.22064573, adding the Experiment 1, 1b and 1c
records).
