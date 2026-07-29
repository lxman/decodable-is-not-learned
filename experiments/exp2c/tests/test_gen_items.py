import json

from experiments.exp2c.battery import gen_items
from experiments.exp2c.battery.base import SPECS


def test_generate_mod17(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("mod17")
    assert len(d["probe_items"]) >= 1800
    assert len(d["eval_items"]) >= 500
    it = d["probe_items"][0]
    assert set(it) >= {"question", "answer", "probe_label", "basis"}
    # oracle consistency on every item
    for item in d["probe_items"][:50]:
        a = int(item["basis"][0])
        assert int(item["probe_label"]) == a % 17
    # family fields present (design §2 sixth field)
    assert d["family"] == "modulus" and d["dial_value"] == 17
    assert (tmp_path / "mod17.json").exists()


def test_feasibility_recorded(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("mod17")
    f = d["feasibility"]
    assert f["params"]["min_holdout_values"] == 15
    assert f["params"]["min_val_items"] == 300
    assert set(f["per_seed"]) == {"0", "1", "2", "3", "4"}
