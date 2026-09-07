# Experiment 2n — adversarial freeze (build + freeze session, 2026-09-06/07)

Fresh-eyes reviewer, cold, on `experiments/exp2n/` at build HEAD
`ef0fa6b6`. The standing assignment, verbatim from the program: find
THE CLASS DEFECT — the defect that would silently DECIDE the verdict —
and close what is found ADDITIVELY (a new refusal, pin, test,
disclosure or record field; never an accepted dial). Zero model contact
and zero network throughout; every execution of `analyze_2n.run()` on
the real tree is a disclosure event, recorded in `PROGRESS.md` and
design §2.

Python: `~/emergence-lab/.venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`,
from the repo root, `-p no:cacheprovider`.

Baseline measured cold BEFORE the freeze touched anything:

| battery | result |
| --- | --- |
| fast modules (`test_battery_2n`, `test_stages_2n`, `test_analyze_2n`, `test_power_2n`, no `-m` filter) | **135 passed**, 257.5 s (= the build's 134 + the one `slow` real-git case the build deselected) |
| worlds + totality (`test_full_shape_2n` + `test_totality_2n`) | (filled in below) |

**Verdict on the assignment: (filled in below).**
