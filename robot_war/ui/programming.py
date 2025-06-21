"""Robot programming interface using menu navigation."""

from typing import List, Optional
from .menu import MenuFactory, ProgramDisplay
from .terminal_output import TerminalOutputManager


class ProgramBuilder:
    """Builds and validates robot programs following Single Responsibility principle."""
    
    def __init__(self, max_steps: int, starting_energy: int):
        self.max_steps = max_steps
        self.starting_energy = starting_energy
        self.program: List[str] = []
        self.emergency_action: Optional[str] = None
    
    def add_instruction(self, instruction: str) -> bool:
        """Add instruction to program. Returns True if successful."""
        if len(self.program) >= self.max_steps:
            return False
        
        self.program.append(instruction)
        return True
    
    def remove_last_instruction(self) -> bool:
        """Remove last instruction from program. Returns True if successful."""
        if self.program:
            self.program.pop()
            return True
        return False
    
    def get_program(self) -> List[str]:
        """Get the current program."""
        return self.program.copy()
    
    def is_complete(self) -> bool:
        """Check if program has at least one instruction."""
        return len(self.program) > 0
    
    def get_total_energy_cost(self) -> int:
        """Calculate total energy cost for one full program execution."""
        from ..core.instructions import InstructionSet
        
        total_cost = 0
        for instruction_str in self.program:
            instruction = InstructionSet.parse_instruction(instruction_str)
            if instruction:
                total_cost += InstructionSet.get_energy_cost(instruction.type)
        return total_cost
    
    def set_emergency_action(self, action: str) -> bool:
        """Set emergency action. Returns True if successful."""
        self.emergency_action = action
        return True
    
    def get_emergency_action(self) -> Optional[str]:
        """Get the current emergency action."""
        return self.emergency_action


class InstructionBuilder:
    """Builds complex instructions with parameters following Single Responsibility."""
    
    def __init__(self):
        self.menu_factory = MenuFactory()
    
    def build_instruction(self, instruction_type: str) -> Optional[str]:
        """Build complete instruction string with parameters if needed."""
        if instruction_type == "DM":
            return self._build_directed_move()
        elif instruction_type == "PT":
            return self._build_proximity_test()
        else:
            # Simple instructions without parameters
            return instruction_type
    
    def _build_directed_move(self) -> Optional[str]:
        """Build DM instruction with direction parameter."""
        direction_menu = self.menu_factory.create_direction_menu()
        direction = direction_menu.navigate()
        
        if direction is None:
            return None
        
        return f"DM({direction})"
    
    def _build_proximity_test(self) -> Optional[str]:
        """Build PT instruction with conditional actions."""
        # Get action for "if enemy detected" - can include FR/FC
        true_action_menu = self.menu_factory.create_combat_action_menu("IF ENEMY DETECTED")
        true_action_type = true_action_menu.navigate()
        
        if true_action_type is None:
            return None
        
        # Build the true action instruction
        true_action = self._build_sub_instruction(true_action_type)
        if true_action is None:
            return None
        
        # Get action for "if no enemy detected" - cannot include FR/FC
        false_action_menu = self.menu_factory.create_non_combat_action_menu("IF NO ENEMY")
        false_action_type = false_action_menu.navigate()
        
        if false_action_type is None:
            return None
        
        # Build the false action instruction
        false_action = self._build_sub_instruction(false_action_type)
        if false_action is None:
            return None
        
        return f"PT({true_action},{false_action})"
    
    def _build_sub_instruction(self, instruction_type: str) -> Optional[str]:
        """Build sub-instruction for PT conditions."""
        if instruction_type == "DM":
            direction_menu = self.menu_factory.create_direction_menu()
            direction = direction_menu.navigate()
            if direction is None:
                return None
            return f"DM({direction})"
        else:
            return instruction_type


