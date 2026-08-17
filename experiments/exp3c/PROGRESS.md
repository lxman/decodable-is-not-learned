# Experiment 3c — build ledger

**2026-08-17 — BUILD SESSION CLOSED. Doc Open items 1–8 all built;
freeze session (3 of 3) is next and opens adversarially.** Closing
state, all cold: fixture suite **89 passed**; mutation check **52/52
KILLED both directions, baseline clean** (two build-time survivors
found and repaired the same run — the new-cell §4 pin arm was masked
by the gate-1 sha arm until an isolating world split them, and the
dtype mutant matched two sites until given per-site context — the
discipline catching fixture blind spots at build, exactly its job);
full-shape **8/8 worlds, every terminal** (DEEPENS / REPLICATES /
RELOCATES / LONE-DRAW, gate-1 ID, all-void ID, void-discloses-and-
proceeds, fired-void-wall-clean); referent battery
`verify_referents_3c` **10/10 on the real trees** (frozen-file sha
pins; stream-map continuity with exp3's committed map; exp3's 16
cells recompute; fires table = pinned verdict record 16/16; fired
address = item 436/seed 0/draw 6 with a length-4 answer; twin record
0 fires over 512,000 + 64,000 draws; §4 item pins; 1000-item
prompt-leak scan clean; power tables byte-stable). Glue smoke built
per stop-#1's standing rule (padded-vocab sampler + quantity-free
real-config width check, both sizes, both pass). Committed artifacts:
`stream_map_3c.json` (80 entries, s0–s3 byte-equal to exp3's map,
seed-4/15 golden literals), `power_3c.json` (quote check disagrees on
exactly the three ledgered doc slips), driver + watcher + runners,
FREEZE_CHECKLIST skeleton with the adversarial assignment and the
candidate surfaces this build did not attack. **INVARIANT HELD: no
model contact, no new sampled quantity, any cell, any seed** — the
only real-tree reads were committed records through frozen loaders.
Three design-doc arithmetic slips (gate-1 volume; luck floor + gap;
LONE-DRAW silence probability) ledgered below with corrections for
Michael to ratify at the freeze; no accepted dial touched.

**2026-08-17 — THIRD DOC ARITHMETIC SLIP, found while building the §7
tables (extends reading 2).** §7's "LONE-DRAW at ~1-in-3 even if the
true rate is 1e-6" is the detection probability mis-assigned to its
own complement: P(zero new fires at the fired cell | p = 1e-6,
n = 384,000) = e^(−0.384) = **.68 — two in three**, not one in three.
LONE-DRAW is ~1-in-3 only at a true rate ≈ 2.9e-6. Recorded with
`agrees: false` in `power_3c.json` (`doc_quotes_check`) alongside the
luck-floor and gap-factor slips; every other §7/§8 quote agrees with
the frozen code (detection .9502/.5361/.3188 at 7.8e-6/2e-6/1e-6;
len-4 stratum n 148,992, observed rate 2.0135e-5, detection .9503;
pooled zero bound 5.851e-6 = 4.00× exp3's 2.340e-5; LONE-DRAW pooled
point 1.953e-6; len-5 geometric rate 7.744e-7, pooled detection
.1157). Doc correction at the freeze, direction unchanged: silence is
even weaker evidence than the doc claimed.

**2026-08-17 — BUILD SESSION OPEN (session 2 of 3).** Design
ACCEPTED AS DRAFTED at `experiment-3c-design.md` (2043c26, all six
dials ruled). This session builds doc Open items 1–8. INVARIANT: no
new sampled quantity for any real cell before tag
`exp3c-preregistered`; the gate-1 single-cell rehearsal at the freeze
is the only sanctioned model contact. Everything below is declared
BEFORE implementation; the freeze session ratifies or amends.

## Readings declared before implementation (freeze to rule)

1. **Gate-1 volume (doc correction needed).** The doc's §3 says
   re-derivation volume "5 × 500 × 64 = 160,000 draws" and §2 says
   "128,000 committed draws". The committed record says: the four
   scored cells carry 64 seed-0 draws/item (4 × 32,000 = 128,000)
   and ctrl_copy/1b carries **8** seed-0 draws/item (4,000) — exp3's
   `DRAWS_PER_SEED` = 64 reversal / 8 control. A 64-draw ctrl_copy
   re-derivation would not be byte-comparable to anything committed
   (chunk plan (8,) vs (16,16,16,16) consumes the generator
   differently). Gate 1 is built against the committed record:
   **132,000 draws, zero tolerance, all five cells.** The doc's two
   volume numbers are arithmetic slips to correct at the freeze; the
   dial (zero-tolerance byte re-derivation of seed-0 across the 5
   gate cells) is untouched.
2. **Luck floor (doc correction needed).** 26^-4 = 1/456,976 =
   **2.19e-6**, not the doc's "≈ 1.5e-6"; the gap to the fired
   stratum's observed 2.01e-5 is **~9.2×**, not "~13". The corrected
   numbers make the §8 disclosure slightly weaker, i.e. more honest.
   `compute_power_3c.py` computes the floors from code and records
   the doc-quote disagreement with `agrees: false` rather than
   silently absorbing it (exp3's convention).
3. **Leak-void route (§6.3 wording made executable).** A new fired
   draw is VOID iff its item's normalized answer occurs case-folded
   in the item's own rendered prompt (the leak class the items rule
   out by construction). "Both rungs' fires void → INSUFFICIENT_DATA"
   is implemented as: at least one new fire existed AND every new
   fire across both rungs is void. Partial voiding is a disclosed
   finding and adjudication proceeds on the surviving fires; zero
   new fires leaves the gate vacuous and LONE-DRAW proceeds. Voided
   fires are disclosed verbatim with addresses either way.
