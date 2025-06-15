"""Unit tests for GameState class - comprehensive coverage."""

import unittest
from robot_war.core.game_state import GameState, GamePhase
from robot_war.core.robot import Robot, RobotStatus
from robot_war.core.instructions import InstructionSet


class TestGameState(unittest.TestCase):
    """Test GameState class methods and game flow."""

    def setUp(self):
        """Set up test game state."""
        self.game = GameState(arena_width=10, arena_height=10)
        self.game.num_obstacles = 0  # No random obstacles for predictable tests

    def test_add_robot_with_default_energy(self):
        """Test adding robot uses default starting energy when None provided."""
        robot = self.game.add_robot(1, None)  # Pass None explicitly
        self.assertEqual(robot.energy, self.game.starting_energy)
        self.assertEqual(len(self.game.robots), 1)

    def test_add_robot_with_custom_energy(self):
        """Test adding robot with custom energy."""
        custom_energy = 2000
        robot = self.game.add_robot(1, custom_energy)
        self.assertEqual(robot.energy, custom_energy)

    def test_start_programming_from_setup(self):
        """Test transitioning from SETUP to PROGRAMMING phase."""
        self.assertEqual(self.game.phase, GamePhase.SETUP)
        self.game.start_programming()
        self.assertEqual(self.game.phase, GamePhase.PROGRAMMING)

    def test_start_programming_from_wrong_phase(self):
        """Test start_programming() does nothing if not in SETUP phase."""
        self.game.phase = GamePhase.BATTLE
        self.game.start_programming()
        self.assertEqual(self.game.phase, GamePhase.BATTLE)  # Should not change

    def test_start_battle_from_setup(self):
        """Test transitioning from SETUP to BATTLE phase."""
        self.game.start_battle()
        self.assertEqual(self.game.phase, GamePhase.BATTLE)
        self.assertEqual(self.game.current_turn, 0)

    def test_start_battle_from_programming(self):
        """Test transitioning from PROGRAMMING to BATTLE phase."""
        self.game.phase = GamePhase.PROGRAMMING
        self.game.start_battle()
        self.assertEqual(self.game.phase, GamePhase.BATTLE)
        self.assertEqual(self.game.current_turn, 0)

    def test_start_battle_from_wrong_phase(self):
        """Test start_battle() does nothing if already in BATTLE or FINISHED."""
        self.game.phase = GamePhase.FINISHED
        original_turn = self.game.current_turn
        self.game.start_battle()
        self.assertEqual(self.game.phase, GamePhase.FINISHED)
        self.assertEqual(self.game.current_turn, original_turn)

    def test_execute_turn_wrong_phase(self):
        """Test execute_turn() returns False if not in BATTLE phase."""
        self.game.phase = GamePhase.SETUP
        result = self.game.execute_turn()
        self.assertFalse(result)

        self.game.phase = GamePhase.PROGRAMMING
        result = self.game.execute_turn()
        self.assertFalse(result)

        self.game.phase = GamePhase.FINISHED
        result = self.game.execute_turn()
        self.assertFalse(result)

    def test_execute_turn_one_robot_left(self):
        """Test execute_turn() ends game when only one robot remains."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)
        
        # Kill robot2
        robot2.take_damage(1000)
        self.assertFalse(robot2.is_alive())
        
        self.game.start_battle()
        result = self.game.execute_turn()
        
        self.assertFalse(result)  # Game should end
        self.assertEqual(self.game.phase, GamePhase.FINISHED)
        self.assertEqual(self.game.winner_id, robot1.player_id)

    def test_execute_turn_max_turns_reached(self):
        """Test execute_turn() ends game when max turns reached."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)
        
        self.game.max_turns = 5
        self.game.start_battle()
        self.game.current_turn = 5  # Set to max turns
        
        result = self.game.execute_turn()
        
        self.assertFalse(result)  # Game should end
        self.assertEqual(self.game.phase, GamePhase.FINISHED)
        # Winner should be determined (highest energy)

    def test_execute_turn_normal_continuation(self):
        """Test execute_turn() continues game normally."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)
        robot1.program = ["RM"]
        robot2.program = ["RM"]
        
        self.game.start_battle()
        original_turn = self.game.current_turn
        
        result = self.game.execute_turn()
        
        self.assertTrue(result)  # Game should continue
        self.assertEqual(self.game.current_turn, original_turn + 1)
        self.assertEqual(self.game.phase, GamePhase.BATTLE)

    def test_determine_winner_no_survivors(self):
        """Test winner determination when no robots survive."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)
        
        # Kill both robots
        robot1.take_damage(1000)
        robot2.take_damage(1000)
        
        self.game._determine_winner()
        
        self.assertIsNone(self.game.winner_id)
        self.assertEqual(self.game.phase, GamePhase.FINISHED)

    def test_determine_winner_last_robot_standing(self):
        """Test winner determination with one survivor."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)
        
        # Kill robot2
        robot2.take_damage(1000)
        
        self.game._determine_winner()
        
        self.assertEqual(self.game.winner_id, robot1.player_id)
        self.assertEqual(self.game.phase, GamePhase.FINISHED)

    def test_determine_winner_highest_energy(self):
        """Test winner determination by highest energy."""
        robot1 = self.game.add_robot(1, 800)
        robot2 = self.game.add_robot(2, 1200)
        robot3 = self.game.add_robot(3, 600)
        
        self.game._determine_winner()
        
        self.assertEqual(self.game.winner_id, robot2.player_id)  # Highest energy
        self.assertEqual(self.game.phase, GamePhase.FINISHED)

    def test_is_game_over_true(self):
        """Test is_game_over() returns True when game finished."""
        self.game.phase = GamePhase.FINISHED
        self.assertTrue(self.game.is_game_over())

    def test_is_game_over_false(self):
        """Test is_game_over() returns False when game not finished."""
        for phase in [GamePhase.SETUP, GamePhase.PROGRAMMING, GamePhase.BATTLE]:
            self.game.phase = phase
            self.assertFalse(self.game.is_game_over())

    def test_get_winner_with_winner(self):
        """Test get_winner() returns winner ID."""
        self.game.winner_id = 5
        self.assertEqual(self.game.get_winner(), 5)

    def test_get_winner_no_winner(self):
        """Test get_winner() returns None when no winner."""
        self.game.winner_id = None
        self.assertIsNone(self.game.get_winner())

    def test_get_game_stats(self):
        """Test get_game_stats() returns correct statistics."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)
        robot2.take_damage(1000)  # Kill robot2
        
        self.game.current_turn = 10
        self.game.phase = GamePhase.BATTLE
        self.game.winner_id = 3
        
        stats = self.game.get_game_stats()
        
        expected_stats = {
            'turn': 10,
            'phase': 'battle',
            'living_robots': 1,  # Only robot1 alive
            'total_robots': 2,
            'winner': 3
        }
        self.assertEqual(stats, expected_stats)

    def test_find_nearest_enemy_basic(self):
        """Test _find_nearest_enemy() finds closest enemy."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)
        robot3 = self.game.add_robot(2, 1000)  # Same team as robot2
        
        robot1.set_position(5, 5)
        robot2.set_position(7, 5)  # Distance 2
        robot3.set_position(9, 5)  # Distance 4
        
        nearest = self.game._find_nearest_enemy(robot1)
        self.assertEqual(nearest, robot2)  # Closer enemy

    def test_find_nearest_enemy_ignores_self(self):
        """Test _find_nearest_enemy() ignores same player robots."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(1, 1000)  # Same player
        robot3 = self.game.add_robot(2, 1000)  # Different player
        
        robot1.set_position(5, 5)
        robot2.set_position(6, 5)  # Closer but same team
        robot3.set_position(8, 5)  # Further but enemy
        
        nearest = self.game._find_nearest_enemy(robot1)
        self.assertEqual(nearest, robot3)  # Should find robot3, not robot2

    def test_find_nearest_enemy_ignores_invisible(self):
        """Test _find_nearest_enemy() ignores invisible robots."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)
        
        robot1.set_position(5, 5)
        robot2.set_position(6, 5)
        robot2.status = RobotStatus.INVISIBLE
        
        nearest = self.game._find_nearest_enemy(robot1)
        self.assertIsNone(nearest)  # Should not find invisible robot

    def test_find_nearest_enemy_no_enemies(self):
        """Test _find_nearest_enemy() returns None when no enemies."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(1, 1000)  # Same team
        
        nearest = self.game._find_nearest_enemy(robot1)
        self.assertIsNone(nearest)

    def test_get_direction_to_nearest_enemy(self):
        """Test _get_direction_to_nearest_enemy() returns correct direction."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)
        
        robot1.set_position(5, 5)
        robot2.set_position(5, 3)  # North of robot1
        
        direction = self.game._get_direction_to_nearest_enemy(robot1)
        from robot_war.core.arena import Direction
        self.assertEqual(direction, Direction.N)

    def test_get_direction_to_nearest_enemy_no_enemy(self):
        """Test _get_direction_to_nearest_enemy() returns None when no enemy."""
        robot1 = self.game.add_robot(1, 1000)
        
        direction = self.game._get_direction_to_nearest_enemy(robot1)
        self.assertIsNone(direction)

    def test_get_direction_from_nearest_enemy(self):
        """Test _get_direction_from_nearest_enemy() returns correct direction."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)
        
        robot1.set_position(5, 5)
        robot2.set_position(5, 3)  # North of robot1
        
        direction = self.game._get_direction_from_nearest_enemy(robot1)
        from robot_war.core.arena import Direction
        self.assertEqual(direction, Direction.S)  # Move away (south)

    def test_get_direction_from_nearest_enemy_no_enemy(self):
        """Test _get_direction_from_nearest_enemy() returns None when no enemy."""
        robot1 = self.game.add_robot(1, 1000)
        
        direction = self.game._get_direction_from_nearest_enemy(robot1)
        self.assertIsNone(direction)

    def test_robot_instruction_execution_no_program(self):
        """Test robot with no program doesn't execute anything."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)  # Need 2 robots for game to continue
        robot1.program = []  # Empty program
        robot2.program = ["RM"]  # Valid program
        
        self.game.start_battle()
        original_energy = robot1.energy
        
        result = self.game.execute_turn()
        
        self.assertTrue(result)  # Game continues
        self.assertEqual(robot1.energy, original_energy)  # No energy used

    def test_robot_instruction_execution_invalid_instruction(self):
        """Test robot with invalid instruction doesn't execute anything."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)  # Need 2 robots for game to continue
        robot1.program = ["INVALID_INSTRUCTION"]
        robot2.program = ["RM"]  # Valid program
        
        self.game.start_battle()
        original_energy = robot1.energy
        
        result = self.game.execute_turn()
        
        self.assertTrue(result)  # Game continues
        self.assertEqual(robot1.energy, original_energy)  # No energy used

    def test_robot_program_counter_advancement(self):
        """Test robot program counter advances after instruction execution."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)  # Need 2 robots for game to continue
        robot1.program = ["RM", "IN", "MI"]
        robot2.program = ["RM"]
        
        self.game.start_battle()
        self.assertEqual(robot1.program_counter, 0)
        
        # Execute one turn
        self.game.execute_turn()
        self.assertEqual(robot1.program_counter, 1)
        
        # Execute another turn
        self.game.execute_turn()
        self.assertEqual(robot1.program_counter, 2)
        
        # Execute third turn (should wrap around)
        self.game.execute_turn()
        self.assertEqual(robot1.program_counter, 0)

    def test_frozen_robot_program_counter_not_advanced(self):
        """Test frozen robots don't advance program counter."""
        robot1 = self.game.add_robot(1, 1000)
        robot2 = self.game.add_robot(2, 1000)  # Need 2 robots for game to continue
        robot1.program = ["RM"]
        robot1.status = RobotStatus.FROZEN
        robot2.program = ["RM"]
        
        self.game.start_battle()
        original_counter = robot1.program_counter
        
        self.game.execute_turn()
        
        self.assertEqual(robot1.program_counter, original_counter)  # Should not advance


if __name__ == '__main__':
    unittest.main()