"""Unit tests for PT (Proximity Test) conditional instruction."""

import unittest
from robot_war.core.game_state import GameState
from robot_war.core.robot import Robot, RobotStatus
from robot_war.core.instructions import InstructionSet, InstructionType


class TestPTInstruction(unittest.TestCase):
    """Test PT (Proximity Test) conditional instruction mechanics."""

    def setUp(self):
        """Set up test game state with known robot positions."""
        self.game = GameState(arena_width=10, arena_height=10)
        self.game.num_obstacles = 0  # No random obstacles for predictable tests
        self.game.proximity_distance = 3  # Set known proximity distance
        
        # Add two robots at known positions
        self.robot1 = self.game.add_robot(1, 1000)  # Player 1
        self.robot2 = self.game.add_robot(2, 1000)  # Player 2
        
        # Set predictable positions: close enough for proximity (distance = 2)
        self.robot1.set_position(5, 5)  # Robot 1 at center
        self.robot2.set_position(5, 7)  # Robot 2 south of robot 1 (distance = 2)
        
        # Update arena robot tracking
        self.game.arena.robots = {
            (5, 5): self.robot1,
            (5, 7): self.robot2
        }

    def test_pt_instruction_parsing_valid(self):
        """Test PT instruction parsing with valid format."""
        test_cases = [
            ("PT(IN,MI)", ("IN", "MI")),
            ("PT(DM(N),RM)", ("DM(N)", "RM")),
            ("PT(AM,PM)", ("AM", "PM")),
            ("PT(FR,RM)", ("FR", "RM")),
            ("PT(FC,IN)", ("FC", "IN")),
            ("PT(FR,FC)", ("FR", "FC")),
        ]
        
        for instruction_str, expected_actions in test_cases:
            instruction = InstructionSet.parse_instruction(instruction_str)
            self.assertIsNotNone(instruction)
            self.assertEqual(instruction.type, InstructionType.PT)
            self.assertEqual(instruction.parameter, expected_actions)

    def test_pt_instruction_parsing_invalid(self):
        """Test PT instruction parsing with invalid formats."""
        invalid_cases = [
            "PT()",           # No actions
            "PT(IN)",         # Only one action
            "PT(IN,MI,RM)",   # Too many actions
            "PT",             # No parentheses
            "PT(IN,)",        # Missing second action
            "PT(,MI)",        # Missing first action
        ]
        
        for invalid_str in invalid_cases:
            instruction = InstructionSet.parse_instruction(invalid_str)
            self.assertIsNone(instruction)

    def test_pt_energy_cost(self):
        """Test PT instruction energy cost."""
        pt_cost = InstructionSet.get_energy_cost(InstructionType.PT)
        self.assertEqual(pt_cost, 4)

    def test_pt_proximity_detection_true(self):
        """Test PT proximity detection when robots are close."""
        # Robots are at distance 2, proximity_distance is 3, so should detect
        result = self.game._check_proximity(self.robot1)
        self.assertTrue(result)

    def test_pt_proximity_detection_false(self):
        """Test PT proximity detection when robots are far apart."""
        # Move robot2 far away (distance > proximity_distance)
        self.robot2.set_position(0, 0)  # Distance from (5,5) = 10
        self.game.arena.robots = {(5, 5): self.robot1, (0, 0): self.robot2}
        
        result = self.game._check_proximity(self.robot1)
        self.assertFalse(result)

    def test_pt_ignores_invisible_robots(self):
        """Test PT doesn't detect invisible robots."""
        # Make robot2 invisible
        self.robot2.status = RobotStatus.INVISIBLE
        
        # Even though robots are close, invisible robot shouldn't be detected
        result = self.game._check_proximity(self.robot1)
        self.assertFalse(result)

    def test_pt_ignores_frozen_robots(self):
        """Test PT doesn't detect frozen robots."""
        # Make robot2 frozen
        self.robot2.status = RobotStatus.FROZEN
        
        # Even though robots are close, frozen robot shouldn't be detected
        result = self.game._check_proximity(self.robot1)
        self.assertFalse(result)

    def test_pt_ignores_self(self):
        """Test PT doesn't detect the robot's own position."""
        # Remove robot2, only robot1 should remain
        del self.game.arena.robots[(5, 7)]
        self.game.robots = [self.robot1]
        
        # Should return false since robot doesn't detect itself
        result = self.game._check_proximity(self.robot1)
        self.assertFalse(result)

    def test_pt_conditional_execution_true_branch(self):
        """Test PT executes first action when proximity test is true."""
        # Set up PT instruction: if enemy nearby, go invisible; else place mine
        self.robot1.program = ["PT(IN,MI)"]
        self.robot1.program_counter = 0
        
        original_energy = self.robot1.energy
        original_status = self.robot1.status
        
        # Execute the PT instruction
        instruction = InstructionSet.parse_instruction("PT(IN,MI)")
        self.game._execute_proximity_test_conditional(self.robot1, instruction)
        
        # Should execute IN (invisibility) since robots are close
        self.assertEqual(self.robot1.status, RobotStatus.INVISIBLE)
        # Should consume PT cost (4) + IN cost (200)
        expected_energy = original_energy - 200  # IN cost (PT cost already deducted)
        self.assertEqual(self.robot1.energy, expected_energy)

    def test_pt_conditional_execution_false_branch(self):
        """Test PT executes second action when proximity test is false."""
        # Move robot2 far away to make proximity test false
        self.robot2.set_position(0, 0)
        self.game.arena.robots = {(5, 5): self.robot1, (0, 0): self.robot2}
        
        original_energy = self.robot1.energy
        original_mine_count = len(self.game.arena.mines)
        
        # Execute PT instruction
        instruction = InstructionSet.parse_instruction("PT(IN,MI)")
        self.game._execute_proximity_test_conditional(self.robot1, instruction)
        
        # Should execute MI (place mine) since no robots nearby
        self.assertEqual(len(self.game.arena.mines), original_mine_count + 1)
        self.assertTrue(self.game.arena.has_mine(5, 5))  # Mine at robot1's position
        
        # Should consume PT cost (4) + MI cost (200)
        expected_energy = original_energy - 200  # MI cost (PT cost already deducted)
        self.assertEqual(self.robot1.energy, expected_energy)

    def test_pt_with_movement_actions(self):
        """Test PT with movement actions like DM(N)."""
        # Set up scenario where proximity test is true
        original_position = self.robot1.get_position()
        
        # Execute PT with movement: if enemy nearby move north, else move south
        instruction = InstructionSet.parse_instruction("PT(DM(N),DM(S))")
        self.game._execute_proximity_test_conditional(self.robot1, instruction)
        
        # Should execute DM(N) since robots are close
        expected_position = (5, 4)  # Move north from (5,5)
        self.assertEqual(self.robot1.get_position(), expected_position)
        
        # Should consume PT cost (4) + DM cost (5)
        expected_energy = 1000 - 5  # DM cost (PT cost already deducted)
        self.assertEqual(self.robot1.energy, expected_energy)

    def test_pt_insufficient_energy_for_chosen_action(self):
        """Test PT behavior when robot can't afford the chosen action."""
        # Set robot energy to only afford PT but not the chosen action
        self.robot1.energy = 100  # Can afford PT (4) but not IN (200)
        original_energy = self.robot1.energy
        original_status = self.robot1.status
        
        instruction = InstructionSet.parse_instruction("PT(IN,MI)")
        self.game._execute_proximity_test_conditional(self.robot1, instruction)
        
        # Robot should not change status (can't afford IN)
        self.assertEqual(self.robot1.status, original_status)
        # Energy should not change (action not executed)
        self.assertEqual(self.robot1.energy, original_energy)

    def test_pt_invalid_chosen_action(self):
        """Test PT behavior with invalid action in conditional."""
        instruction = InstructionSet.parse_instruction("PT(INVALID,MI)")
        if instruction:  # Parsing might fail, which is acceptable
            original_state = (self.robot1.energy, self.robot1.status, len(self.game.arena.mines))
            
            self.game._execute_proximity_test_conditional(self.robot1, instruction)
            
            # Robot state should not change with invalid action
            current_state = (self.robot1.energy, self.robot1.status, len(self.game.arena.mines))
            self.assertEqual(current_state, original_state)

    def test_pt_boundary_proximity_distance(self):
        """Test PT at exact proximity distance boundary."""
        # Set robot2 at exactly proximity_distance away (within 10x10 grid bounds)
        self.game.proximity_distance = 4
        self.robot2.set_position(5, 9)  # Distance = 4 (exactly at boundary, within grid)
        self.game.arena.robots = {(5, 5): self.robot1, (5, 9): self.robot2}
        
        # At distance = proximity_distance, should detect (<=)
        result = self.game._check_proximity(self.robot1)
        self.assertTrue(result)
        
        # Test just beyond boundary - move to distance 5
        self.game.proximity_distance = 3  # Reduce proximity distance
        result = self.game._check_proximity(self.robot1)
        self.assertFalse(result)  # Distance 4 > proximity 3

    def test_pt_multiple_nearby_robots(self):
        """Test PT with multiple robots in proximity."""
        # Add a third robot nearby
        robot3 = self.game.add_robot(3, 1000)
        robot3.set_position(3, 5)  # Distance from robot1 = 2
        self.game.arena.robots[(3, 5)] = robot3
        
        # Should detect proximity with multiple robots nearby
        result = self.game._check_proximity(self.robot1)
        self.assertTrue(result)
        
        # Make robot2 invisible, should still detect robot3
        self.robot2.status = RobotStatus.INVISIBLE
        result = self.game._check_proximity(self.robot1)
        self.assertTrue(result)

    def test_pt_with_fire_row_action(self):
        """Test PT with FR action when enemies are detected."""
        # Position robots for firing test
        self.robot1.set_position(5, 5)
        self.robot2.set_position(3, 5)  # Same row, within range
        self.game.arena.robots = {(5, 5): self.robot1, (3, 5): self.robot2}
        
        original_target_energy = self.robot2.energy
        
        # Execute PT(FR,IN) - should fire since enemy detected
        instruction = InstructionSet.parse_instruction("PT(FR,IN)")
        self.game._execute_proximity_test_conditional(self.robot1, instruction)
        
        # Robot2 should take fire damage
        expected_energy = original_target_energy - 200  # FR damage
        self.assertEqual(self.robot2.energy, expected_energy)

    def test_pt_with_fire_column_action(self):
        """Test PT with FC action when enemies are detected."""
        # Position robots for firing test
        self.robot1.set_position(5, 5)
        self.robot2.set_position(5, 3)  # Same column, within range
        self.game.arena.robots = {(5, 5): self.robot1, (5, 3): self.robot2}
        
        original_target_energy = self.robot2.energy
        
        # Execute PT(FC,MI) - should fire since enemy detected
        instruction = InstructionSet.parse_instruction("PT(FC,MI)")
        self.game._execute_proximity_test_conditional(self.robot1, instruction)
        
        # Robot2 should take fire damage
        expected_energy = original_target_energy - 200  # FC damage
        self.assertEqual(self.robot2.energy, expected_energy)

    def test_pt_fire_no_target_in_line(self):
        """Test PT fire actions when enemy detected but not in firing line."""
        # Position enemy nearby but not in row/column
        self.robot1.set_position(5, 5)
        self.robot2.set_position(3, 3)  # Diagonal, close enough for proximity
        self.game.arena.robots = {(5, 5): self.robot1, (3, 3): self.robot2}
        
        original_target_energy = self.robot2.energy
        
        # Execute PT(FR,RM) - proximity detects enemy but FR won't hit (different row)
        instruction = InstructionSet.parse_instruction("PT(FR,RM)")
        self.game._execute_proximity_test_conditional(self.robot1, instruction)
        
        # Robot2 should not take damage (not in firing line)
        self.assertEqual(self.robot2.energy, original_target_energy)

    def test_pt_proximity_blocked_by_obstacle(self):
        """Test PT proximity detection is blocked by obstacles."""
        # Setup: robot1 at (5,5), robot2 at (5,7), obstacle at (5,6) between them
        self.robot1.set_position(5, 5)
        self.robot2.set_position(5, 7)  # Distance = 2 (within proximity range of 3)
        self.game.arena.robots = {(5, 5): self.robot1, (5, 7): self.robot2}
        
        # Place obstacle between robots
        self.game.arena.place_obstacle(5, 6)
        
        # Even though robots are within proximity distance, obstacle should block detection
        result = self.game._check_proximity(self.robot1)
        self.assertFalse(result)

    def test_pt_proximity_clear_line_of_sight(self):
        """Test PT proximity detection works with clear line of sight."""
        # Setup: robot1 at (5,5), robot2 at (5,7), no obstacles between
        self.robot1.set_position(5, 5)
        self.robot2.set_position(5, 7)  # Distance = 2 (within proximity range of 3)
        self.game.arena.robots = {(5, 5): self.robot1, (5, 7): self.robot2}
        
        # Should detect with clear line of sight
        result = self.game._check_proximity(self.robot1)
        self.assertTrue(result)

    def test_pt_proximity_diagonal_blocked(self):
        """Test PT proximity detection blocked diagonally."""
        # Setup: robot1 at (5,5), robot2 at (7,7), obstacle at (6,6) between them
        self.robot1.set_position(5, 5)
        self.robot2.set_position(7, 7)  # Distance = 4 (within proximity range of 5)
        self.game.arena.robots = {(5, 5): self.robot1, (7, 7): self.robot2}
        self.game.proximity_distance = 5  # Increase range to test diagonal blocking
        
        # Place obstacle in diagonal path
        self.game.arena.place_obstacle(6, 6)
        
        # Obstacle should block diagonal line of sight
        result = self.game._check_proximity(self.robot1)
        self.assertFalse(result)

    def test_line_of_sight_direct_method(self):
        """Test the line of sight method directly."""
        # Clear path
        self.assertTrue(self.game._has_line_of_sight(0, 0, 2, 0))  # Horizontal
        self.assertTrue(self.game._has_line_of_sight(0, 0, 0, 2))  # Vertical
        self.assertTrue(self.game._has_line_of_sight(0, 0, 2, 2))  # Diagonal
        
        # Place obstacle and test blocked paths
        self.game.arena.place_obstacle(1, 0)
        self.assertFalse(self.game._has_line_of_sight(0, 0, 2, 0))  # Blocked horizontal
        self.assertTrue(self.game._has_line_of_sight(0, 0, 0, 2))   # Still clear vertical


if __name__ == '__main__':
    unittest.main()