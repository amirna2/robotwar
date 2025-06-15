"""Color definitions and utilities for terminal display."""

from colorama import init, Fore, Back, Style
init(autoreset=True)  # Auto-reset colors after each print


class Colors:
    """Color constants for different game elements."""

    # Robot colors (bright and distinct)
    ROBOT_1 = Fore.CYAN + Style.BRIGHT
    ROBOT_2 = Fore.GREEN + Style.BRIGHT
    ROBOT_3 = Fore.WHITE + Style.BRIGHT
    ROBOT_4 = Fore.LIGHTMAGENTA_EX + Style.BRIGHT

    # Environment colors
    OBSTACLE = Fore.YELLOW + Style.BRIGHT
    MINE = Fore.RED + Style.BRIGHT
    EMPTY = Fore.WHITE + Style.DIM

    # Special states
    INVISIBLE = Fore.WHITE + Style.DIM
    EXPLOSION = Fore.RED + Back.YELLOW + Style.BRIGHT
    DEAD_ROBOT = Fore.RED + Style.BRIGHT
    FROZEN_ROBOT = Fore.WHITE + Style.DIM  # Same as empty dots - energy preservation

    # UI elements
    HEADER = Fore.CYAN + Style.BRIGHT
    STATS = Fore.GREEN
    ENERGY = Fore.YELLOW
    WINNER = Fore.GREEN + Style.BRIGHT
    ERROR = Fore.RED + Style.BRIGHT
    COMBAT = Fore.RED + Style.BRIGHT  # Combat log entries
    
    # Setup interface colors
    TITLE = Fore.MAGENTA + Style.BRIGHT
    SUBTITLE = Fore.BLUE + Style.BRIGHT
    SECTION = Fore.YELLOW + Style.BRIGHT
    ROBOT = Fore.CYAN + Style.BRIGHT
    SUCCESS = Fore.GREEN + Style.BRIGHT
    WARNING = Fore.YELLOW + Style.BRIGHT
    INFO = Fore.WHITE + Style.BRIGHT

    @classmethod
    def robot_color(cls, player_id: int) -> str:
        """Get color for a specific robot player."""
        colors = [cls.ROBOT_1, cls.ROBOT_2, cls.ROBOT_3, cls.ROBOT_4]
        return colors[(player_id - 1) % len(colors)]

