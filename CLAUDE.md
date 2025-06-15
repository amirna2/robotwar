# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Guidelines for Claude Code
- Always provide clear, concise explanations for code changes.
- Write clean, modular code that adheres to Python best practices.
- Specifically pay attention to SOLID principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion and use them where applicable.
- No hacks or shortcuts; aim for production-ready code.
- Clean up unused imports, variables and code after refactoring.

### Comments and Documentation
- Use meaningful variable and function names that convey intent.
- A note on comments: Write comments that explain the "why" behind complex logic, not the "what" (which should be clear from the code itself).
- Use docstrings for public classes and methods to describe their purpose and usage.
- Use inline comments sparingly, only for non-obvious logic and avoid paraphrasing what the code does.

### Collaboration
- When suggesting changes, explain the reasoning behind them BEFORE making the change.
- If you encounter a bug or issue, provide a clear description of the problem and how you plan to address it.
- If you need to refactor code, explain the benefits of the refactor and how it improves the codebase.
- If you need clarification ask questions before making assumptions about the code or the devleoper's intent.

## Project Overview

Robot War is a Python adaptation of "La guerre des robots" from Jeux & Stratégie magazine (1985). It's a turn-based programming strategy game where players program robots to battle in an arena using a simple instruction set.

## Credits
- Original game design published in Jeux & Stratégie magazine Issue 31 (1985-0203, Page 42-45).
- This adaption in Python aims to preserve the original mechanics while modernizing the codebase for maintainability and extensibility.
- The game features a terminal-based display system using Unicode box-drawing characters for grid rendering.

## Development Commands

```bash
# Run the game
make run
# or: python3 -m robot_war.main

# Install for development
make install
# or: pip install -e .

# Run tests (when implemented)
make test
# or: python -m pytest tests/ -v

# Clean build artifacts
make clean

# Code formatting and linting
make format  # black robot_war/ --line-length=100
make lint    # flake8 robot_war/ --max-line-length=100
```

## Architecture Overview

The codebase follows a modular design with clear separation between game logic, display, and AI:

### Core Engine (`robot_war/core/`)
- **Robot**: Manages individual robot state (energy, position, program execution, status)
- **Arena**: Handles 20x20 grid, 8-directional movement, obstacles, mines, collision detection
- **GameState**: Orchestrates game phases (SETUP → PROGRAMMING → BATTLE → FINISHED), turn management, win conditions
- **Instructions**: Defines 9 instruction types (DM, RM, PS, MI, IN, FT, TR, TC, PT) with energy costs and execution logic

### Display System (`robot_war/ui/`)
- **ArenaDisplay**: Renders grid using Unicode box-drawing characters with dimmed lines for black terminals
- **Colors**: Terminal color management using colorama, robot-specific colors (cyan, yellow, magenta, green)
- Uses simple text symbols: numbers for robots, `#` for obstacles, `*` for mines, `·` for empty cells

### Key Game Mechanics
- **8-directional movement**: N, NE, E, SE, S, SW, W, NW (faithful to 1985 original)
- **Energy system**: Each instruction costs energy, robots die when energy ≤ 0
- **Simultaneous execution**: All robots execute their current instruction each turn
- **Circular programs**: When program ends, restart from first instruction
- **Instruction parsing**: String-based instructions converted to typed objects

## Current State

### Development Status (Updated: 2025-06-14 Evening)

**✅ Completed Instructions:**
- DM (Directed Move) - Full 8-directional movement implemented
- RM (Random Move) - Working with proper random direction selection
- MI (Mine Placement) - Robots can place mines on current position with ownership system
- PM (Pursue Enemy) - Move toward nearest detectable enemy
- AM (Avoid Enemy) - Move away from nearest detectable enemy
- IN (Invisibility) - Tactical countermeasure with proper stealth mechanics
- PT (Proximity Test) - Conditional instruction with PT(action_if_true, action_if_false) format

**⏳ Pending Instructions:**
- FR (Fire Row) - Horizontal firing with damage
- FC (Fire Column) - Vertical firing with damage

**✅ Core Systems Complete:**
- Terminal display with 3x3 grid cell rendering and proper symbols
- Game loop with turn-based execution and proper end game logic
- Robot energy management and death handling
- Arena generation with obstacles and robot spawning
- Dead robot skull obstacles that block movement
- Invisibility mechanics: undetectable for targeting but physically present
- Mine ownership system: own mines block movement, enemy mines explode
- Emergency routines (Circuit de Secours) with configurable energy thresholds
- Winner determination on turn limit (highest energy wins)
- Unit test framework with mine ownership test coverage

## Critical Implementation Notes

- Robot programs are stored as lists of instruction strings (e.g., `["RM", "DM(N)", "MI"]`)
- Game uses `GamePhase` enum to manage state transitions
- Arena position (0,0) is top-left, with y increasing downward
- All robots execute instructions simultaneously before advancing program counters
- Display system specifically designed for black terminal backgrounds with dimmed grid lines

## Original Game Fidelity

The implementation preserves the original 1985 mechanics:
- Fixed 20x20 arena size
- Exact energy costs and damage values from magazine
- 8-directional movement system
- Turn-based simultaneous execution
- Circular program execution
