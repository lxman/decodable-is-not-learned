"""The untrained runner must produce a probe result without training.
Marked slow: it constructs a real model. No assertion is made about whether
S1 fires — that is the experiment's question, not the test's."""
import pytest
from experiments.exp1b.run.run_untrained import record_path, run_untrained


def test_record_path_is_the_durable_unit(tmp_path):
    p = record_path(tmp_path, "grokking", "1M", 100)
    assert p.parent.name == "1M"
    assert p.parent.parent.name == "grokking"
    assert p.name == "seed100.json"


@pytest.mark.slow
def test_produces_a_probe_result_without_training(tmp_path):
    rec = run_untrained("grokking", "1M", 100, out_root=tmp_path)
    assert rec.system == "grokking"
    assert rec.seed == 100
    assert isinstance(rec.s1.present, bool)
    assert rec.s1.checkpoint_id.startswith("init")
    assert record_path(tmp_path, "grokking", "1M", 100).exists()
