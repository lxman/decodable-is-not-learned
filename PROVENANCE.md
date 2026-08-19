# Provenance

Extracted 2026-07-28; re-extracted 2026-08-06 to add the Experiment 2c
record; re-extracted 2026-08-15 to add the Experiment 3a and 3b
records; re-extracted 2026-08-18 to add the Experiment 3 and 3c
records; re-extracted 2026-08-19 to add the Experiment 3d record. All
extractions from the private working repository with
`git filter-repo`, retaining the paths: `experiments/exp2`,
`experiments/exp2b`, `experiments/exp2c`, `experiments/exp3a`,
`experiments/exp3b`, `experiments/exp3`, `experiments/exp3c`,
`experiments/exp3d`, `experiment-2-design.md`,
`experiment-2b-design.md`,
`experiment-2c-design.md`, `experiment-3a-design.md`,
`experiment-3b-design.md`, `experiment-3-design.md`,
`experiment-3c-design.md`, `experiment-3d-design.md`, `paper`,
`.gitignore`. Each re-extraction reproduces the previous one exactly
on the previously retained paths —
the fourteen earlier tag anchors below are unchanged, verified at
re-extraction — and the 2026-08-19 round adds the Experiment 3d record
(closed STRUCTURED; the rank-prediction design, the frozen structural
functional with all 500 committed values and its exact permutation
null, the adversarial freeze record with its two closed findings, the
teacher-forced scoring pass, gate-1 byte re-derivation records, all
new raw draws, the projection sealed before analysis, verdict record,
and retrospective) at its `-preregistered` and `-closed` tags. Author
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

Between 2026-08-06 and the 2026-08-15 re-extraction, seven commits
existed only in this public repository (the paper's §7 addition and
approval, the AI-disclosure section, the Zenodo DOI paragraph, and the
provenance apparatus); their paper content has been carried in the
private paper history since that round. The 2026-08-18 round has no
public-only content beyond this provenance apparatus. The `v1.0` tag
continues to anchor the Zenodo-archived line
(DOI 10.5281/zenodo.21830422) unchanged, so the archived release
remains exactly what was deposited.

The ledgers (`experiments/*/PROGRESS.md`) and closeout artifacts quote
private-repository SHAs, and reference a few working files that are
outside this extraction's scope (`experiments.md`, `environment.md`,
`CLAUDE.md`, essay drafts). The complete old→new commit map is
committed at `provenance/commit-map.txt`. Every experiment whose
record ships here carries both its preregistration and closeout tags;
interim stage tags (e.g. `exp2c-stage1`) exist only in the private
repository. Tag anchors:

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
| exp3d-preregistered | 8b2f1b0 | f16b972 |
| exp3d-closed | 2613a2f | 48a637c |

The private repository — full history, including the referenced
out-of-scope files — is available to editors and reviewers on request.

Archived at Zenodo under concept DOI 10.5281/zenodo.21830421: release
v1.0 (10.5281/zenodo.21830422, the arXiv-v1 snapshot) and release v1.1
(10.5281/zenodo.21998671, adding the Experiment 3 and 3c records).
