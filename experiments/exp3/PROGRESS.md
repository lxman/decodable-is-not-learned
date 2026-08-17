# Experiment 3 — build ledger

**2026-08-17 — CAMPAIGN COMPLETE: 60/60 cells, one stop, zero
attrition. VERDICT PROJECTION below, ledgered BEFORE the frozen
analysis runs (§10.4); the analysis awaits Michael's go and runs
ONCE.** Relaunched campaign ran 1702.5 min (28.4 h) end to end:
4 re-decode tiers (3.6 min, from the pre-stop run), 7 mass tiers
(410m/1b pairs ≈ 81/90 min each; 2.8b 125 min; 6.9b 634 min — fp32
at ~27 GB hit memory pressure, the one big estimate miss; 12b
depth-1 9.6 min — the keep1-only preflight fix proving out live),
4 sampling tiers (410m 107.6 min twin AND trained — identical to the
second; 1b 186.9/186.7 min twin/trained). Twin/trained tier-time
identity is the determinism story visible at the wall clock. Every
cell committed and pushed as it landed by the watcher (per-cell
trail in git); final sweep 07:07:33, results tree clean. mlx
text-server RESTORED (launchctl bootstrap; 11436 answering). The
only campaign irregularity remains stop #1 (the padded-vocab class
table, fixed and ledgered above); no OOM, no retries, no attrition.

**VERDICT PROJECTION (2026-08-17, before analyze_3.run() — reasoned
from committed 3b/2c records and the frozen power table only; no
exp3 result file has been read).** Projected verdict: **PARTIAL —
both 1b cells BULK-ONLY, both 410m cells WALL.** Reasoning: (a) Fire
arm: NO verified full-string fire in any of the four adjudicated
cells. The joint 4–7-character exact path at T = 1.0 for models whose
greedy emission sits at floor should carry per-draw mass orders below
the 1e-5 pooled detection edge; greedy found 0/500 twice (3a, 3b).
(b) Mass arm (the amended within-item statistic): 3b's probe margins
order the cells .7725 (1b/rev7) > .6749 (1b/rev) > .6263 (410m/rev7)
> .5731 (410m/rev), and the unembedding readout is echo-dominated at
410m (greedy 90% input[0]) — the interior-competitor statistic is
echo-neutral, so what remains is whatever consistent last-char
elevation survives the readout. I project the realized θ clears the
~.564 critical rank rate at 1b (both rungs) and falls inside the
blind region at 410m (both rungs) — the precursor visible at the
larger probe size, unresolved at the smaller. (c) Gates: 1 PASS
(copy's first-position mass is the copy signature; sampled
full-string well above .5), 2 PASS (≤2 byte diffs — the same
generate path reproduced byte-identically in 3a and 3b), 3 coherent
everywhere, 5 no contamination (the twins sit at the exact θ=.5
null; a random-weights full-string reversal in 128k draws is
effectively impossible). Named disconfirmers, in advance: ANY
verified fire anywhere (kills the no-fire arm; TAIL-ONLY/ELICITABLE
enter); all four cells mass-significant (→ BULK-ONLY, thesis-friendlier
than projected); none significant (→ WALL, the costliest world). The
least certain call is 410m's mass arm — θ near the blind edge on
both sides; a miss there turns PARTIAL into BULK-ONLY or WALL, and
the retrospective grades it either way.

**2026-08-16 — CAMPAIGN STOP #1 at the first mass tier (3.8 min in;
16/16 re-decode cells committed, ZERO mass or sampling quantities
produced): the frozen class table cannot cover the real model's
distribution. Mechanism-forced fix ledgered HERE, before the re-run;
justification references no outcome because none exists.**

*What happened.* `mass/410m/untrained` crashed on its first item
inside `depth2_masses`'s own distribution guard: "position-1
distribution has 50304 entries against 50277 token classes." The
driver stopped the campaign at the tier boundary (designed behavior);
the watcher committed the finished re-decode cells and exited.

