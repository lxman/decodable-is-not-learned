# Provenance

Extracted 2026-07-28, and re-extracted 2026-08-06 to add the
Experiment 2c record, from the private working repository with
`git filter-repo`, retaining the paths: `experiments/exp2`,
`experiments/exp2b`, `experiments/exp2c`, `experiment-2-design.md`,
`experiment-2b-design.md`, `experiment-2c-design.md`, `paper`,
`.gitignore`. The re-extraction reproduces the 2026-07-28 extraction
exactly on the previously retained paths — the four earlier tag
anchors below are unchanged — and adds the Experiment 2c battery,
screening verdicts (tier 1 and tier 2), ejection records, M1
inclusion record, and frozen analysis code at tag
`exp2c-preregistered`. Author dates and commit ordering are
preserved. File contents at every retained path are byte-identical to
the private repository, with the following declared exceptions:

1. `experiments/exp2b/run/sync_workers.sh`: two `user@LAN-IP`
   literals replaced, throughout history, with `<user>@<llmbox-lan-ip>`
   and `<user>@<devbox-lan-ip>`.
2. Commit and tag author/committer identities rewritten, throughout
   history, from a personal email address to the author's GitHub
   noreply address. Author dates are unchanged.
3. `paper/_build.html` (a PDF-build intermediate committed and deleted
   in the private history) is dropped entirely.

Nothing else is altered: no prose, no data, no code beyond the two
literals above.

The ledgers (`experiments/*/PROGRESS.md`) and closeout artifacts quote
private-repository SHAs, and reference a few working files that are
outside this extraction's scope (`experiments.md`, `environment.md`,
`CLAUDE.md`, essay drafts). The complete old→new commit map is
committed at `provenance/commit-map.txt`. Tag anchors:

| tag | private | public |
|---|---|---|
| exp2-preregistered | 5f48567 | b21f44c |
| exp2-closed | fc7ba9a | 20d6c5b |
| exp2b-preregistered | 7293ff7 | d692504 |
| exp2b-closed | 8375631 | 503ffb0 |
| exp2c-preregistered | 84e6da8 | d8e261d |

The private repository — full history, including the referenced
out-of-scope files — is available to editors and reviewers on request.

Archived at Zenodo: DOI 10.5281/zenodo.21830422 (release v1.0).
