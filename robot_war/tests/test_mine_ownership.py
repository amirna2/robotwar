"""Unit tests for mine ownership and collision logic."""

import unittest
from robot_war.core.game_state import GameState
from robot_war.core.robot import Robot, RobotStatus


class TestMineOwnership(unittest.TestCase):
    """Test mine placement and ownership mechanics."""

    def setUp(self):
        """Set up test game state."""
        self.game = GameState(arena_width=10, arena_height=10)
        self.game.num_obstacles = 0  # No random obstacles for predictable tests
        
        # Add two robots at known positions
        self.robot1 = self.game.add_robot(1, 1000)  # Player 1
        self.robot2 = self.game.add_robot(2, 1000)  # Player 2
        
        # Set predictable positions
        self.robot1.set_position(5, 5)
        self.robot2.set_position(7, 5)
        
        # Update arena robot tracking
        self.game.arena.robots = {
            (5, 5): self.robot1,
            (7, 5): self.robot2
        }

    def test_mine_placement_creates_correct_id(self):
        """Test that mines are created with correct ownership ID."""
        # Robot 1 places mine
        self.game._place_mine(self.robot1)
        
        # Check mine exists at robot position
        self.assertTrue(self.game.arena.has_mine(5, 5))
        
        # Trigger mine to check ID
        mine_data = self.game.arena.trigger_mine(5, 5)
        self.assertIsNotNone(mine_data)
        
        mine_id, damage = mine_data
        self.assertEqual(mine_id, 10)  # Player 1 * 10 = 10
        self.assertEqual(damage, 200)  # Default mine damage

    def test_robot_cannot_step_on_own_mine(self):
        """Test that robots cannot step on their own mines."""
        # Robot 1 places mine at current position
        self.game._place_mine(self.robot1)
        
        # Robot 1 tries to move west (back onto its own mine)
        original_pos = self.robot1.get_position()
        self.robot1.set_position(6, 5)  # Move away first
        self.game.arena.robots[(6, 5)] = self.robot1
        del self.game.arena.robots[(5, 5)]
        
        # Try to move back onto own mine
        from robot_war.core.arena import Direction
        self.game._move_robot(self.robot1, Direction.W)
        
        # Robot should still be at (6, 5), blocked by own mine
        self.assertEqual(self.robot1.get_position(), (6, 5))
        
        # Mine should still exist
        self.assertTrue(self.game.arena.has_mine(5, 5))

    def test_robot_explodes_on_enemy_mine(self):
        """Test that robots take damage from enemy mines."""
        # Robot 1 places mine at current position (5,5)
        self.game._place_mine(self.robot1)
        
        # Move Robot 1 away from the mine
        from robot_war.core.arena import Direction
        self.game._move_robot(self.robot1, Direction.N)  # Move Robot 1 from (5,5) to (5,4)
        
        # Robot 2 moves onto Robot 1's mine
        original_energy = self.robot2.energy
        self.game._move_robot(self.robot2, Direction.W)  # Move from (7,5) to (6,5)
        self.game._move_robot(self.robot2, Direction.W)  # Move from (6,5) to (5,5) - onto mine
        
        # Robot 2 should have taken damage
        self.assertEqual(self.robot2.energy, original_energy - 200)
        
        # Mine should be consumed
        self.assertFalse(self.game.arena.has_mine(5, 5))
        
        # Robot 2 should be at mine position
        self.assertEqual(self.robot2.get_position(), (5, 5))

    def test_mine_ownership_decoding(self):
        """Test mine ID decoding for different players."""
        test_cases = [
            (1, 10),   # Player 1 -> mine ID 10
            (2, 20),   # Player 2 -> mine ID 20
            (3, 30),   # Player 3 -> mine ID 30
            (4, 40),   # Player 4 -> mine ID 40
        ]
        
        for player_id, expected_mine_id in test_cases:
            # Place mine for player
            self.game.arena.place_mine(0, player_id, player_id, 200)
            
            # Retrieve and check mine ID
            mine_data = self.game.arena.trigger_mine(0, player_id)
            self.assertIsNotNone(mine_data)
            
            mine_id, damage = mine_data
            self.assertEqual(mine_id, expected_mine_id)
            
            # Decode ownership
            decoded_owner = mine_id // 10
            self.assertEqual(decoded_owner, player_id)


if __name__ == '__main__':
    unittest.main()