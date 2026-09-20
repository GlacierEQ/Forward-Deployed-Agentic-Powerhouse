from fde_powerhouse.bridges import GeniusBridge, MegaSkillsBridge, MemoryBridge, PipelineBridge


def test_mega_skills_probe_soft():
    p = MegaSkillsBridge().probe()
    assert "available" in p
    assert "repo" in p


def test_genius_probe_and_brief():
    g = GeniusBridge()
    p = g.probe()
    assert "available" in p
    brief = g.role_brief("ForwardDeployedAgentic", ["ship agents"])
    assert brief["role"] == "ForwardDeployedAgentic"


def test_memory_probe():
    p = MemoryBridge().probe()
    assert "tiers_model" in p


def test_pipeline_probe():
    p = PipelineBridge().probe()
    assert p.get("default_deploy_mode") == "approval_packet_only"
