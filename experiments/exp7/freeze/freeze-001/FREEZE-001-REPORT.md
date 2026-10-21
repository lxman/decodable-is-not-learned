# Experiment 7 — Full-Default Synthetic Freeze Report (`freeze-001`)

- **Disposition**: `COMPLETE` (`synthetic_only: true`, `mutations: 43 / 43 KILLED`, `0` model contacts, `0` forbidden imports)
- **Inventory Authority**: `experiments/exp7/build/amendments/calibration-001/coordinator-inventory.json` at commit `977d4ca02113ab91735774dd4974f0beec8e5995` (`271` files: `241` literal base + `30` amended across `CALIBRATION-1`, `FREEZE-1-world-fixture`, and `FREEZE-1-mutant-tests`)
- **Synthetic Producer Fixture**: `/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode/exp7-freeze-001/producer-export.json` (`185,484,064` B, SHA256 `f7bb85daf6b92bc2337f8e976dc7a0d46685e217d69d42beb292416affeda561`)
- **Scratch Freeze Output Root**: `/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode/exp7-freeze-001/freeze-out`

## Stage Receipts & SHA256 Digests

| Artifact | Bytes | SHA256 | Result |
|---|---:|---|---|
| `COMPLETE.json` | `35309` | `4fcba8c7001fd2ff71e40bcc968095446b0f50b8addf6584a77346965c449dd2` | `state: "COMPLETE"`, `mutations: 43` |
| `task-0001.json` (`before: evaluate(copy, "all")`) | `20304` | `4e79f8a529b78edffcca27d0285aa0a9ca3110f42daa1c81e8fbe0fd41a511ee` | `400` tests, `0` failures, `0` errors, `rc=0` |
| `worlds.json` (`freeze_worker.py --task worlds`) | `4266` | `434975391e696eadc0ecef4e622e9a8f9b055aa98f5752c2e8bc9ff185a41b4e` | `state: "COMPLETE"` (`17` clean + `23` poison full-default worlds) |
| `import-scan.json` (`freeze_worker.py --task import-scan`) | `133701` | `f58940a9f554645b08de63f2a4012e339c299a48f0f140992f95154b050a666b` | `state: "COMPLETE"` (`271` files, `0` violations) |
| `read-scan.json` (`freeze_worker.py --task read-scan`) | `202079` | `3b0093faa6f688bb9fa9e74df364c132f4520d1426a95224afac3455341f5570` | `state: "COMPLETE"` (`0` violations) |
| `determinism/determinism.json` (`deterministic_twice`) | `116` | `deac7faa61091132694856f40719fe6569155bed6ab1d996b328e94febd5e72b` | `invocations: 2`, `byte_identical: true`, output SHA256 `0038db847f4c87f9b79e19ad16def07bcfe20904abb1bd71e1135620301d9e45` (`98,579,894` B each) |
| `mutations/original-manifest.json` | `29855` | `539ced310faa6eeaeac8f448253cee84d1757c0afdcf1e1bfd0b8aa893ca109f` | `272` entries (`271` package files + `DISPOSABLE-SYNTHETIC-SOURCE.json`) |
| `mutations/results.json` (`run_mutants`) | `132301` | `28f77d963dce1952bb1ff259a253bcb821eaccec55d3bd2a638216129691b237` | `43 / 43` `KILLED` (`task-0002.json` .. `task-0130.json`) |
| `task-0131.json` (`after: evaluate(copy, "all")`) | `20304` | `4e79f8a529b78edffcca27d0285aa0a9ca3110f42daa1c81e8fbe0fd41a511ee` | `400` tests, `0` failures, `0` errors, `rc=0` (byte-identical to `task-0001.json`) |
