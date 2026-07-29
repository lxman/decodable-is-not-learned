from experiments.exp2c.run import reuse_manifest as rm


def test_build_covers_all_survivors():
    m = rm.build(write=False)
    assert len(m["survivors"]) == 12
    s = m["survivors"]["reverse_string"]
    assert s["item_file"]["sha256"]
    assert not s["item_file"]["path"].startswith("/")
    # 10 known_absent + 10 m3 + 10 shuffled fits per survivor
    for stage in ("known_absent", "m3", "shuffled"):
        assert len(s["fits"][stage]) == 10


def test_verify_detects_no_drift():
    rm.build()
    ok, drifted = rm.verify()
    assert ok is True
    assert drifted == []
