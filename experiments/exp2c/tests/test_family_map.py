"""Tests for the scored-battery family map (Michael's ruling 2026-08-01):
the MC power table must model the full 26-rung scored battery (new-pool
specs surviving tier-1 screening, plus the 12 reused 2b survivors), not
just the 14-rung new-spec pool."""
import json
from pathlib import Path

from experiments.exp2c.battery import family_map

REPO_ROOT = Path(__file__).resolve().parents[3]
ITEMS_DIR = REPO_ROOT / "experiments" / "exp2c" / "battery" / "items"
SCREEN_DIR = REPO_ROOT / "experiments" / "exp2c" / "results" / "screen"
MANIFEST = (REPO_ROOT / "experiments" / "exp2c" / "results" /
            "reuse_manifest.json")


def test_real_tree_exact_size_multiset():
    # Growth-battery pin, updated per tier-1 verdict (screen-aware by
    # construction) AND per M1 adjudication (Michael's ruling 2026-08-06:
    # the 2b inclusion bar applies mechanically — hamming8 ejected, 1b
    # margin CP95 UB .3237 >= .25). The battery stands at 34 rungs,
    # 16 families, [4,4,4, 2x9, 1,1,1,1]: base_repr at 4 (base7,
    # oct2dec, base12_digitsum, base13); antonym/odd_one_out at 2;
    # order_stat/seq_extrap at 2; str_align drops to singleton
    # (hamming12 alone). pos_letter's two rungs REJECTED at tier-1 stay
    # excluded, as base12 does.
    families = family_map.scored_battery_families(ITEMS_DIR, SCREEN_DIR)
    assert len(families) == 34
    assert len(set(families.values())) == 16
    assert families["base13"] == "base_repr"
    assert families["odd6"] == "odd_one_out"
    assert families["antonym6"] == "antonym"
    assert "letter_sum" not in families and "letter_prod" not in families
    assert "base12" not in families
    # M1 ejection (ruling 2026-08-06): hamming8 out, its sibling stays
    assert "hamming8" not in families
    assert families["hamming12"] == "str_align"

    sizes = family_map.family_sizes(ITEMS_DIR, SCREEN_DIR)
    assert sorted(sizes, reverse=True) == \
        [4, 4, 4] + [2] * 9 + [1, 1, 1, 1]


def test_base12_ejected_base12_digitsum_present():
    families = family_map.scored_battery_families(ITEMS_DIR, SCREEN_DIR)
    assert "base12" not in families
    assert families["base12_digitsum"] == "base_repr"


def test_reused_families_keys_match_manifest_survivors():
    manifest = json.loads(MANIFEST.read_text())
    assert set(family_map.REUSED_FAMILIES) == set(manifest["survivors"])


def test_reject_verdict_excludes_rung(tmp_path):
    items_dir = tmp_path / "items"
    screen_dir = tmp_path / "screen"
    items_dir.mkdir()
    (screen_dir / "tier1").mkdir(parents=True)

    (items_dir / "ejections.json").write_text("{}")
    (items_dir / "keep_me.json").write_text(
        json.dumps({"name": "keep_me", "family": "widget"}))
    (items_dir / "reject_me.json").write_text(
        json.dumps({"name": "reject_me", "family": "widget"}))
    (items_dir / "no_verdict.json").write_text(
        json.dumps({"name": "no_verdict", "family": "widget"}))

    (screen_dir / "tier1" / "keep_me.json").write_text(
        json.dumps({"name": "keep_me", "tier": 1, "fits": [], "verdict": "pass"}))
    (screen_dir / "tier1" / "reject_me.json").write_text(
        json.dumps({"name": "reject_me", "tier": 1, "fits": [], "verdict": "reject"}))
    # no_verdict.json has no tier1 file at all -- must also be excluded

    families = family_map.scored_battery_families(items_dir, screen_dir)
    # new-pool part: only the "pass"-verdict rung survives
    assert families["keep_me"] == "widget"
    assert "reject_me" not in families
    assert "no_verdict" not in families
    # reused part is merged in regardless (REUSED_FAMILIES is unconditional)
    assert family_map.REUSED_FAMILIES.items() <= families.items()
    assert len(families) == 1 + len(family_map.REUSED_FAMILIES)
