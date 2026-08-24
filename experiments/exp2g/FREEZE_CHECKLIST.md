# Exp 2g — Freeze Checklist (session 3 of 3 — worked 2026-08-23 on Michael's word "run the freeze")

The build ledger (`PROGRESS.md`) is the comparison; nothing here is
ticked until re-run in a fresh process. Assignment: find the class
defect. Zero model contact except the sanctioned `.bin` load
rehearsal (I-7's parked half; load + digest + free, no generation, no
new quantity for any cell).

## Standing adversarial assignments (worked FIRST, cold)

- [ ] The class defect: (1) open()/np.load/json.loads sweep over the
      analyzer's call graph — every verdict input pinned or refused;
      (2) the refusal terminal from every tree the runner can leave;
      (3) the seal's reach (a verdict on any predictor but the sealed
      one); (4) the fix wave's new guards attacked (_sweep_ready,
      collected gate-1 reads, secondary non-gating).
- [ ] Cold re-runs: suite, referent battery, worlds, determinism,
      __main__ smokes, mutation harness (52 mutants incl. the two
      post-wave arith_next mutants).
- [ ] Parked items from the final review: with_2d_secondaries world;
      .bin one-checkpoint load rehearsal; power-record attachment.
- [ ] Ratification package: findings A–N + freeze findings, verbatim.

## Log

- [x] **open()/np.load sweep (io.open patched — the first pass missed Path.read_text): 949 reads on a full world run with the real referent manifest and the 2d secondaries.** 772 world-tree (every record content-checked by step_record_failures/gate1_failures), 139 manifest-pinned, 14 frozen-import-pinned, 23 item files sha-checked at load against battery_2d.ITEMS_SHA_PIN (a frozen-import literal), 1 = referents_2g.json itself (self-pinned by REFERENTS_FILE_SHA256). ZERO unpinned verdict inputs. → **F-2**: the manifest's note says "every committed file analyze_2g reads from other trees" but holds only the 11 predictor item files; the 23 others are pinned by frozen code, not listed. Closed additively: manifest extended to all 34 item files (N_FILES 162), re-pin chain run.
- [x] **F-1 (found before the sweep): the analyzer never attaches the power record** — §7 says the verdict is read under the declaration, 2d's verdict carried its power block, 2g's did not. Closed additively: power_2g.json sha-pinned (POWER_SHA256) and loaded through collect(); the verdict carries declared_status + declaration; a missing/mismatched record is a collected failure.
- [x] Cold, fresh processes at the freeze HEAD: referent battery 11/11; battery_2g/labels_2g/strata_2g __main__ smokes reproduce the frozen tables (21-step grid + exclusion; 11 label gates incl. arith_next's dual referent; count_div13 merges 10→9 only); slow gate P 1 passed (10.1 s); suite 88 + 1 skipped (this HEAD, fresh process, ~2 min).
- [x] **.bin load rehearsal (I-7's parked half, sanctioned; the sweep's dominant serialization).** 2.8b step30000 (kind `bin`) through the PRODUCTION loader: download → sha256 verified against the manifest (fb19c88132…) → clean dir with 2c's pinned config → from_pretrained → loading_info {missing 0, unexpected 0, mismatched 0} → tensor digest bb9ab307253aa97c → freed. 52.9 s download+load, 2.2 s digest, no generation, no forward pass, no new quantity for any cell. The torch-2.12/transformers-5.13 `.bin` path works. Residual after free: the empty per-size cache directory only.
- [x] **Closures landed (612b339):** F-1 power record sha-pinned (27b4dfbb…) and attached through collect(); F-2 manifest → 162 files (def2e0e2…), battery 11/11 cold after the re-pin; with_2d_secondaries world (the three 2d secondaries computed on the real tree, incl. the committed 1b-performable counts 87/89/4/8/1/0/19; non-gating under a broken d2_root). Suite 92 + 1 skipped.
- [x] **The real tree today delivers its own refusal:** analyzer → INSUFFICIENT_DATA with 4 failures, the seal named first, gate-1 missing named, power POWERED n_sim 1000 riding in the referents; the runner refuses at require_seal before any loader. The pre-stage state cannot produce a verdict or load a model.
- [x] **Mutation re-run over the final code (detached, fresh): 52/53 killed by the harness; the one non-kill was the freeze's own new power-pin mutant with a stale target string ("target-not-found", never applied) — retargeted to the real line (`if got != sha_pin:` in load_power) and verified single-shot: mutated → test_analyze_2g 1 failed (KILLED); restored → 12 passed. Effective 53/53.** No stranded backups; tree clean.
- [x] **THE CLASS DEFECT: NOT FOUND.** The three lineage candidates attacked and cleared executably: (1) no verdict input unpinned at analysis time (the 949-read sweep: every read world-tree-content-checked, manifest-pinned, frozen-import-pinned, or literal-pinned; F-2 closed the manifest's completeness gap); (2) every tree the runner can leave delivers INSUFFICIENT_DATA (worlds W6/W7/W8 through the production path; the fix wave's collected gate-1 reads; the real pre-stage tree refuses with the seal named first); (3) no production path is untested where it can bite — the .bin serialization rehearsed end to end, the with_2d secondaries exercised on the real 2d tree and non-gating under a broken one. Two additive findings (F-1 power record unattached; F-2 manifest incompleteness) closed without moving any accepted dial.
