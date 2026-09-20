from fde_powerhouse.invoke import ALLOWED_PIPELINES, invoke_pipeline, mega_skills_root


def test_allowlist():
    assert "control-plane" in ALLOWED_PIPELINES
    assert "inception-to-deployment" in ALLOWED_PIPELINES


def test_invoke_skips_without_path(monkeypatch):
    monkeypatch.delenv("FDE_PATH_MEGA_SKILLS", raising=False)
    # force no estate path
    r = invoke_pipeline("control-plane", validate_only=True)
    assert r.status in ("skip", "fail")
    assert r.available is False or r.action == "skip"


def test_reject_unknown_pipeline():
    r = invoke_pipeline("not-a-real-pipeline", validate_only=True)
    assert r.status == "fail"
    assert r.action == "reject"


def test_mega_root_none_by_default(monkeypatch):
    monkeypatch.delenv("FDE_PATH_MEGA_SKILLS", raising=False)
    # may still resolve if estate.yaml has path; just ensure function returns Path|None
    root = mega_skills_root()
    assert root is None or root.is_dir()
