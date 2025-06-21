"""AI Robot Profiles with Strategic Programming Patterns.

This module defines various AI robot personalities with distinct strategic approaches,
programming patterns, and emergency behaviors. Each profile represents a different
playstyle to provide varied and challenging opponents.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class AIPersonality(Enum):
    """AI personality types defining strategic approaches."""

    BERSERKER = 'berserker'
    GUARDIAN = 'guardian'
    HUNTER = 'hunter'
    GHOST = 'ghost'
    WANDERER = 'wanderer'
    SNIPER = 'sniper'
    TRAPPER = 'trapper'
    SURVIVOR = 'survivor'


@dataclass
class AIProfile:
    """Complete AI robot profile with strategy and personality."""
    name: str
    personality: AIPersonality
    description: str
    program: List[str]
    emergency_action: str
    energy_threshold: int
    preferred_names: List[str]
    strategy_notes: str


class AIProfileLibrary:
    """Library of AI robot profiles with varied strategic approaches."""
    
    @staticmethod
    def get_profiles() -> Dict[str, AIProfile]:
        """Get all available AI profiles."""
        return {
            "berserker": AIProfile(
                name="Berserker",
                personality=AIPersonality.BERSERKER,
                description="Aggressive front-line fighter, charges enemies with overwhelming force",
                program=[
                    "PT(PM, RM)",      # If enemy nearby, pursue; else random move
                    "PT(FR, FC)",      # If enemy nearby, fire row; else fire column
                    "PM",              # Always pursue nearest enemy
                    "PT(FR, PM)",      # If enemy nearby, fire row; else pursue
                    "RM",              # Random movement to avoid patterns
                    "PM",              # Pursue again
                    "FR",              # Fire row
                    "FC"               # Fire column
                ],
                emergency_action="FR",
                energy_threshold=300,
                preferred_names=["Destructor", "Rampage", "Fury", "Blitz", "Crusher"],
                strategy_notes="High-energy consumption, direct confrontation approach"
            ),
            
            "guardian": AIProfile(
                name="Guardian",
                personality=AIPersonality.GUARDIAN,
                description="Defensive specialist, uses mines and positioning to control territory",
                program=[
                    "MI",              # Lay mine immediately
                    "PT(AM, RM)",      # If enemy nearby, avoid; else random move
                    "DM(N)",           # Move north (territorial control)
                    "MI",              # Another mine
                    "DM(E)",           # Move east
                    "PT(IN, MI)",      # If enemy nearby, go invisible; else lay mine
                    "DM(S)",           # Move south
                    "MI",              # More mines
                    "DM(W)",           # Move west (completing patrol)
                    "PT(FR, FC)"       # Fire if enemy detected
                ],
                emergency_action="IN",
                energy_threshold=400,
                preferred_names=["Fortress", "Sentinel", "Aegis", "Bastion", "Citadel"],
                strategy_notes="Territory control through mine placement and defensive positioning"
            ),
            
            "hunter": AIProfile(
                name="Hunter",
                personality=AIPersonality.HUNTER,
                description="Tactical predator, uses stealth and precision strikes",
                program=[
                    "PT(PM, RM)",      # If enemy detected, pursue; else scout
                    "IN",              # Go invisible for stealth approach
                    "PM",              # Move toward target while invisible
                    "PT(FR, FC)",      # Fire when in range
                    "AM",              # Retreat after attack
                    "PT(PM, RM)",      # Re-engage or reposition
                    "MI",              # Lay trap mine
                    "PM"               # Resume hunting
                ],
                emergency_action="AM",
                energy_threshold=500,
                preferred_names=["Stalker", "Predator", "Shadow", "Viper", "Phantom"],
                strategy_notes="Hit-and-run tactics with invisibility and precise targeting"
            ),
            
            "ghost": AIProfile(
                name="Ghost",
                personality=AIPersonality.GHOST,
                description="Stealth specialist, masters invisibility and surprise attacks",
                program=[
                    "IN",              # Start invisible
                    "RM",              # Random movement while invisible
                    "PT(PM, RM)",      # Pursue if enemy nearby, else keep moving
                    "IN",              # Invisible again
                    "PT(FR, FC)",      # Strike when opportunity arises
                    "AM",              # Retreat after attack
                    "IN",              # Back to stealth
                    "RM"               # Random movement
                ],
                emergency_action="IN",
                energy_threshold=600,
                preferred_names=["Wraith", "Specter", "Mirage", "Echo", "Shade"],
                strategy_notes="Maximum stealth utilization with unpredictable movement patterns"
            ),
            
            "wanderer": AIProfile(
                name="Wanderer",
                personality=AIPersonality.WANDERER,
                description="Unpredictable explorer, uses chaos and opportunistic strikes",
                program=[
                    "RM",              # Random movement
                    "PT(MI, RM)",      # Randomly lay mine or keep moving
                    "RM",              # More random movement
                    "PT(FR, FC)",      # Fire if enemy detected
                    "RM",              # Random movement
                    "PT(PM, AM)",      # Pursue or avoid based on proximity
                    "RM",              # Random movement
                    "PT(IN, MI)"       # Randomly go invisible or lay mine
                ],
                emergency_action="RM",
                energy_threshold=250,
                preferred_names=["Nomad", "Drifter", "Chaos", "Rogue", "Vagrant"],
                strategy_notes="Unpredictable behavior makes it hard to counter"
            ),
            
            "sniper": AIProfile(
                name="Sniper",
                personality=AIPersonality.SNIPER,
                description="Long-range specialist, focuses on positioning and precise shots",
                program=[
                    "PT(FR, FC)",      # Fire if enemy in range
                    "DM(N)",           # Move to high ground (north)
                    "PT(FR, FC)",      # Fire again
                    "DM(E)",           # Reposition east
                    "PT(FR, FC)",      # Fire
                    "PT(AM, RM)",      # Avoid if enemy too close, else random move
                    "PT(FR, FC)",      # Fire
                    "MI"               # Lay defensive mine
                ],
                emergency_action="AM",
                energy_threshold=350,
                preferred_names=["Marksman", "Eagle", "Longshot", "Precision", "Crosshair"],
                strategy_notes="Maintains distance and focuses on accurate long-range attacks"
            ),
            
            "trapper": AIProfile(
                name="Trapper",
                personality=AIPersonality.TRAPPER,
                description="Mine warfare expert, creates deadly obstacle courses",
                program=[
                    "MI",              # Lay mine
                    "DM(N)",           # Move north
                    "MI",              # Another mine
                    "DM(E)",           # Move east
                    "MI",              # More mines
                    "DM(S)",           # Move south
                    "MI",              # Even more mines
                    "DM(W)",           # Move west
                    "PT(AM, RM)",      # Avoid enemies or random move
                    "MI"               # Final mine
                ],
                emergency_action="MI",
                energy_threshold=800,
                preferred_names=["Minefield", "Bombshell", "Tripwire", "Demolitionist", "Boomer"],
                strategy_notes="Creates mine mazes to control battlefield geography"
            ),
            
            "survivor": AIProfile(
                name="Survivor",
                personality=AIPersonality.SURVIVOR,
                description="Endurance specialist, focuses on outlasting opponents",
                program=[
                    "PT(AM, RM)",      # Avoid enemies or move randomly
                    "PT(IN, MI)",      # Go invisible if threatened, else lay mine
                    "AM",              # Always try to avoid confrontation
                    "PT(AM, RM)",      # Avoid or random movement
                    "MI",              # Lay defensive mine
                    "AM",              # Keep avoiding
                    "PT(FR, FC)",      # Only fire if absolutely necessary
                    "AM"               # Return to avoidance
                ],
                emergency_action="AM",
                energy_threshold=200,
                preferred_names=["Endurance", "Turtle", "Hermit", "Pacifist", "Outlast"],
                strategy_notes="Conservative energy management and conflict avoidance"
            )
        }
    
    @staticmethod
    def get_random_profile() -> AIProfile:
        """Get a random AI profile."""
        profiles = AIProfileLibrary.get_profiles()
        return random.choice(list(profiles.values()))
    
    @staticmethod
    def get_profile_by_name(name: str) -> Optional[AIProfile]:
        """Get specific AI profile by name."""
        profiles = AIProfileLibrary.get_profiles()
        return profiles.get(name.lower())
    
    @staticmethod
    def get_profile_names() -> List[str]:
        """Get list of all available profile names."""
        return list(AIProfileLibrary.get_profiles().keys())
    
    @staticmethod
    def get_balanced_team(num_robots: int) -> List[AIProfile]:
        """Get a balanced team of AI profiles for varied gameplay."""
        profiles = list(AIProfileLibrary.get_profiles().values())
        
        # Ensure diversity by picking different personality types
        selected = []
        personalities_used = set()
        
        # First pass: pick one of each personality type
        for profile in profiles:
            if len(selected) >= num_robots:
                break
            if profile.personality not in personalities_used:
                selected.append(profile)
                personalities_used.add(profile.personality)
        
        # Second pass: fill remaining slots randomly
        while len(selected) < num_robots:
            profile = random.choice(profiles)
            selected.append(profile)
        
        return selected[:num_robots]


def get_ai_robot_name(profile: AIProfile) -> str:
    """Generate a name for an AI robot based on its profile."""
    return random.choice(profile.preferred_names)


def validate_ai_program(program: List[str]) -> bool:
    """Validate that an AI program uses valid instructions."""
    valid_instructions = {
        'DM', 'RM', 'PM', 'AM', 'MI', 'IN', 'FR', 'FC', 'PT'
    }
    
    for instruction in program:
        # Handle PT conditional format: PT(action_if_true, action_if_false)
        if instruction.startswith('PT('):
            continue
        # Handle DM directional format: DM(direction)
        elif instruction.startswith('DM('):
            continue
        # Check basic instruction
        elif instruction not in valid_instructions:
            return False
    
    return True