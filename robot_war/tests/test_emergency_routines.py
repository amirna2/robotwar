"""Unit tests for emergency routine (Circuit de Secours) system."""

import unittest
from robot_war.core.game_state import GameState
from robot_war.core.robot import Robot, RobotStatus
from robot_war.core.instructions import InstructionSet, InstructionType


class TestEmergencyRoutines(unittest.TestCase):
    """Test emergency routine system mechanics."""

    def setUp(self):
        """Set up test game state with robots."""
        self.game = GameState(arena_width=10, arena_height=10)
        self.game.num_obstacles = 0  # No random obstacles for predictable tests
        
        # Add robot at known position
        self.robot = self.game.add_robot(1, 1000)
        self.robot.set_position(5, 5)
        
        # Update arena robot tracking
        self.game.arena.robots = {(5, 5): self.robot}

    def test_emergency_threshold_initialization(self):
        """Test that emergency threshold is set correctly on robot creation."""
        # Emergency threshold should be highest instruction cost + buffer (200 + 10 = 210)
        expected_threshold = max(InstructionSet.ENERGY_COSTS.values()) + 10
        self.assertEqual(self.robot.emergency_energy_threshold, expected_threshold)
        self.assertEqual(expected_threshold, 210)  # MI/IN cost 200, +10 buffer

    def test_emergency_action_initialization(self):
        """Test that emergency action starts as None."""
        self.assertIsNone(self.robot.emergency_action)

    def test_emergency_trigger_with_low_energy(self):
        """Test emergency routine triggers when energy drops below threshold."""
        # Set emergency action and low energy
        self.robot.emergency_action = "RM"  # Random move (5 energy cost)
        self.robot.energy = 200  # Below threshold of 210
        
        original_position = self.robot.get_position()
        
        # Execute a turn - should trigger emergency routine instead of normal instruction
        self.robot.program = ["MI"]  # Expensive instruction robot can't afford
        self.robot.program_counter = 0
        
        # Execute robot instructions
        self.game._execute_robot_instructions([self.robot])
        
        # Robot should have executed emergency action (RM) instead of MI
        # Since RM is random, we can't predict exact position, but it should have moved or energy changed
        self.assertEqual(self.robot.energy, 195)  # 200 - 5 (RM cost)

    def test_emergency_trigger_insufficient_energy_for_normal_instruction(self):
        """Test emergency triggers when robot can't afford current instruction."""
        # Set emergency action and energy just below instruction cost
        self.robot.emergency_action = "DM(N)"  # 5 energy cost
        self.robot.energy = 100  # Can afford emergency but not MI
        self.robot.program = ["MI"]  # 200 energy cost
        self.robot.program_counter = 0
        
        original_position = self.robot.get_position()
        
        # Execute robot instructions
        self.game._execute_robot_instructions([self.robot])
        
        # Should execute emergency action (DM(N)) instead of MI
        expected_position = (5, 4)  # Move north from (5,5)
        self.assertEqual(self.robot.get_position(), expected_position)
        self.assertEqual(self.robot.energy, 95)  # 100 - 5 (DM cost)

    def test_no_emergency_action_freezes_robot(self):
        """Test robot freezes when no emergency action is set and energy is low."""
        # No emergency action set
        self.robot.emergency_action = None
        self.robot.energy = 50  # Below threshold
        self.robot.program = ["MI"]  # Expensive instruction
        self.robot.program_counter = 0
        
        original_energy = self.robot.energy
        original_position = self.robot.get_position()
        
        # Execute robot instructions
        self.game._execute_robot_instructions([self.robot])
        
        # Robot should be frozen
        self.assertEqual(self.robot.status, RobotStatus.FROZEN)
        self.assertEqual(self.robot.energy, original_energy)  # No energy consumed
        self.assertEqual(self.robot.get_position(), original_position)  # No movement

    def test_emergency_action_insufficient_energy_freezes_robot(self):
        """Test robot freezes when it can't afford its emergency action."""
        # Set expensive emergency action robot can't afford
        self.robot.emergency_action = "MI"  # 200 energy cost
        self.robot.energy = 50  # Not enough for emergency action
        self.robot.program = ["DM(N)"]  # Any instruction
        self.robot.program_counter = 0
        
        original_energy = self.robot.energy
        
        # Execute robot instructions
        self.game._execute_robot_instructions([self.robot])
        
        # Robot should be frozen since it can't afford emergency action
        self.assertEqual(self.robot.status, RobotStatus.FROZEN)
        self.assertEqual(self.robot.energy, original_energy)  # No energy consumed

    def test_emergency_action_execution_types(self):
        """Test different types of emergency actions."""
        test_cases = [
            # (emergency_action, initial_energy, expected_energy_cost, expected_status)
            ("RM", 300, 5, RobotStatus.ALIVE),          # Random move
            ("DM(S)", 300, 5, RobotStatus.ALIVE),       # Directed move
            ("IN", 300, 200, RobotStatus.INVISIBLE),    # Invisibility
            ("MI", 250, 200, RobotStatus.ALIVE),        # Mine placement - use 250 energy to avoid death
        ]
        
        for emergency_action, initial_energy, expected_cost, expected_status in test_cases:
            with self.subTest(emergency_action=emergency_action):
                # Reset robot state
                self.robot.energy = initial_energy
                self.robot.status = RobotStatus.ALIVE
                self.robot.emergency_action = emergency_action
                self.robot.set_position(5, 5)
                self.game.arena.robots = {(5, 5): self.robot}
                self.game.arena.mines.clear()  # Clear any mines from previous tests
                
                # Set energy to initial energy
                self.robot.energy = initial_energy
                
                # Execute emergency routine directly
                self.game._execute_emergency_routine(self.robot)
                
                # Check results
                expected_energy = initial_energy - expected_cost
                self.assertEqual(self.robot.energy, expected_energy)
                self.assertEqual(self.robot.status, expected_status)

    def test_emergency_action_mine_placement(self):
        """Test emergency routine placing mines."""
        self.robot.emergency_action = "MI"
        self.robot.energy = 250  # Enough for MI (200 cost)
        
        original_mine_count = len(self.game.arena.mines)
        
        # Execute emergency routine
        self.game._execute_emergency_routine(self.robot)
        
        # Should have placed a mine
        self.assertEqual(len(self.game.arena.mines), original_mine_count + 1)
        self.assertTrue(self.game.arena.has_mine(5, 5))  # Mine at robot position

    def test_emergency_action_movement(self):
        """Test emergency routine movement actions."""
        movement_cases = [
            ("DM(N)", (5, 4)),   # North
            ("DM(E)", (6, 5)),   # East  
            ("DM(S)", (5, 6)),   # South
            ("DM(W)", (4, 5)),   # West
        ]
        
        for emergency_action, expected_position in movement_cases:
            with self.subTest(emergency_action=emergency_action):
                # Reset robot position
                self.robot.set_position(5, 5)
                self.robot.energy = 250
                self.robot.emergency_action = emergency_action
                self.game.arena.robots = {(5, 5): self.robot}
                
                # Execute emergency routine
                self.game._execute_emergency_routine(self.robot)
                
                # Check robot moved to expected position
                self.assertEqual(self.robot.get_position(), expected_position)

    def test_emergency_action_invalid_instruction(self):
        """Test emergency routine with invalid emergency action."""
        self.robot.emergency_action = "INVALID"
        self.robot.energy = 250
        
        original_state = (self.robot.energy, self.robot.status, self.robot.get_position())
        
        # Execute emergency routine
        self.game._execute_emergency_routine(self.robot)
        
        # Robot state should not change with invalid emergency action
        current_state = (self.robot.energy, self.robot.status, self.robot.get_position())
        self.assertEqual(current_state, original_state)

    def test_emergency_routine_robot_death(self):
        """Test robot death during emergency action execution."""
        # Set robot with very low energy that will die from emergency action
        self.robot.energy = 5  # Will die after any action
        self.robot.emergency_action = "DM(N)"  # 5 energy cost
        
        # Execute emergency routine
        self.game._execute_emergency_routine(self.robot)
        
        # Robot should be dead 
        self.assertEqual(self.robot.status, RobotStatus.DEAD)
        
        # Robot should be removed from arena at new position and skull placed
        final_position = self.robot.get_position()  # Should be (5,4) after moving north
        self.assertNotIn(final_position, self.game.arena.robots)
        
        # Should have placed skull obstacle at final position
        from robot_war.core.arena import CellType
        final_x, final_y = final_position
        self.assertEqual(self.game.arena.grid[final_y][final_x], CellType.DEAD_ROBOT)

    def test_emergency_vs_normal_execution_priority(self):
        """Test that emergency routine takes priority over normal instruction."""
        # Set up scenario where robot could execute normal instruction but should use emergency
        self.robot.energy = 200  # Below threshold (210) but above instruction cost
        self.robot.emergency_action = "DM(E)"
        self.robot.program = ["DM(N)"]  # Different direction
        self.robot.program_counter = 0
        
        # Execute turn
        self.game._execute_robot_instructions([self.robot])
        
        # Should execute emergency action (move east) not normal instruction (move north)
        expected_position = (6, 5)  # East from (5,5)
        self.assertEqual(self.robot.get_position(), expected_position)

    def test_frozen_robot_program_counter_not_advanced(self):
        """Test that frozen robots don't advance their program counter."""
        # Set up robot that will freeze
        self.robot.emergency_action = None
        self.robot.energy = 50  # Below threshold
        self.robot.program = ["MI", "DM(N)", "RM"]
        self.robot.program_counter = 0
        
        original_counter = self.robot.program_counter
        
        # Execute turn
        self.game._execute_robot_instructions([self.robot])
        
        # Robot should be frozen and program counter unchanged
        self.assertEqual(self.robot.status, RobotStatus.FROZEN)
        self.assertEqual(self.robot.program_counter, original_counter)

    def test_emergency_action_energy_exactly_at_threshold(self):
        """Test behavior when robot energy equals emergency threshold."""
        # Set energy exactly at threshold
        self.robot.energy = self.robot.emergency_energy_threshold  # 210
        self.robot.emergency_action = "DM(N)"
        self.robot.program = ["MI"]  # Expensive instruction
        self.robot.program_counter = 0
        
        # Execute turn
        self.game._execute_robot_instructions([self.robot])
        
        # Should trigger emergency since energy <= threshold
        expected_position = (5, 4)  # Move north
        self.assertEqual(self.robot.get_position(), expected_position)
        self.assertEqual(self.robot.energy, 205)  # 210 - 5 (DM cost)

    def test_multiple_robots_emergency_independence(self):
        """Test that each robot's emergency system works independently."""
        # Add second robot
        robot2 = self.game.add_robot(2, 1000)
        robot2.set_position(7, 7)
        self.game.arena.robots[(7, 7)] = robot2
        
        # Set different emergency conditions
        self.robot.energy = 50  # Below threshold, no emergency action
        self.robot.emergency_action = None
        self.robot.program = ["MI"]
        
        robot2.energy = 200  # Below threshold, has emergency action
        robot2.emergency_action = "DM(W)"
        robot2.program = ["MI"]
        
        # Execute turn for both robots
        self.game._execute_robot_instructions([self.robot, robot2])
        
        # Robot 1 should be frozen
        self.assertEqual(self.robot.status, RobotStatus.FROZEN)
        self.assertEqual(self.robot.get_position(), (5, 5))  # No movement
        
        # Robot 2 should execute emergency action
        self.assertEqual(robot2.status, RobotStatus.ALIVE)
        self.assertEqual(robot2.get_position(), (6, 7))  # Moved west
        self.assertEqual(robot2.energy, 195)  # 200 - 5 (DM cost)


if __name__ == '__main__':
    unittest.main()