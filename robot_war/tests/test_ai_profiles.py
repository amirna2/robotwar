"""Tests for AI robot profiles system."""

import unittest
from robot_war.ai.profiles import AIProfileLibrary, AIPersonality, get_ai_robot_name, validate_ai_program


class TestAIProfiles(unittest.TestCase):
    """Test AI profile system functionality."""

    def test_all_profiles_exist(self):
        """Test that all expected AI profiles are available."""
        profiles = AIProfileLibrary.get_profiles()
        expected_profiles = [
            "berserker", "guardian", "hunter", "ghost", 
            "wanderer", "sniper", "trapper", "survivor"
        ]
        
        for profile_name in expected_profiles:
            self.assertIn(profile_name, profiles)
            
        self.assertEqual(len(profiles), len(expected_profiles))

    def test_profile_completeness(self):
        """Test that each profile has all required attributes."""
        profiles = AIProfileLibrary.get_profiles()
        
        for profile_name, profile in profiles.items():
            # Check required attributes exist
            self.assertTrue(hasattr(profile, 'name'))
            self.assertTrue(hasattr(profile, 'personality'))
            self.assertTrue(hasattr(profile, 'description'))
            self.assertTrue(hasattr(profile, 'program'))
            self.assertTrue(hasattr(profile, 'emergency_action'))
            self.assertTrue(hasattr(profile, 'energy_threshold'))
            self.assertTrue(hasattr(profile, 'preferred_names'))
            self.assertTrue(hasattr(profile, 'strategy_notes'))
            
            # Check program is not empty
            self.assertGreater(len(profile.program), 0)
            
            # Check preferred names is not empty
            self.assertGreater(len(profile.preferred_names), 0)
            
            # Check energy threshold is reasonable
            self.assertGreater(profile.energy_threshold, 0)
            self.assertLessEqual(profile.energy_threshold, 1000)

    def test_program_validation(self):
        """Test that all AI programs use valid instructions."""
        profiles = AIProfileLibrary.get_profiles()
        
        for profile_name, profile in profiles.items():
            with self.subTest(profile=profile_name):
                self.assertTrue(validate_ai_program(profile.program), 
                               f"Invalid program in {profile_name}: {profile.program}")

    def test_personality_enum_coverage(self):
        """Test that all profiles have valid personality types."""
        profiles = AIProfileLibrary.get_profiles()
        valid_personalities = set(p.value for p in AIPersonality)
        
        for profile_name, profile in profiles.items():
            self.assertIn(profile.personality.value, valid_personalities)

    def test_get_profile_by_name(self):
        """Test retrieving specific profiles by name."""
        # Test valid profile
        berserker = AIProfileLibrary.get_profile_by_name("berserker")
        self.assertIsNotNone(berserker)
        self.assertEqual(berserker.personality, AIPersonality.BERSERKER)
        
        # Test case insensitive
        guardian = AIProfileLibrary.get_profile_by_name("GUARDIAN")
        self.assertIsNotNone(guardian)
        self.assertEqual(guardian.personality, AIPersonality.GUARDIAN)
        
        # Test invalid profile
        invalid = AIProfileLibrary.get_profile_by_name("nonexistent")
        self.assertIsNone(invalid)

    def test_get_random_profile(self):
        """Test getting random profiles."""
        profile1 = AIProfileLibrary.get_random_profile()
        profile2 = AIProfileLibrary.get_random_profile()
        
        self.assertIsNotNone(profile1)
        self.assertIsNotNone(profile2)
        
        # Profiles should be from our library
        all_profiles = list(AIProfileLibrary.get_profiles().values())
        self.assertIn(profile1, all_profiles)
        self.assertIn(profile2, all_profiles)

    def test_get_balanced_team(self):
        """Test balanced team generation."""
        # Test small team
        team_2 = AIProfileLibrary.get_balanced_team(2)
        self.assertEqual(len(team_2), 2)
        
        # Test medium team
        team_4 = AIProfileLibrary.get_balanced_team(4)
        self.assertEqual(len(team_4), 4)
        
        # Test large team (more than unique personalities)
        team_10 = AIProfileLibrary.get_balanced_team(10)
        self.assertEqual(len(team_10), 10)
        
        # Check diversity in smaller teams (should prefer different personalities)
        personalities_in_team = [robot.personality for robot in team_4]
        unique_personalities = set(personalities_in_team)
        self.assertGreaterEqual(len(unique_personalities), min(4, len(AIPersonality)))

    def test_get_ai_robot_name(self):
        """Test AI robot name generation."""
        berserker = AIProfileLibrary.get_profile_by_name("berserker")
        name = get_ai_robot_name(berserker)
        
        self.assertIn(name, berserker.preferred_names)
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)

    def test_profile_strategic_diversity(self):
        """Test that profiles have diverse strategic approaches."""
        profiles = AIProfileLibrary.get_profiles()
        
        # Check that different profiles have different programs
        programs = [tuple(profile.program) for profile in profiles.values()]
        unique_programs = set(programs)
        
        # Should have diverse programs (at least 75% unique)
        self.assertGreater(len(unique_programs), len(programs) * 0.75)
        
        # Check emergency actions are diverse
        emergency_actions = [profile.emergency_action for profile in profiles.values()]
        unique_emergencies = set(emergency_actions)
        
        # Should have multiple different emergency strategies
        self.assertGreater(len(unique_emergencies), 1)

    def test_specific_profile_characteristics(self):
        """Test specific characteristics of key profiles."""
        # Berserker should be aggressive
        berserker = AIProfileLibrary.get_profile_by_name("berserker")
        self.assertIn("PM", berserker.program)  # Should pursue enemies
        self.assertTrue(any("FR" in instr or "FC" in instr for instr in berserker.program))  # Should fire
        
        # Guardian should be defensive
        guardian = AIProfileLibrary.get_profile_by_name("guardian")
        self.assertIn("MI", guardian.program)  # Should lay mines
        self.assertEqual(guardian.emergency_action, "IN")  # Should go invisible when in danger
        
        # Ghost should use invisibility
        ghost = AIProfileLibrary.get_profile_by_name("ghost")
        self.assertIn("IN", ghost.program)  # Should use invisibility
        self.assertEqual(ghost.emergency_action, "IN")  # Emergency should also be invisibility
        
        # Trapper should focus on mines
        trapper = AIProfileLibrary.get_profile_by_name("trapper")
        mine_count = trapper.program.count("MI")
        self.assertGreater(mine_count, 2)  # Should lay many mines


if __name__ == '__main__':
    unittest.main()