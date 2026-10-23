"""Estate bridges — mega-skills, genius, memory, pipelines, gemini_live, mcp_mesh, pointer_memory."""

from .gemini_live import GeminiLiveBridge
from .genius import GeniusBridge
from .mcp_mesh import MCPMeshBridge
from .mega_skills import MegaSkillsBridge
from .memory import MemoryBridge
from .pipelines import PipelineBridge
from .pointer_memory import PointerMemoryBridge

__all__ = [
    "GeminiLiveBridge",
    "GeniusBridge",
    "MCPMeshBridge",
    "MegaSkillsBridge",
    "MemoryBridge",
    "PipelineBridge",
    "PointerMemoryBridge",
]
