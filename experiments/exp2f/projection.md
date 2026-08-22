# Exp 2f — Projection (SEALED before the analyzer runs)

Standing practice: written and committed before `analyze_2f.run()`
executes, graded in the retrospective. **Disclosure (design §2):**
the generator-side inputs are committed bytes whose exact-match
counts I know (arith_next 831 | 531 of 32,000 and argmax 13 | 19 of
500; sub3_mid 35 | 34 and 0 | 0); their LABEL-match rates are
derivable and have NOT been computed — what follows about them is
reasoning from the exact counts, the floors (.120 / .132) and the
freeze's shape enumeration (digit-run leads 97.6–100 %, nothing
scored). The probe reading on the eval items is a new measurement:
the activations exist since 19:42 today and no probe has been fit on
them. Gate 1 is already on the record: IDENTICAL ×8.

## Sealed at commit: (this commit) — 2026-08-22

### Verdict
- Projected verdict: **INVERTED** (p ≈ .6), with **LADDER** the named
  alternative (≈ .35) and SILENT the remainder. The mechanism I
  expect is the one §7 declared: the sampler's bar is +.004 at
  32,000 draws, the probe's +.05 at 500 items with Bonferroni; a
  genuine last-digit competence of .15–.20 at 410m/1b clears the
  sampler's bar by a wide margin and sits at or below the probe's.
- The cell that decides: **arith_next/1b**. Projected D = (probe ?,
  sampling 1, argmax 1) — sampling and argmax detected; the probe
  the open question, with its best accuracy projected in
  **.15–.20** against a .170 bar, i.e. straddling it.

### Per rung, per instrument (label = last digit / middle digit)
- **arith_next, sampling, both sizes: DETECTED.** The label-match
  rate must be at least exact + chance on the rest ≈ .026 + .974 ×
  ~.10 ≈ .12 at 410m and ≈ .017 + ~.10 ≈ .115 at 1b — barely the
  floor. Above that floor is partial competence: the last digit of
  a + 4d depends only on the last digits of a and d, the easiest
  part of the problem, and the model emits 2–3-digit numbers
  98 % of the time. I project label-match **.16–.24** at both sizes
  (z ≫ 3), so D_samp = 1 at 410m AND 1b. If instead the rate lands
  at .12–.13, the wrong numbers are not near-misses and 2d's "not
  silent" was the exact matches alone.
- **arith_next, argmax: 1b DETECTED (≈ .17–.22 vs bar .156), 410m
  marginal (≈ .14–.18 vs .156).** Greedy 1b has 19/500 exact; its
  last-digit rate should exceed its sampled rate (greedy picks the
  mode).
- **arith_next, probe: best site at 1b ≈ .15–.20, best site at 410m
  ≈ .13–.17.** The prompt-end position at a late layer should carry
  the next token's identity, and 2–3-digit numbers are often single
  tokens, so the probe reads roughly "the last digit of what the
  model is about to say" — about the argmax label-match rate, not
  more. With the bar at .170 / .172 that is a coin flip at 1b and a
  likely miss at 410m. Void (twin detection): **no** — the twin's
  best site should read ≈ .10–.13; printed.
- **sub3_mid: (0, 0, 0) at both sizes** — the sampler's middle-digit
  rate ≈ .13–.14 against .132 (the 3-digit shape is 88 % but the
  digits are guesses), argmax 0/500 exact and ≈ .12–.14 label, the
  probe at chance. The all-silent control, as §7 said.

### Secondaries
- arith_next under mod 7: sampling detected (rate ≈ .16 + ε vs
  .156 — weaker; mod 7 credits only exact and ±7k misses); argmax
  likely not; probe not (a residue is not a linear feature).
- α = .05: the 1b probe crosses its bar (≈ .155) — the verdict under
  the sensitivity may flip to LADDER; that is the reading the
  retrospective must weigh against the declared asymmetry.
- Pilot tier: same pattern as main at arith_next, 4,000 draws.
- CV probe on the probe items (n ≈ 400 / 200 held out): higher than
  the eval reading if anything (in-distribution items).
- 2c's committed starved records printed: .135 / .130 at the
  degenerate site, below chance.

### Named disconfirmers
- LADDER with the 1b probe ≥ .20: the representation carries the
  last digit more strongly than the output does — the essay's claim
  survives on arithmetic and 2c's silence was entirely its target.
- SILENT (sampler label-match ≤ .125 at both sizes): 2d's "not
  silent" premise retracted.
- Both arith_next cells void: the twin reads the last digit — a
  token-identity leak in the prompt (the last term's last digit is
  in the question); if that happens, the label leaks through the
  question end position and the void rule did its job.

### Misses I expect to be graded on
- The probe's best accuracy (I have no measurement of anything like
  it on this model); the argmax 410m call; the exact label-match
  rates.

### What I will NOT do after seeing the numbers
- No second label promoted; no α moved; no site family widened; no
  per-item slicing; the one pre-committed change stays UNSPENT.
