"""Game setup interface with intro screen and configuration."""

import time
import random
from typing import List, Optional, Tuple
from dataclasses import dataclass
from robot_war.ui.colors import Colors
from robot_war.ui.terminal_output import TerminalOutputManager
from robot_war.ai.profiles import AIProfileLibrary, get_ai_robot_name
from colorama import Style, init

# Initialize colorama for cross-platform color support
init()


@dataclass
class GameConfig:
    """Configuration settings for a game session."""
    grid_width: int = 20
    grid_height: int = 20
    max_turns: int = 50
    max_program_steps: int = 20
    num_robots: int = 2
    proximity_distance: int = 5
    starting_energy: int = 1500
    num_obstacles: int = 20


@dataclass
class RobotConfig:
    """Configuration for a single robot."""
    name: str
    is_ai: bool = False
    ai_profile: Optional[str] = None


class GameSetup:
    """Handles game intro, setup flow, and configuration."""

    AI_PROFILES = AIProfileLibrary.get_profile_names()

    SUBTITLES = [
        "Tactics at Terminal Velocity",
        "Back to the Grid",
        "Code To Victory",
        "Battle By Code",
        "Code Tactics And Win"
    ]

    def __init__(self):
        self.config = GameConfig()
        self.robots: List[RobotConfig] = []
        self.terminal = TerminalOutputManager()  # Dependency injection

    def run_intro(self) -> bool:
        """Display intro screen with title and animation. Returns True if user wants to continue."""
        self.terminal.clear_screen()

        # Display animated title
        self._display_animated_title()

        # Wait for user input, centered
        print()  # Add spacing line
        prompt = "Press ENTER to start setup, or 'q' to quit..."
        self.terminal.print_centered(prompt, Colors.HEADER)
        user_input = self.terminal.input_centered().strip().lower()

        return user_input != 'q'

    def run_setup(self) -> Tuple[GameConfig, List[RobotConfig]]:
        """Run the complete setup flow and return configuration."""
        self.terminal.clear_screen()
        self.terminal.print_centered("🛠️  ROBOT WAR SETUP  🛠️\n", Colors.HEADER)

        # Configure game parameters
        self._setup_game_parameters()

        # Configure robots
        self._setup_robots()

        # Display final configuration
        self._display_final_config()

        return self.config, self.robots

    def _display_animated_title(self):
        """Display the animated game title."""
        # Choose random subtitle
        random_subtitle = random.choice(self.SUBTITLES)
        
        title_lines = [
            "╔═══════════════════════════════════════╗",
            "║                                       ║",
            "║            R.O.B.O.T W.A.R            ║",
            "║                                       ║",
            f"║ {random_subtitle.center(37)} ║",
            "║                                       ║",
            "╚═══════════════════════════════════════╝"
        ]

        # Display title with animation, centered
        for line in title_lines:
            self.terminal.print_centered(line, Colors.TITLE)
            time.sleep(0.05)

        # Animated subtitle, centered
        subtitle = "Last robot wins!"
        from .terminal_output import TerminalSizer, TextFormatter
        padding = TerminalSizer.calculate_center_padding(subtitle)
        print(f"\n{Colors.SUBTITLE}{' ' * padding}", end="")
        for char in subtitle:
            print(char, end="", flush=True)
            time.sleep(0.05)
        print(f"{Style.RESET_ALL}")

        time.sleep(0.5)

    def _setup_game_parameters(self):
        """Configure basic game parameters."""
        self.terminal.print_centered("📏 Game Parameters", Colors.SECTION)

        # Grid size
        while True:
            print()  # Add spacing
            self.terminal.print_centered(f"Arena size (current: {self.config.grid_width}x{self.config.grid_height})")
            size_input = self.terminal.input_centered("Enter new size (e.g., '25' for 25x25, or press ENTER to keep current): ").strip()
            if not size_input:  # Empty input - keep current
                break
            if size_input.isdigit():
                size = int(size_input)
                if 10 <= size <= 50:
                    self.config.grid_width = size
                    self.config.grid_height = size
                    break
                else:
                    self.terminal.print_centered("Size must be between 10 and 50. Try again.", Colors.WARNING)
            else:
                self.terminal.print_centered("Please enter a valid number or press ENTER.", Colors.WARNING)

        # Number of turns
        while True:
            print()  # Add spacing
            self.terminal.print_centered(f"Max turns (current: {self.config.max_turns})")
            turns_input = self.terminal.input_centered("Enter max turns (or press ENTER to keep current): ").strip()
            if not turns_input:  # Empty input - keep current
                break
            if turns_input.isdigit():
                turns = int(turns_input)
                if 10 <= turns <= 200:
                    self.config.max_turns = turns
                    break
                else:
                    self.terminal.print_centered("Turns must be between 10 and 200. Try again.", Colors.WARNING)
            else:
                self.terminal.print_centered("Please enter a valid number or press ENTER.", Colors.WARNING)

        # Program steps
        while True:
            print()  # Add spacing
            self.terminal.print_centered(f"Max program steps per robot (current: {self.config.max_program_steps})")
            steps_input = self.terminal.input_centered("Enter max program steps (or press ENTER to keep current): ").strip()
            if not steps_input:
                break
            if steps_input.isdigit():
                steps = int(steps_input)
                if 5 <= steps <= 100:
                    self.config.max_program_steps = steps
                    break
                else:
                    self.terminal.print_centered("Steps must be between 5 and 100. Try again.", Colors.WARNING)
            else:
                self.terminal.print_centered("Please enter a valid number or press ENTER.", Colors.WARNING)

        # Number of robots
        while True:
            print()  # Add spacing
            self.terminal.print_centered(f"Number of robots (current: {self.config.num_robots})")
            robots_input = self.terminal.input_centered("Enter number of robots (2-8, or press ENTER to keep current): ").strip()
            if not robots_input:
                break
            if robots_input.isdigit():
                num_robots = int(robots_input)
                if 2 <= num_robots <= 8:
                    self.config.num_robots = num_robots
                    break
                else:
                    self.terminal.print_centered("Number of robots must be between 2 and 8. Try again.", Colors.WARNING)
            else:
                self.terminal.print_centered("Please enter a valid number or press ENTER.", Colors.WARNING)

        # Proximity distance
        while True:
            print()  # Add spacing
            self.terminal.print_centered(f"Proximity test distance (current: {self.config.proximity_distance})")
            prox_input = self.terminal.input_centered("Enter proximity distance (1-10, or press ENTER to keep current): ").strip()
            if not prox_input:
                break
            if prox_input.isdigit():
                distance = int(prox_input)
                if 1 <= distance <= 10:
                    self.config.proximity_distance = distance
                    break
                else:
                    self.terminal.print_centered("Proximity distance must be between 1 and 10. Try again.", Colors.WARNING)
            else:
                self.terminal.print_centered("Please enter a valid number or press ENTER.", Colors.WARNING)

    def _setup_robots(self):
        """Configure individual robots."""
        print()  # Add spacing
        self.terminal.print_centered("🤖 Robot Configuration", Colors.SECTION)

        self.robots = []
        
        # Enter player names - when done, remaining slots become AI
        for i in range(self.config.num_robots):
            print()  # Add spacing
            self.terminal.print_centered(f"Robot {i+1}:", Colors.ROBOT)
            name_input = self.terminal.input_centered(f"Enter player name (or press ENTER to fill remaining slots with AI): ").strip()
            
            if not name_input:
                # Done with human players - fill remaining with AI
                balanced_profiles = AIProfileLibrary.get_balanced_team(self.config.num_robots - i)
                for j, profile in enumerate(balanced_profiles):
                    robot_name = get_ai_robot_name(profile)
                    robot_config = RobotConfig(name=robot_name, is_ai=True, ai_profile=profile.personality.value)
                    self.robots.append(robot_config)
                    self.terminal.print_centered(f"AI Robot: {robot_name} ({profile.name} - {profile.description})", Colors.INFO)
                break
            else:
                # Human player
                robot_config = RobotConfig(name=name_input, is_ai=False, ai_profile=None)
                self.robots.append(robot_config)

    def _display_final_config(self):
        """Display the final configuration for confirmation."""
        self.terminal.clear_screen()
        self.terminal.print_centered("📋 FINAL CONFIGURATION 📋\n", Colors.HEADER)

        # Game parameters
        self.terminal.print_centered("Game Settings:", Colors.SECTION)
        self.terminal.print_centered(f"  Arena: {self.config.grid_width}x{self.config.grid_height}")
        self.terminal.print_centered(f"  Max turns: {self.config.max_turns}")
        self.terminal.print_centered(f"  Program steps: {self.config.max_program_steps}")
        self.terminal.print_centered(f"  Proximity distance: {self.config.proximity_distance}")
        self.terminal.print_centered(f"  Starting energy: {self.config.starting_energy}")
        self.terminal.print_centered(f"  Obstacles: {self.config.num_obstacles}")

        # Robot configuration
        print()  # Add spacing
        self.terminal.print_centered("Robots:", Colors.SECTION)
        for i, robot in enumerate(self.robots):
            ai_info = f" (AI: {robot.ai_profile})" if robot.is_ai else " (Human)"
            self.terminal.print_centered(f"  {i+1}. {robot.name}{ai_info}")

        print()  # Add spacing
        self.terminal.print_centered("Setup complete! Press ENTER to continue to programming phase...", Colors.SUCCESS)
        self.terminal.input_centered("")


    @staticmethod
    def wait_for_key(prompt: str = "Press ENTER to continue...") -> str:
        """Wait for user to press a key."""
        return input(f"{Colors.INFO}{prompt}{Style.RESET_ALL}")
