"""Test to verify robots cannot have negative energy."""

import unittest
from robot_war.core.robot import Robot, RobotStatus


class TestNegativeEnergyFix(unittest.TestCase):
    """Test that robots cannot have negative energy values."""

    def test_take_damage_prevents_negative_energy(self):
        """Test that take_damage prevents negative energy."""
        robot = Robot(1, 5, 5, energy=50)
        
        robot.take_damage(100)
        
        self.assertEqual(robot.energy, 0)
        self.assertEqual(robot.status, RobotStatus.DEAD)

    def test_use_energy_prevents_negative_energy(self):
        """Test that use_energy prevents negative energy."""
        robot = Robot(1, 5, 5, energy=50)
        
        success = robot.use_energy(50)
        
        self.assertTrue(success)
        self.assertEqual(robot.energy, 0)
        self.assertEqual(robot.status, RobotStatus.DEAD)

    def test_multiple_damage_applications(self):
        """Test multiple damage applications don't create negative energy."""
        robot = Robot(1, 5, 5, energy=100)
        
        robot.take_damage(60)
        self.assertEqual(robot.energy, 40)
        self.assertEqual(robot.status, RobotStatus.ALIVE)
        
        robot.take_damage(50)
        self.assertEqual(robot.energy, 0)
        self.assertEqual(robot.status, RobotStatus.DEAD)

    def test_exact_energy_depletion(self):
        """Test exact energy depletion works correctly."""
        robot = Robot(1, 5, 5, energy=100)
        
        robot.take_damage(100)
        self.assertEqual(robot.energy, 0)
        self.assertEqual(robot.status, RobotStatus.DEAD)

    def test_energy_cannot_go_below_zero_after_death(self):
        """Test that energy stays at 0 even after robot is already dead."""
        robot = Robot(1, 5, 5, energy=100)
        
        robot.take_damage(150)
        self.assertEqual(robot.energy, 0)
        self.assertEqual(robot.status, RobotStatus.DEAD)
        
        robot.take_damage(50)
        self.assertEqual(robot.energy, 0)
        self.assertEqual(robot.status, RobotStatus.DEAD)


if __name__ == '__main__':
    unittest.main()