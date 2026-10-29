from pathlib import Path
from unittest.mock import patch

from fde_powerhouse.estate import (
    estate_status,
    load_estate,
    resolve_repo,
    safe_exists,
    safe_glob,
    safe_is_dir,
    safe_is_file,
)


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


def test_inaccessible_candidate_is_unavailable_not_error():
    """Regression for CI run 39922801573: PermissionError on /root candidates.

    pathlib's Path.exists()/is_file()/is_dir() re-raise PermissionError
    when a parent directory cannot be traversed (a non-root CI runner
    probing /root). The probe must treat that as unavailable, never as
    a crash, and never as verified.
    """
    with patch.object(Path, "exists", side_effect=PermissionError("denied")):
        assert safe_exists("/root/.agents/skills") is False
        entry = resolve_repo(load_estate(), "mega_skills")
        assert entry["available"] is False
        assert entry.get("effective_path") is None
    with patch.object(Path, "is_file", side_effect=PermissionError("denied")):
        assert safe_is_file("/root/.mcp_config.json") is False
    with patch.object(Path, "is_dir", side_effect=PermissionError("denied")):
        assert safe_is_dir("/root/.gemini") is False
    with patch.object(Path, "glob", side_effect=PermissionError("denied")):
        assert safe_glob("/root/.agents/skills", "*/SKILL.md") == []
