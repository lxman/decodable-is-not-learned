import io
import json

import numpy as np
import pytest

from experiments.exp5 import battery_5 as b5
from experiments.exp5 import slice_5 as sl5


class _Tok:
    """A fake tokenizer: one id per whitespace word (id = len(word)), no
    specials — enough to drive build_slice_5's counting exactly."""
    eos_token_id = 0

    def __call__(self, text, add_special_tokens=False, truncation=False, max_length=None):
        ids = [len(w) for w in text.split()]
        if truncation and max_length is not None:
            ids = ids[:max_length]
        return {"input_ids": ids}


def _zst_file(tmp_path, docs):
    import zstandard as zstd
    raw = "".join(json.dumps({"text": t, "meta": {"pile_set_name": s}}) + "\n" for t, s in docs)
    p = tmp_path / "val.jsonl.zst"
    p.write_bytes(zstd.ZstdCompressor().compress(raw.encode("utf-8")))
    return p


def test_iter_documents_streams_in_file_order(tmp_path):
    p = _zst_file(tmp_path, [("a b c", "Pile-CC"), ("d e", "Github")])
    assert list(sl5.iter_documents_5(p)) == [("a b c", "Pile-CC"), ("d e", "Github")]


def test_build_slice_counts_skips_truncates_and_lands_exactly(tmp_path):
    # docs of 70, 10 (skipped: < 64), 70, 2048+50 (truncated to 2048), 70 words
    docs = [(" ".join(["x"] * 70), "A"), (" ".join(["y"] * 10), "B"),
            (" ".join(["x"] * 70), "A"), (" ".join(["z"] * 2098), "C"),
            (" ".join(["x"] * 70), "A")]
    p = _zst_file(tmp_path, docs)
    sl = sl5.build_slice_5(_Tok(), p, n_scored=69 + 69 + 100, max_tokens=2048, min_tokens=64)
    m = sl["meta"]
    assert m["n_read"] == 4 and m["n_skipped"] == 1 and m["n_docs"] == 3
    assert m["n_scored"] == 238
    assert m["last_doc_truncated"] == {"doc_index": 2, "from": 2048, "to": 101}
    assert sl["offsets"].tolist() == [0, 70, 140, 241]
    assert sl["set_names"] == ["A", "C"] and sl["set_index"].tolist() == [0, 0, 1]
    assert int((sl["offsets"][1:] - sl["offsets"][:-1] - 1).sum()) == 238


def test_build_slice_refuses_when_the_file_runs_out(tmp_path):
    p = _zst_file(tmp_path, [(" ".join(["x"] * 70), "A")])
    with pytest.raises(ValueError, match="ran out"):
        sl5.build_slice_5(_Tok(), p, n_scored=1000)


def test_write_load_roundtrip_and_sha_pin(tmp_path):
    p = _zst_file(tmp_path, [(" ".join(["x"] * 70), "A"), (" ".join(["w"] * 80), "B")])
    sl = sl5.build_slice_5(_Tok(), p, n_scored=100)
    out = tmp_path / "slice.npz"
    sl5.write_slice_5(out, sl)
    from experiments.exp2g import battery_2g as bg
    back = sl5.load_slice_5(out, sha_pin=bg.sha256_file(out))
    assert sl5.slice_equal_5(sl, back) == []
    with pytest.raises(ValueError, match="pinned"):
        sl5.load_slice_5(out, sha_pin="0" * 64)
    sl5.write_slice_5(tmp_path / "again.npz", sl)
    assert (tmp_path / "again.npz").read_bytes() == out.read_bytes()   # byte-deterministic


