"""Main entry point for Robot War game."""

import sys
from robot_war.core.game_state import GameState, GamePhase
from robot_war.ui.display import AnimatedDisplay
from robot_war.ui.setup import GameSetup


def main():
    """Main game loop."""
    # Run intro and setup
    setup = GameSetup()
    
    # Show intro screen
    if not setup.run_intro():
        print("Thanks for playing!")
        return
    
    # Run setup flow
    game_config, robot_configs = setup.run_setup()
    
    # Create display and game with configuration
    display = AnimatedDisplay(animation_delay=0.5)
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
        robot = game.add_robot(i + 1, game_config.starting_energy)
        
        if robot_config.is_ai:
            # AI robots get predefined programs based on their profile
            if robot_config.ai_profile == "aggressive":
                robot.program = ["PM", "PM", "MI", "DM(N)"]
                robot.emergency_action = "PM"
            elif robot_config.ai_profile == "defensive":
                robot.program = ["MI", "IN", "RM", "PT(MI,RM)"]
                robot.emergency_action = "IN"
            elif robot_config.ai_profile == "explorer":
                robot.program = ["RM", "RM", "RM", "PT(IN,MI)"]
                robot.emergency_action = "RM"
            else:  # tactical
                robot.program = ["PT(PM,AM)", "DM(E)", "MI", "IN"]
                robot.emergency_action = "PT(IN,RM)"
        else:
            # Human players program their robots interactively
            from robot_war.ui.programming import RobotProgrammingInterface
            print(f"\n🤖 Programming {robot_config.name}'s robot...")
            
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
                print("Programming cancelled. Exiting game.")
                return

    # Setup arena
    game.setup_arena()

    print(f"\n🔥 Starting battle...")
    import time
    time.sleep(1)

    # Start battle
    game.start_battle()

    # Run game loop with visual display
    turn_count = 0
    while not game.is_game_over() and turn_count < 50:  # Increased limit for testing movement
        # Show arena
        display.set_animation_speed(0.7)
        display.animate_turn(game)

        # Execute turn
        continues = game.execute_turn()
        if not continues:
            break

        turn_count += 1

    # If we hit the turn limit, determine winner
    if not game.is_game_over():
        game._determine_winner()

    # Show final results
    display.clear_screen()
    print(display.render_game_header())
    print("\n🏁 GAME OVER! 🏁")
    print(display.render_arena(game))

    winner = game.get_winner()
    print("\n" + display.render_winner(winner))


if __name__ == "__main__":
    main()
