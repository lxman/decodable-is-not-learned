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

**HUNT CONCLUDED (2026-08-17, ledgered before implementation —
PROGRESS.md freeze entry): two findings, both closed the same day.**
FINDING A (3a's lineage, one level up): `load_prompts` was the only
verdict input with no executable pin at analysis time — the leak
gate re-rendered prompts from the live item files, full-shape worlds
inject prompts, no mutant touched it; post-campaign item-file drift
could silently flip void determinations. Closed: sha_refs is now a
REQUIRED argument, the resolved bytes hash-checked against the §4
pin before any prompt renders; drifted-pin + missing-arg fixtures;
softening + hardening mutants. FINDING B: the gate-1 record's
`committed_draws_sha256` was never compared to the exp3 tree the
analyzer pools. Closed: `check_gate1_committed_shas` in `run()` and
the full-shape battery path (synthetic gate-1 records now carry TRUE
hashes of the synthetic exp3 tree, so every world exercises it);
doctored-sha + missing-file fixtures; softening + hardening mutants.
No accepted dial touched — both closures are additive refusals. The
other flagged surfaces were attacked and CLEARED with rulings in the
ledger (criterion semantics, quantifier edges, stratum accounting,
`diff_seed0` coverage algebra, path-assert convention, luck-floor
overlap, namespace virginity). Suite 89 → 93; mutants 52 → 56.

## Rulings required (build-session readings, PROGRESS.md 2026-08-17)

- [ ] Reading 1 — gate-1 volume built to the committed record:
      132,000 draws (64/item scored, 8/item ctrl_copy), zero
      tolerance. DOC CORRECTION to §2/§3 (160,000 and 128,000 both
      wrong) — Michael's ratification. *Freeze: code side VERIFIED
      cold (loader enforces exp3's committed depths per rung; the
      volume fixture scales to exactly 132,000); box waits on the
      doc ruling.*
- [ ] Reading 2 (+ extension) — luck floor 26^-4 = 2.19e-6, gap
      ~9.2×; LONE-DRAW silence at p = 1e-6 is .68 (two in three),
      not 1-in-3. DOC CORRECTIONS to §7/§8 — Michael's ratification.
      All three recorded `agrees: false` in `power_3c.json`. *Freeze:
      code side VERIFIED cold (floors from code; quote check
      disagrees on exactly the three); box waits on the doc ruling.*
- [x] Reading 3 — leak-void criterion (casefolded answer occurs in
      its own rendered prompt); "both rungs' fires void" implemented
      as ≥1 new fire AND every new fire void → INSUFFICIENT_DATA;
      partial voiding discloses and proceeds; zero fires leaves the
      gate vacuous. **RATIFIED, and ruled RIGHT over the doc's
      literal wording**: 2c's verify normalizes to the first token,
      so fired draws are decorated and the answer — not the draw's
      verbatim text — is the leaking object; scan and gate share one
      operationalization. Strengthened by finding A (prompt source
      now pinned).
- [x] Reading 4 — the standing twin referent as an executable
      independent assert (0 fires across all 8 exp3 twin cells,
      whatever the referent table says). **RATIFIED** — the
      laundering guard is independent of the fires table; mutant
      covered; twin-fire world hard-errors.
- [x] Reading 5 — adjudication reads NEW non-void fire counts only;
      everything pooled/stratified/descriptive is disclosure.
      **RATIFIED** — every branch reads only fired/wall non-void
      counts; pre-void mutants killed; no branch reads pooled,
      strata, descriptives, or the luck floor.
- [x] Reading 6 — exp3-side referent asserts: fires table (sha-pinned
      verdict record) 16/16, fired address = (item 436, seed 0,
      draw 6), fired answer length 4. **RATIFIED** — two-pass
      address extraction cross-checked against the loader recompute.
- [x] Reading 7 — stream-map continuity (s0–s3 byte-equal to exp3's
      committed map; one formula, namespace 'exp3' deliberately).
      **RATIFIED** — formula equality + per-entry recompute + overlap
      byte-equality; seeds 4–15 are virgin substreams (twins are
      mode-separated; determinism fixture namespace-separated).
- [x] Reading 8 — record shapes (seeds 4–15, dps 64, k 768; gate-1
      comparison records with verbatim diffs and the committed-file
      sha). **RATIFIED** — and the committed-file sha is now
      LOAD-BEARING (finding B), not just present.
- [x] LONE-DRAW frozen reading confirmed VERBATIM in the reason text
      (existence stands; not retractable by silence; single-event
      regime stated plainly) — the design's costliest-world dial.
      **CONFIRMED**: every load-bearing phrase of §1's reading is in
      the frozen branch ("STANDS — it is committed, verified",
      "not retractable by later silence (the asymmetry rule, applied
      symmetrically to our own result)", "single-event regime stated
      plainly: reachability demonstrated, rate below this design's
      resolving power"); pooled numbers computed live, reproducing
      1/512,000 (1.95e-6) on the real tree; the lone_draw world
      asserts the phrases.
- [ ] FINDING A closure ratified: leak-gate prompt source pinned to
      the §4 referents at analysis time (required sha_refs argument;
      hard error before rendering). Additive refusal, no dial moved.
- [ ] FINDING B closure ratified: gate-1 committed_draws_sha256
      cross-checked against the pooled exp3 tree in run() and the
      full-shape path. Additive refusal, no dial moved.

## Cold re-runs (all must pass, from a fresh process, before the tag)

- [x] Full fixture suite green, pycache cleared first
      (`PYTHONDONTWRITEBYTECODE=1 python -m pytest
      experiments/exp3c/tests/`). Build close: 89 passed; **FREEZE
      COLD RUN: 93 passed** (89 + the findings' four fixtures).
- [x] Mutation check both directions
      (`experiments/exp3c/tests/mutation_check.py`), single run on a
      quiescent tree. Build close: **52/52 KILLED, baseline clean**
      (two build-time survivors repaired: the new-cell §4 pin arm was
      masked by the gate-1 sha arm — isolating world added; the
      dtype mutant pattern was non-unique — split per site). **FREEZE
      COLD RUN: KILLED 56/56, no survivors, baseline clean** (52 + 
      the findings' four, both directions; first run's tail clipped
      the count line, re-run captured in full — both runs killed
      everything).
- [x] Full-shape batteries reach EVERY terminal (`python -m
      experiments.exp3c.tests.full_shape`): four worlds, both
      INSUFFICIENT_DATA routes, void-discloses-and-proceeds,
      fired-void-wall-clean. Build close: 8/8 ok. **FREEZE COLD RUN:
      8/8, ALL TERMINAL BRANCHES REACHED** (now through the
      finding-B loop closure — synthetic gate-1 records carry true
      tree hashes).
- [x] `python -m experiments.exp3c.verify_referents_3c`: the full
      referent battery on the real trees. Build close: 10/10.
      **FREEZE COLD RUN: 10/10** (the 1000-item scan now through the
      pinned load_prompts; referent_check_3c.json rewritten
      byte-identical).
- [x] `power_3c.json` recomputed from the frozen code,
      byte-identical; quote check disagrees on EXACTLY the three
      ledgered slips. **FREEZE COLD RUN: byte-identical (sha
      8d7bc741… before and after; git clean); disagreements exactly
      the three.**
- [x] Glue smoke (stop-#1's standing rule):
      `tests/test_glue_smoke_3c.py` — padded-vocab synthetic sampler
      pass + quantity-free real-config width check, both campaign
      sizes. **FREEZE COLD RUN: 2 passed.**
- [x] Determinism fixture re-run cold, TWICE in separate processes
      (`python -m experiments.exp3.run.determinism_fixture --out …`),
      byte-identical to each other AND to exp3's committed
      `determinism_reference.json` (stack-drift detector; synthetic
      prompts, dedicated namespace — no committed item sampled).
      **FREEZE COLD RUN: run1 == run2 byte-identical; run1 ==
      committed reference byte-identical. The stack has not drifted
      since exp3.**
- [x] **Gate-1 single-cell rehearsal — THE ONLY MODEL CONTACT before
      the tag:** `rederive_cell("ctrl_copy", "1b")` — 4,000 committed
      seed-0 draws re-derived end to end and byte-compared; expect
      IDENTICAL; the record is kept (it is the campaign's own
      preregistered comparison, made early) and the result ledgered
      either way. A diff here means the stack drifted since exp3 and
      the campaign must not launch. **FREEZE: 4,000/4,000 IDENTICAL,
      n_diffs 0, record kept at results/gate1/1b_trained/
      ctrl_copy.json (torch 2.12.1 / transformers 5.13.0); the
      record's committed_draws_sha256 hash-matches the live exp3
      file (finding B's loop, closed on the first real record). The
      full pipeline — load, upcast, render, tokenize, stream formula,
      chunked sampling, truncate, decode — reproduces exp3's
      committed bytes exactly.**
- [x] Empty-tree hard error: `python -m experiments.exp3c.analyze_3c`
      on the (still-empty) results tree exits with
      FileNotFoundError, never a verdict. **FREEZE: exit 1,
      FileNotFoundError at the first missing gate-1 record — run
      BEFORE the rehearsal wrote anything; the exp3-side 16-cell
      load passed cold on the way.**
- [x] Storage headroom: ~16 MB gz projected for the new draws
      (ledgered coefficient 10.2 B/draw × 1,536,000). **FREEZE:
      362 Gi free.**

## At the tag

- [ ] Tag `exp3c-preregistered` on the ruling-complete, cold-green
      commit; push tag (with Michael's go).
- [ ] Campaign preflight ladder + per-cell push authorization
      reconfirmed with Michael (§10.3; commit_watcher pushes per
      cell).
