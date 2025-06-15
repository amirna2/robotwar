"""Unit tests for Arena class - grid management, obstacles, mines, and positioning."""

import unittest
from robot_war.core.arena import Arena, CellType, Direction
from robot_war.core.robot import Robot


class TestArena(unittest.TestCase):
    """Test Arena grid management and positioning mechanics."""

    def setUp(self):
        """Set up test arena."""
        self.arena = Arena(width=10, height=10)

    def test_arena_initialization(self):
        """Test arena creates correct grid dimensions."""
        self.assertEqual(self.arena.width, 10)
        self.assertEqual(self.arena.height, 10)
        self.assertEqual(len(self.arena.grid), 10)  # Height (rows)
        self.assertEqual(len(self.arena.grid[0]), 10)  # Width (columns)
        
        # All cells should start empty
        for row in self.arena.grid:
            for cell in row:
                self.assertEqual(cell, CellType.EMPTY)

    def test_is_valid_position(self):
        """Test position validation within arena bounds."""
        # Valid positions
        self.assertTrue(self.arena.is_valid_position(0, 0))
        self.assertTrue(self.arena.is_valid_position(5, 5))
        self.assertTrue(self.arena.is_valid_position(9, 9))
        
        # Invalid positions
        self.assertFalse(self.arena.is_valid_position(-1, 0))
        self.assertFalse(self.arena.is_valid_position(0, -1))
        self.assertFalse(self.arena.is_valid_position(10, 5))
        self.assertFalse(self.arena.is_valid_position(5, 10))

    def test_is_passable(self):
        """Test passability checks for different cell types."""
        # Empty cell should be passable
        self.assertTrue(self.arena.is_passable(5, 5))
        
        # Obstacle should not be passable
        self.arena.place_obstacle(5, 5)
        self.assertFalse(self.arena.is_passable(5, 5))
        
        # Dead robot should not be passable
        self.arena.place_dead_robot(3, 3)
        self.assertFalse(self.arena.is_passable(3, 3))
        
        # Out of bounds should not be passable
        self.assertFalse(self.arena.is_passable(-1, 0))
        self.assertFalse(self.arena.is_passable(10, 10))

    def test_obstacle_placement(self):
        """Test obstacle placement and grid state."""
        self.arena.place_obstacle(5, 5)
        self.assertEqual(self.arena.grid[5][5], CellType.OBSTACLE)
        
        # Invalid position should not place obstacle
        original_grid = [row[:] for row in self.arena.grid]  # Deep copy
        self.arena.place_obstacle(-1, 0)
        self.assertEqual(self.arena.grid, original_grid)

    def test_dead_robot_placement(self):
        """Test dead robot (skull) placement."""
        self.arena.place_dead_robot(7, 7)
        self.assertEqual(self.arena.grid[7][7], CellType.DEAD_ROBOT)

    def test_mine_placement_and_retrieval(self):
        """Test mine placement with ownership encoding."""
        # Place mine for player 1
        self.arena.place_mine(5, 5, 1, 200)
        
        self.assertTrue(self.arena.has_mine(5, 5))
        self.assertFalse(self.arena.has_mine(5, 6))
        
        # Trigger mine and check data
        mine_data = self.arena.trigger_mine(5, 5)
        self.assertIsNotNone(mine_data)
        
        mine_id, damage = mine_data
        self.assertEqual(mine_id, 10)  # Player 1 * 10
        self.assertEqual(damage, 200)
        
        # Mine should be consumed after triggering
        self.assertFalse(self.arena.has_mine(5, 5))

    def test_mine_trigger_nonexistent(self):
        """Test triggering mine at position with no mine."""
        result = self.arena.trigger_mine(5, 5)
        self.assertIsNone(result)

    def test_direction_offsets(self):
        """Test direction offset calculations."""
        test_cases = [
            (Direction.N, (0, -1)),
            (Direction.NE, (1, -1)),
            (Direction.E, (1, 0)),
            (Direction.SE, (1, 1)),
            (Direction.S, (0, 1)),
            (Direction.SW, (-1, 1)),
            (Direction.W, (-1, 0)),
            (Direction.NW, (-1, -1)),
        ]
        
        for direction, expected_offset in test_cases:
            offset = self.arena.get_direction_offset(direction)
            self.assertEqual(offset, expected_offset)

    def test_adjacent_positions(self):
        """Test getting adjacent positions (8-directional)."""
        # Center position should have 8 adjacent positions
        adjacent = self.arena.get_adjacent_positions(5, 5)
        self.assertEqual(len(adjacent), 8)
        
        expected_positions = {
            (4, 4), (5, 4), (6, 4),  # North row
            (4, 5),         (6, 5),  # Same row (excluding center)
            (4, 6), (5, 6), (6, 6)   # South row
        }
        self.assertEqual(set(adjacent), expected_positions)
        
        # Corner position should have fewer adjacent positions
        corner_adjacent = self.arena.get_adjacent_positions(0, 0)
        self.assertEqual(len(corner_adjacent), 3)
        expected_corner = {(0, 1), (1, 0), (1, 1)}
        self.assertEqual(set(corner_adjacent), expected_corner)

    def test_get_random_empty_position(self):
        """Test random empty position generation."""
        # Should return valid position
        x, y = self.arena.get_random_empty_position()
        self.assertTrue(self.arena.is_valid_position(x, y))
        self.assertTrue(self.arena.is_passable(x, y))
        
        # Should respect exclusion set
        exclude = {(5, 5), (6, 6)}
        x, y = self.arena.get_random_empty_position(exclude)
        self.assertNotIn((x, y), exclude)

    def test_get_random_empty_position_with_obstacles(self):
        """Test random position generation avoids obstacles."""
        # Fill most of arena with obstacles, leave one empty spot
        for y in range(10):
            for x in range(10):
                if (x, y) != (9, 9):  # Leave (9,9) empty
                    self.arena.place_obstacle(x, y)
        
        x, y = self.arena.get_random_empty_position()
        self.assertEqual((x, y), (9, 9))

    def test_get_random_empty_position_no_space(self):
        """Test exception when no empty positions available."""
        # Fill entire arena with obstacles
        for y in range(10):
            for x in range(10):
                self.arena.place_obstacle(x, y)
        
        with self.assertRaises(Exception):
            self.arena.get_random_empty_position()

    def test_obstacle_generation(self):
        """Test random obstacle generation."""
        obstacle_count = 5
        self.arena.generate_obstacles(obstacle_count)
        
        # Count placed obstacles
        placed_obstacles = 0
        for row in self.arena.grid:
            for cell in row:
                if cell == CellType.OBSTACLE:
                    placed_obstacles += 1
        
        self.assertEqual(placed_obstacles, obstacle_count)

    def test_find_nearest_robot_position(self):
        """Test finding nearest robot using Manhattan distance."""
        # Add robots to arena
        robot1 = Robot(1, 3, 3, 1000)
        robot2 = Robot(2, 7, 7, 1000)
        robot3 = Robot(3, 1, 8, 1000)
        
        self.arena.robots = {
            (3, 3): robot1,
            (7, 7): robot2,
            (1, 8): robot3
        }
        
        # From (5, 5), robot1 at (3, 3) should be nearest
        # Distance to (3,3) = |5-3| + |5-3| = 4
        # Distance to (7,7) = |5-7| + |5-7| = 4  
        # Distance to (1,8) = |5-1| + |5-8| = 7
        # Both robot1 and robot2 are equidistant, should return one of them
        nearest = self.arena.find_nearest_robot_position(5, 5)
        self.assertIn(nearest, [(3, 3), (7, 7)])
        
        # From (2, 2), robot1 should definitely be nearest
        nearest = self.arena.find_nearest_robot_position(2, 2)
        self.assertEqual(nearest, (3, 3))

    def test_find_nearest_robot_with_exclusions(self):
        """Test finding nearest robot with exclusion set."""
        robot1 = Robot(1, 3, 3, 1000)
        robot2 = Robot(2, 7, 7, 1000)
        
        self.arena.robots = {
            (3, 3): robot1,
            (7, 7): robot2
        }
        
        # Exclude closest robot, should return second closest
        nearest = self.arena.find_nearest_robot_position(2, 2, exclude_positions={(3, 3)})
        self.assertEqual(nearest, (7, 7))

    def test_get_move_towards(self):
        """Test calculating direction to move towards target."""
        test_cases = [
            # (from_x, from_y, to_x, to_y, expected_direction)
            (5, 5, 5, 4, Direction.N),    # North
            (5, 5, 6, 4, Direction.NE),   # Northeast
            (5, 5, 6, 5, Direction.E),    # East
            (5, 5, 6, 6, Direction.SE),   # Southeast
            (5, 5, 5, 6, Direction.S),    # South
            (5, 5, 4, 6, Direction.SW),   # Southwest
            (5, 5, 4, 5, Direction.W),    # West
            (5, 5, 4, 4, Direction.NW),   # Northwest
        ]
        
        for from_x, from_y, to_x, to_y, expected in test_cases:
            result = self.arena.get_move_towards(from_x, from_y, to_x, to_y)
            self.assertEqual(result, expected)
        
        # Same position should return None
        result = self.arena.get_move_towards(5, 5, 5, 5)
        self.assertIsNone(result)

    def test_get_move_towards_large_distances(self):
        """Test move towards with large distances (should normalize)."""
        # Moving towards distant target should still give correct direction
        result = self.arena.get_move_towards(0, 0, 10, 10)
        self.assertEqual(result, Direction.SE)
        
        result = self.arena.get_move_towards(10, 10, 0, 0)
        self.assertEqual(result, Direction.NW)

    def test_get_move_away(self):
        """Test calculating direction to move away from target."""
        test_cases = [
            # (from_x, from_y, avoid_x, avoid_y, expected_direction)
            (5, 5, 5, 4, Direction.S),    # Away from North = South
            (5, 5, 6, 4, Direction.SW),   # Away from Northeast = Southwest
            (5, 5, 6, 5, Direction.W),    # Away from East = West
            (5, 5, 6, 6, Direction.NW),   # Away from Southeast = Northwest
            (5, 5, 5, 6, Direction.N),    # Away from South = North
            (5, 5, 4, 6, Direction.NE),   # Away from Southwest = Northeast
            (5, 5, 4, 5, Direction.E),    # Away from West = East
            (5, 5, 4, 4, Direction.SE),   # Away from Northwest = Southeast
        ]
        
        for from_x, from_y, avoid_x, avoid_y, expected in test_cases:
            result = self.arena.get_move_away(from_x, from_y, avoid_x, avoid_y)
            self.assertEqual(result, expected)
        
        # Same position should return None
        result = self.arena.get_move_away(5, 5, 5, 5)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()