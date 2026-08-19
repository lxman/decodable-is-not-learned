# Exp 3d — Freeze Checklist (session 3 of 3)

The freeze OPENS ADVERSARIALLY (design header + §11): cold re-read of
`experiment-3d-design.md` and every module under `experiments/exp3d/`
with the standing assignments, then the cold battery, then the
ratification list with Michael, then the tag. Campaign launch is a
SEPARATE explicit go (§10; per-block push cadence reconfirmed at
launch, watcher authorization included).

## Standing adversarial assignments (work these FIRST, cold)

- [ ] **Find the class defect.** The lineage to beat: 3a's valueless
      verdict input; 3c finding A (the one verdict input resolved
      outside the pins — for 3d, hunt anything the verdict reads that
      is neither sha-pinned nor recomputed-and-compared: candidate
      surfaces include the power record's non-m_min fields, the
      scoring records' unpinned fields, the span table, the
      per-seed-block partition, the ℓ-arm's None handling in ranks);
      3c finding B (attested-but-uncompared hashes — 3d compares both
      directions, verify the closure actually closes BOTH).
- [ ] **Fuzz the verify criterion for totality** (stop-#1 standing
      rule) over the emission alphabet: punctuation-wrapped interior
      whitespace (the committed crasher class), unicode
      (' eyxh?\n\nA: 现在' is a committed fire!), empty draws, pure
      whitespace, newline-first draws, the leading-space-absent
      verified class ('vezdlr'). The wrapper must be total on the
      draw side and hard on the answer side, and the 13-fire referent
      battery must reproduce through it.
- [ ] **Attack the functional's degrees of freedom** (named surface,
      §11). One instance found+closed at build (float summation order
      — PROGRESS.md); assume more: log2 vs ln consistency, the LZ78
      trailing-phrase convention against the doc's "standard", midrank
      convention at full-stratum ties, the selection formula's
      remaining freedom (exact float equality in the tie-chain), the
      decile bucket's index tie-break, +inf handling in ℓ-cost ranks.
- [ ] **Attack the build-frozen dials** (PROGRESS.md's ratification
      list): the λ rule (is the Gamma-moment estimator the committed
      record's measurement, or a choice that flatters power? the
      sensitivity grid is the exhibit either way), the ctrl gate band
      (catches every plausible bug class? too wide to catch a subtle
      one?), the conditional ≥ .99 span bar, the DP-cap crossover,
      the alternative-normalization reading.

## Cold battery (fresh processes, pycache cleared, every box)

- [ ] Fixture suite cold: 116 expected (plus any freeze additions).
- [ ] Mutation battery cold, both directions, baseline clean —
      51/51 expected killed (build record below).
- [ ] Full-shape worlds: 8/8 terminals (13 tests).
- [ ] Referent battery `verify_referents_3d.py`: 13/13 on the real
      trees.
- [ ] `select_functional.py` re-run → `functional_selection_3d.json`
      byte-identical (sha before/after recorded here).
- [ ] `compute_power_3d.py` re-run → `power_3d.json` byte-identical.
- [ ] `span_validation_3d.py` re-run → `span_validation_3d.json`
      byte-identical.
- [ ] `dump_stream_map_3d()` re-run → `stream_map_3d.json`
      byte-identical; `check_stream_map_3d()` + 3c's
      `check_stream_map()` both clean.
- [ ] Determinism fixture (exp3's `run/determinism_fixture.py`) twice
      in separate processes, byte-identical to exp3's committed
      reference — the sampler is byte-pinned, so the standing
      reference applies verbatim.
- [ ] Campaign driver dry-run: 6 tiers in the frozen §10 order;
      runner refusal preconditions verified on an empty tree.
- [ ] **Gate-1 single-cell rehearsal — the ONLY sanctioned model
      contact before the tag, on Michael's word:**
      `rederive_cell_3d("410m")` end to end against 3c's committed
      seed-8 stream (32,000 draws; the stream carries the 410m 'ecde'
      fire). Expect IDENTICAL / n_diffs 0; the record is kept as the
      campaign's own comparison made early (3c's precedent: stack
      torch 2.12.1 / transformers 5.13.0 has reproduced exp3's
      streams byte-identically three times).

## Ratification with Michael (before the tag)

- [ ] Doc slips a–e (PROGRESS.md, build session): fp16→float32;
      436 = 'qvux'; 11-of-13; the 1/194 tie-free example vs the
      realized binary len-4 stratum (m_min = 1 via len-6, p = 1/151);
      expected |F| 12.3. Corrections applied to the doc ONLY on his
      ruling, ledger-first.
