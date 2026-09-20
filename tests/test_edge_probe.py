from fde_powerhouse.edge_probe import probe_edge


def test_probe_edge_small_sample():
    # Network may be flaky in CI; allow partial failures, require structure
    receipt = probe_edge(limit=3, timeout=4.0, workers=3)
    d = receipt.to_dict()
    assert d["sample_size"] == 3
    assert "sha256" in d and len(d["sha256"]) == 64
    assert len(d["items"]) == 3