class RobotProgrammingInterface:
    """Main programming interface coordinating all components."""
    
    def __init__(self, robot_name: str, max_steps: int, starting_energy: int):
        self.robot_name = robot_name
        self.max_steps = max_steps
        self.starting_energy = starting_energy
        
        self.program_builder = ProgramBuilder(max_steps, starting_energy)
        self.instruction_builder = InstructionBuilder()
        self.menu_factory = MenuFactory()
        self.terminal = TerminalOutputManager()  # Dependency injection
    
    def program_robot(self) -> List[str]:
        """Run the programming interface. Returns the completed program."""
        while True:
            # Show current program status
            self._display_program_status()
            
            # Show main menu options
            action = self._show_main_menu()
            
            if action == "add":
                self._add_instruction()
            elif action == "remove":
                self._remove_instruction()
            elif action == "emergency":
                self._set_emergency_action()
            elif action == "done":
                if self.program_builder.is_complete():
                    break
                else:
                    self._show_message("Program must have at least one instruction!")
            elif action == "quit":
                return []  # Empty program indicates quit
        
        return self.program_builder.get_program()
    
    def _display_program_status(self):
        """Display current program and stats."""
        print('\033[2J\033[H', end='')  # Clear screen
        
        display = ProgramDisplay(
            self.robot_name,
            self.program_builder.get_program(),
            self.max_steps,
            self.starting_energy
        )
        display_output = display.render()
        # Center each line of the program display
        for line in display_output.split('\n'):
            print(self.terminal.text_formatter.center_text(line))
    
    def _show_main_menu(self) -> str:
        """Show main programming menu with program display."""
        from .menu import MenuItem, MenuSelector
        
        items = []
        
        # Add instruction option
        if len(self.program_builder.program) < self.max_steps:
            items.append(MenuItem("Add Instruction", "add", "Add new instruction to program"))
        
        # Remove instruction option
        if self.program_builder.program:
            items.append(MenuItem("Remove Last Instruction", "remove", "Remove last instruction"))
        
        # Emergency action option
        emergency_text = "Set Emergency Action" if not self.program_builder.emergency_action else "Change Emergency Action"
        items.append(MenuItem(emergency_text, "emergency", "Set action when energy is low"))
        
        # Done option
        if self.program_builder.is_complete():
            items.append(MenuItem("Finish Programming", "done", "Complete robot programming"))
        
        # Always show quit option
        items.append(MenuItem("Quit Programming", "quit", "Exit without saving"))
        
        # Create menu with custom navigation that shows program display
        menu = MenuSelector("PROGRAMMING OPTIONS", items)
        
        # Navigate with program display integration
        return self._navigate_with_display(menu)
    
    def _navigate_with_display(self, menu) -> str:
        """Navigate menu while showing program display at top."""
        if not menu.items:
            return "quit"
        
        while True:
            # Clear screen and show program display
            print('\033[2J\033[H', end='')
            
            display = ProgramDisplay(
                self.robot_name,
                self.program_builder.get_program(),
                self.max_steps,
                self.starting_energy,
                self.program_builder.get_emergency_action()
            )
            display_output = display.render()
            # Center each line of the program display
            for line in display_output.split('\n'):
                print(self.terminal.text_formatter.center_text(line))
            
            # Show menu below program display, centered
            menu.renderer.selected_index = menu.selected_index
            menu_output = menu.renderer.render()
            for line in menu_output.split('\n'):
                print(self.terminal.text_formatter.center_text(line))
            
            # Get user input
            key = menu.keyboard.get_key()
            
            from .menu import MenuKey
            if key == MenuKey.UP:
                menu.selected_index = (menu.selected_index - 1) % len(menu.items)
            elif key == MenuKey.DOWN:
                menu.selected_index = (menu.selected_index + 1) % len(menu.items)
            elif key == MenuKey.ENTER:
                selected_item = menu.items[menu.selected_index]
                return menu.select(selected_item)
            elif key == MenuKey.ESCAPE:
                return "quit"
    
    def _add_instruction(self):
        """Add new instruction to program."""
        # Select instruction type
        instruction_menu = self.menu_factory.create_instruction_menu()
        instruction_type = instruction_menu.navigate()
        
        if instruction_type is None:
            return  # User cancelled
        
        # Build complete instruction with parameters
        complete_instruction = self.instruction_builder.build_instruction(instruction_type)
        
        if complete_instruction is None:
            return  # User cancelled during parameter selection
        
        # Add to program
        if not self.program_builder.add_instruction(complete_instruction):
            self._show_message("Cannot add more instructions - program is full!")
    
    def _remove_instruction(self):
        """Remove last instruction from program."""
        if not self.program_builder.remove_last_instruction():
            self._show_message("No instructions to remove!")
    
    def _set_emergency_action(self):
        """Set emergency action for low energy situations."""
        # Select emergency instruction type
        instruction_menu = self.menu_factory.create_instruction_menu()
        instruction_type = instruction_menu.navigate()
        
        if instruction_type is None:
            return  # User cancelled
        
        # Build complete instruction with parameters
        complete_instruction = self.instruction_builder.build_instruction(instruction_type)
        
        if complete_instruction is None:
            return  # User cancelled during parameter selection
        
        # Set emergency action
        self.program_builder.set_emergency_action(complete_instruction)
    
    def _show_message(self, message: str):
        """Display a message and wait for user acknowledgment."""
        print()  # Add spacing
        self.terminal.print_centered(message)
        self.terminal.print_centered("Press any key to continue...")
        import sys
        import termios
        import tty
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def program_robot(robot_name: str, max_steps: int = 20, starting_energy: int = 1500) -> List[str]:
    """Main entry point for robot programming. Returns list of instruction strings."""
    interface = RobotProgrammingInterface(robot_name, max_steps, starting_energy)
    return interface.program_robot()