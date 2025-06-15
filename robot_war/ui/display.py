"""Color-based arena display system with BIG symbols."""

from typing import Dict, List
from robot_war.core.arena import Arena, CellType
from robot_war.core.robot import Robot, RobotStatus
from robot_war.core.game_state import GameState
from robot_war.ui.colors import Colors
from robot_war.ui.game_symbols import GameSymbols
from colorama import Style, Fore


class ArenaDisplay:
    """Handles visual representation of the game arena using emojis."""

    def __init__(self):
        pass  # Using color functions instead

    def render_arena(self, game_state: GameState) -> str:
        """Render the complete arena with proper grid lines."""
        arena = game_state.arena
        lines = []

        # Add header with turn infoinfo
        lines.append(f"{Colors.HEADER}Turn {game_state.current_turn} - Phase: {game_state.phase.value}{Style.RESET_ALL}")

        # Top border (dimmed)
        grid_color = f"{Fore.WHITE}{Style.DIM}"  # Dim gray
        top_line = f"{grid_color}┌" + "┬".join("───" for _ in range(arena.width)) + f"┐{Style.RESET_ALL}"
        lines.append(top_line)

        # Render each row with grid lines
        for y in range(arena.height):
            # Cell content row
            row = f"{grid_color}│{Style.RESET_ALL}"
            for x in range(arena.width):
                cell_content = self._get_cell_content(arena, x, y, game_state.robots)
                row += cell_content + f"{grid_color}│{Style.RESET_ALL}"
            lines.append(row)

            # Horizontal separator (except for last row)
            if y < arena.height - 1:
                sep_line = f"{grid_color}├" + "┼".join("───" for _ in range(arena.width)) + f"┤{Style.RESET_ALL}"
                lines.append(sep_line)

        # Bottom border (dimmed)
        bottom_line = f"{grid_color}└" + "┴".join("───" for _ in range(arena.width)) + f"┘{Style.RESET_ALL}"
        lines.append(bottom_line)

        # Add robot stats
        lines.append("")
        lines.extend(self._get_robot_status_lines(game_state))
        
        # Add combat log if there were any combat actions this turn
        if game_state.combat_log:
            lines.append("")
            lines.append(f"{Colors.COMBAT}🔥 Combat Actions:{Style.RESET_ALL}")
            for log_entry in game_state.combat_log:
                lines.append(f"{Colors.COMBAT}{log_entry}{Style.RESET_ALL}")

        return "\n".join(lines)

    def _get_cell_content(self, arena: Arena, x: int, y: int, robots: List[Robot]) -> str:
        """Get the content for a grid cell (3 characters wide)."""
        # Check for robots first (highest priority)
        for robot in robots:
            if robot.get_position() == (x, y) and robot.is_alive():
                if robot.status == RobotStatus.INVISIBLE:
                    return GameSymbols.invisible_robot_symbol()
                elif robot.status == RobotStatus.FROZEN:
                    return GameSymbols.frozen_robot_symbol(robot.player_id)
                else:
                    return GameSymbols.robot_symbol(robot.player_id)

        # Check for mines
        if arena.has_mine(x, y):
            return GameSymbols.mine_symbol()

        # Check for obstacles
        if arena.grid[y][x] == CellType.OBSTACLE:
            return GameSymbols.obstacle_symbol()

        # Check for dead robots (skulls)
        if arena.grid[y][x] == CellType.DEAD_ROBOT:
            return GameSymbols.dead_robot_symbol()

        # Empty cell
        return GameSymbols.empty_symbol()

    def _get_robot_status_lines(self, game_state: GameState) -> List[str]:
        """Generate status lines for all robots."""
        lines = []
        living_robots = game_state.get_living_robots()

        if not living_robots:
            lines.append("💀 No robots remaining")
            return lines

        lines.append(f"🤖 Active Robots: {len(living_robots)}")

        for robot in living_robots:
            color = Colors.robot_color(robot.player_id)

            # Get current instruction
            current_instruction = robot.get_current_instruction() or "None"

            # Add status indicator for special states
            status_indicator = ""
            if robot.status == RobotStatus.FROZEN:
                status_indicator = f" {Colors.FROZEN_ROBOT}[FROZEN]{Style.RESET_ALL}"
            elif robot.status == RobotStatus.INVISIBLE:
                status_indicator = f" {Colors.INVISIBLE}[INVISIBLE]{Style.RESET_ALL}"

            status_line = (
                f"{color}Player {robot.player_id}{Style.RESET_ALL}: "
                f"({robot.x}, {robot.y}) "
                f"{Colors.ENERGY}⚡{robot.energy}{Style.RESET_ALL} "
                f"Next: {current_instruction}{status_indicator}"
            )
            lines.append(status_line)

        return lines

    def render_explosion(self, x: int, y: int) -> str:
        """Render an explosion effect at coordinates."""
        return f"💥 Explosion at ({x}, {y})!"

    def render_mine_placed(self, x: int, y: int) -> str:
        """Render mine placement notification."""
        return f"💣 Mine placed at ({x}, {y})"

    def render_robot_destroyed(self, robot: Robot) -> str:
        """Render robot destruction message."""
        # Simple emoji mapping for players
        player_emojis = {1: "🤖", 2: "🤖", 3: "🤖", 4: "🤖"}
        emoji = player_emojis.get(robot.player_id, "🤖")
        return f"💀 {emoji} Player {robot.player_id} destroyed!"

    def render_winner(self, winner_id: int) -> str:
        """Render winner announcement."""
        if winner_id is None:
            return "💀 No survivors! It's a draw!"

        # Simple emoji mapping for players
        player_emojis = {1: "🤖", 2: "🤖", 3: "🤖", 4: "🤖"}
        emoji = player_emojis.get(winner_id, "🤖")
        return f"🏆 {emoji} Player {winner_id} wins! 🏆"

    def clear_screen(self):
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def render_game_header(self) -> str:
        """Render the game title and header."""
        header = [
            "🤖 ROBOT WAR 🤖",
            "La guerre des robots (1985)",
            "=" * 40
        ]
        return "\n".join(header)


class AnimatedDisplay(ArenaDisplay):
    """Extended display with animation capabilities."""

    def __init__(self, animation_delay: float = 1.0):
        super().__init__()
        self.animation_delay = animation_delay

    def animate_turn(self, game_state: GameState):
        """Display arena with animation delay."""
        import time

        self.clear_screen()
        print(self.render_game_header())
        print()
        print(self.render_arena(game_state))

        if self.animation_delay > 0:
            time.sleep(self.animation_delay)

    def set_animation_speed(self, delay: float):
        """Set animation delay between turns."""
        self.animation_delay = max(0.0, delay)
