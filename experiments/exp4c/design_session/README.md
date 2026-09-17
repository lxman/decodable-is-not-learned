# Experiment 4c — design-session computations (2026-09-17)

Analysis-only, committed bytes, zero model contact. These are the five
disclosure events listed in `experiment-4c-design.md` §2, as run, plus
the design-stage power estimate of §4. Scripts 01–05 are the scratch
files copied verbatim (01 takes the output path as argv[1]; 02–04 take
the series file; they were run with `PYTHONPATH` at the repo root and
the `~/emergence-lab/.venv` interpreter). `series_known4.json` is 01's
output: a_r(t) for all 34 tasks on Exp 4's four trajectories, with each
run's rising / flat / transient sets and clear indices.

Everything here is POST HOC on four runs whose Exp 4 and 4b results the
designer knew. It is motivation and a known-answer gate, never evidence.

## Outputs, verbatim

02 (pooled, independent-draw placebo null, B = 10,000, seed 0):

    ALL windowed rising cells: n=42  mean quantile U=0.6224  placebo null mean 0.5004 SD 0.0464  p_high=0.0049
      pythia_2.8b: n=7 nF=27  U=0.487  null SD 0.113  p_high=0.547
      olmo2_7b: n=13 nF=16  U=0.630  null SD 0.086  p_high=0.068
      smollm3_3b: n=7 nF=14  U=0.694  null SD 0.116  p_high=0.046
      comma_7b: n=15 nF=16  U=0.646  null SD 0.079  p_high=0.030

03 (exact sign flips of q − 1/2; the type split):

    ALL cells vs ALL flat: n=42 U=0.6224 | rung-level (17 rungs) p=0.0092 | family-block (9 families) p=0.0391
    ARITHMETIC rising vs ARITHMETIC flat: n=26 U=0.5103 | rung-level (11) p=0.4331 | family-block (6) p=0.4531
         per run .270 / .448 / .667 / .633
    NON-arithmetic rising vs ALL flat: n=16 U=0.7595 | rung-level (6) p=0.0156 | family-block (3) p=0.1250
         per run .889 / .738 / .750 / .738

04 (never-performing non-arithmetic tasks ranked among arithmetic flat
tasks, mean over the grid): 18 task-runs, mean 0.420; odd6 .80 and
odd_one_out .91 on Pythia 2.8b; hamming12 .02–.07 on Pythia and OLMo-2.

05 (design-stage power, 2,000 draws per arm, rho in {0, .5}):

    null                       P(p<.01) .007–.009   P(p<.05) .042–.043
    uniform lead .60                    .151–.214            .434–.515
    uniform lead .65                    .384–.510            .751–.853
    uniform lead .70                    .719–.817            .956–.988
    discovery shape .51 / .76           .085–.091            .320–.332
