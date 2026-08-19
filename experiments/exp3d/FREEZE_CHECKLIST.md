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