*Mechanism, verified before this entry (tokenizer + config.json
reads only — no model load, no quantity):* GPT-NeoX pads the
embedding/unembedding to a multiple of 128 — `len(tok) = 50277`,
`config.vocab_size = 50304`. The 27 ids in [50277, 50304) are DEAD:
no encoding produces them, `batch_decode([[50300]]) = ['']`, and
sequence decode skips them transparently (`decode([50300, g]) =
'g'`). `classify_tokenizer` built its table over `len(tok)`, so the
model-width softmax was refused by the very 3a-class guard built for
malformed distributions — refusal instead of miscount, working as
designed. Why no fixture caught it: the build's synthetic glue model
was constructed with `vocab_size=len(tok)` (test_mass_glue.tiny_model)
— the padded-width mismatch never existed in any synthetic world, and
the pre-tag invariant deferred the new instrument's first real-model
contact to campaign time. 3b never met this: HFRunner only calls
generate, which samples and decodes over the same padded width
transparently (why the re-decode tiers passed byte-clean tonight).

*The fix (mechanism-forced, semantics-free).* The frozen class
definition already decides the dead ids' class: "None means the token
defers the first visible character (pure whitespace, non-breaking
space, EMPTY DECODE)" — dead ids decode to '' and sequence decode
skips them, so a sampled dead id defers the first character to the
next position: they ARE the deferral class. `classify_tokenizer`
gains `n_logits` (the model's `config.vocab_size`, passed by the
runner's two call sites); the table is built over the model width;
the dead band classes to the whitespace path through the existing
`first_char('') = None` rule and takes depth-2 rows like any live
deferral id (+27 ids ≈ two extra 16-row chunks per item, marginal).
The sampler needs NO change: its draws already ranged over the padded
width — 3b's generate identically — and decode disposes of dead ids
exactly as it always has. No threshold, statistic, gate, criterion,
verdict branch, or stored-record shape changes; the letter/residual/
terminal/ws buckets keep their definitions with the table now total
over the distribution's support. Fixtures added in both directions:
a padded synthetic model (vocab_size > len(tok)) proving the width is
covered, dead ids class as deferral, and the depth-2 cache equality
holds; the refusal still firing when the table is built without
`n_logits`; and the quantity-free real-config smoke that SHOULD have
been on the freeze checklist — `classify_tokenizer(tok, n_logits from
the local config.json)` covering the width (the missing integration
check, now permanent).

*Classification under the process rules:* this is the crash-fix class
("a failed gate gets ONE mechanism-justified fix, written to the
ledger BEFORE the re-run"), 3b's-OOM-shaped but touching frozen glue,
NOT the one pre-committed change — it completes execution and shades
no number (none exists). Michael may overrule this classification in
review; per-cell resume makes a revert cost only the mass cells
produced after this entry. *Retrospective lesson, recorded now:* the
build invariant ("no real-model quantities pre-tag") silently covered
"no real-model GLUE contact pre-tag"; a quantity-free tokenizer/config
smoke belongs on every future freeze checklist alongside the referent
checks. Relaunch after fix: same commands, skip-if-exists resumes at
mass/410m/untrained.

**2026-08-16 — CAMPAIGN LAUNCH, on Michael's word ("Launch now, push
per cell") — §10.3 fully satisfied: preflight ladder done this
session (all five local sizes), per-cell push authorization
reconfirmed.** Launch state: tag `exp3-preregistered` = ae82394;
working tree clean at launch; no result cell exists. Operational
notes, disclosed before the first cell: (1) the mlx text-server
(launchd `com.mlx.text-server`, port 11436) is BOOTED OUT for the
campaign per 3b's precedent — plain kill respawned it (KeepAlive), so
it was `launchctl bootout`-ed; RESTORE after the campaign with
`launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.mlx.text-server.plist`
and verify HTTP on 11436. The embeddings (11435) and VLM (8080)
servers stay up — the 6.9b fp32 preflight passed under today's exact
load, an existence proof the heaviest tier fits. (2) Per-cell commits
are made by `run/commit_watcher.sh` (NEW, driver-class, operational
only): 5-minute cycle, 2-minute warm-file mtime guard, pushes each
commit, exits on the driver's terminal line after a final sweep. The
frozen driver itself is untouched. (3) Driver runs detached
(nohup+disown), log at `experiments/exp3/logs/campaign.log`,
tier-per-process, per-cell resume — any interruption resumes with
`python -m experiments.exp3.run.campaign_3`.

**2026-08-16 — MICHAEL RATIFIES THE §5 AMENDMENT ("ratified"); tag
`exp3-preregistered` applied to the ratification commit and pushed.**
The ruling closes the freeze checklist's final ruling box. The tagged
state is the cold-green tree of f0b5fe0 plus ratification records
only (no code bytes changed after the cold battery). Design doc
status flips to FROZEN at the tag. Still open before any cell runs
(§10.3, "At the tag" box): campaign launch is Michael's word, with
per-cell push authorization reconfirmed at launch. The preflight
ladder half of that box is already satisfied (all five local sizes,
this session). No mass or sampling quantity exists for any real cell;
the eval side of this experiment has never been touched.

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

**2026-08-16 — FREEZE SESSION CLOSES: every checklist box checked
except the one that is Michael's by design. THE TAG IS NOT APPLIED —
`exp3-preregistered` waits on Michael's ratification of the §5
amendment (or his election of the disclose-only alternative).** The
session's three findings, most severe first: (1) the class defect —
§5's w̃ statistic credited set-level lexical priming and
anti-concentrated priors (entry below; amended to the within-item
interior-competitor form, primer kill demonstrated K=500/500
p≈3e-151 before the fix, exact ties after); (2) gate-3 scope crack —
both gate-1 arms can pass over an incoherent positive control (ruled:
`GATE3_FATAL_CELLS` = adjudicated + ctrl_copy trained); (3) the 12b
mass tier was preflight-gated on the broken-class batched path it
never uses (fixed: `--keep1-only`, disclosed in the report). Cold
verification, all from fresh processes on the committed bytes: suite
**140 passed**; full-shape **17/17 worlds, all terminals**; mutation
**56/56 KILLED, baseline clean** (the first official run's 55/56
caught the gate-3 widening making `id_gate1_mass` non-isolating — a
fixture blind spot repaired with the coherent-instruments gate-1
world, the mutation discipline doing exactly its job); referents
**14/14** with twin hashes equal to 3b's records
(`335d46b7…`/`fa3fe1d2…`), rewritten `referent_check.json`
byte-identical; determinism fixture **byte-identical** to the
committed reference (stack unchanged: torch 2.12.1 / transformers
5.13.0 / mps); power tables **byte-identical** to committed
`power.json` (282 critical; .9539 at θ=.60; .2799 at .55; blind edge
.563; 2.3405e-5 — the amendment left `sign_test_significance`
untouched, exactly as claimed); empty-tree `run()` hard-errors;
preflight **all five local sizes pass** (410m/1b/2.8b/6.9b f32 full,
worst batched-row diff 8.64e-06; 12b f16 keep1-only, diff 0.0). The
build-session invariant held through the freeze: no mass or sampling
quantity was computed for any real cell or model — model contact was
the checklist's own artifacts (twin construction on CPU, determinism
fixture and preflights on synthetic pinned prompts); the only
committed-record reads were 3b's closed continuations (the priming
diagnostic) and the referent surface. NEXT: Michael reads the
amendment entry + the §5 diff; on "ratify" the tag goes on the
current commit and §10.3 campaign authorization is reconfirmed; on
"revert" the amendment backs out to the w̃ form with the degenerates
disclosed in §7/§8 before any tag.

