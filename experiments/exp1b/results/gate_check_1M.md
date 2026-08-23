# Exp 1b — ground-truth gate confirmation at 1M (design open item 2)

**Question.** Do Exp 1's three training recipes still reproduce their
ground-truth gates on 1b's fresh seeds? Seeds 100–104 are disjoint from Exp
1's 0–4 by construction, so nothing guarantees a recipe tuned and confirmed on
seed 0 behaves the same way on seed 100. This is the STOP GATE: a failure here
is reported, never adjusted, and 1b's one pre-committed change is already
spent on the floor-corrected S1 (design §4), so there is nothing left to spend
even if adjusting were permitted.

One seed (100) of each trained row, at 1M. Each row's gate is the one its own
runner asserts — no gate was invented for this check, and `certified` is read
from the record rather than recomputed.

**Result: 3 of 3 PASS.** The campaign is clear to launch.

| row | seed | gate quantity | required | measured | verdict | wall-clock |
|---|---|---|---|---|---|---|
| `grokking` | 100 | memorization→generalization gap | mem before gen, both reached | mem @202 → gen @2099, gap **1897** steps; final train 1.000 / test 1.000 | **PASS** | 475 s |
| `lubana_above` | 100 | transitioned AND held | `giant_frac_min` > 0.3, transition exists, `final_metric` ≥ 0.5 | giant_frac_min **0.868**, transition @**39069**, final **1.000**, peak 1.000 | **PASS** | 5,964 s |
| `lubana_below` | 100 | stayed flat | `giant_frac_mean` < 0.1, `peak_metric` < 0.150 | giant_frac_mean **0.0057**, peak **0.126**, no transition, final 0.084 | **PASS** | 8,304 s |

Total 14,743 s ≈ 4 h 6 min, 2026-08-12 12:07 → 16:13.

## Reading the numbers

**`grokking`** reproduces the Exp 1 shape on a fresh seed. Exp 1's confirmation
run recorded seed 0 at mem @262 → gen @1578; seed 100 gives mem @202 → gen
@2099. The gap is wider, the phenomenon is the same, and the run reaches
perfect train and test accuracy well inside the 10,000-step budget.

**`lubana_above`** transitions decisively and holds: the giant component covers
87% of each class at its worst point, and the capability metric saturates at
1.000 rather than merely crossing the 0.5 level. Nothing marginal here.

**`lubana_below` is the one worth looking at twice.** It passes, but with the
narrowest margin of the three, and it is the row whose failure would be most
consequential — it is the percolation ground truth, the only row asserting
that a capability genuinely cannot form.

- The *graph* side is not close: `giant_frac_mean` 0.0057 against a 0.1 bar,
  a factor of 18. The generating structure is unambiguously sub-critical.
- The *capability* side is closer than the graph side suggests.
  `peak_metric` 0.126 against the 0.150 bar leaves 0.024 of headroom — the
  peak sits at 1.26× chance where the bar is 1.5× chance. It cleared by 16%
  of the bar, not by an order of magnitude.
- `final_metric` 0.084 is *below* chance (0.100), and `transition_step` is
  `None`: the run never crossed the transition level at any point in 100,000
  steps. The peak is a fluctuation, not an approach to a threshold.

So the row passes on the quantity that matters and the direction of travel is
right, but a successor should not assume this bar has room. A seed whose
fluctuation peaked 20% higher would have failed a gate that nothing about the
underlying structure suggests should fail. That is a property of the bar, not
of the science, and it is recorded here rather than discovered later.

## Provenance

| row | `git_sha` stamped |
|---|---|
| `grokking` | `fa5dbc5-dirty` |
| `lubana_above` | `4381ea9` |
| `lubana_below` | `7a4ee4a` |

The grokking record stamps dirty; the other two do not. The dirt was two
things, both cleared between the first cell and the second: the untracked
exp2c M4 eval records (committed at `62c2c1e`) and this experiment's own
checkpoints (gitignored at `f9f0e33`). The grokking cell was not re-run to
tidy its stamp — the design's attrition rule permits a re-run only for a
*failed* gate, with a logged reason, and re-running a passing cell for
cosmetic provenance is exactly the silent replacement that rule forbids.

`lubana_above`'s record was committed the moment it landed so that
`lubana_below` began from a clean tree. Without that, an uncommitted record
dirties the tree for the next cell — the mechanism that left Exp 1 with 25 of
its 45 records dirty. The campaign should follow the same practice.

## Unrelated crash during the run

A `Python` crash dialog appeared at 14:40:51 while `lubana_below` was
training. It was **not** this campaign: PID 98213, a 33-second-old child of
`~/.hermes/hermes-agent/venv/bin/hermes` (98127), dying with SIGTRAP in
`libsystem_malloc` inside `MPSGraph compileWithDevice:` during CoreML dialect
initialisation. The campaign (PID 77083) was verified alive and advancing at
the time by checkpoint mtimes, and completed normally 93 minutes later.

Recorded because it points at a real operational risk for the full campaign:
another process was compiling Metal graphs on the same GPU. `run_lubana` does
not resume mid-cell, so an MPS fault taking a lubana cell down costs the whole
cell — up to ~2 h 18 min at 1M, and more at 10M.
