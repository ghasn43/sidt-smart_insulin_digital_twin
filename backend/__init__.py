"""
Smart Insulin Digital Twin Backend.
Core simulation and optimization engine.
"""

from . import core
from . import physiology
from . import manufacturability
from . import nano
from . import optimize

__version__ = "1.0.0"
__all__ = [
    'core',
    'physiology',
    'manufacturability',
    'nano',
    'optimize',
]
