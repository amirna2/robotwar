# Robot War 🤖

Original game design published in Jeux & Stratégie magazine Issue 31 (1985-0203, Page 42-45).
This is a Python adaptation of the classic turn-based programming strategy game where players program robots to battle in an arena.

## Description

Robot War is a turn-based programming strategy game where players program robots to battle in an arena. Each robot executes a sequence of instructions (movement, attacks, mine laying) while managing limited energy resources.

## Features

- 🤖 Program robots with simple instruction sets
- ⚔️ Turn-based simultaneous execution
- 💣 Mines, obstacles, and tactical positioning
- ⚡ Energy management system
- 🎯 8-directional movement and attacks
- 🌫️ Invisibility and special abilities
- 🏆 1-4 player support with AI opponents

## Installation

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd RobotWar

# Run directly with Python
python -m robot_war.main
```

### Install as Package
```bash
# Install in development mode
pip install -e .

# Run the game
robot-war
```

### Requirements
- Python 3.7+
- No external dependencies (uses only standard library)

## How to Play

1. **Setup**: Configure number of players, robot energy, arena obstacles
2. **Programming**: Write instruction sequences for your robots
3. **Battle**: Watch robots execute programs simultaneously
4. **Victory**: Last robot standing wins!

## Instruction Set

| Code | Action | Energy Cost | Description |
|------|--------|-------------|-------------|
| DM   | Directed Move | 5 | Move in chosen direction (N/NE/E/SE/S/SW/W/NW) |
| RM   | Random Move | 5 | Move in random direction |
| PM   | Pursue Move | 10 | Move toward nearest enemy |
| AM   | Avoid Move | 15 | Move away from nearest enemy |
| MI   | Lay Mine | 200 | Place mine (200 damage) |
| IN   | Invisibility | 200 | Become invisible for 1 turn |
| FR   | Fire Row | 100 | Fire horizontally (200 damage) |
| FC   | Fire Column | 100 | Fire vertically (200 damage) |
| PT   | Proximity Test | 4 | Test for adjacent mines/enemies |

## Development

### Project Structure
```
robot_war/
├── core/           # Game engine
├── ui/             # User interface
├── ai/             # AI opponents
├── utils/          # Configuration
└── tests/          # Unit tests
```

### Running Tests
```bash
python -m pytest tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Original Game

Based on "La guerre des robots" published in Jeux & Stratégie #31 (February 1985). The original was written in BASIC for Apple II computers.

## License

MIT License - see LICENSE file for details.
