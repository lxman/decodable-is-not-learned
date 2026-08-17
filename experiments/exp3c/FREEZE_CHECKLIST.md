# Exp 3c freeze checklist (the build session wrote it; the freeze
# session executes it COLD and rules on it)

**Status: NOT FROZEN. Do not tag until every box is checked in the
freeze session itself.**

The freeze session opens adversarially: cold re-read of
`experiment-3c-design.md` and this tree, assignment = find the class
defect. The lineage to assume from: 3a's was a verdict input with no
value on its own battery; 2c's was a floor that credits format;
exp3's build had an arithmetic path wrong at the kernel level and its
freeze found a §5 statistic crediting set-level lexical priming.
Assume this tree still contains one and hunt for it. Candidate
surfaces this build knows it did NOT adversarially attack: the
leak-void criterion's substring form (casefolded answer ∈ rendered
prompt), the reading-3 "all fires void" quantifier edges, the
per-address stratum accounting, and the gate-1 record's trust surface
(the runner writes `n_diffs`; the analyzer validates shape and volume
but cannot re-derive bytes without a model).

## Rulings required (build-session readings, PROGRESS.md 2026-08-17)

- [ ] Reading 1 — gate-1 volume built to the committed record:
      132,000 draws (64/item scored, 8/item ctrl_copy), zero
      tolerance. DOC CORRECTION to §2/§3 (160,000 and 128,000 both
      wrong) — Michael's ratification.
- [ ] Reading 2 (+ extension) — luck floor 26^-4 = 2.19e-6, gap
      ~9.2×; LONE-DRAW silence at p = 1e-6 is .68 (two in three),
      not 1-in-3. DOC CORRECTIONS to §7/§8 — Michael's ratification.
      All three recorded `agrees: false` in `power_3c.json`.
- [ ] Reading 3 — leak-void criterion (casefolded answer occurs in
      its own rendered prompt); "both rungs' fires void" implemented
      as ≥1 new fire AND every new fire void → INSUFFICIENT_DATA;
      partial voiding discloses and proceeds; zero fires leaves the
      gate vacuous. Ratify or amend.
- [ ] Reading 4 — the standing twin referent as an executable
      independent assert (0 fires across all 8 exp3 twin cells,
      whatever the referent table says).
- [ ] Reading 5 — adjudication reads NEW non-void fire counts only;
      everything pooled/stratified/descriptive is disclosure.
- [ ] Reading 6 — exp3-side referent asserts: fires table (sha-pinned
      verdict record) 16/16, fired address = (item 436, seed 0,
      draw 6), fired answer length 4.
- [ ] Reading 7 — stream-map continuity (s0–s3 byte-equal to exp3's
      committed map; one formula, namespace 'exp3' deliberately).
- [ ] Reading 8 — record shapes (seeds 4–15, dps 64, k 768; gate-1
      comparison records with verbatim diffs and the committed-file
      sha).
- [ ] LONE-DRAW frozen reading confirmed VERBATIM in the reason text
      (existence stands; not retractable by silence; single-event
      regime stated plainly) — the design's costliest-world dial.

## Cold re-runs (all must pass, from a fresh process, before the tag)

- [ ] Full fixture suite green, pycache cleared first
      (`PYTHONDONTWRITEBYTECODE=1 python -m pytest
      experiments/exp3c/tests/`). Build close: 89 passed.
- [ ] Mutation check both directions
      (`experiments/exp3c/tests/mutation_check.py`), single run on a
      quiescent tree. Build close: **52/52 KILLED, baseline clean**
      (two build-time survivors repaired: the new-cell §4 pin arm was
      masked by the gate-1 sha arm — isolating world added; the
      dtype mutant pattern was non-unique — split per site).
- [ ] Full-shape batteries reach EVERY terminal (`python -m
      experiments.exp3c.tests.full_shape`): four worlds, both
      INSUFFICIENT_DATA routes, void-discloses-and-proceeds,
      fired-void-wall-clean. Build close: 8/8 ok.
- [ ] `python -m experiments.exp3c.verify_referents_3c`: the full
      referent battery on the real trees. Build close: 10/10
      (frozen-file pins; map continuity; exp3 tally recompute; fires
      table 16/16; fire address pin; twin record 512k+64k; §4 item
      pins; 1000-item prompt-leak scan; power byte recompute; exp3
      determinism reference present).
- [ ] `power_3c.json` recomputed from the frozen code,
      byte-identical; quote check disagrees on EXACTLY the three
      ledgered slips.
- [ ] Glue smoke (stop-#1's standing rule):
      `tests/test_glue_smoke_3c.py` — padded-vocab synthetic sampler
      pass + quantity-free real-config width check, both campaign
      sizes.
- [ ] Determinism fixture re-run cold, TWICE in separate processes
      (`python -m experiments.exp3.run.determinism_fixture --out …`),
      byte-identical to each other AND to exp3's committed
      `determinism_reference.json` (stack-drift detector; synthetic
      prompts, dedicated namespace — no committed item sampled).
- [ ] **Gate-1 single-cell rehearsal — THE ONLY MODEL CONTACT before
      the tag:** `rederive_cell("ctrl_copy", "1b")` — 4,000 committed
      seed-0 draws re-derived end to end and byte-compared; expect
      IDENTICAL; the record is kept (it is the campaign's own
      preregistered comparison, made early) and the result ledgered
      either way. A diff here means the stack drifted since exp3 and
      the campaign must not launch.
- [ ] Empty-tree hard error: `python -m experiments.exp3c.analyze_3c`
      on the (still-empty) results tree exits with
      FileNotFoundError, never a verdict.
- [ ] Storage headroom: ~16 MB gz projected for the new draws
      (ledgered coefficient 10.2 B/draw × 1,536,000).

## At the tag

- [ ] Tag `exp3c-preregistered` on the ruling-complete, cold-green
      commit; push tag (with Michael's go).
- [ ] Campaign preflight ladder + per-cell push authorization
      reconfirmed with Michael (§10.3; commit_watcher pushes per
      cell).
