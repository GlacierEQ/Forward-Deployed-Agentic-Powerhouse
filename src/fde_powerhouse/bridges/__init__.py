"""Estate bridges — mega-skills, genius, memory, pipelines (adapters only)."""

from .genius import GeniusBridge
from .mega_skills import MegaSkillsBridge
from .memory import MemoryBridge
from .pipelines import PipelineBridge

__all__ = [
    "MegaSkillsBridge",
    "GeniusBridge",
    "MemoryBridge",
    "PipelineBridge",
]
