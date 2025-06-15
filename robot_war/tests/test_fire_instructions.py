"""Unit tests for FR (Fire Row) and FC (Fire Column) instructions."""

import unittest
from robot_war.core.game_state import GameState
from robot_war.core.robot import Robot, RobotStatus
from robot_war.core.instructions import InstructionSet, InstructionType


class TestFireInstructions(unittest.TestCase):
    """Test FR (Fire Row) and FC (Fire Column) attack instructions."""

    def setUp(self):
        """Set up test game state with robots and obstacles."""
        self.game = GameState(arena_width=10, arena_height=10)
        self.game.num_obstacles = 0  # No random obstacles for predictable tests
        self.game.proximity_distance = 5  # Set proximity distance for firing range
        
        # Add test robots
        self.shooter = self.game.add_robot(1, 1000)  # Player 1 (shooter)
        self.target1 = self.game.add_robot(2, 1000)  # Player 2 (target)
        self.target2 = self.game.add_robot(3, 1000)  # Player 3 (target)
        
        # Clear arena robots dict and set manually for predictable tests
        self.game.arena.robots.clear()

    def test_fr_energy_cost(self):
        """Test FR instruction energy cost."""
        fr_cost = InstructionSet.get_energy_cost(InstructionType.FR)
        self.assertEqual(fr_cost, 100)

    def test_fc_energy_cost(self):
        """Test FC instruction energy cost."""
        fc_cost = InstructionSet.get_energy_cost(InstructionType.FC)
        self.assertEqual(fc_cost, 100)

    def test_fr_damage_value(self):
        """Test FR instruction damage value."""
        fr_damage = InstructionSet.get_damage(InstructionType.FR)
        self.assertEqual(fr_damage, 200)

    def test_fc_damage_value(self):
        """Test FC instruction damage value."""
        fc_damage = InstructionSet.get_damage(InstructionType.FC)
        self.assertEqual(fc_damage, 200)

    def test_fr_hits_left_target(self):
        """Test FR fires left and hits target."""
        # Setup: shooter at (5,5), target at (2,5) - same row, left side
        self.shooter.set_position(5, 5)
        self.target1.set_position(2, 5)
        self.game.arena.robots = {(5, 5): self.shooter, (2, 5): self.target1}
        
        original_target_energy = self.target1.energy
        
        # Execute FR
        self.game._fire_row(self.shooter)
        
        # Target should take 200 damage
        expected_energy = original_target_energy - 200
        self.assertEqual(self.target1.energy, expected_energy)

    def test_fr_hits_right_target(self):
        """Test FR fires right and hits target."""
        # Setup: shooter at (5,5), target at (8,5) - same row, right side
        self.shooter.set_position(5, 5)
        self.target1.set_position(8, 5)
        self.game.arena.robots = {(5, 5): self.shooter, (8, 5): self.target1}
        
        original_target_energy = self.target1.energy
        
        # Execute FR
        self.game._fire_row(self.shooter)
        
        # Target should take 200 damage
        expected_energy = original_target_energy - 200
        self.assertEqual(self.target1.energy, expected_energy)

    def test_fr_hits_both_sides(self):
        """Test FR hits targets on both left and right sides."""
        # Setup: shooter at (5,5), targets at (2,5) and (8,5)
        self.shooter.set_position(5, 5)
        self.target1.set_position(2, 5)  # Left target
        self.target2.set_position(8, 5)  # Right target
        self.game.arena.robots = {
            (5, 5): self.shooter,
            (2, 5): self.target1,
            (8, 5): self.target2
        }
        
        original_energy1 = self.target1.energy
        original_energy2 = self.target2.energy
        
        # Execute FR
        self.game._fire_row(self.shooter)
        
        # Both targets should take 200 damage
        self.assertEqual(self.target1.energy, original_energy1 - 200)
        self.assertEqual(self.target2.energy, original_energy2 - 200)

    def test_fc_hits_up_target(self):
        """Test FC fires up and hits target."""
        # Setup: shooter at (5,5), target at (5,2) - same column, above
        self.shooter.set_position(5, 5)
        self.target1.set_position(5, 2)
        self.game.arena.robots = {(5, 5): self.shooter, (5, 2): self.target1}
        
        original_target_energy = self.target1.energy
        
        # Execute FC
        self.game._fire_column(self.shooter)
        
        # Target should take 200 damage
        expected_energy = original_target_energy - 200
        self.assertEqual(self.target1.energy, expected_energy)

    def test_fc_hits_down_target(self):
        """Test FC fires down and hits target."""
        # Setup: shooter at (5,5), target at (5,8) - same column, below
        self.shooter.set_position(5, 5)
        self.target1.set_position(5, 8)
        self.game.arena.robots = {(5, 5): self.shooter, (5, 8): self.target1}
        
        original_target_energy = self.target1.energy
        
        # Execute FC
        self.game._fire_column(self.shooter)
        
        # Target should take 200 damage
        expected_energy = original_target_energy - 200
        self.assertEqual(self.target1.energy, expected_energy)

    def test_fc_hits_both_directions(self):
        """Test FC hits targets both up and down."""
        # Setup: shooter at (5,5), targets at (5,2) and (5,8)
        self.shooter.set_position(5, 5)
        self.target1.set_position(5, 2)  # Up target
        self.target2.set_position(5, 8)  # Down target
        self.game.arena.robots = {
            (5, 5): self.shooter,
            (5, 2): self.target1,
            (5, 8): self.target2
        }
        
        original_energy1 = self.target1.energy
        original_energy2 = self.target2.energy
        
        # Execute FC
        self.game._fire_column(self.shooter)
        
        # Both targets should take 200 damage
        self.assertEqual(self.target1.energy, original_energy1 - 200)
        self.assertEqual(self.target2.energy, original_energy2 - 200)

    def test_fr_range_limitation(self):
        """Test FR respects proximity distance range limit."""
        # Setup: shooter at (5,5), target at (0,5) - distance 5 (at boundary)
        self.game.proximity_distance = 5
        self.shooter.set_position(5, 5)
        self.target1.set_position(0, 5)  # Distance = 5
        self.game.arena.robots = {(5, 5): self.shooter, (0, 5): self.target1}
        
        original_target_energy = self.target1.energy
        
        # Execute FR - should hit (distance = proximity_distance)
        self.game._fire_row(self.shooter)
        self.assertEqual(self.target1.energy, original_target_energy - 200)
        
        # Reset target health and move it beyond range
        self.target1.energy = 1000
        self.target1.set_position(0, 4)  # Different row, same distance but wrong direction
        del self.game.arena.robots[(0, 5)]
        self.game.arena.robots[(0, 4)] = self.target1
        
        # Execute FR - should not hit (different row)
        self.game._fire_row(self.shooter)
        self.assertEqual(self.target1.energy, 1000)  # No damage

    def test_fr_obstacle_blocking(self):
        """Test FR shots are blocked by obstacles."""
        # Setup: shooter at (5,5), obstacle at (3,5), target at (1,5)
        self.shooter.set_position(5, 5)
        self.target1.set_position(1, 5)
        self.game.arena.robots = {(5, 5): self.shooter, (1, 5): self.target1}
        
        # Place obstacle between shooter and target
        self.game.arena.place_obstacle(3, 5)
        
        original_target_energy = self.target1.energy
        
        # Execute FR - shot should be blocked by obstacle
        self.game._fire_row(self.shooter)
        
        # Target should not take damage (shot blocked)
        self.assertEqual(self.target1.energy, original_target_energy)

    def test_fc_obstacle_blocking(self):
        """Test FC shots are blocked by obstacles."""
        # Setup: shooter at (5,5), obstacle at (5,3), target at (5,1)
        self.shooter.set_position(5, 5)
        self.target1.set_position(5, 1)
        self.game.arena.robots = {(5, 5): self.shooter, (5, 1): self.target1}
        
        # Place obstacle between shooter and target
        self.game.arena.place_obstacle(5, 3)
        
        original_target_energy = self.target1.energy
        
        # Execute FC - shot should be blocked by obstacle
        self.game._fire_column(self.shooter)
        
        # Target should not take damage (shot blocked)
        self.assertEqual(self.target1.energy, original_target_energy)

    def test_fr_stops_at_first_target(self):
        """Test FR stops at first target hit, doesn't continue through."""
        # Setup: shooter at (5,5), target1 at (3,5), target2 at (1,5)
        self.shooter.set_position(5, 5)
        self.target1.set_position(3, 5)  # Closer target
        self.target2.set_position(1, 5)  # Further target behind target1
        self.game.arena.robots = {
            (5, 5): self.shooter,
            (3, 5): self.target1,
            (1, 5): self.target2
        }
        
        original_energy1 = self.target1.energy
        original_energy2 = self.target2.energy
        
        # Execute FR
        self.game._fire_row(self.shooter)
        
        # First target should be hit, second should be protected
        self.assertEqual(self.target1.energy, original_energy1 - 200)
        self.assertEqual(self.target2.energy, original_energy2)  # No damage

    def test_fr_ignores_own_team(self):
        """Test FR doesn't hit robots from same player."""
        # Setup: two robots from same player in firing line
        teammate = self.game.add_robot(1, 1000)  # Same player ID as shooter
        self.shooter.set_position(5, 5)
        teammate.set_position(3, 5)  # Same row as shooter
        self.game.arena.robots = {(5, 5): self.shooter, (3, 5): teammate}
        
        original_teammate_energy = teammate.energy
        
        # Execute FR
        self.game._fire_row(self.shooter)
        
        # Teammate should not be damaged
        self.assertEqual(teammate.energy, original_teammate_energy)

    def test_fire_instructions_kill_target(self):
        """Test FR/FC properly handle target death."""
        # Setup: target with low health
        self.shooter.set_position(5, 5)
        self.target1.set_position(3, 5)
        self.target1.energy = 100  # Less than FR damage (200)
        self.game.arena.robots = {(5, 5): self.shooter, (3, 5): self.target1}
        
        # Execute FR
        self.game._fire_row(self.shooter)
        
        # Target should be dead
        self.assertFalse(self.target1.is_alive())
        # Dead robot should be removed from arena and replaced with skull
        self.assertNotIn((3, 5), self.game.arena.robots)
        # Check if skull/dead robot obstacle was placed
        self.assertFalse(self.game.arena.is_passable(3, 5))

    def test_pt_fr_conditional_execution(self):
        """Test PT(FR,RM) - fire if enemy detected, random move otherwise."""
        # Setup: robots close enough for proximity detection
        self.shooter.set_position(5, 5)
        self.target1.set_position(3, 5)  # Close target for proximity
        self.game.arena.robots = {(5, 5): self.shooter, (3, 5): self.target1}
        self.game.proximity_distance = 3
        
        original_target_energy = self.target1.energy
        
        # Execute PT(FR,RM) instruction - simulate full execution with energy deduction
        instruction = InstructionSet.parse_instruction("PT(FR,RM)")
        self.assertIsNotNone(instruction)
        pt_cost = InstructionSet.get_energy_cost(InstructionType.PT)
        
        # Deduct PT cost first (as done in main execution loop)
        self.shooter.use_energy(pt_cost)
        self.game._execute_proximity_test_conditional(self.shooter, instruction)
        
        # Should execute FR (enemy detected), target should take damage
        self.assertEqual(self.target1.energy, original_target_energy - 200)

    def test_pt_fc_conditional_execution(self):
        """Test PT(FC,IN) - fire if enemy detected, go invisible otherwise."""
        # Setup: robots close enough for proximity detection
        self.shooter.set_position(5, 5)
        self.target1.set_position(5, 3)  # Close target in same column
        self.game.arena.robots = {(5, 5): self.shooter, (5, 3): self.target1}
        self.game.proximity_distance = 3
        
        original_target_energy = self.target1.energy
        
        # Execute PT(FC,IN) instruction - simulate full execution with energy deduction
        instruction = InstructionSet.parse_instruction("PT(FC,IN)")
        self.assertIsNotNone(instruction)
        pt_cost = InstructionSet.get_energy_cost(InstructionType.PT)
        
        # Deduct PT cost first (as done in main execution loop)
        self.shooter.use_energy(pt_cost)
        self.game._execute_proximity_test_conditional(self.shooter, instruction)
        
        # Should execute FC (enemy detected), target should take damage
        self.assertEqual(self.target1.energy, original_target_energy - 200)

    def test_pt_false_branch_no_firing(self):
        """Test PT doesn't execute FR/FC when no enemies detected."""
        # Setup: no nearby enemies
        self.shooter.set_position(5, 5)
        self.target1.set_position(0, 0)  # Far away target
        self.game.arena.robots = {(5, 5): self.shooter, (0, 0): self.target1}
        self.game.proximity_distance = 3
        
        original_target_energy = self.target1.energy
        original_shooter_status = self.shooter.status
        
        # Execute PT(FR,IN) instruction - simulate full execution with energy deduction
        instruction = InstructionSet.parse_instruction("PT(FR,IN)")
        pt_cost = InstructionSet.get_energy_cost(InstructionType.PT)
        
        # Deduct PT cost first (as done in main execution loop)
        self.shooter.use_energy(pt_cost)
        # Then execute the conditional
        self.game._execute_proximity_test_conditional(self.shooter, instruction)
        
        # Should execute IN (no enemy detected), not FR
        self.assertEqual(self.target1.energy, original_target_energy)  # No damage
        self.assertEqual(self.shooter.status, RobotStatus.INVISIBLE)  # Shooter went invisible


if __name__ == '__main__':
    unittest.main()