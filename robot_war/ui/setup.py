"""Game setup interface with intro screen and configuration."""

import time
from typing import List, Optional, Tuple
from dataclasses import dataclass
from robot_war.ui.colors import Colors
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

    AI_PROFILES = [
        "aggressive",    # Focuses on PM (pursue) and attacking
        "defensive",     # Uses mines and IN (invisibility)
        "explorer",      # Random movement and exploration
        "tactical"       # Uses PT (proximity test) heavily
    ]

    def __init__(self):
        self.config = GameConfig()
        self.robots: List[RobotConfig] = []

    def run_intro(self) -> bool:
        """Display intro screen with title and animation. Returns True if user wants to continue."""
        self._clear_screen()

        # Display animated title
        self._display_animated_title()

        # Wait for user input
        print(f"\n{Colors.HEADER}Press ENTER to start setup, or 'q' to quit...{Style.RESET_ALL}")
        user_input = input().strip().lower()

        return user_input != 'q'

    def run_setup(self) -> Tuple[GameConfig, List[RobotConfig]]:
        """Run the complete setup flow and return configuration."""
        self._clear_screen()
        print(f"{Colors.HEADER}🛠️  ROBOT WAR SETUP  🛠️{Style.RESET_ALL}\n")

        # Configure game parameters
        self._setup_game_parameters()

        # Configure robots
        self._setup_robots()

        # Display final configuration
        self._display_final_config()

        return self.config, self.robots

    def _display_animated_title(self):
        """Display the animated game title."""
        title_lines = [
            "╔═══════════════════════════════════════╗",
            "║                                       ║",
            "║            R.O.B.O.T W.A.R            ║",
            "║                                       ║",
            "║        Program. Battle. Survive.      ║",
            "║                                       ║",
            "╚═══════════════════════════════════════╝"
        ]

        # Display title with animation
        for line in title_lines:
            print(f"{Colors.TITLE}{line}{Style.RESET_ALL}")
            time.sleep(0.05)

        # Animated subtitle
        subtitle = "Last robot wins!"
        print(f"\n{Colors.SUBTITLE}", end="")
        for char in subtitle:
            print(char, end="", flush=True)
            time.sleep(0.05)
        print(f"{Style.RESET_ALL}")

        time.sleep(0.5)

    def _setup_game_parameters(self):
        """Configure basic game parameters."""
        print(f"{Colors.SECTION}📏 Game Parameters{Style.RESET_ALL}")

        # Grid size
        while True:
            print(f"\nArena size (current: {self.config.grid_width}x{self.config.grid_height})")
            size_input = input("Enter new size (e.g., '25' for 25x25, or press ENTER to keep current): ").strip()
            if not size_input:  # Empty input - keep current
                break
            if size_input.isdigit():
                size = int(size_input)
                if 10 <= size <= 50:
                    self.config.grid_width = size
                    self.config.grid_height = size
                    break
                else:
                    print(f"{Colors.WARNING}Size must be between 10 and 50. Try again.{Style.RESET_ALL}")
            else:
                print(f"{Colors.WARNING}Please enter a valid number or press ENTER.{Style.RESET_ALL}")

        # Number of turns
        while True:
            print(f"\nMax turns (current: {self.config.max_turns})")
            turns_input = input("Enter max turns (or press ENTER to keep current): ").strip()
            if not turns_input:  # Empty input - keep current
                break
            if turns_input.isdigit():
                turns = int(turns_input)
                if 10 <= turns <= 200:
                    self.config.max_turns = turns
                    break
                else:
                    print(f"{Colors.WARNING}Turns must be between 10 and 200. Try again.{Style.RESET_ALL}")
            else:
                print(f"{Colors.WARNING}Please enter a valid number or press ENTER.{Style.RESET_ALL}")

        # Program steps
        while True:
            print(f"\nMax program steps per robot (current: {self.config.max_program_steps})")
            steps_input = input("Enter max program steps (or press ENTER to keep current): ").strip()
            if not steps_input:
                break
            if steps_input.isdigit():
                steps = int(steps_input)
                if 5 <= steps <= 100:
                    self.config.max_program_steps = steps
                    break
                else:
                    print(f"{Colors.WARNING}Steps must be between 5 and 100. Try again.{Style.RESET_ALL}")
            else:
                print(f"{Colors.WARNING}Please enter a valid number or press ENTER.{Style.RESET_ALL}")

        # Number of robots
        while True:
            print(f"\nNumber of robots (current: {self.config.num_robots})")
            robots_input = input("Enter number of robots (2-8, or press ENTER to keep current): ").strip()
            if not robots_input:
                break
            if robots_input.isdigit():
                num_robots = int(robots_input)
                if 2 <= num_robots <= 8:
                    self.config.num_robots = num_robots
                    break
                else:
                    print(f"{Colors.WARNING}Number of robots must be between 2 and 8. Try again.{Style.RESET_ALL}")
            else:
                print(f"{Colors.WARNING}Please enter a valid number or press ENTER.{Style.RESET_ALL}")

        # Proximity distance
        while True:
            print(f"\nProximity test distance (current: {self.config.proximity_distance})")
            prox_input = input("Enter proximity distance (1-10, or press ENTER to keep current): ").strip()
            if not prox_input:
                break
            if prox_input.isdigit():
                distance = int(prox_input)
                if 1 <= distance <= 10:
                    self.config.proximity_distance = distance
                    break
                else:
                    print(f"{Colors.WARNING}Proximity distance must be between 1 and 10. Try again.{Style.RESET_ALL}")
            else:
                print(f"{Colors.WARNING}Please enter a valid number or press ENTER.{Style.RESET_ALL}")

    def _setup_robots(self):
        """Configure individual robots."""
        print(f"\n{Colors.SECTION}🤖 Robot Configuration{Style.RESET_ALL}")

        self.robots = []
        
        # Enter player names - when done, remaining slots become AI
        for i in range(self.config.num_robots):
            print(f"\n{Colors.ROBOT}Robot {i+1}:{Style.RESET_ALL}")
            name_input = input(f"Enter player name (or press ENTER to fill remaining slots with AI): ").strip()
            
            if not name_input:
                # Done with human players - fill remaining with AI
                import random
                for j in range(i, self.config.num_robots):
                    ai_profile = random.choice(self.AI_PROFILES)
                    robot_name = f"{ai_profile.capitalize()}-Bot"
                    robot_config = RobotConfig(name=robot_name, is_ai=True, ai_profile=ai_profile)
                    self.robots.append(robot_config)
                    print(f"{Colors.INFO}AI Robot: {robot_name} ({ai_profile} profile){Style.RESET_ALL}")
                break
            else:
                # Human player
                robot_config = RobotConfig(name=name_input, is_ai=False, ai_profile=None)
                self.robots.append(robot_config)

    def _display_final_config(self):
        """Display the final configuration for confirmation."""
        self._clear_screen()
        print(f"{Colors.HEADER}📋 FINAL CONFIGURATION 📋{Style.RESET_ALL}\n")

        # Game parameters
        print(f"{Colors.SECTION}Game Settings:{Style.RESET_ALL}")
        print(f"  Arena: {self.config.grid_width}x{self.config.grid_height}")
        print(f"  Max turns: {self.config.max_turns}")
        print(f"  Program steps: {self.config.max_program_steps}")
        print(f"  Proximity distance: {self.config.proximity_distance}")
        print(f"  Starting energy: {self.config.starting_energy}")
        print(f"  Obstacles: {self.config.num_obstacles}")

        # Robot configuration
        print(f"\n{Colors.SECTION}Robots:{Style.RESET_ALL}")
        for i, robot in enumerate(self.robots):
            ai_info = f" (AI: {robot.ai_profile})" if robot.is_ai else " (Human)"
            print(f"  {i+1}. {robot.name}{ai_info}")

        print(f"\n{Colors.SUCCESS}Setup complete! Press ENTER to continue to programming phase...{Style.RESET_ALL}")
        input()

    def _clear_screen(self):
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def wait_for_key(prompt: str = "Press ENTER to continue...") -> str:
        """Wait for user to press a key."""
        return input(f"{Colors.INFO}{prompt}{Style.RESET_ALL}")
