"""Menu navigation system with arrow key support for robot programming."""

import sys
import termios
import tty
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Any
from enum import Enum


class MenuKey(Enum):
    UP = 'up'
    DOWN = 'down'
    ENTER = 'enter'
    ESCAPE = 'escape'
    UNKNOWN = 'unknown'


class Navigable(ABC):
    """Interface for navigable menu items."""
    
    @abstractmethod
    def get_display_text(self) -> str:
        """Get text to display for this menu item."""
        pass
    
    @abstractmethod
    def get_value(self) -> Any:
        """Get the value this menu item represents."""
        pass


class Renderable(ABC):
    """Interface for renderable menu components."""
    
    @abstractmethod
    def render(self) -> str:
        """Render the component to string."""
        pass


class Selectable(ABC):
    """Interface for selectable menu behavior."""
    
    @abstractmethod
    def select(self, item: Navigable) -> Any:
        """Handle selection of a menu item."""
        pass


class MenuItem(Navigable):
    """A single menu item with display text and value."""
    
    def __init__(self, display_text: str, value: Any, description: str = ""):
        self.display_text = display_text
        self.value = value
        self.description = description
    
    def get_display_text(self) -> str:
        return self.display_text
    
    def get_value(self) -> Any:
        return self.value


class KeyboardInput:
    """Handles terminal keyboard input for menu navigation."""
    
    @staticmethod
    def get_key() -> MenuKey:
        """Get a single keypress and return corresponding MenuKey."""
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())
            
            # Read key
            key = sys.stdin.read(1)
            
            # Handle escape sequences (arrow keys)
            if key == '\x1b':
                key += sys.stdin.read(2)
                if key == '\x1b[A':
                    return MenuKey.UP
                elif key == '\x1b[B':
                    return MenuKey.DOWN
                else:
                    return MenuKey.ESCAPE
            elif key == '\r' or key == '\n':
                return MenuKey.ENTER
            elif key == '\x1b':
                return MenuKey.ESCAPE
            else:
                return MenuKey.UNKNOWN
                
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class MenuRenderer(Renderable):
    """Renders menu with box drawing and highlighting."""
    
    def __init__(self, title: str, items: List[MenuItem], selected_index: int = 0):
        self.title = title
        self.items = items
        self.selected_index = selected_index
    
    def render(self) -> str:
        """Render the menu with box drawing characters."""
        if not self.items:
            return f"┌─ {self.title} ─┐\n│ No items             │\n└──────────────────────┘"
        
        # Use fixed width for consistent appearance across all menus
        FIXED_BOX_WIDTH = 40
        
        # Build menu
        lines = []
        
        # Top border with title
        title_with_spaces = f" {self.title} "
        available_space = FIXED_BOX_WIDTH - len(title_with_spaces) - 2  # 2 for "┌" and "┐"
        left_dashes = available_space // 2
        right_dashes = available_space - left_dashes
        lines.append(f"┌{'─' * left_dashes}{title_with_spaces}{'─' * right_dashes}┐")
        
        # Menu items
        for i, item in enumerate(self.items):
            text = item.get_display_text()
            if i == self.selected_index:
                content = f"  > {text}"
            else:
                content = f"    {text}"
            
            # Truncate if too long, then pad to fixed width
            if len(content) > FIXED_BOX_WIDTH - 2:
                content = content[:FIXED_BOX_WIDTH - 5] + "..."
            
            padding = FIXED_BOX_WIDTH - len(content) - 2  # 2 for borders
            lines.append(f"│{content}{' ' * padding}│")
        
        # Bottom border
        lines.append(f"└{'─' * (FIXED_BOX_WIDTH - 2)}┘")
        
        return '\n'.join(lines)


class MenuSelector(Selectable):
    """Main menu selection handler with navigation logic."""
    
    def __init__(self, title: str, items: List[MenuItem]):
        self.title = title
        self.items = items
        self.selected_index = 0
        self.renderer = MenuRenderer(title, items, self.selected_index)
        self.keyboard = KeyboardInput()
    
    def select(self, item: Navigable) -> Any:
        """Handle item selection - returns the selected value."""
        return item.get_value()
    
    def navigate(self) -> Optional[Any]:
        """Run the menu navigation loop. Returns selected value or None if escaped."""
        if not self.items:
            return None
        
        while True:
            # Clear screen and render menu
            print('\033[2J\033[H', end='')  # Clear screen, move cursor to top
            self.renderer.selected_index = self.selected_index
            print(self.renderer.render())
            
            # Get user input
            key = self.keyboard.get_key()
            
            if key == MenuKey.UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif key == MenuKey.DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
            elif key == MenuKey.ENTER:
                selected_item = self.items[self.selected_index]
                return self.select(selected_item)
            elif key == MenuKey.ESCAPE:
                return None