- [ ] Build-dial list (PROGRESS.md): λ rule + λ̂ = .025641; ctrl gate
      band [0.5r, r+.02]; MC seed 20260818 / 1e6 + DP cap 64;
      power-sim seed 20260819 / 200k; conditional span bar ≥ .99;
      4-seed blocks as the §10.4 unit; harness.py pin; the
      normalization reading.
- [ ] **The §7 concession, explicit:** DECLARED UNDERPOWERED IN
      ADVANCE — power .2616 at the observed-concentration
      alternative against the .75 bar (sensitivity grid disclosed);
      the experiment runs anyway per §7's pre-authorization and 1c's
      precedent, and the tranche's rate-resolution value stands
      regardless of the rank verdict. Michael's eyes on this line
      specifically.
- [ ] Tag `exp3d-preregistered` on his go; push tag.
- [ ] Campaign launch = SEPARATE go (§10.3-equivalent): preflight
      ladder, mlx text-server handling per 3b/3c precedent if
      resident, watcher + per-block push authorization reconfirmed.

## Build-session cold-state record (for comparison at freeze)

Suite 117 passed; full-shape 13/13 (8 worlds); referents 13/13;
mutation KILLED 51/51 baseline clean (first run 50/51 — survivor
closed structurally, PROGRESS.md item 13); artifacts byte-identical
on re-run: functional_selection_3d.json (2a2c358e…), power_3d.json
(88a0b74c…), span_validation_3d.json (c36e3714…), stream_map_3d.json.

---

## Session 3 results (2026-08-18) — adversarial pass + cold battery

Full detail in `PROGRESS.md` (FREEZE SESSION block). Summary against the
boxes above:

**Standing assignments**
- [x] **Class defect — FOUND, two instances, both CLOSED.** F1:
      `answer_type` (the verify criterion's normalization branch — what
      counts as a fire) was taken from the first shard record and
      compared to nothing; 3c pinned exactly this field and 3d had
      dropped the leg. F2: gate 1's coverage was self-consistent only
      (`draws_compared == n × dps` for ANY n), so a truncated
      re-derivation would pass the zero-tolerance gate. Both
      demonstrated executably against the real loaders before closure;
      both closed as additive refusals with fixtures and mutants.
      Neither was reachable through the real producer — stated plainly,
      not talked up.
- [x] **Verify totality fuzz — CLEARED.** 81,026 draw-side inputs over
      the emission alphabet (full 29-char whitespace class × the strip
      set, unicode incl. the item-370 fire, lone surrogates, zero-width
      and format chars, empty/whitespace-only/newline-first, the
      no-leading-space verified class, 40k seeded randoms, non-str JSON
      values): 0 escapes, 0 non-bool returns. Answer side hard 3/3.
      Also closed by construction: `IndexError` from `s.split()[0]` is
      the ONLY exception reachable on a `str`.
- [x] **The functional's degrees of freedom — CLEARED.** Log base,
      LZ78 trailing-phrase convention, midrank ties, selection-formula
      float equality, decile index tie-break, +inf in ℓ-cost ranks all
      attacked; len-4's two values are exact in binary FP so the binary
      stratum carries no ulp risk; `-0.0` benign.
- [x] **Build-frozen dials — attacked.** λ rule cleared (λ̂ = .0256 sits
      on the MORE powerful side of the committed grid and still declares
      underpowered — the dial cannot flatter the declared outcome), and
      the alternative's selection-optimism raised as ratification item
      g. Ctrl band, span bar, DP-cap crossover, normalization reading:
      no defect found.

**Cold battery**
- [x] Fixture suite cold: **121** (117 + 4 new F1/F2 fixtures).
- [x] Mutation battery both directions: **KILLED 56/56, baseline clean**
      (51 + 5 new). Three `[broken-target]` reports on the first
      post-closure run — two new mutants whose bare `if n != n_items:`
      also matched the scoring loader's 12-space occurrence, plus the
      PRE-EXISTING cross-shard mutant whose target F1 had extended — all
      retargeted and killed.
- [x] Full-shape worlds: 8/8 terminals (13 tests).
- [x] Referent battery: **13/13** on the real trees.
- [x] `functional_selection_3d.json` byte-identical `2a2c358e…`
- [x] `power_3d.json` byte-identical `88a0b74c…`
- [x] `span_validation_3d.json` byte-identical `c36e3714…`
- [x] `stream_map_3d.json` byte-identical `55ff2294…`; both overlap laws
      clean. **The closures move no committed number** — as pure
      refusals must.
