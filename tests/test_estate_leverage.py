from fde_powerhouse.estate_leverage import catalog_summary, leverage_map, load_catalog


def test_catalog_loads():
    c = load_catalog()
    assert c.get("schema", "").startswith("fde.estate_catalog")
    assert "mega_skills" in c
    assert "genius_mastery" in c


def test_catalog_summary_counts():
    s = catalog_summary()
    assert s["mega_skills"]["atomic"] == 709
    assert s["mega_skills"]["mega"] == 29
    assert s["mega_skills"]["pipelines"] >= 6
    assert s["genius_mastery"]["kernel"] is True
    assert s["production_gate_dimensions"] == 7


def test_leverage_map_compose():
    m = leverage_map("compose")
    assert m["mode"] == "compose"
    assert len(m["recommendations"]) >= 3
    systems = {r["system"] for r in m["recommendations"]}
    assert "mega-skills" in systems
    assert "Genius-Mastery" in systems