**2026-08-16 — FREEZE SESSION OPENS (session 3 of 3), adversarially.
THE CLASS DEFECT IS FOUND: §5's w̃-competitor statistic credits
lexical/format letter statistics as capability signal — 2c's death
class, in this design's primary criterion. Amendment declared below,
BEFORE any code is changed; the tag is HELD for Michael's
ratification.**

*The defect.* §5's s_i = m_i(y_i) − Σ_{c≠y_i} w̃_c m_i(c) compares the
correct letter's mass against a cross-item frequency-weighted average
of the other 25 letters. The doc's null claim ("a format-only emitter
and a letter-uniform guesser both give θ = .5 by construction") holds
only for the two degenerates §8 lists. Two mechanisms outside them
fire the test with zero item-level information:

1. *Context-letter priming (the fatal one).* A model that elevates
   mass on every character present in the quoted input string —
   position-blind in-context copying, among the best-documented small-
   LM behaviours — elevates m_i(y_i) on EVERY item, because the answer
   is a permutation of the input and y_i is always one of the input's
   characters, while the w̃-competitors mostly are not. Per-letter
   boost δ gives s_i ≈ δ(1 − 6/25) > 0 essentially always → θ ≈ 1 →
   certain false significance at n = 500 on all four adjudicated
   cells, manufacturing BULK-ONLY/ELICITABLE — the thesis-friendly
   direction — with zero position (reversal) knowledge. §8's echo row
   analysed only input[0] echo (~4% first-char coincidence) and missed
   the set-level effect entirely.
