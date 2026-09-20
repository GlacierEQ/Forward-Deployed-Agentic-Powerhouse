"""Forward Deployed Agentic Powerhouse — maximized + invert-scan."""

__version__ = "0.7.0"

from .cycle import run_cycle
from .modes import MODES
from .plan import CyclePlan, build_plan
from .showcase import run_showcase

__all__ = [
    "run_cycle",
    "run_showcase",
    "MODES",
    "CyclePlan",
    "build_plan",
    "__version__",
]
