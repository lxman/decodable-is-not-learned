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
5. **Letter-support rule for the §5 statistic (declared at item-3
   build, before the analyzer exists).** §5 defines w̃ over "answer
   first letters" and stores m_i(c) for c ∈ a–z; the competitor sum
   Σ w̃_c m_i(c) is therefore computable exactly when every answer
   first character in the rung lies in a–z. That holds for both
   reversal rungs and ctrl_copy (random lowercase strings). It cannot
   hold for clock24_d999, whose answers begin with DIGITS — masses the
   §5 stored unit does not carry. Reading: the sign test is computed
   over the empirical letter support; a rung whose support leaves a–z
   records sign_test computable=False, significant=False, p=1.0,
   n_eff=0 with the reason disclosed. Consequences: gate 5's
   mass-significance arm is inert on clock24's twins (its verified
   full-string arm and gate 3's coherence check — which read only
   label_mass and draws — remain live), and clock24 keeps its §6 role
   (gates and descriptives, the agreement quadrant) untouched. An
   ADJUDICATED cell whose sign test is not computable is a hard error,
   not a verdict: the §4 sha pin makes that unreachable except by
   battery corruption, and a vacuous statistic must never adjudicate.
   Extending the stored vector to digits was considered and rejected
   as an amendment (§5's stored unit is the a–z vector); the freeze
   may widen it if the adversarial read prefers.
6. **Gate-1 CP form.** §6.1's "pooled sampled full-string rate's 95%
   CP lower bound" is read as the LOWER END OF THE TWO-SIDED .95
   Clopper–Pearson interval (the program's reporting convention since
   1c), computed on the analyzer's own recomputed verified count over
   the ctrl_copy cell's pooled 4 × k draws, per probe size.
7. **Cross-battery pins.** Every exp3 cell (mass, sampling, redecode)
   must carry the rung's single items_sha256 pin — the §4 referent
   from 3b's records — and its probe_labels/answers arrays must equal
   the referent's, with n agreeing; any disagreement is a malformed
   battery (hard error before gates). The runner already derives all
   three from the sha-pinned item files, so on an honest campaign
   this can only fire if a record was hand-edited or half-copied.
8. **Eval-size mass cells take no significance test** — 3b's scope
   rule, §9's words ("descriptive; no verdict branch reads it"):
   significant is recorded as None there, no sign test is run, and
   the scale trend ships as a mean-label-mass descriptive per size.
   The mutation suite pins the scope in both directions.
9. **Cell-level coherence bracket (completing reading 2).** Gate 3
   compares the cell's recomputed sampled FIRST-CHAR success count
   (3b's first_char against the item's label, over n = the cell's
   total draws) with the bracket [mean_i m_i(y_i),
   mean_i (m_i(y_i) + r_i)] — the mean over the cell's items, which
   is the population rate the pooled equal-draws-per-item count
   estimates. Disjointness at the §6.3 CP level is incoherence;
   computed and disclosed for all 16, ID trigger on the 4 adjudicated
   (reading 2).

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

**2026-08-15 — mass-module findings (Open item 1), for the freeze
read.** (a) The real vocabulary has **340** whitespace-class ids, not
§5's "handful" — every multi-space run token. Cost model updates (item
7's audit quantifies); the operationalization is unchanged: every
whitespace-only token expands at depth 2, no thresholding, since a
threshold deletes tail mass and tail mass is the question. (b) Two of
the 340 are the tokenizer's SPECIAL ids (eos/pad), whose
skip-special decode is ''. Declared reading: special ids are
**terminal**, not whitespace-path — the sampled channel stops at EOS
(generate's semantics, which produced 3b's committed continuations),
so no character ever follows; routing their mass through depth 2 would
credit letter paths sampling cannot realize and manufacture a gate-3
incoherence out of the instrument's own bookkeeping. Terminal mass
joins neither letter mass nor residual and is disclosed per item as
its own bucket. §5's "whitespace-only token" language never covered
specials (their decode is empty, not whitespace); this is a reading,
not an amendment, and the sampler stops at EOS to match. Fixtures pin
both directions.

**2026-08-15 — build session 2a closes; build CONTINUES in a fresh
session (2b) before any freeze.** Landed and pushed this session:
Open items 8 (referents, 14/14), 1 (mass module), 2 (sampler + gate-4
determinism at fp32 + the stack-defect fence), 5+7 (runner,
tier-per-process driver, storage audit), and the FREEZE_CHECKLIST
skeleton. **Carried to build session 2b: Open items 3 (analyze_3's
statistic + verdict tree + full fixture suite one-per-provision both
directions + mutation testing), 4 (full-shape batteries to every
terminal), 6 (exact power tables from the frozen code).** Reason for
the split: the fp16-MPS defect investigation consumed most of the
session, and the verdict tree is precision code this program does not
write at the tail of a long context — 2c's and 3a's class defects
both lived in exactly that kind of code. The freeze remains a
separate, later session that opens adversarially (the
design|build|freeze boundary is unchanged; the build merely spans two
contexts). No mass or sampling quantity has been computed for any
real cell; the invariant held all session.

**2026-08-15 — Open items 5+7 complete: runner, tier-per-process
driver, storage audit.** `run/run_cell.py`: three cell kinds behind
one executable dtype-policy table (`cell_policy`, fixture-pinned);
redecode is 3b's fp16 generate path verbatim (gate 2 must reproduce
3b's bytes); mass fp32 depth-2 with the 12b fp16 depth-1 exception;
sampling fp32 probe-sizes-only with every raw draw stored
(gzip jsonl, duplicate-refusing reader) beside a summary record whose
per-seed tallies use 2c's verify and 3b's first_char — convenience
copies the analyzer recomputes from raw and refuses on disagreement.
`run/campaign_3.py`: committed at build; tier-per-process (one child
per (kind, size, mode), one model load, exit frees the cache); §10.3
order fixture-pinned (re-decode → mass ladder, twins first, sizes
ascending → twin sampling → trained sampling 410m before 1b);
preflight gates every (size, dtype) before its first tier and STOPS
the campaign on failure. Dry-run verified: 15 tiers, 60 cells, the
policy visible per tier. Storage audit (Open item 7): 1,152,000 draws
(8 reversal cells × 128,000 + 8 control cells × 16,000) ≈ 10–15 MB
gzipped across 16 files; 28 mass cells × 500 item-vectors ≈ 10 MB;
re-decode ≈ 3 MB — everything committed per cell, nothing discarded.
Suite: 68 tests green.

**2026-08-15 — STACK DEFECT FOUND AND FENCED: fp16-MPS batched
inference is broken on this machine; the campaign dtype policy is
fp32.** The build's most consequential finding, in the order the
evidence arrived:

1. *Symptom.* Gate 4's determinism fixture (seeded sampling, synthetic
   prompts, pythia-410m fp16 MPS, two processes) was NOT
   byte-identical: all 16 draws of one prompt differed at their first
   sampled character; the other two prompts reproduced exactly.
