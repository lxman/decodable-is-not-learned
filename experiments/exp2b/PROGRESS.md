# Experiment 2b — Progress Ledger

Traceability ledger (process rule 8), from day zero. Design doc:
`../../experiment-2b-design.md` (status DRAFT, dial review accepted 2026-07-17;
freeze commit + tag `exp2b-preregistered` lands at M0 completion per Michael's
standing authorization at the Exp 2 closeout).

## Milestones

| Milestone | What | Status | Tests |
|---|---|---|---|
| M0 | Battery item files + oracles + starving splits + feasibility + `analyze.py` + power table; FREEZE | tranche 1 built (see below) | 21 ✓ |
| M1 | Inclusion: argmax at 410m/1b on all candidates; scored battery fixed | — | — |
| M2 | Gates: known-absent (starved untrained), known-present, shuffled (binomial tolerances), ctrl_copy argmax | — | — |
| M3 | Stage 1: starved probes at 410m/1b, 5 seeds; scores committed + TAGGED | — | — |
| M4 | Stage 2: argmax at 2.8b/6.9b/12b | — | — |
| M5 | Frozen analysis; verdict; report | — | — |

## M0 build, tranche 1 (2026-07-18) — split machinery + non-wordlist specs

**Design revision applied first** (doc §2 revision note, same date): #3/#4
retargeted to middle-digit-of-result (carry/borrow counts are additive-threshold
composable — a linear probe expresses [Σf(tokᵢ) ≥ θ] via per-token scores and
generalizes across held-out pairs; the mod-10 wrap is not so expressible);
#10 (time arithmetic) to reserve, same mechanism, no clean repair. General rule
recorded in the doc: every field-4 argument must show a non-additive wrap or
interaction.

**Split machinery (`splits.py`):** basis = per-item component tuple; starving
split holds out values per component; val = ALL components held out, train =
ALL kept, mixed dropped. `shared_components` mode draws ONE holdout set over
the union for specs whose components share a value space (gcd operands, sort3
members) — per-position holdouts leak there. Class coverage on both sides
enforced by seeded rejection (≤200 redraws); feasibility = the design's field-5
minima for all 5 seeds, committed per capability inside the item file.

**Build-time catches (each would have been a silent confound):**
- gcd/sort3 positional leak → `shared_components` (above).
- reverse_string basis corrected to the FINAL BPE CHUNK per the design table
  (whole-string holdout starves nothing — random strings share final chunks);
  `_final_chunk` uses the pinned 410m tokenizer (one tokenizer suite-wide).
- bin2dec widened to 8–11 bits (6-bit space = 32 unique questions < 2500) and
  div7 to ≤9999 (990 < 2500) — feasibility, not difficulty; mod-wrap
  composability arguments unaffected.
- month_offset (36 questions) and letter_half (26) CANNOT meet the uniqueness
  rule at full counts: kept in SPECS, expected to EJECT at M0 generation
  (`items/ejections.json`), per the design's field-5 ejection path. An earlier
  draft set `allow_dupes=True` on both to dodge the gate — reverted; duplicate
  eval items would break the CP bounds' independence assumption for scored
  capabilities.

**Conventions:** BASE_SEED=20260718, per-spec seed = BASE_SEED + position in
the FULL spec list (ejections never shift other streams); no sys.path
insertions (exp2's shadowing lesson); oracles AND basis extractors parse
question text only; `models.py` = exp2's SHA-pinned loaders verbatim.

**Tests: 21 pass** — split invariants (value-disjointness, class coverage,
shared-mode no-positional-leak), oracle+basis agreement per generating spec,
small-space ejection behavior, tokenizer-basis suffix property, and the
design's core claim executed directly: a per-value lookup table fit on train
scores 0.0 on starved validation.

## M0 build, tranche 2 (2026-07-19) — wordlists + word/semantic/relational specs

**Wordlists** (`battery/wordlists.py`, exp2's file + 2b additions, all
integrity-checked in-session): CATEGORIES_2B 10×16 (no cross-category member),
ANTONYMS 117 pairs (unique cues), RHYME_FAMILIES 30×8 (every word verified
against its family suffix), CAPITALS 116 (well-known subset, deliberate),
NAMES_2B 40 unique, IRREGULAR_PLURALS 40 / IRREGULAR_PAST 60, UNIT_PAIRS 16
(powers 1–3 balanced 5/5/6).

**Specs** (`battery/generators_t2.py`, 15 more → SPECS = 30): design revision
#2 applied (doc §2 second note — choice formats for #20/21/22/25, #18 parity
retarget, structural-pattern bases for #27/#28). One-way import only
(generators.py imports t2 at its bottom; a two-way import was order-dependent
— caught when the smoke test imported t2 first).

**Build-time catches, tranche 2:**
- **Mention-order canonicalization collapses entity_track's pattern space:**
  raw 3⁴=81 transfer patterns → 14 canonical (first transfer is always
  mention-0→mention-1), under the 15-value minimum → 5 transfers (41 patterns,
  verified empirically over 3000 draws).
- **Uniform value holdout starves rare label classes** (unscramble/caesar
  first letters): added `stratify_by_label` split mode (per-label-group
  holdout, k=1, refuses single-value classes) AND letter-stratified
  generation so no rare class enters the items — exp2's lesson on both sides.
- The `_quick` test helper dropped new SplitParams fields on rebuild →
  `dataclasses.replace` (a silent-drop class of bug).
- cat_parity shot answer was wrong on first draft (hammer, saw, oak = 2 tools,
  not 3) — caught on self-review; the oracle-agreement gate would also have
  caught it at generation.
- deduce3/entity_track probe labels briefly carried a "pos|pattern" packing
  that polluted the class space — label is the position alone; the basis_fn
  recomputes the pattern from text (independence discipline).

**Tests: 36 pass** (oracle+basis agreement for all non-tokenizer specs at
reduced counts, both tokenizer bases against the real tokenizer, ejection
behavior for all five small-space candidates, split invariants incl. the new
stratified mode).

**Tranche 3 (next):** `probe_starved` (group-split probe reusing the frozen
stats primitives; records null SD for the floor-signature check);
`analyze.py` (MIN_N=20, ALPHA_PERM=0.01) + MC power table; full-count
generation under the canonical venv (feasibility ejections recorded);
pre-freeze gate rehearsal on exp2's activations; FREEZE.