4. **The standing twin referent, executable.** exp3's committed twin
   record re-asserted at every load: all 8 untrained cells recompute
   to 0 full-string fires — 512,000 reversal-twin draws (4 cells ×
   128,000) plus 64,000 control-twin draws (4 cells × 16,000). (The
   doc's "0 fires / 512,000 twin draws, 8 cells" conflates the two
   groups; the executable form checks both.) Cited in the verdict
   record; any recompute disagreement is a hard error (the referent
   moved), not a verdict.
5. **Adjudication reads NEW non-void fire counts only.** The four
   worlds branch on (fired-cell-new-fires > 0, any-wall-new-fires >
   0) after leak voiding. Pooled 1024-draw rates, per-seed tallies,
   length strata, mean draw length, and the pooled-vs-new comparison
   are computed and disclosed in full but no verdict branch reads
   them (§5 "descriptives, never adjudicated"; no trend test).
6. **exp3-side referent asserts (hard errors, not verdicts).** At
   load: (a) the recomputed full-string count and draw count of
   every one of exp3's 16 sampling cells must equal the committed
   `exp3/results/verdict.json` fires table; (b) the four scored
   cells' fire ADDRESSES, re-extracted from exp3's committed raw
   draws, must be exactly {reverse_string/1b: [(item 436, seed 0,
   draw 6)]} and empty elsewhere; (c) the fired item's answer length
   must be 4 (the stratum the §7 length-4 numbers assume).
7. **Stream-map continuity.** `stream_map_3c.json` covers the 5
   gate/scored cells × all 16 seeds (0–15) under exp3's exact
   formula and namespace ('exp3|…', deliberately unchanged). Its
   s0–s3 entries must equal exp3's committed `stream_map.json`
   entries for those cells — asserted executable at load and pinned
   with golden literals (including seed-4 and seed-15 values) in the
   fixtures. One formula governs the whole pooled set.
8. **New-cell record shape.** `results/sampling/{size}_trained/
   {rung}.json` + `.draws.jsonl.gz` in exp3's exact runner layout,
   with `seeds: [4..15]`, `draws_per_seed: 64`, `k_total: 768`,
   dtype float32, and per-seed convenience tallies the analyzer
   recomputes from raw draws (both trees) and refuses on
   disagreement. Gate-1 comparison records at
   `results/gate1/{size}_trained/{rung}.json`: draws_compared
   (32,000 scored / 4,000 ctrl), n_diffs, every differing draw
   verbatim with (item, seed, draw) address, and the sha256 of the
   committed exp3 draws file compared against. A gate-1 record
   claiming 0 draws compared is valueless and refused (3a's class).

## Layout + storage audit (doc Open item 6)

```
experiments/exp3c/
  analyze_3c.py            frozen analysis: two-tree loaders, verdict tree
  rederive.py              gate-1 byte re-derivation (pure comparator + cell runner)
  compute_power_3c.py      §7 exact tables from the frozen code → power_3c.json
  stream_map_3c.json       committed seed-extended map (5 cells × 16 seeds)
  run/campaign_3c.py       tier-per-process driver (gate1 tiers before sampling)
  run/run_cell_3c.py       cell runners (imports exp3's frozen sampler + helpers)
  run/commit_watcher.sh    per-cell committer (exp3's pattern, exp3c paths)
  tests/                   fixtures, full_shape (both trees), mutation_check
  results/sampling/{410m,1b}_trained/{rung}.{json,draws.jsonl.gz}   NEW draws
  results/gate1/{410m,1b}_trained/{rung}.json                       comparison records
```

Storage: exp3's committed reversal draws measure ~10.2 B/draw
gzipped (1,303,456 B / 128,000 draws, reverse_string/1b). New volume
4 cells × 500 items × 768 draws = 1,536,000 draws ≈ **15.7 MB gz**
(doc's ≈13 MB is the right order; measured coefficient recorded
here). Gate-1 re-derivation draws are DISCARDED after comparison —
only the comparison records (KB-scale JSON) persist. No new twin
draws, no mass tree, no redecode tree.

## Provenance-asserted imports (doc Open item 1)

Imported, never copied: `experiments.exp3.sampler` (sample_item,
stream_seed — the frozen generation law), `experiments.exp3.
analyze_3` (SEEDS, DRAWS_PER_SEED, PROBE_SIZES, REVERSAL_RUNGS,
score_first_char, clopper_pearson, cp_upper, load_sampling_cells,
load_gate2_referents, items_sha_referents, load_verify),
`experiments.exp3.run.run_cell` (load_capability, _load_model,
write_draws, per_seed_tallies, _provenance, _assert_module_
provenance — 2c's harness wins the `harness` name, exp2b supplies
`models`, both hash-asserted by path exactly as exp3 does). exp3's
`run/preflight_paths.py` gates each size at campaign launch,
unmodified.