class ProgramDisplay(Renderable):
    """Displays current robot program being built."""
    
    def __init__(self, robot_name: str, program: List[str], max_steps: int, starting_energy: int, emergency_action: str = None):
        self.robot_name = robot_name
        self.program = program
        self.max_steps = max_steps
        self.starting_energy = starting_energy
        self.emergency_action = emergency_action
    
    def render(self) -> str:
        """Render the program display header."""
        from ..core.instructions import InstructionSet, InstructionType
        
        # Calculate energy cost
        total_energy_cost = 0
        for instruction_str in self.program:
            instruction = InstructionSet.parse_instruction(instruction_str)
            if instruction:
                total_energy_cost += InstructionSet.get_energy_cost(instruction.type)
        
        # Build display with proper width
        header_text = f"ROBOT PROGRAMMING - {self.robot_name}"
        display_width = max(60, len(header_text) + 4)  # Minimum 60 chars, or wider if needed
        
        lines = []
        lines.append(header_text)
        lines.append("─" * display_width)
        
        # Show current program - display all steps, not truncated
        if self.program:
            lines.append("Current Program:")
            for i, instruction in enumerate(self.program, 1):
                lines.append(f"  {i:2d}. {instruction}")
        else:
            lines.append("Current Program: [Empty]")
        
        lines.append("")  # Spacing line
        
        # Show stats on separate lines for clarity
        lines.append(f"Energy Cost: {total_energy_cost}")
        lines.append(f"Steps: {len(self.program)}/{self.max_steps}")
        
        # Show emergency action
        if self.emergency_action:
            lines.append(f"Emergency Action: {self.emergency_action}")
        else:
            lines.append("Emergency Action: [Not Set]")
        
        lines.append("─" * display_width)
        lines.append("")  # Empty line for spacing
        
        return '\n'.join(lines)


class MenuFactory:
    """Factory for creating different types of menus following Open/Closed principle."""
    
    @staticmethod
    def create_instruction_menu() -> MenuSelector:
        """Create menu for selecting robot instructions."""
        items = [
            MenuItem("DM (Directed Move)", "DM", "Move in chosen direction"),
            MenuItem("RM (Random Move)", "RM", "Move in random direction"),
            MenuItem("PM (Pursue Enemy)", "PM", "Move toward nearest enemy"),
            MenuItem("AM (Avoid Enemy)", "AM", "Move away from nearest enemy"),
            MenuItem("MI (Place Mine)", "MI", "Place mine on current position"),
            MenuItem("IN (Invisibility)", "IN", "Become invisible for 1 turn"),
            MenuItem("PT (Proximity Test)", "PT", "Conditional action based on nearby enemies"),
        ]
        return MenuSelector("SELECT INSTRUCTION", items)
    
    @staticmethod
    def create_direction_menu() -> MenuSelector:
        """Create menu for selecting movement directions."""
        items = [
            MenuItem("N (North)", "N", "Move north"),
            MenuItem("NE (Northeast)", "NE", "Move northeast"),
            MenuItem("E (East)", "E", "Move east"),
            MenuItem("SE (Southeast)", "SE", "Move southeast"),
            MenuItem("S (South)", "S", "Move south"),
            MenuItem("SW (Southwest)", "SW", "Move southwest"),
            MenuItem("W (West)", "W", "Move west"),
            MenuItem("NW (Northwest)", "NW", "Move northwest"),
        ]
        return MenuSelector("SELECT DIRECTION", items)
    
    @staticmethod
    def create_action_menu(context: str) -> MenuSelector:
        """Create menu for selecting actions in PT conditions."""
        items = [
            MenuItem("DM (Directed Move)", "DM", "Move in chosen direction"),
            MenuItem("RM (Random Move)", "RM", "Move in random direction"),
            MenuItem("PM (Pursue Enemy)", "PM", "Move toward nearest enemy"),
            MenuItem("AM (Avoid Enemy)", "AM", "Move away from nearest enemy"),
            MenuItem("MI (Place Mine)", "MI", "Place mine on current position"),
            MenuItem("IN (Invisibility)", "IN", "Become invisible for 1 turn"),
        ]
        return MenuSelector(f"SELECT ACTION ({context})", items)