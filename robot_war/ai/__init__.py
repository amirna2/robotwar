"""AI opponents and strategies for Robot War.

This module provides sophisticated AI robot profiles with diverse strategic approaches,
from aggressive berserkers to defensive guardians and stealthy ghosts.
"""

from .profiles import (
    AIPersonality,
    AIProfile,
    AIProfileLibrary,
    get_ai_robot_name,
    validate_ai_program
)

__all__ = [
    'AIPersonality',
    'AIProfile',
    'AIProfileLibrary',
    'get_ai_robot_name',
    'validate_ai_program'
]