"""Main entry point for Robot War game."""

import sys
import time
from robot_war.core.game_state import GameState, GamePhase
from robot_war.ui.display import AnimatedDisplay
from robot_war.ui.rich_display import RichArenaDisplay
from robot_war.ui.setup import GameSetup
from robot_war.ui.terminal_output import TerminalOutputManager
from robot_war.ai.profiles import AIProfileLibrary


def main():
    """Main game loop."""
    # Create terminal manager for centered output
    terminal = TerminalOutputManager()
    
    # Run intro and setup
    setup = GameSetup()
    
    # Show intro screen
    if not setup.run_intro():
        terminal.print_centered("Thanks for playing!")
        return
    
    # Run setup flow
    game_config, robot_configs = setup.run_setup()
    
    # Create display and game with configuration
    display = RichArenaDisplay()
    game = GameState(
        arena_width=game_config.grid_width,
        arena_height=game_config.grid_height
    )
    
    # Apply configuration to game
    game.max_turns = game_config.max_turns
    game.proximity_distance = game_config.proximity_distance
    game.starting_energy = game_config.starting_energy
    game.num_obstacles = game_config.num_obstacles
    game.program_length = game_config.max_program_steps

    # Add robots based on configuration
    for i, robot_config in enumerate(robot_configs):
        robot = game.add_robot(i + 1, game_config.starting_energy, robot_config.name)
        
        if robot_config.is_ai:
            # AI robots get sophisticated programs based on their profile
            ai_profile = AIProfileLibrary.get_profile_by_name(robot_config.ai_profile)
            if ai_profile:
                robot.program = ai_profile.program.copy()
                robot.emergency_action = ai_profile.emergency_action
                robot.energy_threshold = ai_profile.energy_threshold
                terminal.print_centered(f"  {robot_config.name} loaded with {ai_profile.name} strategy", "cyan")
            else:
                # Fallback to basic random program
                robot.program = ["RM", "PT(PM,AM)", "MI", "RM"]
                robot.emergency_action = "RM"
        else:
            # Human players program their robots interactively
            from robot_war.ui.programming import RobotProgrammingInterface
            print()  # Add spacing
            terminal.print_centered(f"🤖 Programming {robot_config.name}'s robot...")
            
            interface = RobotProgrammingInterface(
                robot_config.name,
                game_config.max_program_steps,
                game_config.starting_energy
            )
            robot.program = interface.program_robot()
            
            # Set emergency action from programming interface
            robot.emergency_action = interface.program_builder.get_emergency_action() or "RM"
            
            # Check if player quit programming
            if not robot.program:
                terminal.print_centered("Programming cancelled. Exiting game.")
                return

    # Setup arena
    game.setup_arena()

    print()  # Add spacing
    terminal.print_centered(f"🔥 Starting battle...")
    time.sleep(1)

    # Start battle
    game.start_battle()

    # Start live display for smooth updates
    display.start_live_display()
    
    try:
        # Run game loop with Rich visual display
        while not game.is_game_over():
            # Update display with current game state
            display.update_live_display(game)
            
            # Wait briefly for user to see the state
            time.sleep(1.5)
            
            # Execute turn
            continues = game.execute_turn()
            if not continues:
                break

        # If we hit the turn limit, determine winner
        if not game.is_game_over():
            game._determine_winner()

        # Final display update
        display.update_live_display(game)
        time.sleep(2)
        
    finally:
        # Stop live display
        display.stop_live_display()

    # Show final battle results
    display.display_battle_summary(game)
    display.wait_for_input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
