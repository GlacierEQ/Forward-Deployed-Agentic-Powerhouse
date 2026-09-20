from fde_powerhouse.estate import estate_status, load_estate, resolve_repo


def test_load_estate():
    estate = load_estate()
    assert "repos" in estate
    assert "mega_skills" in estate["repos"]
    assert "genius_mastery" in estate["repos"]


def test_resolve_missing_path():
    estate = load_estate()
    entry = resolve_repo(estate, "mega_skills")
    assert entry["available"] is False or entry.get("effective_path")


def test_estate_status_keys():
    status = estate_status()
    assert "mega_skills" in status
    assert "aspen_grove_memory" in status or "pro_memory" in status
