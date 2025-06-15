#!/usr/bin/env python3
"""Simple test script for the programming interface."""

from robot_war.ui.programming import program_robot

def main():
    print("Testing Robot Programming Interface")
    print("=" * 40)
    
    # Test programming interface
    program = program_robot("TestRobot", max_steps=5, starting_energy=1500)
    
    print(f"\nFinal program: {program}")

if __name__ == "__main__":
    main()