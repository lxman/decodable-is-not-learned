# Experiment 3c — build ledger

**2026-08-18 — CLOSED: VERDICT DEEPENS (tag `exp3c-closed`; frozen
analyze_3c run ONCE on Michael's go, full record
`results/verdict.json`, human summary `results/VERDICT.txt`,
projection graded in `results/retrospective.md`).** The fired cell
fires again — 9/384,000 new, pooled 10/512,000 = 1.953e-5, CI
[9.37e-6, 3.59e-5], new-draw point 3.0× exp3's — AND the
reverse_string/410m wall falls (3/384,000, all len-4 at 9.2× the
luck floor); rev_string7 stays silent at both sizes (pooled zeros
≤ 5.85e-6, 4.0× exp3's resolution). Zero leak-voids; twin referent
0/512k+64k re-asserted; gate-1 132,000/132,000 byte-identical.
Twelve new fires disclosed verbatim: len-4 dominant (10), len-5 one,
and ONE len-6 — item 200 'rxxxxd', the projection's named miss,
whose repeated-letter run collapses the joint path cost (~2,700×
above its stratum's luck floor; the geometric length anchor is too
coarse for structured answers — successor rate models should
condition on answer compressibility). Item heterogeneity is the
unnamed texture: item 123 fires at BOTH sizes (4 of 12 fires), item
447 twice on one seed. Projection: verdict/gates/pooled-numbers HIT
exactly; len-6 the named miss, fired; mean-length prediction
ungradeable (exp3 committed no referent). One stop (verify
totality, ratified), pre-committed change UNSPENT, zero attrition,
12.0 h. Next: essay + experiments.md signature-2 updates per the
DEEPENS world; methods-paper criterion-totality note (stop #1);
supporting-repo re-extraction gains the exp3 AND exp3c rounds
together; staged successors (rank prediction; entropy-conditioned
rate models) remain separate experiments.

**2026-08-18 — CAMPAIGN COMPLETE (run 2: 433.1 m; runs 1+2 ≈ 12.0 h
against the ~14–15 h projection). One stop (ledgered below, fix
ratified), zero attrition, all 13 result files committed and pushed
per cell by the watcher, both watchers exited on their terminal
lines.** Resume determinism confirmed executable: reverse_string/
410m's re-run decompressed draw stream is BYTE-IDENTICAL to run 1's
pre-fix committed stream (git e0c8916 vs working tree; only the gzip
container's mtime header differs), including the crasher draw
reproduced exactly at item 395/seed 12/draw 22 — scored False by the
total wrapper this time instead of killing the tally. The runner's
per-cell convenience lines (visible in the campaign log, as in
exp3): rev_string7 0/384,000 at BOTH sizes; reverse_string
3/384,000 at 410m and 9/384,000 at 1b. These are pre-void raw
tallies printed by campaign code; the frozen analyzer recomputes
everything from raw draws and adjudicates. NOTHING ANALYZED: per
§10.4 the frozen script runs once, on Michael's go, after this
projection.

## Verdict projection (ledgered BEFORE the frozen analysis; written
## with the runner's convenience tallies visible, exp3's precedent;
## graded in the retrospective)

- **Projected verdict: DEEPENS** — fired-cell new fires > 0 (9) AND
  ≥1 previously walled cell fires (reverse_string/410m, 3): the
  sampled channel's reach grows with budget in both rate and extent;
  signature 2's resolution parameter measurably load-bearing (§1).
- Gates all clean: gate-1 five records 0 diffs (committed); frozen
  pins, stream map, §4 pins, cross-tree consistency pass;
  stored-vs-recompute tallies agree at all four cells (the two
  run-1-era records carried zero crashers, so the old and total
  verify tally identically there); **zero leak-voids** (the freeze
  scan proved no answer occurs in any committed prompt, and the
  prompt source is pinned).
- Pooled rates: fired cell 10/512,000 = 1.953e-5 (exp3's 1 + new 9);
  reverse_string/410m 3/512,000 = 5.859e-6 (exp3 0 + new 3);
  rev_string7 pooled zeros at both sizes, CP95 ≤ 5.851e-6 each.
- Finer predictions, falsifiable at analysis: (1) new fires
  concentrate in the length-4 stratum; length-6 stays zero;
  length-5 carries at most a small tail (0–2). (2) Per-seed spread
  consistent with a thin Poisson across the 12 new seeds — no
  single seed carries the bulk of the 9. (3) Mean new-draw lengths
  sit near exp3's committed values (stable stack). (4) The len-4
  stratum rates sit meaningfully ABOVE the 26^-4 = 2.19e-6 luck
  floor printed beside them (≈9× at 410m, ≈25× at 1b if
  len-4-concentrated), while rev_string7's zeros sit beside a
  26^-7 ≈ 1.25e-10 floor — the direction §8 said a computed path
  should move: luck falls 26× per character, the observed profile
  falls with length but the len-4 channel is far above luck.
- Misses that would matter: any length-6 fire (strains the geometric
  story), heavy single-seed clustering (stream questions, though
  fires are exact-verified), ANY void (the by-construction guarantee
  failed), or a stored-vs-recompute disagreement (runner/analyzer
  split — instrument, not data).

**2026-08-18 — STOP #1 RULING: APPROVED (Michael, "approved").**
Option (a) — the 3c-local total wrapper — implemented as
recommended: `load_verify_3c` in `analyze_3c.py` resolves 2c's
harness with `load_verify`'s exact path discipline and composes the
criterion from 2c's own frozen `normalize_answer`, guarding ONLY the
draw side (`except IndexError → False`; a draw whose normalization
is whitespace-only cannot equal any letters-type answer). The
answer side stays UNGUARDED on purpose: a crashing answer is a
broken battery and must remain a hard error. Call surfaces switched:
`run()`'s verify_fn, the two loader defaults (`load_new_cells`,
`extract_fire_addresses`), the runner's tallies (new 3c-local
`per_seed_tallies_3c` — exp3's plain-loop tally verbatim with
verify_fn injected, preserving the two-implementation independence
of stored-vs-recompute), the referent battery's exp3-tree load, and
full_shape's `run_battery` (mirroring `run()`). exp2c's and exp3's
frozen files untouched. Fixtures: totality + identity-off-the-crash-
class spot checks + answer-side hard error + runner-tally crasher
case; mutation gains the guard both directions (crasher re-raises;
wrapper never fires). ACCOUNTING, per the posed default Michael
approved: a LEDGERED STOP in exp3's stop-#1 precedent — the one
pre-committed change remains UNSPENT (if Michael intended this to
spend the change, one word reverses this line before close-out).
Acceptance bar for resume: referent battery 10/10 with the 16/16
fires table, address pin, and twin record reproduced IDENTICALLY
through the wrapper. **BAR MET, all cold: suite 96 passed
(pycache-cleared; 93 + the three stop-#1 fixtures); full-shape 8/8
terminals through run()'s own verify producer; referent battery
10/10 — the 16/16 fires table, the (436, 0, 6) address pin, and the
512k+64k twin record reproduce identically via verify_3c, the
executable proof of verdict-preservation on the whole committed
corpus; mutation KILLED 58/58, baseline clean (56 + the guard both
directions). Campaign relaunched: reverse_string/410m re-runs its
deterministic streams and completes the record through the total
tally; then sampling/1b. Watcher relaunched, per-cell push
authorization standing.**

**2026-08-17 — CAMPAIGN STOP #1 (hour ~4.8 of the campaign; the
driver stopped itself; NOTHING SCORED, no verdict quantity computed,
the analyzer never ran).** 2c's frozen `verify` is PARTIAL on its
own input domain: `normalize_answer` (exp2c/harness.py:64,
`s.split()[0] if s else s`) raises IndexError when the normalized
string is truthy but whitespace-only by `split()`'s definition. The
reachable class: a first line whose content, after the FIRST
`.strip()` eats outer whitespace and the final punctuation-only
strip (`.strip(".!?\"' ")`) removes the wrapping, is bare non-space
whitespace INTERIOR to punctuation — `"\t"` being the canonical
member (synthetic repro: `'"\t"'`, `'.\t.'`, `' " \t " '` all
crash; `'"\t'` does NOT — the trailing tab is outer and the first
strip eats it). A T = 1.0 draw finally emitted one: **item 395,
seed 12, draw 22 of reverse_string/410m's new stream — the SOLE
crasher in 384,000 draws** (`' "\t"\n\nQ: Spell the string \''`,
disclosed verbatim; the model emitted quote-tab-quote then began a
new Q: block). rev_string7/410m's 384,000 new draws: zero. exp3's
committed reverse_string/410m stream: zero (executably re-scanned).
Every closed experiment's analysis COMPLETED over its full data, so
zero crashers existed in any committed stream — **the defect can
only raise, never return a wrong verdict; every closed verdict
stands untouched.** exp3's 1.34M-draw clean history was luck of the
streams, not totality.

**State at the stop, all banked and committed by the watcher:**
gate 1 ALL FIVE CELLS CLEAN — 132,000 draws re-derived, 0 diffs both
sizes (the stack byte-reproduces exp3's streams; the campaign's
biggest de-risk, done). rev_string7/410m sampling COMPLETE: 0
verified fires in 384,000 new draws (record + raw draws committed —
a wall at 3× exp3's per-cell resolution so far, adjudicated by
nothing yet). reverse_string/410m: raw draws fully written and
deterministic (the streams are a pure function of (cell, seed,
item)); the crash hit the CONVENIENCE-TALLY step after write_draws,
so the record is unwritten and skip-if-exists will re-run the cell
byte-identically. sampling/1b never started (tier order held).
Driver printed STOPPED; watcher swept and exited.

**Why the freeze missed it:** the adversarial read attacked the
criterion's SEMANTICS (format-crediting, the leak class) and the
glue's decode path; nobody fuzzed `verify` for TOTALITY over the
draw alphabet. 3a's lineage in a new costume: a frozen verdict
function partial on its own domain, waiting for entropy to find the
hole.

**Fix options prepared for Michael (the instrument is tagged-frozen;
no fix applied without his ruling):**

- **(a) RECOMMENDED — 3c-local total wrapper.** `verify_3c(pred,
  answer, answer_type)` in the exp3c tree: 2c's verify, with the
  crashing class mapped to False — a draw whose normalization is
  whitespace-only cannot equal any letters-type answer; garbage
  never fires. Applied at 3c's two call surfaces only (a 3c-local
  per_seed_tallies in the runner, replacing the exp3 import; the
  analyzer's verify_fn). exp2c's and exp3's frozen files UNTOUCHED.
  Verdict-preserving on every input that does not crash, by
  construction; proof made executable by re-running the referent
  battery through the wrapper — the 16/16 fires table, the address
  pin, and the twin record must reproduce IDENTICALLY. Regression
  fixture pins the class (wrapper returns False where bare
  harness.verify raises); mutation gains a guard mutant both
  directions.
- (b) Fix exp2c's harness in place — REJECTED as recommendation: a
  closed experiment's frozen tree, and the public supporting repo
  carries the extracted copy (drift).
- (c) Score crashing draws as attrition/excluded — REJECTED: drops
  data a total criterion scores fine, and complicates every count.

**Process question for Michael:** exp3's stop-#1 precedent was a
ledgered stop (instrument crash, fixed pre-data, pre-committed
change UNSPENT). This stop is the same shape — discovered
mid-campaign, nothing scored, fix verdict-preserving — but the fix
touches the frozen analyzer, so Michael rules whether it is a
ledgered stop or spends 3c's one pre-committed change.

**Resume plan once ratified:** implement (a) + fixtures/mutants;
cold re-run suite + mutation + referent battery (identity of the
16/16 recompute through the wrapper is the acceptance bar); relaunch
the driver (skip-if-exists: gate-1 and rev_string7/410m stand;
reverse_string/410m re-runs deterministically; then sampling/1b);
relaunch the watcher. Per-cell push authorization unchanged.


**2026-08-17 — CAMPAIGN LAUNCHED (post-tag). Per-cell push
authorization RECONFIRMED with Michael at launch (§10.3; "Launch
now, pushes authorized"), the freeze checklist's last box.** Driver
`campaign_3c.py` running tier-per-process in the committed order —
gate1/410m → gate1/1b → sampling/410m → sampling/1b, preflight per
size, skip-if-exists (the rehearsal's ctrl_copy/1b gate-1 record
stands as that cell's campaign record, exactly as preregistered);
`commit_watcher.sh` committing+pushing result files per cell.
Preflight 410m/float32 OK at launch; expected ~14–15 h. Analysis
does NOT run automatically: projection ledgered first, then the
frozen script once, on Michael's go (§10.4).

**2026-08-17 — FREEZE SESSION OPEN (session 3 of 3, adversarial).**
Cold re-read of `experiment-3c-design.md` and the whole exp3c tree
plus the imported frozen surfaces (exp3 sampler/analyze_3/run_cell,
2c harness verify/render_prompt/ITEMS_DIR resolution). Assignment:
find the class defect. Everything below is declared BEFORE any code
changes; amendments implemented after this entry, cold re-runs after
that, Michael's ratification before the tag.

## Freeze findings (declared before implementation)

**FINDING A — the session's class-defect finding (3a's lineage, one
level up): the leak gate's prompts are the ONLY verdict input with no
executable pin at analysis time.** Inventory of `verdict_3c` inputs:
new cells (items_sha256 pinned to the §4 referents, tallies recomputed
from raw draws), gate-1 records (shape/volume validated), exp3 cells
(recompute vs the sha-pinned committed verdict fires table + address
re-extraction), exp3 referent (sha-pinned file), sha_refs (3b's
referent records, cross-checked three ways) — and `prompts`, which
`run()` re-renders at analysis time from the LIVE exp2c/exp2b item
files with no hash check against anything. Design §2.1's own
death-proofing clause says every input is "an exp3-committed record
verified present at freeze **or produced by a frozen loader that
hard-errors on malformation**"; §4's header says "every input, a
committed value." `load_prompts` satisfies neither: an item file
drifted AFTER the campaign renders different prompts, and the leak
gate silently flips void determinations — a genuine fire
false-voided (a lone REPLICATES fire becomes INSUFFICIENT_DATA via
the all-void route; a partial false-void distorts adjudication
counts) with nothing anywhere to notice. The seam is invisible to the
whole battery by construction: the full-shape worlds INJECT synthetic
prompts, the two prompt fixtures and the referent-battery scan
validate today's files at freeze time, and no mutant touches
`load_prompts` — the production path is exactly the untested path.
Drift BEFORE the campaign is caught (the runner records the file's
sha and the shape check pins it); drift AFTER it was not.
**Amendment (no accepted dial touched — the criterion, quantifiers,
worlds, and §6.3 semantics are unchanged; this adds a refusal):**
`load_prompts(sha_refs, ...)` — sha_refs becomes a REQUIRED first
argument; the loader hashes the item-file bytes it actually resolved
and hard-errors unless they equal the rung's §4 pin, before
rendering. All callers updated (run, verify_referents, fixtures);
a drifted-pin fixture and a pin-dropped mutant added.

**FINDING B — gate-1 record trust surface, loop not closed.** The
gate-1 record stores `committed_draws_sha256` (what the runner
byte-compared against) and the loader refuses records that lack it —
but nothing ever compares it to the exp3 tree the analyzer itself
pools. The attestation "seed-0 regeneration is byte-identical to file
X" and the pooled bytes "file Y currently on disk" are never proven
to be about the same file; a post-campaign swap of an exp3 draws file
would keep a clean-looking gate-1 record while the pooled counts came
from something else (the fires-table recompute would likely trip on
counts, but continuity-of-bytes is exactly gate 1's job, and the
record's own field closes it for free). **Amendment (additive
refusal, same character as A):** `check_gate1_committed_shas(gate1_
records, exp3_root)` — sha256 of each of the 5 gate cells' committed
exp3 draws files must equal the record's field; called in `run()`
and in the full-shape battery path (whose synthetic gate-1 records
now carry the TRUE hashes of the synthetic exp3 tree, so every world
exercises the check); a doctored-sha fixture and a check-dropped
mutant added.

**2026-08-17 — RATIFIED BY MICHAEL, SAME DAY ("You have my
approval"): the three doc corrections, the findings A/B closures,
the tag, and the push of the freeze commits.** Corrections applied
to `experiment-3c-design.md` §2/§3/§7/§8 exactly as staged (gate-1
volume 132,000; luck floor 2.19e-6, gap ~9.2×; LONE-DRAW silence
.68 at 1e-6 with the 1-in-3 point relocated to its true rate
≈ 2.9e-6); Status header now FROZEN with the ratification recorded.
Readings 1–2 boxes and the A/B boxes checked. Tag
`exp3c-preregistered` on the ruling-complete commit; campaign launch
(and its per-cell push authorization, §10.3) remains a separate
explicit go.

**2026-08-17 — FREEZE COLD BATTERY COMPLETE (record below preceded
the ratification).**
Everything cold, fresh processes, pycache cleared: suite **93
passed** (89 + the findings' four); mutation **KILLED 56/56, baseline
clean** (52 + the findings' four, both directions; the first run's
tail clipped the count line — logically implied 56/56 via the absent
survivors block — and a full-capture re-run recorded the literal
line; both runs killed everything); full-shape **8/8 terminals**, now
through the finding-B loop closure; referent battery **10/10** on the
real trees through the pinned load_prompts; power_3c.json
**byte-identical** (sha 8d7bc741… before/after), quote check
disagreeing on exactly the three ledgered slips; glue smoke 2/2;
determinism fixture **twice in separate processes, byte-identical to
each other AND to exp3's committed reference** — the stack has not
drifted; empty-tree run **FileNotFoundError, exit 1, never a
verdict** (run before the rehearsal wrote anything; the exp3-side
16-cell load passed cold en route); storage 362 Gi free vs ~16 MB
needed. **Gate-1 single-cell rehearsal — the only model contact:
ctrl_copy/1b, 4,000/4,000 draws IDENTICAL, n_diffs 0** (torch 2.12.1
/ transformers 5.13.0), record kept at
`results/gate1/1b_trained/ctrl_copy.json`, its attested
committed_draws_sha256 hash-matching the live exp3 file — finding
B's loop closed on the first real record. Readings 1–8 ruled
(3–8 RATIFIED; 1–2 verified on the code side, boxes waiting on the
doc ruling); LONE-DRAW reason text confirmed verbatim. INVARIANT
HELD: no new sampled quantity for any real cell — the rehearsal is a
read + regenerate + compare of committed bytes. Remaining before tag
`exp3c-preregistered`: Michael ratifies the three doc corrections
(exact edit texts prepared), the findings A/B closures, and gives
the tag + push go; campaign per-cell push authorization reconfirmed
at launch.

**Surfaces attacked, no defect found (rulings for the checklist):**
the leak-void substring criterion — reading 3's answer-in-prompt form
is RIGHT and strictly stronger than the doc's literal "fired draw's
text found in its own prompt": 2c's verify normalizes to the first
token, so fired draws are decorated (' qvux' fires for 'qvux') and
the draw's verbatim text would essentially never occur in a prompt —
the answer is the leaking object; the scan and the gate use the same
operationalization, so the by-construction guarantee and the gate
cannot disagree. Quantifier edges: all-void → ID requires ≥1 fire
and counts per ADDRESS on both sides of the comparison; a single
voided lone fire routes to ID, never LONE-DRAW; partial voiding
proceeds on survivors (full-shape worlds cover all three, incl. the
fired-void-wall-clean pre-void-mutant killer). Stratum accounting:
per-address non-void counting against pinned per-item denominators,
exp3 side per-item — consistent both trees. `diff_seed0` coverage
algebra: committed keys and regenerated keys are forced equal from
both directions (None-get hard error one way, extra-set hard error
the other), so `draws_compared = n_items × dps` cannot overclaim
against a truncated committed file. harness.py/models.py are
path-asserted, not content-pinned — CONSIDERED and left as exp3's
frozen convention: render_prompt sits inside gate-1's byte
comparison and verify inside the 16/16 fires-table recompute, so
drift in either is caught executably by referents that ARE pinned.
The luck-floor-vs-REPLICATES overlap (a single len-4 fire is ~28%
probable under a pure 26^-4 emitter across 148,992 stratum draws) is
§8's disclosed weak point, an accepted dial, printed beside every
rate — not re-litigated. Namespace/seed collision: seeds 4–15 under
'exp3|{rung}|{size}|trained' are virgin substreams (exp3 drew 0–3
only; twins are mode-separated; the determinism fixture uses its own
namespace); ctrl_copy's map rows for seeds 4–15 are surplus
documentation, never drawn.

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
