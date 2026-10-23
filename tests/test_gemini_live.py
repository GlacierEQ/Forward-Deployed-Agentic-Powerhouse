"""Unit tests for Gemini Live 3.8 and AI gateway bridge."""

from fde_powerhouse.bridges.gemini_live import GeminiLiveBridge, LiveSessionConfig


def test_gemini_live_session_config_defaults():
    cfg = LiveSessionConfig()
    d = cfg.to_dict()
    assert d["model"] == "gemini-3.8-live-preview"
    assert d["thinking_budget"] == 2048
    assert d["enable_vad"] is True
    assert "response_modalities" in d["generation_config"]


def test_gemini_live_tool_declaration():
    bridge = GeminiLiveBridge()
    decl = bridge.build_tool_declaration(
        fn_name="search_case_evidence",
        description="Search evidentiary vault for docket records",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": ["query"],
        },
    )
    assert decl["name"] == "search_case_evidence"
    assert "description" in decl
    assert decl["parameters"]["type"] == "OBJECT"
    assert "query" in decl["parameters"]["properties"]


def test_gemini_live_session_builder():
    bridge = GeminiLiveBridge()
    tools = [
        bridge.build_tool_declaration(
            fn_name="verify_hash",
            description="Verify SHA-256",
            parameters={"properties": {"path": {"type": "string"}}},
        )
    ]
    cfg = bridge.build_session_config(
        model="gemini-3.8-live-preview",
        system_instruction="Operate as forward deployed engineer",
        tools=tools,
        thinking_budget=4096,
        voice_name="Aoede",
    )
    assert cfg["model"] == "gemini-3.8-live-preview"
    assert cfg["thinking_budget"] == 4096
    assert len(cfg["tools"]) == 1
    assert cfg["system_instruction"] == "Operate as forward deployed engineer"


def test_gemini_live_inference_routing():
    bridge = GeminiLiveBridge()
    res = bridge.route_inference("Execute forward deployed cycle")
    assert res["status"] == "routed"
    assert res["selected_model"] == "gemini-3.8-live-preview"
    assert "streaming_transport" in res
    assert res["extended_thinking"] is True


def test_gemini_live_probe():
    bridge = GeminiLiveBridge()
    probe = bridge.probe()
    assert "available" in probe
    assert "providers" in probe
    assert "gemini" in probe["providers"]
    assert len(probe["supported_models"]) >= 4