2. *First root cause.* The fp16-MPS FULL-LOGITS multi-token forward
   returns garbage on this stack — near-uniform distributions (top-1
   ≈ 1/50304) and hidden states orthogonal to fp32 truth — for every
   prompt tried, while `generate`, `logits_to_keep=1` forwards, and
   fp32 anything are sane (fp32 MPS == fp32 CPU exactly in every
   probe). The divergent prompt was garbage racing; the "stable" ones
   were byte-stable garbage. 3b was never exposed: HFRunner only
   calls `generate`. Both instrument modules were switched to
   `logits_to_keep=1` (they only ever need last-position logits) and
   the fixture went byte-identical — but that determinism was
   determinism of a still-wrong computation, exposed next.
3. *Second, worse root cause.* An fp16 campaign-dtype variant of the
   glue equality fixture failed on the tiny synthetic model with one
   saturated row. Chasing it: in a BATCHED single-token cached step
   (the shape of every depth-2 mass pass and every sampling step), at
   fp16 on MPS, on the real 410m, **rows 1–15 of 16 are garbage and
   only row 0 is correct** — reproducibly across repeats, top-1 values
   quantized to 1.0, 1/3, 1/4, 1/6 (overflow ties); the corruption
   follows row index, not token id; forcing the expanded cache
   contiguous changes nothing; the tiny model reproduces it only
   state-dependently. fp32 rows all match batch-1 references to
   <1e-4; bf16 was clean on the tiny model but is a different-weights
   choice and was not pursued.