2. *Anti-concentrated item-independent priors.* For any item-
   independent letter distribution f, s_i > 0 ⟺ f(y_i) > Σ_c w̃_c f(c),
   so θ = the w̃-mass of letters whose f exceeds the w̃-weighted mean —
   .5 only by accident of shape. f uniform over 20 letters with 6
   rare letters suppressed gives θ ≈ 20/26 ≈ .77: fires, format-only.
   (Right-skewed English-like priors give θ < .5 — conservative — but
   the class is uncontrolled in both directions.)

*Evidence both shapes are live on these exact cells* (read from 3b's
CLOSED committed continuations — no model queried, no mass or sampling
quantity computed; the invariant holds): the greedy first character
lands inside the item's own answer-letter set at rates .968
(rev_string7/410m), .970 (reverse_string/410m), .984
(reverse_string/1b) against multiset-chance .239/.173/.173 — and it is
the ECHO character (input[0] = answer's last char) at .912/.896/.942,
against correct-first-char rates .052/.032/.026. Input-letter mass
concentration is massive and real. And rev_string7/1b greedy-emits a
single fixed letter ('o') on 498/500 items — a collapsed item-
independent prior, the degenerate-prior shape in the flesh.

*The amendment (pre-tag; nothing is frozen yet; the one pre-committed
post-freeze change is NOT touched).* The competitor set moves inside
the item: s_i = m_i(a_i[0]) − mean_{j=1..L−2} m_i(a_i[j]), the
answer's first-character mass against the mean mass of its own
INTERIOR characters (positions 1..L−2, multiplicity kept, L = answer
length). The answer's LAST character — the input's first character,
the echo target — is read on neither side. Everything else about the
statistic is unchanged: the same per-item stored a–z vector, the same
sign-with-SIGN_TIE_EPS rule, the same exact one-sided binomial tail
through the untouched `sign_test_significance`, the same n_tests
Bonferroni, the same bracket upper end (whole per-item residual
credited to a_i[0], competitors at computed masses), the same
adjudication-reads-lower rule.

*Why this is the right null, provably.* The permutation rungs' input
characters are iid uniform; conditional on the multiset, the position
assignment is uniform. For ANY mechanism whose mass function depends
on the input only through position-symmetric features (item-
independent priors, format priors, and set-level lexical priming
alike), the character at the input's last position and the characters
at its interior positions are exchangeable — so P(s_i > 0) =
P(s_i < 0) and θ = .5 EXACTLY, ties symmetric. Set-level priming
cancels algebraically (every read character carries the same boost).
Echo (input[0] favoritism) touches an excluded position: it moves
neither side. What fires the one-sided test is exactly mass that
favors the input's LAST character over its interior — the position-1
reversal signature, the very quantity 3b's probe read from the
residual stream. On ctrl_copy the same statistic reads first-position
favoritism over the interior — copying's own signature — so gate 1
tests the instrument against the capability it certifies, and
recency-toward-input[-1] copying (ans[-1], excluded) cannot fake it.

*Computability (reading 5, re-keyed).* The statistic is computable
for a rung iff every character it reads (each item's a_i[0] and
interior) lies in the stored a–z block. Both reversal rungs and
ctrl_copy: answers verified 100% lowercase alpha, lengths 7/7 and
4–6/4–6 (min interior 2 competitors, no structural ties).
clock24_d999 reads digits → computable=False, never significant,
hard error if adjudicated — reading 5's outcome, unchanged. Items
with L < 3 (none exist in the committed batteries) are structural
ties, disclosed in n_ties; the all-ties path (reading 3) covers the
vacuous extreme. The w̃ single-letter-support guard is dead code under
the amendment (there is no w̃) and is removed with it.

*What the amendment deliberately does not touch:* the stored per-item
mass unit and every loader; gate 1's CP arm; gate 2; gate 3's
label-mass bracket and level; gate 5's arms; step 6's worlds;
`sign_test_significance` and therefore the committed `power.json`
(same critical counts at every n; §7's θ re-reads as
P(s_i > 0) under the new s_i — the power table's arithmetic is
identical); the sampler, masses module, runner, campaign order,
preflight, and determinism artifacts. Blast radius: one competitor-
construction block inside `rung_sign_test`, its fixture block, the
full-shape worlds' synthetic answers and split cases (interior-aware),
and the retired w̃ mutants replaced by competitor-set mutants.

*Process.* This entry precedes any code change (the rule: mechanism
argued in the ledger first, justification never referencing the
outcome it would produce). The doc is DRAFT — a pre-tag amendment
spends nothing — but §5 is Michael-approved text and the amendment
changes adjudication semantics, so the TAG WAITS: the freeze session
completes every ruling, re-run, and fixture cold, and
`exp3-preregistered` is applied only on Michael's ratification of
this entry (or his preference for the disclose-only alternative,
recorded below, in which case the amendment reverts before the tag).
*Disclose-only alternative, for the record:* keep §5's w̃ statistic
and add the two degenerates to §7/§8 as named false-fire routes. Not
recommended: 2c's chance-floor defect was likewise found before the
verdict and not fixed, and CLAUDE.md records how that reads in
retrospect; a preregistered criterion with a known certain-fire
format route cannot honor §8's "the bar is passable and can genuinely
fail."

**2026-08-16 — freeze ruling on reading 2 (gate-3 trigger scope):
WIDENED to adjudicated ∪ ctrl_copy-trained (6 cells), argued and
ledgered before the code change.** The build's reading 2 said a
control-cell incoherence "in practice also takes gate 1 down" and left
widening to the freeze. The adversarial pass found the crack in that
"in practice": gate 1's two arms are the mass SIGN test (which needs
rank elevation, not a high mean) and the FULL-STRING CP lower bound —
a world with ctrl_copy label mass ≈ .10 (sign test fires: interior
competitors at zero) and sampled rates ≈ .625 (full-string CP lower
> .5) passes both arms while the first-char count's CP interval is
wildly disjoint from the mass bracket. The run would proceed past a
positive control whose two instruments disagree — and the control IS
the certificate that the instruments measure anything. Ruling: the
gate-3 INSUFFICIENT_DATA trigger fires on the four adjudicated cells
AND the two ctrl_copy trained cells. Twins stay disclosed-only
(contamination sentinels, not instruments under test; the
twin-incoherence world stays non-fatal), and clock24_d999 stays
disclosed-only (its digit-space decode path is not on any adjudicated
route; an ID on a clock-only drift would kill the run over a cell no
verdict branch reads). Coherence stays computed and disclosed for all
16 (reading 2's other half, unchanged). Conservative direction: the
widening adds ID routes and cannot manufacture a world. Implemented
after this entry as `GATE3_FATAL_CELLS`; a full-shape world pins the
exact crack (ctrl incoherent, both gate-1 arms passing → ID), and a
mutant narrowing the fatal set back to the adjudicated four must die.

**2026-08-16 — freeze finding #3 (operational, driver-level): the 12b
mass tier is gated on a preflight of a path it never uses.**
`campaign_3.py` preflights every (size, dtype) before its first mass
or sampling tier; for the 12b mass tier that invocation is
`preflight_paths --size 12b --dtype float16`, whose batched-step
row check exercises exactly the fp16-MPS batched cached-step class the
build root-caused as broken (410m/float16 FAILS it by design). The
12b mass tier runs DEPTH 1 — batch-1 keep1 prompt forwards only, the
verified-sane fp16 class — precisely BECAUSE the batched path is
broken; if 12b/fp16 batched fails the way 410m/fp16 does, the frozen
driver stops the campaign at a tier whose own arithmetic is fine.
Consequence bounded: 12b cells are descriptive (no verdict branch
reads them), so the failure mode is a halted campaign, not a wrong
number. Fix (pre-tag, driver-level, decides-what-runs only):
`preflight_paths` gains `--keep1-only` (skip the batched-step check,
keep the prompt keep1-vs-re-forward check), and the driver passes it
exactly when the tier's dtype is float16 — the gate verifies the
paths the tier uses. The fp32 pairs keep the full check, batched rows
included. Rationale mirrors the redecode tiers, which have no
preflight because generate is the sane class and gate 2 byte-checks
them end to end.

**2026-08-16 — build session 2b closes: BUILD COMPLETE (all eight Open
items landed); the freeze remains a separate, later session that opens
adversarially.** The session spanned 2026-08-15→16. Landed and
committed this session (0fb7a33 readings, 5c0fdd6 statistic, a2c3735
loaders + maker, 96a04d4 verdict + full shape, e6abb8e power +
mutation): analyzer readings 5–9 declared in this file before any
implementation; the §5 statistic; the three battery loaders with the
fire recompute; the §6 verdict tree; fifteen full-shape worlds
reaching every terminal; the 54-mutant check, all killed; the exact
power tables. Suite: 131 green. **The invariant held all session** —
no mass or sampling quantity was computed for any real cell or model;
the only committed-record contact was reads of 2b/2c/3a/3b artifacts
(floors, margins, referent shapes, verify semantics) and synthetic
worlds. The freeze checklist now carries UNCHECKED ruling boxes for
readings 5–9 and the tie epsilon alongside the session-2a items; no
box is checked, no tag exists. Next session: the adversarial freeze
(assignment: find the class defect), then `exp3-preregistered`.

**2026-08-16 — operational note (for the freeze session and any
future mutation work): mutation_check.py is foreground-only, on a
quiescent tree.** The harness snapshots analyze_3.py at start, writes
mutants in place, and restores ITS OWN snapshot after each cycle — an
edit made while it runs is silently reverted, and a live mutant can
transiently sit on disk. Caught in this session: a redundant
backgrounded re-run clobbered the sign_test_significance refactor
mid-edit (the tree briefly showed the BYTE_TOLERANCE=500 mutant). The
run was killed, the file restored from git, the edit re-applied, and
the final 54/54 run was executed in the foreground with no concurrent
edits. No mutant state was ever committed.

**2026-08-16 — Open item 6 complete: exact power tables from the
frozen code.** `compute_power.py` INVERTS the frozen
`sign_test_significance` (extracted from rung_sign_test so the
adjudication convention exists in exactly one place) rather than
re-deriving the tail; `power.json` committed and locked to the code by
`test_power.py` (the freeze re-runs the comparison cold). Numbers:
critical count **exactly 282 of 500** at α = .01/4 one-sided (the
doc's ≈282); power **.9539** at θ = .60 (doc ≈.95); **.2799** at
θ = .55 — **the doc's ≈.26 quote was off by .02 and is superseded by
the exact value** (§7 anticipated exactly this: "exact table
recomputed at freeze from the frozen code"); blind edge **.563** at
power .5 (doc "blind for θ ≲ .57", consistent); post-tie-n grid
100–500 for the realized-n_eff recompute path; detection 1−(1−p)^k at
the pooled 128,000/16,000 with the .95-detectable rate asserted equal
to `cp_upper(0, k)` — 2.3405e-5, the WALL statement's number.

**2026-08-15/16 — Open items 3 + 4 complete: statistic, loaders,
verdict tree, full-shape worlds, mutation both directions.** Built
strictly test-first (every fixture watched failing before its code
existed). (a) `rung_sign_test`: the §5 within-distribution statistic
with per-item w̃ renormalization, the single-letter guard, the
letter-support rule (reading 5) recording digit-support cells
computable=False — and a HARD ERROR if such a cell is ever
adjudicated; bracket upper end per reading 1, adjudication reads
lower. **SIGN_TIE_EPS = 1e-12** pins sign-vs-tie resolution: above
f64 dust on algebraically-zero s_i (the format-only kill test cancels
exactly), below anything fp32 logits express; the sub-epsilon fixture
holds both directions. (b) Loaders: canonical subdirs only with
stray-file refusal; the ledgered dtype/depth policy executable at
load; per-item mass validation; the sampling loader re-reads every
raw draw and REFUSES stored-tally disagreement — the maker computes
its stored tallies with an INDEPENDENT plain loop over 2c's verify,
so agreement crosses two implementations. (c) `verdict()`: everything
computed and disclosed before the first branch; gates in §6
precedence; reading-7 pins in the shape check; WALL text carries the
computed blind region and the probe-as-arbiter sentence. (d) Fifteen
full-shape worlds through the real loaders with real floors+margins:
four worlds, PARTIAL, four ID routes with gate 1's two arms
separated, both contamination interactions (mass arm and fire arm
each exercised), bracket disagreement (upper significant, lower
adjudicates, finding disclosed), eval-descriptive scope, twin
incoherence non-fatal, and the coherence level margin (230/5120 vs
[.038, .038]: coherent at 1−.01/16, disjoint at .95 — catches a
wrong-level gate 3). (e) `mutation_check.py`: 54 mutants, softening
AND hardening, ALL KILLED, baseline clean. **One equivalent mutant
excluded and documented:** deleting the explicit all-ties branch is
unobservable because `binom.sf(-1, 0, .5) = 1.0` — the branch is the
ledgered reading made visible, not a behaviour change; the freeze
read should know it is belt-and-braces.

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
