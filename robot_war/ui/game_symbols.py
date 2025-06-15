"""Game symbols and visual elements for terminal display."""

from colorama import Style
from robot_war.ui.colors import Colors


class GameSymbols:
    """Defines visual symbols used in the game display."""

    # Raw symbols (without colors)
    ROBOT = "1"  # Will be replaced with player ID
    OBSTACLE = "⎕"
    MINE = "◉"
    EMPTY = "·"
    INVISIBLE_ROBOT = "?"
    DEAD_ROBOT = "X"
    @classmethod
    def robot_symbol(cls, player_id: int) -> str:
        """Get colored robot symbol with player ID."""
        color = Colors.robot_color(player_id)
        return f"{color} {player_id} {Style.RESET_ALL}"

    @classmethod
    def obstacle_symbol(cls) -> str:
        """Get colored obstacle symbol."""
        return f"{Colors.OBSTACLE} {cls.OBSTACLE} {Style.RESET_ALL}"

    @classmethod
    def mine_symbol(cls) -> str:
        """Get colored mine symbol."""
        return f"{Colors.MINE} {cls.MINE} {Style.RESET_ALL}"

    @classmethod
    def empty_symbol(cls) -> str:
        """Get colored empty cell symbol."""
        return f"{Colors.EMPTY} {cls.EMPTY} {Style.RESET_ALL}"

    @classmethod
    def invisible_robot_symbol(cls) -> str:
        """Get colored invisible robot symbol."""
        return f"{Colors.INVISIBLE} {cls.INVISIBLE_ROBOT} {Style.RESET_ALL}"

    @classmethod
    def dead_robot_symbol(cls) -> str:
        """Get colored dead robot symbol."""
        return f"{Colors.DEAD_ROBOT} {cls.DEAD_ROBOT} {Style.RESET_ALL}"

    @classmethod
    def frozen_robot_symbol(cls, player_id: int) -> str:
        """Get colored frozen robot symbol (energy preservation mode)."""
        return f"{Colors.FROZEN_ROBOT} {player_id} {Style.RESET_ALL}"
