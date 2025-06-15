"""Game configuration constants and settings."""

# Default game settings (from original)
DEFAULT_ARENA_WIDTH = 20
DEFAULT_ARENA_HEIGHT = 20
DEFAULT_PROGRAM_LENGTH = 20
MAX_PROGRAM_LENGTH = 40
DEFAULT_STARTING_ENERGY = 1500
DEFAULT_NUM_OBSTACLES = 20

# Game limits
MAX_PLAYERS = 4
MIN_PLAYERS = 1
MAX_TURNS = 1000

# Display settings
ROBOT_EMOJIS = {
    1: "🤖",
    2: "🦾", 
    3: "⚙️",
    4: "🔩"
}

CELL_EMOJIS = {
    'empty': "⬜",
    'obstacle': "🧱",
    'mine': "💣",
    'explosion': "💥",
    'invisible': "🌫️"
}

DIRECTION_EMOJIS = {
    'N': "⬆️",
    'NE': "↗️", 
    'E': "➡️",
    'SE': "↘️",
    'S': "⬇️",
    'SW': "↙️",
    'W': "⬅️",
    'NW': "↖️"
}

UI_EMOJIS = {
    'energy': "⚡",
    'target': "🎯",
    'loop': "🔄"
}