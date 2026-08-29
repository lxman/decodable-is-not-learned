# experiments/exp2k/tests/test_tier_2k.py
"""tier_2k with a FAKE sampler and no model: the record shape, the
continuous gate 1 (pass on the committed bytes; halt + marker + .HALTED
rows on one changed draw), skip-if-exists, refusal while a marker
exists, the rung set from 2i's record, run()'s refusals (prereg, seal
exists, frozen unpinned), dry-run, and the rehearsal's no-write
guarantee."""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2i import battery_2i as bi
from experiments.exp2k import battery_2k as bk
from experiments.exp2k.run import rehearse_2k as rh
from experiments.exp2k.run import tier_2k as tr

RUNG = "antonym"


class _Tok:
    all_special_ids = [0]


def _committed(size=RUNG and "1b"):
    return bk.committed_by_item(bk.committed_rows(size, RUNG))


def _fake_sampler(committed, *, diff_at=None):
    def sampler(model, tok, prompt, *, rung, size, mode, item_idx, seeds, draws_per_seed,
                max_new_tokens, terminal_ids):
        assert rung == RUNG and mode == "trained" and tuple(seeds) == bk.SEEDS_2K
        assert draws_per_seed == 64 and max_new_tokens == bt.max_new_tokens(RUNG)
        out = {0: list(committed[item_idx])}
        if diff_at is not None and item_idx == diff_at:
            out[0][3] = out[0][3] + "!"
        for s in (1, 2, 3):
            out[s] = [f" zzz{s}"] * 64
        return out
    return sampler


def _ctx(size="1b"):
    return (_Tok(), None, bk.pythia_sha(size))


@pytest.fixture
def pinned(monkeypatch):
    monkeypatch.setattr(bk, "FROZEN_SHA256_2K", bk.frozen_from_disk(strict=False))


def test_run_rung_writes_the_record_and_passes_gate1(tmp_path, pinned):
    committed = _committed()
    rec = tr.run_rung("1b", RUNG, out_root=tmp_path, model_ctx=_ctx(), verify_fn=a2d.load_verify(),
                      sampler=_fake_sampler(committed))
    cap = bt.load_item_file(RUNG)
    assert bk.tier_record_failures_2k(rec, size="1b", rung=RUNG, cap=cap,
                                      committed_sha=bi.PYTHIA_PREDICTOR_FILES[("1b", RUNG)]) == []
    assert rec["gate1"]["n_diffs"] == 0 and rec["gate1"]["items_compared"] == 500
    rows = bk.read_rows_2k(bk.tier_draws_path(tmp_path, "1b", RUNG))
    assert bk.diff_seed0(rows, bk.committed_rows("1b", RUNG)) == []
    assert rows[0]["draws"]["2"][0] == " zzz2"
    # tallies: seed 0 = 2d's committed tally for the cell; seeds 1–3 zero
    crec = json.loads(bk.committed_record_path("1b", RUNG).read_text())
    assert rec["per_seed_tallies"]["0"] == crec["per_seed_tallies"]["0"]
    assert rec["per_seed_tallies"]["3"] == {"full_string": 0, "n_draws": 32000}
    assert bk.halt_markers(tmp_path) == []
    # skip-if-exists: a sampler that raises is never called
    def boom(*a, **k):
        raise AssertionError("sampler called on a complete rung")
    again = tr.run_rung("1b", RUNG, out_root=tmp_path, model_ctx=_ctx(),
                        verify_fn=a2d.load_verify(), sampler=boom)
    assert again == rec


def test_gate1_halts_on_one_changed_draw(tmp_path, pinned):
    committed = _committed()
    with pytest.raises(RuntimeError, match="GATE 1 FIRED"):
        tr.run_rung("1b", RUNG, out_root=tmp_path, model_ctx=_ctx(), verify_fn=a2d.load_verify(),
                    sampler=_fake_sampler(committed, diff_at=7))
    m = bk.halt_marker_path(tmp_path, "1b", RUNG)
    assert m.is_file()
    marker = json.loads(m.read_text())
    assert marker["item"] == 7 and marker["n_diffs"] == 1 and marker["diffs"][0]["draw"] == 3
    assert marker["items_compared"] == 8 and marker["rung"] == RUNG and marker["size"] == "1b"
    assert not bk.tier_draws_path(tmp_path, "1b", RUNG).exists()
    assert not bk.tier_record_path(tmp_path, "1b", RUNG).exists()
    with gzip.open(bk.halted_draws_path(tmp_path, "1b", RUNG), "rt") as f:
        n = sum(1 for _ in f)
    assert n == 8
    # freeze F-1: the scan covers BOTH artifacts the halt leaves — the
    # marker and the evidence gz — so either alone refuses.
    assert bk.halt_markers(tmp_path) == [m, bk.halted_draws_path(tmp_path, "1b", RUNG)]
    m.unlink()
    assert bk.halt_markers(tmp_path) == [bk.halted_draws_path(tmp_path, "1b", RUNG)]
    m.write_text(json.dumps(marker))
    # any later call refuses while the marker exists — even a clean sampler
    with pytest.raises(RuntimeError, match="halt"):
        tr.run_rung("1b", RUNG, out_root=tmp_path, model_ctx=_ctx(), verify_fn=a2d.load_verify(),
                    sampler=_fake_sampler(committed))


