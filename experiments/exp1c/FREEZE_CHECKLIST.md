# Exp 1c — Freeze Checklist

Adjudicated 2026-08-14, before the `exp1c-preregistered` tag. Every item is
GREEN (verified) or RULED (a judgement call, recorded with its reasoning).
Nothing is left as "probably fine".

## The frozen artifact

`experiment-1c-design.md` + `experiments/exp1c/analyze_1c.py` +
`experiments/exp1c/records.py` + `experiments/exp1c/run/profile_lib.py` +
`experiments/exp1c/run/run_profile.py` + the 83-fixture suite.

| # | item | status |
|---|---|---|
| 1 | Design doc complete; all five open items closed before the tag | **GREEN** — 3 and 4 closed by measurement/ruling on 2026-08-14; 1, 2, 5 closed by construction |
| 2 | Analysis script written **with its own loader** | **GREEN** — `load_profiles` → `assemble_cells` → `verdict` is one fixture-tested path (§9; 1b's gap) |
| 3 | Fixture suite, one synthetic case per preregistered provision | **GREEN** — 83 tests across 5 files, all pass |
| 4 | Mutation-tested in both directions | **GREEN** — 20/20 killed, `tests/mutation_check.py` |
| 5 | Prediction on the record before any probe | **GREEN** — "layer-0 only, leakage not structure" (Michael, 2026-08-14), design header |
| 6 | Dumbest-baseline analysis written before freeze (standing rule since Exp 2) | **GREEN** — §6, six distinct failure routes |
| 7 | Power computed, underpowered region disclosed in advance | **GREEN** — §5 table; Type-I calibrated 0.009–0.013 at α=0.01; 0.33 power at a 0.02 margin stated as the region a FAIL cannot interpret |
| 8 | Capability metric measured, not assumed | **GREEN** — all 40 cells, mean 0.0976 vs chance 0.1000, no density trend; the conjunction is live |
| 9 | Checkpoint → model reconstruction verified | **GREEN** — `strict=True` on 4 spot cells, 939,312 params at 1M / 12,870,144 at 10M; state dict only, **not probed** |
| 10 | Twin init is density-invariant, as §3 claims | **GREEN** — bit-identical across all four densities at fixed (size, seed); distinct across sizes |
| 11 | `experiments/exp1/` and `experiments/exp1b/` unmodified | **GREEN** — empty diff against `exp1b-closed` |
| 12 | Nothing probed before the freeze | **GREEN** — only model construction, state-dict loads and checkpoint-header reads |
| 13 | One pre-committed change | **GREEN — UNSPENT** |
| 14 | Campaign driver | **RULED — not written, disclosed** (below) |
| 15 | Seeds not disjoint from 1b | **RULED — unavoidable, disclosed** (below) |
| 16 | Stage A checkpoint steps | **RULED — sourced from 1b's records** (below) |

## Rulings

**14 — the campaign driver does not exist.** 1b had `run/campaign_1b.py`;
1c has only the per-cell runner. Ruled acceptable to freeze without it:
the driver is execution orchestration and cannot touch the verdict, which
is fixed by the frozen `analyze_1c.py` and locked by the fixture suite.
The §8 ordering it would enforce — twins first, then Stage A, then Stage
B — is a documented commitment and will be honoured and ledgered whether
a driver enforces it or a human does. Recorded here rather than
discovered later. It is written **after** the tag and is not part of the
frozen artifact.

**15 — 1c reuses seeds 100–104, which are 1b's seeds.** The program's
rule is that fresh runs use seeds disjoint from their predecessor's, so
no run reuses an initialization whose outcome is already known. That rule
**cannot be honoured here and is not**: 1c trains nothing. It reads
checkpoints the 1b campaign already wrote, and those exist only at seeds
100–104. Two consequences, disclosed rather than mitigated:

  - Stage A deliberately re-reads the very cells 1b scored. That is the
    point of a confirmation gate on known answers, not a leak.
  - The sweep shares model initializations with 1b's scored rows. It does
    **not** share data — each density is a different generated graph — so
    the shared seed means shared init only. No sweep outcome was known to
    anyone before this experiment, because the probe was never run on
    those checkpoints.

**16 — Stage A must read the same checkpoint 1b scored**, not the sweep's
terminal step, or it would not reproduce a known answer. Those steps live
in each 1b record's `s1.checkpoint_id` (e.g. `step_0004516` for
lubana_above/10M/seed100) and are passed to `run_profile(..., step=)`.
The runner takes the step explicitly and has no default for the Stage A
systems, so an omitted step is an error rather than a silent substitution
of the wrong checkpoint.

## What could still make this experiment worthless

Stated at freeze so it cannot be presented as hindsight:

1. **Stage A may fail and halt everything.** If the depth margin cannot
   reproduce `lubana_above` (10/10 S1-present in 1b) or reads structure
   in `lubana_below` (0/10 in 1b), the verdict is INSUFFICIENT_DATA and
   the sweep is never probed. This is a real possibility, not a
   formality: 1b's rows were scored on the argmax statistic and 1c scores
   a mean over six depth sites. They are different statistics and the
   second has never been measured.
2. **The measured sd may put the design in its own underpowered region.**
   §5 commits to finalising the power table against Stage A's measured sd
   *before* Stage B runs, and to declaring an underpowered experiment in
   advance rather than discovering it in the verdict.
3. **The composition confound is not fixed and cannot be.** At higher
   density the surviving singletons are a more selected set, biasing the
   primary test toward the null — which is toward the frozen prediction.
