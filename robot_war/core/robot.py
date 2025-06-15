"""Robot class - handles robot state, energy, and program execution."""

from typing import List, Optional, Tuple
from enum import Enum


class RobotStatus(Enum):
    ALIVE = "alive"
    DEAD = "dead"
    INVISIBLE = "invisible"
    FROZEN = "frozen"  # Energy preservation mode - can't afford next instruction


class Robot:
    """A robot that can be programmed and battles in the arena."""
    
    def __init__(self, player_id: int, x: int, y: int, energy: int = 1500, name: str = None):
        self.player_id = player_id
        self.name = name or f"Robot {player_id}"  # Use provided name or default
        self.x = x
        self.y = y
        self.energy = energy
        self.max_energy = energy
        self.program: List[str] = []
        self.program_counter = 0
        self.status = RobotStatus.ALIVE
        self.invisible_turns = 0
        self.emergency_action: Optional[str] = None  # Circuit de Secours
        # Set emergency threshold slightly above highest instruction cost to ensure affordability
        from .instructions import InstructionSet
        self.emergency_energy_threshold = max(InstructionSet.ENERGY_COSTS.values()) + 10
        
    def get_current_instruction(self) -> Optional[str]:
        """Get the current instruction to execute."""
        if not self.program:
            return None
        return self.program[self.program_counter]
    
    def advance_program_counter(self):
        """Move to next instruction, wrapping around if at end."""
        if self.program:
            self.program_counter = (self.program_counter + 1) % len(self.program)
    
    def take_damage(self, damage: int):
        """Apply damage to robot."""
        self.energy -= damage
        if self.energy <= 0:
            self.status = RobotStatus.DEAD
    
    def use_energy(self, cost: int) -> bool:
        """Use energy for an action. Returns True if successful."""
        if self.energy >= cost:
            self.energy -= cost
            if self.energy <= 0:
                self.status = RobotStatus.DEAD
            return True
        return False
    
    def set_invisible(self, turns: int = 1):
        """Make robot invisible for specified turns."""
        self.status = RobotStatus.INVISIBLE
        self.invisible_turns = turns
    
    def update_invisibility(self):
        """Update invisibility status."""
        if self.status == RobotStatus.INVISIBLE:
            self.invisible_turns -= 1
            if self.invisible_turns <= 0:
                self.status = RobotStatus.ALIVE
    
    def is_alive(self) -> bool:
        """Check if robot is alive (includes frozen robots)."""
        return self.status != RobotStatus.DEAD
    
    def can_execute(self) -> bool:
        """Check if robot can execute instructions (not frozen or dead)."""
        return self.status not in [RobotStatus.DEAD, RobotStatus.FROZEN]
    
    def get_position(self) -> Tuple[int, int]:
        """Get robot's current position."""
        return (self.x, self.y)
    
    def set_position(self, x: int, y: int):
        """Set robot's position."""
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Robot {self.player_id} at ({self.x}, {self.y}) - Energy: {self.energy}"