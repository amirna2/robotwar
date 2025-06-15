"""Game state management, turn processing, and win conditions."""

from typing import List, Dict, Optional, Tuple
from enum import Enum

from .robot import Robot, RobotStatus
from .arena import Arena
from .instructions import Instruction, InstructionType, InstructionSet


class GamePhase(Enum):
    SETUP = "setup"
    PROGRAMMING = "programming"
    BATTLE = "battle"
    FINISHED = "finished"


class GameState:
    """Manages overall game state, turns, and win conditions."""

    def __init__(self, arena_width: int = 20, arena_height: int = 20):
        self.arena = Arena(arena_width, arena_height)
        self.robots: List[Robot] = []
        self.phase = GamePhase.SETUP
        self.current_turn = 0
        self.max_turns = 1000  # Prevent infinite games
        self.winner_id: Optional[int] = None

        # Game configuration
        self.num_players = 1
        self.program_length = 20
        self.starting_energy = 1500
        self.num_obstacles = 20
        self.proximity_distance = 5  # Distance for PT (Proximity Test) instruction
        
        # Combat log for this turn
        self.combat_log: List[str] = []

    def add_robot(self, player_id: int, energy: Optional[int] = None, name: Optional[str] = None) -> Robot:
        """Add a robot to the game."""
        if energy is None:
            energy = self.starting_energy

        # Find empty position for robot
        used_positions = {robot.get_position() for robot in self.robots}
        x, y = self.arena.get_random_empty_position(used_positions)

        robot = Robot(player_id, x, y, energy, name)
        self.robots.append(robot)
        self.arena.robots[(x, y)] = robot

        return robot

    def get_living_robots(self) -> List[Robot]:
        """Get all robots that are still alive."""
        return [robot for robot in self.robots if robot.is_alive()]

    def setup_arena(self):
        """Generate obstacles in the arena."""
        # Get all robot positions to exclude from obstacle placement
        robot_positions = {robot.get_position() for robot in self.robots}
        self.arena.generate_obstacles(self.num_obstacles, robot_positions)

    def start_programming(self):
        """Transition to programming phase."""
        if self.phase == GamePhase.SETUP:
            self.phase = GamePhase.PROGRAMMING

    def start_battle(self):
        """Transition to battle phase."""
        if self.phase in [GamePhase.SETUP, GamePhase.PROGRAMMING]:
            self.phase = GamePhase.BATTLE
            self.current_turn = 0

    def execute_turn(self) -> bool:
        """Execute one turn of the battle. Returns True if game continues."""
        if self.phase != GamePhase.BATTLE:
            return False

        living_robots = self.get_living_robots()
        if len(living_robots) <= 1:
            self._determine_winner()
            return False

        if self.current_turn >= self.max_turns:
            self._determine_winner()
            return False

        # Clear combat log for this turn
        self.combat_log.clear()

        # Update robot states from previous turn first
        for robot in living_robots:
            robot.update_invisibility()

        # Execute all robot instructions simultaneously
        self._execute_robot_instructions(living_robots)

        # Advance program counters (but not for frozen robots)
        for robot in living_robots:
            if robot.can_execute():  # Only advance if robot can still execute instructions
                robot.advance_program_counter()

        self.current_turn += 1
        return True

    def _execute_robot_instructions(self, robots: List[Robot]):
        """Execute instructions for all robots simultaneously."""
        # TODO: This is a simplified version - needs full implementation
        # Will need to handle movement conflicts, attacks, etc.

        for robot in robots:
            if not robot.is_alive():
                continue

            # Skip frozen robots (energy preservation mode)
            if not robot.can_execute():
                continue

            instruction_str = robot.get_current_instruction()
            if not instruction_str:
                continue

            instruction = InstructionSet.parse_instruction(instruction_str)
            if not instruction:
                continue

            # Check energy cost - use emergency routine if can't afford instruction
            energy_cost = InstructionSet.get_energy_cost(instruction.type)
            if robot.energy < energy_cost or robot.energy <= robot.emergency_energy_threshold:
                if robot.emergency_action:
                    self._execute_emergency_routine(robot)
                else:
                    robot.status = RobotStatus.FROZEN  # No emergency action - freeze
                continue

            was_alive = robot.is_alive()
            
            if not robot.use_energy(energy_cost):
                continue  # Should not happen due to check above

            # Check if robot died from energy loss
            if was_alive and not robot.is_alive():
                self._handle_robot_death(robot)
                continue

            self._execute_single_instruction(robot, instruction)

    def _execute_single_instruction(self, robot: Robot, instruction: Instruction):
        """Execute a single instruction for a robot."""
        # This is a placeholder - needs full implementation
        instruction_type = instruction.type

        if instruction_type == InstructionType.DM:
            # Directed movement
            self._move_robot(robot, instruction.direction)
        elif instruction_type == InstructionType.RM:
            # Random movement
            direction = InstructionSet.get_random_direction()
            self._move_robot(robot, direction)
        elif instruction_type == InstructionType.IN:
            # Invisibility
            robot.set_invisible(1)
        elif instruction_type == InstructionType.MI:
            # Place mine
            self._place_mine(robot)
        elif instruction_type == InstructionType.PM:
            # Pursue nearest enemy
            target_direction = self._get_direction_to_nearest_enemy(robot)
            if target_direction:
                self._move_robot(robot, target_direction)
        elif instruction_type == InstructionType.AM:
            # Avoid nearest enemy (flee)
            flee_direction = self._get_direction_from_nearest_enemy(robot)
            if flee_direction:
                self._move_robot(robot, flee_direction)
        elif instruction_type == InstructionType.PT:
            # Proximity test with conditional execution: PT(action_if_true, action_if_false)
            self._execute_proximity_test_conditional(robot, instruction)
        elif instruction_type == InstructionType.FR:
            # Fire row - shoot left and right
            self._fire_row(robot)
        elif instruction_type == InstructionType.FC:
            # Fire column - shoot up and down
            self._fire_column(robot)

    def _move_robot(self, robot: Robot, direction):
        """Move robot in specified direction if possible."""
        if direction is None:
            return

        current_x, current_y = robot.get_position()
        dx, dy = self.arena.get_direction_offset(direction)
        new_x, new_y = current_x + dx, current_y + dy

        # Check if move is valid
        if not self.arena.is_passable(new_x, new_y):
            return

        # Check for robot collision
        if (new_x, new_y) in self.arena.robots:
            return  # Position occupied

        # Check for mines before moving - own mines block movement
        if self.arena.has_mine(new_x, new_y):
            mine_data = self.arena.trigger_mine(new_x, new_y)
            if mine_data:
                mine_id, damage = mine_data
                mine_owner = mine_id // 10  # Decode ownership from mine ID
                
                if mine_owner == robot.player_id:
                    # Own mine - put it back and block movement
                    self.arena.place_mine(new_x, new_y, robot.player_id, damage)
                    return  # Can't step on own mines
                else:
                    # Enemy mine - explode after moving
                    # Update robot position first
                    del self.arena.robots[(current_x, current_y)]
                    robot.set_position(new_x, new_y)
                    self.arena.robots[(new_x, new_y)] = robot
                    
                    # Apply mine damage
                    was_alive = robot.is_alive()
                    robot.take_damage(damage)
                    
                    # Check if robot died from mine damage
                    if was_alive and not robot.is_alive():
                        self._handle_robot_death(robot)
                    return

        # No mine - normal movement
        del self.arena.robots[(current_x, current_y)]
        robot.set_position(new_x, new_y)
        self.arena.robots[(new_x, new_y)] = robot

    def _place_mine(self, robot: Robot):
        """Place a mine at robot's current position."""
        x, y = robot.get_position()

        # Don't place mine if there's already one there
        if self.arena.has_mine(x, y):
            return

        # Place mine with standard damage
        damage = InstructionSet.get_damage(InstructionType.MI)
        self.arena.place_mine(x, y, robot.player_id, damage)

    def _determine_winner(self):
        """Determine the winner based on current game state."""
        living_robots = self.get_living_robots()

        if len(living_robots) == 0:
            # No survivors - no winner
            self.winner_id = None
        elif len(living_robots) == 1:
            # Last robot standing
            self.winner_id = living_robots[0].player_id
        else:
            # Multiple survivors - highest energy wins
            winner = max(living_robots, key=lambda r: r.energy)
            self.winner_id = winner.player_id

        self.phase = GamePhase.FINISHED

    def is_game_over(self) -> bool:
        """Check if the game is finished."""
        return self.phase == GamePhase.FINISHED

    def get_winner(self) -> Optional[int]:
        """Get the winner's player ID, or None if no winner."""
        return self.winner_id

    def get_game_stats(self) -> Dict:
        """Get current game statistics."""
        living_robots = self.get_living_robots()
        return {
            'turn': self.current_turn,
            'phase': self.phase.value,
            'living_robots': len(living_robots),
            'total_robots': len(self.robots),
            'winner': self.winner_id
        }

    def _find_nearest_enemy(self, robot: Robot) -> Optional[Robot]:
        """Find the nearest enemy robot to the given robot."""
        robot_x, robot_y = robot.get_position()
        nearest_enemy = None
        min_distance = float('inf')

        for other_robot in self.get_living_robots():
            # Skip self and invisible robots (undetectable for targeting)
            if other_robot.player_id == robot.player_id:
                continue
            if other_robot.status == RobotStatus.INVISIBLE:
                continue  # Invisible robots can't be targeted by PM/AM

            other_x, other_y = other_robot.get_position()
            distance = abs(robot_x - other_x) + abs(robot_y - other_y)  # Manhattan distance
            
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = other_robot

        return nearest_enemy

    def _get_direction_to_nearest_enemy(self, robot: Robot):
        """Get the best direction to move toward the nearest enemy."""
        nearest_enemy = self._find_nearest_enemy(robot)
        if not nearest_enemy:
            return None

        robot_x, robot_y = robot.get_position()
        enemy_x, enemy_y = nearest_enemy.get_position()

        return self.arena.get_move_towards(robot_x, robot_y, enemy_x, enemy_y)

    def _get_direction_from_nearest_enemy(self, robot: Robot):
        """Get the best direction to move away from the nearest enemy."""
        nearest_enemy = self._find_nearest_enemy(robot)
        if not nearest_enemy:
            return None

        robot_x, robot_y = robot.get_position()
        enemy_x, enemy_y = nearest_enemy.get_position()

        return self.arena.get_move_away(robot_x, robot_y, enemy_x, enemy_y)

    def _handle_robot_death(self, robot: Robot):
        """Handle robot death - place skull obstacle and remove from robots dict."""
        x, y = robot.get_position()
        
        # Remove robot from arena robots dict
        if (x, y) in self.arena.robots:
            del self.arena.robots[(x, y)]
        
        # Place dead robot (skull) as obstacle
        self.arena.place_dead_robot(x, y)

    def _execute_proximity_test_conditional(self, robot: Robot, pt_instruction: Instruction):
        """Execute PT conditional instruction: PT(action_if_true, action_if_false)."""
        if not pt_instruction.parameter or len(pt_instruction.parameter) != 2:
            return  # Invalid PT instruction format
        
        action_if_true, action_if_false = pt_instruction.parameter
        
        # Perform proximity test
        proximity_result = self._check_proximity(robot)
        
        # Choose action based on proximity result
        chosen_action_str = action_if_true if proximity_result else action_if_false
        
        # Parse and execute the chosen action
        chosen_instruction = InstructionSet.parse_instruction(chosen_action_str)
        if chosen_instruction:
            # Calculate energy cost for the chosen action (PT cost already deducted)
            action_cost = InstructionSet.get_energy_cost(chosen_instruction.type)
            
            # Use energy for PT + action (already used PT energy in main execution)
            if robot.use_energy(action_cost):
                self._execute_single_instruction(robot, chosen_instruction)

    def _check_proximity(self, robot: Robot) -> bool:
        """Check for enemy robots within configured distance with line-of-sight."""
        robot_x, robot_y = robot.get_position()
        
        # Check for enemies within proximity distance (invisible/frozen robots return FALSE)
        for other_robot in self.get_living_robots():
            if other_robot.player_id == robot.player_id:
                continue  # Skip self
            if other_robot.status in [RobotStatus.INVISIBLE, RobotStatus.FROZEN]:
                continue  # Invisible and frozen robots are not detected by PT
            
            other_x, other_y = other_robot.get_position()
            distance = abs(robot_x - other_x) + abs(robot_y - other_y)
            if distance <= self.proximity_distance:
                # Check line-of-sight - obstacles block detection
                if self._has_line_of_sight(robot_x, robot_y, other_x, other_y):
                    return True
        
        return False  # No enemies detected within range

    def _has_line_of_sight(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """Check if there's a clear line of sight between two positions."""
        # Special case: same position
        if from_x == to_x and from_y == to_y:
            return True
        
        # Use simple line traversal - check each step along the path
        dx = to_x - from_x
        dy = to_y - from_y
        
        # Get the number of steps (max of dx, dy)
        steps = max(abs(dx), abs(dy))
        
        # Calculate step increments
        x_step = dx / steps if steps > 0 else 0
        y_step = dy / steps if steps > 0 else 0
        
        # Check each position along the line (excluding start, including end)
        for i in range(1, steps + 1):
            x = from_x + round(x_step * i)
            y = from_y + round(y_step * i)
            
            # Check if position is valid and passable
            if not self.arena.is_valid_position(x, y):
                return False
            
            # For the target position, we don't check passability (robot can be there)
            if x == to_x and y == to_y:
                return True
                
            # For intermediate positions, check if passable
            if not self.arena.is_passable(x, y):
                return False
        
        return True

    def _execute_emergency_routine(self, robot: Robot):
        """Execute robot's emergency action (Circuit de Secours)."""
        if not robot.emergency_action:
            return
        
        emergency_instruction = InstructionSet.parse_instruction(robot.emergency_action)
        if not emergency_instruction:
            return
        
        # Check if robot can afford emergency action
        emergency_cost = InstructionSet.get_energy_cost(emergency_instruction.type)
        if robot.energy >= emergency_cost:
            was_alive = robot.is_alive()
            
            if robot.use_energy(emergency_cost):
                self._execute_single_instruction(robot, emergency_instruction)
                
                # Check if robot died from emergency action
                if was_alive and not robot.is_alive():
                    self._handle_robot_death(robot)
        else:
            # Can't even afford emergency action - freeze
            robot.status = RobotStatus.FROZEN

    def _fire_row(self, robot: Robot):
        """Fire horizontally in both directions from robot position."""
        robot_x, robot_y = robot.get_position()
        max_range = self.proximity_distance  # Limited by proximity detector range
        damage = InstructionSet.get_damage(InstructionType.FR)
        
        self.combat_log.append(f"{robot.name} fires FR from ({robot_x},{robot_y})")
        
        # Fire left (decreasing X)
        for distance in range(1, max_range + 1):
            target_x = robot_x - distance
            if not self.arena.is_valid_position(target_x, robot_y):
                break  # Out of bounds
            
            # Check for obstacle - blocks shot
            if not self.arena.is_passable(target_x, robot_y):
                break  # Shot blocked by obstacle
            
            # Check for robot target
            target_robot = self.arena.robots.get((target_x, robot_y))
            if target_robot and target_robot.player_id != robot.player_id:
                # Hit enemy robot (invisible robots can still be hit by area fire)
                was_alive = target_robot.is_alive()
                target_robot.take_damage(damage)
                
                # Log the hit
                status = "destroyed" if not target_robot.is_alive() else f"damaged for {damage}"
                self.combat_log.append(f"  → hits {target_robot.name} at ({target_x},{robot_y}) - {status}")
                
                if was_alive and not target_robot.is_alive():
                    self._handle_robot_death(target_robot)
                break  # Shot stops after hitting target
        
        # Fire right (increasing X)
        for distance in range(1, max_range + 1):
            target_x = robot_x + distance
            if not self.arena.is_valid_position(target_x, robot_y):
                break  # Out of bounds
            
            # Check for obstacle - blocks shot
            if not self.arena.is_passable(target_x, robot_y):
                break  # Shot blocked by obstacle
            
            # Check for robot target
            target_robot = self.arena.robots.get((target_x, robot_y))
            if target_robot and target_robot.player_id != robot.player_id:
                # Hit enemy robot
                was_alive = target_robot.is_alive()
                target_robot.take_damage(damage)
                
                # Log the hit
                status = "destroyed" if not target_robot.is_alive() else f"damaged for {damage}"
                self.combat_log.append(f"  → hits Robot {target_robot.player_id} at ({target_x},{robot_y}) - {status}")
                
                if was_alive and not target_robot.is_alive():
                    self._handle_robot_death(target_robot)
                break  # Shot stops after hitting target

    def _fire_column(self, robot: Robot):
        """Fire vertically in both directions from robot position."""
        robot_x, robot_y = robot.get_position()
        max_range = self.proximity_distance  # Limited by proximity detector range
        damage = InstructionSet.get_damage(InstructionType.FC)
        
        self.combat_log.append(f"{robot.name} fires FC from ({robot_x},{robot_y})")
        
        # Fire up (decreasing Y)
        for distance in range(1, max_range + 1):
            target_y = robot_y - distance
            if not self.arena.is_valid_position(robot_x, target_y):
                break  # Out of bounds
            
            # Check for obstacle - blocks shot
            if not self.arena.is_passable(robot_x, target_y):
                break  # Shot blocked by obstacle
            
            # Check for robot target
            target_robot = self.arena.robots.get((robot_x, target_y))
            if target_robot and target_robot.player_id != robot.player_id:
                # Hit enemy robot
                was_alive = target_robot.is_alive()
                target_robot.take_damage(damage)
                
                # Log the hit
                status = "destroyed" if not target_robot.is_alive() else f"damaged for {damage}"
                self.combat_log.append(f"  → hits {target_robot.name} at ({robot_x},{target_y}) - {status}")
                
                if was_alive and not target_robot.is_alive():
                    self._handle_robot_death(target_robot)
                break  # Shot stops after hitting target
        
        # Fire down (increasing Y)
        for distance in range(1, max_range + 1):
            target_y = robot_y + distance
            if not self.arena.is_valid_position(robot_x, target_y):
                break  # Out of bounds
            
            # Check for obstacle - blocks shot
            if not self.arena.is_passable(robot_x, target_y):
                break  # Shot blocked by obstacle
            
            # Check for robot target
            target_robot = self.arena.robots.get((robot_x, target_y))
            if target_robot and target_robot.player_id != robot.player_id:
                # Hit enemy robot
                was_alive = target_robot.is_alive()
                target_robot.take_damage(damage)
                if was_alive and not target_robot.is_alive():
                    self._handle_robot_death(target_robot)
                break  # Shot stops after hitting target
