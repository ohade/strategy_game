"""Tests for the core game logic and state updates."""

import pytest
import math

from game_logic import update_unit_movement, find_closest_target, update_targeting

# --- Mocks --- #

class MockUnit:
    """Mock Unit class for testing game logic."""
    def __init__(self, x: float, y: float, unit_id: int, speed: float = 100.0):
        self.world_x: float = x
        self.world_y: float = y
        self.id: int = unit_id
        self.speed: float = speed
        self.destination: tuple[float, float] | None = None

    def __eq__(self, other):
        if not isinstance(other, MockUnit):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

# --- Tests --- #

def test_unit_moves_towards_destination():
    """Test that a unit moves closer to its destination after an update."""
    unit = MockUnit(x=0, y=0, unit_id=1, speed=100)
    unit.destination = (300, 400) # Target is 500 units away (3-4-5 triangle)
    dt = 0.1 # Delta time in seconds

    start_pos = (unit.world_x, unit.world_y)
    start_dist = math.hypot(unit.destination[0] - start_pos[0], unit.destination[1] - start_pos[1])

    # Calculate expected movement for verification
    expected_dist_moved = unit.speed * dt
    direction_x = (unit.destination[0] - start_pos[0]) / start_dist
    direction_y = (unit.destination[1] - start_pos[1]) / start_dist
    expected_x = start_pos[0] + direction_x * expected_dist_moved
    expected_y = start_pos[1] + direction_y * expected_dist_moved

    # Call the actual game logic function
    update_unit_movement(unit, dt)

    end_pos = (unit.world_x, unit.world_y)
    end_dist = math.hypot(unit.destination[0] - end_pos[0], unit.destination[1] - end_pos[1])

    # Check if the unit moved approximately the correct distance
    assert math.isclose(unit.world_x, expected_x)
    assert math.isclose(unit.world_y, expected_y)
    # Check if the distance to the destination decreased by the expected amount
    assert math.isclose(start_dist - end_dist, expected_dist_moved)


def test_find_closest_target():
    """Test that find_closest_target returns the closest unit."""
    unit = MockUnit(x=0, y=0, unit_id=1)
    target1 = MockUnit(x=100, y=0, unit_id=2)
    target2 = MockUnit(x=50, y=0, unit_id=3)
    target3 = MockUnit(x=200, y=0, unit_id=4)
    
    targets = [target1, target2, target3]
    
    # Target2 should be closest (at distance 50)
    closest = find_closest_target(unit, targets)
    assert closest.id == target2.id
    
    # Empty list should return None
    assert find_closest_target(unit, []) is None


def test_update_targeting():
    """Test that update_targeting sets the correct target based on unit type."""
    friendly_unit = MockUnit(x=0, y=0, unit_id=1)
    friendly_unit.type = 'friendly'
    friendly_unit.state = 'idle'
    friendly_unit.set_target_called = False
    friendly_unit.last_target = None
    
    def mock_set_target(target):
        friendly_unit.set_target_called = True
        friendly_unit.last_target = target
        
    friendly_unit.set_target = mock_set_target
    
    enemy_unit = MockUnit(x=100, y=0, unit_id=2)
    enemy_unit.type = 'enemy'
    
    # Test friendly unit targeting enemy
    update_targeting(friendly_unit, [friendly_unit], [enemy_unit])
    
    assert friendly_unit.set_target_called
    assert friendly_unit.last_target.id == enemy_unit.id
