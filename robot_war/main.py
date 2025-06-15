"""Main entry point for Robot War game."""

import sys
from robot_war.core.game_state import GameState, GamePhase
from robot_war.utils.config import DEFAULT_STARTING_ENERGY
from robot_war.ui.display import AnimatedDisplay


def main():
    """Main game loop."""
    # Create display and game
    display = AnimatedDisplay(animation_delay=0.5)  # Half-second between turns
    game = GameState()

    # Simple test setup for now
    display.clear_screen()
    print(display.render_game_header())
    print("\nSetting up test game...")

    # Add some robots
    robot1 = game.add_robot(1, DEFAULT_STARTING_ENERGY)
    robot2 = game.add_robot(2, DEFAULT_STARTING_ENERGY)

    # Simple PT test: Robot1 moves west, Robot2 moves west and tests proximity
    robot1.program = ["DM(W)", "DM(W)", "DM(W)", "DM(W)"]  # Just move west steadily
    robot1.emergency_action = "RM"  # Random move when in emergency
    
    robot2.program = ["DM(W)", "DM(W)", "PT(IN,MI)", "DM(W)"]  # Move west, then: if enemy nearby go invisible, else place mine
    robot2.emergency_action = "IN"  # Go invisible when in emergency

    # Setup arena
    game.setup_arena()

    print(f"Game setup complete!")
    print(f"Robots: {len(game.robots)}")
    print(f"Arena: {game.arena.width}x{game.arena.height}")
    print(f"Obstacles: {game.num_obstacles}")

    print("\n🔥 Starting battle in 2 seconds...")
    import time
    time.sleep(2)

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