4. *Policy (freeze to ratify).* Mass and sampling run at FLOAT32 — an
   EXACT upcast of the same fp16 checkpoint values 3b probed, so the
   same-weights claim survives with strictly more accurate arithmetic;
   compute-precision choice disclosed in the verdict. The gate-2
   greedy re-decode stays fp16 + `generate` — 3b's exact path, the
   sane one, reproducing 3b's exact bytes. Sizes through 6.9b fit
   fp32 on 48 GB tier-per-process. **12b does not fit fp32** (≈47.6
   GB): its four mass cells — descriptive-only, no verdict branch
   reads them — run fp16 through the verified-sane batch-1 keep1
   prompt forward at DEPTH 1, with the whole whitespace-path mass
   folded into the residual, i.e. a wider honest bracket, disclosed
   per cell. Budget revision: fp32 roughly doubles sampling time
   (≈28 h across the two probe sizes; two to three nights, per-cell
   resume, unchanged Sparks policy).
5. *Guards.* (a) `run/preflight_paths.py`, committed: per-(size,
   dtype) verification on synthetic prompts — every row of a
   heterogeneous-id batched step must match its batch-1 reference —
   gating every campaign tier before any cell runs; 410m/float32
   passes (committed `preflight_410m_float32.json`), 410m/float16
   FAILS as expected. The full-ladder preflight is a campaign-start
   step and a freeze checklist item. (b) The gate-4 determinism
   reference is re-committed at fp32 (two processes byte-identical;
   the fp16-era reference was byte-stable garbage and was replaced
   the same day — recorded in `determinism_check.json`). (c) At
   campaign, gate 1's ctrl mass sign test cannot pass on a flat or
   corrupted distribution. (d) Nothing in exp3 reads a full-logits
   multi-token forward; both modules carry the load-bearing comment.
   Corroboration kept in the record: draw 0 of each fixture cell (row
   0 — the only sane fp16 row) reproduces byte-identically between
   the fp16-era and fp32 references; the corrupt rows all changed.

**2026-08-15 — Open item 1 complete: mass module.** `masses.py`: token
classification routes through `first_char` itself (one whitespace/
casefold definition for both instruments — gate 3 can only ever catch
code-path drift, never a definition mismatch this module introduced);
depth-2 expansion over every whitespace-only token, residual and
terminal buckets disclosed per item; the per-item stored unit carries
the full a–z vector, the label's own mass (digit labels included —
clock24's space), residual, ws-path and terminal masses. Malformed
distributions (wrong length, negative, not summing to 1, live
whitespace id with no depth-2 row) are refused, 3a's class. Model glue:
harness batch-of-one encoding (no pad, no BOS), prompt KV cache
expanded once to the 16-row chunk shape, single-token steps, crop
between chunks — the pinned transformers-5 stack has no legacy cache,
so the path is `batch_repeat_interleave`/`crop`, and its equality with
full re-forwards is fixtured to <5e-5 on CPU AND on MPS (synthetic
2-layer GPTNeoX over the real vocabulary; no real model touched).
Suite: 47 tests green (19 mass math, 5 glue, 23 referent surface).

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
