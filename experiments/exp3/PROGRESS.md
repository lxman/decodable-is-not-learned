# Experiment 3 — build ledger

Design doc: `experiment-3-design.md` (DRAFT — NOT FROZEN; committed
131737a, all sections approved by Michael including the mass-pairing
amendment). Three-session protocol, boundary = context clear (Michael's
pacing ruling, 2026-08-15): design | build | freeze. This file is the
running ledger; it opens with the build session and closes at
`exp3-closed`.

## 2026-08-15 — build session opens (session 2 of 3)

Scope: the doc's Open items 1–8. No freeze this session, no
`exp3-preregistered` tag this session; the freeze is a third session
that opens adversarially (cold re-read, assignment: find the class
defect).

**Invariant, standing until the tag:** no mass quantity and no sampling
quantity is computed for any real cell or model. Model contact this
session is limited to (a) the MPS seeded-sampling determinism fixture
on synthetic pinned prompts, (b) the untrained-twin state-dict
construction check at seed 0, (c) reads of committed records
(items_sha256 values, 3b cell records, floors, margins). Scoring 3b's
committed continuations with exp3's ported `first_char` (the gate-1
anchor recompute, .9940/.9940) reads no model and creates no new
quantity: those numbers are in 3b's closed record already.

Push-as-you-go authorized by Michael this session (2026-08-15).
Campaign-time per-cell push authorization is a separate §10.3 item,
reconfirmed at campaign time.

**Build-session readings of the doc, declared before implementation,
for the freeze session to ratify or amend:**

1. **Bracket ends (§5).** The residual is unattributed whitespace-path
   mass; the bracket on a cell's mass is [mass, mass + residual]. The
   upper-end sign test credits the whole per-item residual to the
   correct letter (s_i_hi = (m_i(y_i) + r_i) − Σ w̃_c m_i(c));
   competitors stay at their computed masses — the upper end is the end
   most favorable to the claim, which is the end a bracket must
   contain. **Adjudication (§6.6 "mass significant?") reads the
   computed lower end.** The upper end is computed wherever §5's rule
   fires (residual > .01 in an adjudicated cell) and lower/upper
   disagreement is reported as its own finding in the verdict record
   (§5's words). Reason: crediting unattributed residual to y_i by
   default would manufacture signal exactly the way 2c's chance floor
   did — the design's own §2.2 lesson, applied to this instrument.
2. **Gate-3 trigger scope (§6.3).** The coherence check is computed and
   disclosed for all 16 sampling cells at the §6.3 level (exact
   two-sided CP at α = .01/16 against the cell's mass bracket); the
   INSUFFICIENT_DATA branch triggers on the four adjudicated cells,
   which is §6.3's own wording ("in any adjudicated cell") under §1's
   definition of adjudicated (reversal rung × probe size). A
   control-cell incoherence is disclosed in full and in practice also
   takes gate 1 down; widening the trigger to all 16 is a freeze
   decision if the adversarial read wants it.
3. **All-ties cell.** If every s_i in a cell ties (n_eff = 0), the sign
   test cannot fire: significant = False, p recorded as 1.0, n_eff = 0
   disclosed. A cell with no usable items argues nothing either way;
   the post-tie power recompute (§7) makes the blindness explicit
   rather than letting a vacuous test adjudicate.
4. **Sampling stream map (§3 "streams committed per (cell, seed)").**
   Refined to a substream per (cell, seed, item): generator seed =
   first 8 bytes of sha256("exp3|{rung}|{size}|{mode}|s{seed}|i{item}"),
   draws for that (item, seed) taken from that generator in a fixed
   chunk partition (16 rows per forward batch, chunks in index order),
   so every unit reproduces independently of batch composition and
   restart order. The cell is the resume unit (3b's). The map is
   frozen in `sampler.py` and dumped to `stream_map.json` at build.

Layout decided at build (Open item 7), so no later choice can shade it:
`results/mass/{size}_{mode}/{rung}.json` (28 cells; per-item 26-letter
vectors, label-char mass, residuals), `results/sampling/{size}_{mode}/
{rung}.json` (16 cells; per-seed tallies, per-item pass counts) with
raw draws beside it in `{rung}.draws.jsonl.gz` (every draw, nothing
discarded), `results/redecode/{size}_{mode}/{rung}.json` (16 gate-2
cells, 3b record shape). Only canonical subdirectories are ever read
back (3b's load_cells rule), so verdict artifacts at `results/` top
level can never be re-ingested as data.

### Entries

**2026-08-15 — Open item 8 complete: referents verified, 14/14.**
Scaffold committed (`analyze_3.py` referent surface, `tests/`,
`verify_referents.py`). All §4 referents exist with defined values:
gate-2's 16 probe-size 3b cells load with full structural checks; each
rung's `items_sha256` agrees across its four 3b cells AND equals the
hash of the item file exp3 will load (2c tree ×3, 2b tree ×1); gate-1
anchors hold (2c inclusion 480/490 of 500; exp3's ported `first_char`
reproduces 497/500 = .9940 from 3b's committed ctrl_copy continuations
at both sizes — the port validated against a closed number); floors
survive the sha pin + recompute-assert; margins round to the doc's 4dp
quotes; and the seed-0 twins construct deterministically on CPU with
state hashes equal to 3b's recorded `335d46b7…` (410m) and `fa3fe1d2…`
(1b). Fixture suite opens at 23 tests, loader/helper surface, both
directions. No mass or sampling quantity computed for any real cell.
