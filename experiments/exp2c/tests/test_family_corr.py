from experiments.exp2c import family_corr


def test_estimate_reads_2b_record():
    d = family_corr.estimate(write=False)
    assert set(p["pair"][0] for p in d["pairs"]) == {"add3_mid", "base7"}
    assert 0.0 <= d["rho_family"] <= 0.9
    # sanity: correlations computed from 5-seed vectors, both sizes
    assert all(len(p["seed_margins_a"]) == 5 for p in d["pairs"])
