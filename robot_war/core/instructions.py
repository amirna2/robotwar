"""Instruction set definitions and execution logic."""

from enum import Enum
from typing import Dict, Any, Optional
import random

from .arena import Direction


class InstructionType(Enum):
    DM = "directed_move"     # Move in player-chosen direction. e.g. DM(NW)
    RM = "random_move"       # Move in random direction
    PM = "pursue_enemy"      # Move toward nearest enemy
    AM = "avoid_enemy"       # Move away from nearest enemy
    MI = "lay_mine"          # Place mine on current tile
    IN = "invisibility"      # Become invisible for 1 turn
    FR = "fire_row"          # Fire horizontally
    FC = "fire_column"       # Fire vertically
    PT = "proximity_test"    # Test if mine or enemy is adjacent


class Instruction:
    """Represents a single robot instruction."""

    def __init__(self, instruction_type: InstructionType,
                 direction: Optional[Direction] = None,
                 parameter: Any = None):
        self.type = instruction_type
        self.direction = direction  # For DM (directed move)
        self.parameter = parameter  # For future extensions

    def __str__(self):
        if self.direction:
            return f"{self.type.name}({self.direction.name})"
        return self.type.name


class InstructionSet:
    """Defines energy costs, damage values, and execution logic for instructions."""

    ENERGY_COSTS = {
        InstructionType.DM: 5,
        InstructionType.RM: 5,
        InstructionType.PM: 10,
        InstructionType.MI: 200,
        InstructionType.IN: 200,
        InstructionType.AM: 15,
        InstructionType.FR: 100,
        InstructionType.FC: 100,
        InstructionType.PT: 4
    }

    DAMAGE_VALUES = {
        InstructionType.MI: 200,  # Mine damage
        InstructionType.FR: 200,  # Row fire damage
        InstructionType.FC: 200   # Column fire damage
    }

    @classmethod
    def get_energy_cost(cls, instruction_type: InstructionType) -> int:
        """Get energy cost for an instruction."""
        return cls.ENERGY_COSTS.get(instruction_type, 0)

    @classmethod
    def get_damage(cls, instruction_type: InstructionType) -> int:
        """Get damage value for an instruction."""
        return cls.DAMAGE_VALUES.get(instruction_type, 0)

    @classmethod
    def get_all_directions(cls) -> list:
        """Get all available directions for movement."""
        return list(Direction)

    @classmethod
    def get_random_direction(cls) -> Direction:
        """Get a random direction."""
        return random.choice(list(Direction))

    @classmethod
    def parse_instruction(cls, instruction_str: str) -> Optional[Instruction]:
        """Parse instruction string into Instruction object."""
        parts = instruction_str.split('(')
        instruction_name = parts[0].strip().upper()

        try:
            instruction_type = InstructionType[instruction_name]
        except KeyError:
            return None

        direction = None
        parameter = None
        
        if len(parts) > 1:
            if instruction_type == InstructionType.DM:
                # Extract direction for DM instruction
                direction_str = parts[1].rstrip(')').strip().upper()
                try:
                    direction = Direction[direction_str]
                except KeyError:
                    return None
            elif instruction_type == InstructionType.PT:
                # Extract conditional actions for PT instruction: PT(action1,action2)
                # Handle nested parentheses properly
                full_content = instruction_str[instruction_str.find('(')+1:instruction_str.rfind(')')]
                actions = []
                paren_depth = 0
                current_action = ""
                
                for char in full_content:
                    if char == '(':
                        paren_depth += 1
                        current_action += char
                    elif char == ')':
                        paren_depth -= 1
                        current_action += char
                    elif char == ',' and paren_depth == 0:
                        actions.append(current_action.strip())
                        current_action = ""
                    else:
                        current_action += char
                
                if current_action.strip():
                    actions.append(current_action.strip())
                
                # Check that we have exactly 2 non-empty actions
                if len(actions) != 2 or any(not action for action in actions):
                    return None  # PT requires exactly 2 non-empty actions
                parameter = tuple(actions)  # Store as (action_if_true, action_if_false)
        elif instruction_type == InstructionType.PT:
            # PT requires parentheses with actions
            return None

        return Instruction(instruction_type, direction, parameter)

    @classmethod
    def instruction_to_string(cls, instruction: Instruction) -> str:
        """Convert instruction to string representation."""
        if instruction.direction:
            return f"{instruction.type.name}({instruction.direction.name})"
        return instruction.type.name

    @classmethod
    def get_instruction_description(cls, instruction_type: InstructionType) -> str:
        """Get human-readable description of instruction."""
        descriptions = {
            InstructionType.DM: "Move in chosen direction (N/NE/E/SE/S/SW/W/NW)",
            InstructionType.RM: "Move in random direction",
            InstructionType.PM: "Move toward nearest enemy",
            InstructionType.MI: "Place mine on current tile",
            InstructionType.IN: "Become invisible for 1 turn",
            InstructionType.AM: "Move away from nearest enemy",
            InstructionType.FR: "Fire horizontally (hits first enemy in row)",
            InstructionType.FC: "Fire vertically (hits first enemy in column)",
            InstructionType.PT: "Test if mine or enemy is adjacent"
        }
        return descriptions.get(instruction_type, "Unknown instruction")


def create_program_from_strings(instruction_strings: list) -> list:
    """Create a program from list of instruction strings."""
    program = []
    for instruction_str in instruction_strings:
        instruction = InstructionSet.parse_instruction(instruction_str)
        if instruction:
            program.append(instruction)
    return program