- [x] **Determinism fixture ×2 — BYTE-IDENTICAL THREE WAYS.** Both
      fresh processes and exp3's committed reference all hash
      `791ce4779c29b566ac3e3e0a78d2488df7257229e8dd7006a00b40eb0450f4cb`,
      with torch 2.12.1 / transformers 5.13.0 serialized INTO the
      compared bytes — the stack has not drifted since exp3. (Checklist
      wording note for ratification: this box and the "ONLY sanctioned
      model contact" box are in tension on their face; the invariant the
      fixture cannot violate is "no new sampled quantity for any REAL
      cell" — it samples synthetic prompts in a dedicated stream
      namespace.)
- [x] Campaign driver dry-run: 6 tiers in the frozen §10 order; runner
      refusal preconditions verified on an empty tree — scoring and
      sampling both refuse BEFORE the model loads.
- [x] **Gate-1 single-cell rehearsal — IDENTICAL, n_diffs 0.**
      `rederive_cell_3d("410m")` end to end vs 3c's committed seed-8
      stream: **32,000/32,000 draws byte-identical**, 0 diffs, the
      fire-carrying stream ('ecde' at 410m) among them. Record attests
      `b3422b4f…` == the file on disk == the §4 literal pin
      (finding-B loop clean, both directions). Stack torch 2.12.1 /
      transformers 5.13.0, model_sha 9879c9b5. **The fourth consecutive
      byte-identical reproduction of the committed streams on this
      stack.** Record kept as the campaign's own comparison made early;
      the 1b half runs at launch.

**Ratification (open)**
- [ ] Doc slips a–e.
- [ ] Build-dial list.
- [ ] The §7 concession line — plus freeze items **f** (the calibration
      sentence is true of one tail: STRUCTURED .0482 AND ANTI .0450, so
      P(directional verdict | no signal) = .0932), **g** (the .2616 is
      selection-flavoured and therefore optimistic — this strengthens
      the concession), **h** (m_min = 1 is realized at in-sample item
      200, so a THIN rejection could be persistence wearing a
      forecast's p-value; immaterial at 1b, material at non-gating
      410m).
- [ ] Tag `exp3d-preregistered`; push tag.
- [ ] Campaign launch = SEPARATE go.

**Harness lesson:** the mutation battery mutates repo sources IN PLACE.
Nothing may run beside it — a concurrent run this session produced three
spurious full-shape failures that re-ran clean. Sequential only; a
"failure" seen during a mutation run is evidence of nothing.

## Michael's rulings (2026-08-18) — freeze ratified

- **Doc slips a–e: APPLY ALL FIVE.** Applied to
  `experiment-3d-design.md`: §3 fp16→float32; §3 item 436 'xuvq'→
  'qvux' (both the fires list and the texture sentence); §5.4 and §8
  "10 of 13"→"11 of 13"; §6's impossible tie-free example replaced with
  the realized structure (cheapest len-4 class = 45 items, so no len-4
  fire beats 45/194 = .23; m_min = 1 arrives through len-6's
  unique-cheapest answer at p = 1/151 = .0066); §6 expected |F| 8–12 →
  12.3 observed-concentration (14.8 flat).
  *Left standing and flagged:* §3's separate sentence "3c's conversion
  suggests roughly 8–12 distinct new-fired items" is the PROVENANCE of
  the old range, explicitly framed as a rough heuristic, and 12.3 sits
  inside it — not corrected, because it is a different claim by a
  different method, not a restatement.
- **Build-dial list: RATIFIED AS FROZEN**, all eight. The λ rule was
  attacked hardest and cleared: λ̂ = .0256 sits on the MORE powerful
  side of the committed sensitivity grid and still declares
  underpowered, so it cannot have been chosen to flatter.
- **§7 concession: FIX f, ADD g.** Both applied in place in
  `PROGRESS.md` build item 4, marked CORRECTED AT FREEZE with the
  reasons; the freeze block carries the full derivation. Nothing
  silently absorbed.
- **Tag and push: GO.** One commit carrying the two closures, their
  fixtures and mutants, both ledgers, the doc corrections, and the
  410m gate-1 record; tag `exp3d-preregistered`; push both. Campaign
  launch remains a SEPARATE go.