def test_slice_equal_5_catches_a_set_index_mismatch():
    """Task 6 mutation kill: `slice_equal_5` compares `set_index`, not
    only `ids`/`offsets` — two slices whose ids/offsets/set_names all
    agree but whose per-document set assignment differs must NOT read
    as equal."""
    a = {"ids": np.array([1, 2, 3], np.int32), "offsets": np.array([0, 2, 3], np.int64),
        "set_index": np.array([0, 1], np.int16), "set_names": ["A", "B"],
        "meta": {"n_docs": 2, "n_read": 2, "n_skipped": 0, "n_scored": 1,
                "last_doc_truncated": None}}
    b = {**a, "set_index": np.array([1, 0], np.int16)}
    assert sl5.slice_equal_5(a, dict(a)) == []
    assert "set_index" in sl5.slice_equal_5(a, b)


def test_slice_batches_right_pad_and_mask():
    sl = {"ids": np.array([1, 2, 3, 4, 5, 6, 7], np.int32), "offsets": np.array([0, 3, 7]),
          "set_index": np.array([0, 0], np.int16), "set_names": ["A"], "meta": {}}
    (docs, ids, mask), = list(sl5.slice_batches_5(sl, 8))
    assert docs == [0, 1]
    assert ids.tolist() == [[1, 2, 3, b5.PAD_ID_5], [4, 5, 6, 7]]
    assert mask.tolist() == [[1, 1, 1, 0], [1, 1, 1, 1]]


def test_loss_from_per_doc_is_the_token_weighted_mean():
    sl = {"ids": np.zeros(10, np.int32), "offsets": np.array([0, 4, 10]),
          "set_index": np.array([0, 1], np.int16), "set_names": ["A", "B"],
          "meta": {"n_scored": 8}}
    out = sl5.loss_from_per_doc_5(sl, per_doc_sums=np.array([3.0, 10.0]),
                                  per_doc_n=np.array([3, 5]))
    assert out["n_scored"] == 8 and abs(out["loss"] - 13.0 / 8) < 1e-12
    assert out["per_set"]["A"] == {"loss": 1.0, "n_tokens": 3}
    assert out["per_set"]["B"] == {"loss": 2.0, "n_tokens": 5}
    assert out["per_doc_loss"] == [1.0, 2.0]


def test_loss_record_passes_battery_contract_on_the_pure_aggregation():
    sl = {"ids": np.zeros(10, np.int32), "offsets": np.array([0, 4, 10]),
          "set_index": np.array([0, 1], np.int16), "set_names": ["A", "B"],
          "meta": {"n_scored": 8}}
    rec = sl5.loss_from_per_doc_5(sl, per_doc_sums=np.array([3.0, 10.0]), per_doc_n=np.array([3, 5]))
    rec.update({"slice_sha256": "s", "batch_size": 8, "pad_id": 0, "logits_dtype": "float16",
                "log_softmax_dtype": "float32", "finite": True, "n_nonfinite": 0,
                "stack": {"torch": "x"}, "device": "cuda", "host_sha256": "h"})
    host = {"stack": {"torch": "x"}, "device": "cuda", "sha256": "h"}
    assert b5.loss_record_failures_5(rec, size="1b", step=1, host=host, slice_sha="s", n_scored=8) == []
    bad = b5.loss_record_failures_5(rec, size="1b", step=1, host=host, slice_sha="s")
    assert bad and bad[0] == f"1b/step1/_loss: n_scored 8 != {b5.SLICE_N_SCORED_5}"


@pytest.mark.slow
def test_committed_slice_loads_at_its_pin_and_meta_matches():
    sl = sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5)
    assert sl["meta"]["n_scored"] == b5.SLICE_N_SCORED_5
    assert int((sl["offsets"][1:] - sl["offsets"][:-1] - 1).sum()) == b5.SLICE_N_SCORED_5
    assert all(int(n) >= b5.SLICE_MIN_TOKENS_5 for n in (sl["offsets"][1:] - sl["offsets"][:-1])[:-1])
    assert int((sl["offsets"][1:] - sl["offsets"][:-1]).max()) <= b5.SLICE_MAX_TOKENS_5
    for k, v in b5.SLICE_META_PIN_5.items():
        assert sl["meta"][k] == v, k
