from fde_powerhouse.genius_invoke import invoke_genius_doctor, invoke_genius_role_brief


def test_genius_doctor_skips_without_path(monkeypatch):
    monkeypatch.delenv("FDE_PATH_GENIUS_MASTERY", raising=False)
    r = invoke_genius_doctor()
    assert r.status in ("skip", "ok", "fail")


def test_role_brief_always_ok():
    r = invoke_genius_role_brief()
    assert r.status == "ok"
    assert r.detail["brief"]["role"] == "ForwardDeployedAgentic"
