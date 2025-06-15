"""Arena class - manages the game grid, obstacles, mines, and positioning."""

from typing import List, Tuple, Optional, Set
from enum import Enum
import random


class CellType(Enum):
    EMPTY = "empty"
    OBSTACLE = "obstacle" 
    MINE = "mine"
    DEAD_ROBOT = "dead_robot"


class Direction(Enum):
    N = (0, -1)
    NE = (1, -1)
    E = (1, 0)
    SE = (1, 1)
    S = (0, 1)
    SW = (-1, 1)
    W = (-1, 0)
    NW = (-1, -1)


class Arena:
    """Game arena with grid-based positioning and obstacles."""
    
    def __init__(self, width: int = 20, height: int = 20):
        self.width = width
        self.height = height
        self.grid = [[CellType.EMPTY for _ in range(width)] for _ in range(height)]
        self.mines = {}  # Position -> (owner_id, damage)
        self.robots = {}  # Position -> Robot
        
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is within arena bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_passable(self, x: int, y: int) -> bool:
        """Check if position can be moved to."""
        if not self.is_valid_position(x, y):
            return False
        cell_type = self.grid[y][x]
        return cell_type not in [CellType.OBSTACLE, CellType.DEAD_ROBOT]
    
    def place_obstacle(self, x: int, y: int):
        """Place an obstacle at position."""
        if self.is_valid_position(x, y):
            self.grid[y][x] = CellType.OBSTACLE
    
    def place_dead_robot(self, x: int, y: int):
        """Place a dead robot (skull) at position - becomes an obstacle."""
        if self.is_valid_position(x, y):
            self.grid[y][x] = CellType.DEAD_ROBOT
    
    def place_mine(self, x: int, y: int, owner_id: int, damage: int = 200):
        """Place a mine at position."""
        if self.is_valid_position(x, y):
            mine_id = owner_id * 10  # Encode ownership: Player 1 = 10, Player 2 = 20, etc.
            self.mines[(x, y)] = (mine_id, damage)
    
    def has_mine(self, x: int, y: int) -> bool:
        """Check if there's a mine at position."""
        return (x, y) in self.mines
    
    def trigger_mine(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Trigger mine at position. Returns (mine_id, damage) or None."""
        pos = (x, y)
        if pos in self.mines:
            mine_data = self.mines[pos]
            del self.mines[pos]
            return mine_data
        return None
    
    def get_direction_offset(self, direction: Direction) -> Tuple[int, int]:
        """Get x,y offset for a direction."""
        return direction.value
    
    def get_adjacent_positions(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all valid adjacent positions (8-directional)."""
        adjacent = []
        for direction in Direction:
            dx, dy = direction.value
            new_x, new_y = x + dx, y + dy
            if self.is_valid_position(new_x, new_y):
                adjacent.append((new_x, new_y))
        return adjacent
    
    def get_random_empty_position(self, exclude_positions: Set[Tuple[int, int]] = None) -> Tuple[int, int]:
        """Get a random empty position, optionally excluding certain positions."""
        if exclude_positions is None:
            exclude_positions = set()
        
        attempts = 0
        max_attempts = 1000
        
        while attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            if (x, y) not in exclude_positions and self.is_passable(x, y):
                return (x, y)
            
            attempts += 1
        
        # Fallback: find first available position
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in exclude_positions and self.is_passable(x, y):
                    return (x, y)
        
        raise Exception("No empty positions available in arena")
    
    def generate_obstacles(self, count: int, exclude_positions: Set[Tuple[int, int]] = None):
        """Randomly place obstacles in the arena."""
        if exclude_positions is None:
            exclude_positions = set()
        
        placed = 0
        while placed < count:
            try:
                x, y = self.get_random_empty_position(exclude_positions)
                self.place_obstacle(x, y)
                exclude_positions.add((x, y))
                placed += 1
            except Exception:
                break  # No more positions available
    
    def find_nearest_robot_position(self, from_x: int, from_y: int, 
                                   exclude_positions: Set[Tuple[int, int]] = None) -> Optional[Tuple[int, int]]:
        """Find nearest robot position using Manhattan distance."""
        if exclude_positions is None:
            exclude_positions = set()
        
        nearest_pos = None
        min_distance = float('inf')
        
        for pos in self.robots:
            if pos not in exclude_positions:
                x, y = pos
                distance = abs(x - from_x) + abs(y - from_y)
                if distance < min_distance:
                    min_distance = distance
                    nearest_pos = pos
        
        return nearest_pos
    
    def get_move_towards(self, from_x: int, from_y: int, to_x: int, to_y: int) -> Optional[Direction]:
        """Get best direction to move towards target."""
        dx = to_x - from_x
        dy = to_y - from_y
        
        if dx == 0 and dy == 0:
            return None
        
        # Normalize to -1, 0, or 1
        dx = max(-1, min(1, dx))
        dy = max(-1, min(1, dy))
        
        # Find matching direction
        for direction in Direction:
            if direction.value == (dx, dy):
                return direction
        
        return None
    
    def get_move_away(self, from_x: int, from_y: int, avoid_x: int, avoid_y: int) -> Optional[Direction]:
        """Get best direction to move away from target."""
        # Invert the direction
        target_direction = self.get_move_towards(from_x, from_y, avoid_x, avoid_y)
        if target_direction is None:
            return None
        
        dx, dy = target_direction.value
        opposite_offset = (-dx, -dy)
        
        # Find matching direction
        for direction in Direction:
            if direction.value == opposite_offset:
                return direction
        
        return None