def test_run_rung_refuses_a_model_sha_that_is_not_2d_s(tmp_path, pinned):
    with pytest.raises(RuntimeError, match="model_sha"):
        tr.run_rung("1b", RUNG, out_root=tmp_path, model_ctx=(_Tok(), None, "other"),
                    verify_fn=a2d.load_verify(), sampler=_fake_sampler(_committed()))


def test_gate1_catches_a_short_draw_list_even_when_the_matching_prefix_agrees(tmp_path, pinned):
    # one draw short on item 0's seed-0 stream, but every draw that IS
    # present matches — the per-draw `g != w` comparison alone finds
    # nothing (zip stops at the shorter side); only the explicit
    # length check catches the missing coverage.
    committed = _committed()

    def sampler(model, tok, prompt, *, rung, size, mode, item_idx, seeds, draws_per_seed,
                max_new_tokens, terminal_ids):
        out = {0: list(committed[item_idx])}
        if item_idx == 0:
            out[0] = out[0][:-1]
        for s in (1, 2, 3):
            out[s] = [f" zzz{s}"] * 64
        return out

    with pytest.raises(RuntimeError, match="GATE 1 FIRED"):
        tr.run_rung("1b", RUNG, out_root=tmp_path, model_ctx=_ctx(), verify_fn=a2d.load_verify(),
                    sampler=sampler)


def test_run_rung_refuses_against_2bs_pin_even_when_it_matches_the_committed_record(
        tmp_path, pinned, monkeypatch):
    # the committed record's own model_sha equals 2b's REAL pin, so a
    # model_ctx sha that matches the record but not 2b's pin only
    # distinguishes the FIRST refusal (against bk.pythia_sha) from the
    # SECOND, later one (against the committed record) — closing the gap
    # where the first check could be silently dropped and the second
    # would still fire on ordinary drifted input.
    real_sha = json.loads(bk.committed_record_path("1b", RUNG).read_text())["model_sha"]
    monkeypatch.setattr(bk, "pythia_sha", lambda size: "not-2bs-real-pin")
    with pytest.raises(RuntimeError, match="model_sha"):
        tr.run_rung("1b", RUNG, out_root=tmp_path, model_ctx=(_Tok(), None, real_sha),
                    verify_fn=a2d.load_verify(), sampler=_fake_sampler(_committed()))


def test_rungs_2k_is_2i_r_cap_alphabetical():
    assert tr.rungs_2k() == bk.R_CAP_DESIGN
    with pytest.raises(ValueError, match="R_CAP"):
        tr.rungs_2k(root_2i=Path("/nonexistent"))


def test_run_refuses_without_the_tag_and_with_a_seal(tmp_path, pinned):
    with pytest.raises(RuntimeError, match="does not exist"):
        tr.run("1b", out_root=tmp_path, loader=lambda size, device: _ctx(size),
               sampler=_fake_sampler(_committed()), tag_exists=lambda t: False)
    ok = dict(tag_exists=lambda t: True,
              blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel))
    bk.seal_path(tmp_path).parent.mkdir(parents=True)
    bk.seal_path(tmp_path).write_text("{}")
    with pytest.raises(RuntimeError, match="sealed"):
        tr.run("1b", out_root=tmp_path, loader=lambda size, device: _ctx(size),
               sampler=_fake_sampler(_committed()), **ok)


def test_run_refuses_unpinned_frozen(tmp_path, monkeypatch):
    monkeypatch.setattr(bk, "FROZEN_SHA256_2K", {})
    with pytest.raises(RuntimeError, match="not pinned"):
        tr.run("1b", out_root=tmp_path, loader=lambda size, device: _ctx(size),
               sampler=_fake_sampler(_committed()), tag_exists=lambda t: True,
               blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel))


def test_run_dry_run_lists_pending_and_loads_nothing(tmp_path, pinned, capsys):
    def no_loader(size, device):
        raise AssertionError("loader called on a dry run")
    tr.run("1b", out_root=tmp_path, loader=no_loader, dry_run=True, tag_exists=lambda t: True,
           blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel))
    out = capsys.readouterr().out
    assert "9 rung(s)" in out and "add3_mid" in out


def test_run_one_rung_end_to_end_with_the_fake(tmp_path, pinned, monkeypatch):
    monkeypatch.setattr(tr, "rungs_2k", lambda root_2i=None: (RUNG,))
    recs = tr.run("1b", out_root=tmp_path, loader=lambda size, device: _ctx(size),
                  sampler=_fake_sampler(_committed()), tag_exists=lambda t: True,
                  blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel))
    assert len(recs) == 1 and tr.tier_complete(tmp_path, "1b") is False   # 8 rungs pending
    assert bk.tier_record_path(tmp_path, "1b", RUNG).is_file()


def test_rehearsal_prints_and_writes_nothing(tmp_path, capsys):
    committed = _committed()
    r = rh.run(rung=RUNG, item=0, size="1b", out_root=tmp_path,
               loader=lambda size, device: _ctx(size), sampler=_fake_sampler(committed))
    assert r["seed0_identical"] is True and r["n_draws"] == 256
    assert not (tmp_path / "results").exists()
    out = capsys.readouterr().out
    assert "IDENTICAL" in out
    r2 = rh.run(rung=RUNG, item=0, size="1b", out_root=tmp_path,
                loader=lambda size, device: _ctx(size),
                sampler=_fake_sampler(committed, diff_at=0))
    assert r2["seed0_identical"] is False and r2["n_diffs"] == 1
