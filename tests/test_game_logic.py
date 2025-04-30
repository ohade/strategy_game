"""Tests for the core game logic and state updates."""

import pytest
import math

from game_logic import update_unit_movement, find_closest_target, update_targeting
from effects import AttackEffect  # Import for attack effect test

# --- Mocks --- #

class MockUnit:
    """Mock Unit class for testing game logic."""
    def __init__(self, x: float, y: float, unit_id: int, speed: float = 100.0, attack_range: float = 50.0,
                 attack_power: int = 10, attack_cooldown: float = 1.0, hp: int = 100):
        self.world_x: float = x
        self.world_y: float = y
        self.draw_x: float = x  # For attack effect generation
        self.draw_y: float = y
        self.id: int = unit_id
        self.speed: float = speed
        self.destination: tuple[float, float] | None = None
        self.move_target = None  # Could be another unit or a point
        self.state = "idle"  # idle, moving, attacking, destroyed
        self.attack_range = attack_range
        self.attack_power = attack_power
        self.attack_cooldown = attack_cooldown
        self.current_attack_cooldown = 0.0
        self.hp = hp
        self.type = 'friendly'  # Default, can be changed in tests
        self.damaged_by = None  # Track who damaged this unit
        self.damage_amount = 0  # Track damage amount for tests
        
    def take_damage(self, amount: int, attacker=None):
        """Mock take_damage to track damage for tests."""
        self.hp -= amount
        self.damaged_by = attacker
        self.damage_amount = amount
        return self.hp <= 0  # Return True if destroyed

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


def test_check_attack_range():
    """Test that check_attack_range correctly determines if units are in range."""
    # This function doesn't exist yet - it will be implemented in game_logic.py
    from game_logic import check_attack_range
    
    attacker = MockUnit(x=0, y=0, unit_id=1, attack_range=50)
    target_in_range = MockUnit(x=40, y=0, unit_id=2)    # Distance 40, within range
    target_at_edge = MockUnit(x=50, y=0, unit_id=3)     # Distance 50, exactly at range
    target_out_of_range = MockUnit(x=60, y=0, unit_id=4) # Distance 60, outside range
    
    assert check_attack_range(attacker, target_in_range) is True
    assert check_attack_range(attacker, target_at_edge) is True
    assert check_attack_range(attacker, target_out_of_range) is False
    
    # Test with a different range
    attacker.attack_range = 30
    assert check_attack_range(attacker, target_in_range) is False


def test_perform_attack():
    """Test that perform_attack correctly applies damage and generates effects."""
    # This function doesn't exist yet - it will be implemented in game_logic.py
    from game_logic import perform_attack
    
    attacker = MockUnit(x=0, y=0, unit_id=1, attack_power=15, attack_cooldown=1.0)
    attacker.type = 'friendly'
    attacker.current_attack_cooldown = 0.0  # Ready to attack
    
    target = MockUnit(x=40, y=0, unit_id=2, hp=100)
    target.type = 'enemy'
    
    # Perform attack and check results
    effect = perform_attack(attacker, target, dt=0.1)
    
    # Check damage was applied
    assert target.damaged_by == attacker
    assert target.damage_amount == 15
    assert target.hp == 85
    
    # Check cooldown was reset
    assert attacker.current_attack_cooldown == attacker.attack_cooldown
    
    # Check effect was generated
    assert isinstance(effect, AttackEffect)
    assert effect.start_pos == (attacker.draw_x, attacker.draw_y)
    assert effect.end_pos == (target.draw_x, target.draw_y)


def test_update_unit_attack():
    """Test the full attack update logic."""
    # This function doesn't exist yet - it will be implemented in game_logic.py
    from game_logic import update_unit_attack
    
    # Test case 1: Unit with no target
    unit1 = MockUnit(x=0, y=0, unit_id=1)
    unit1.state = "idle"
    effect = update_unit_attack(unit1, 0.1)
    assert effect is None
    
    # Test case 2: Unit targeting another unit but out of range
    attacker = MockUnit(x=0, y=0, unit_id=2, attack_range=50)
    attacker.state = "attacking"
    target = MockUnit(x=100, y=0, unit_id=3) # Out of range
    attacker.move_target = target
    
    effect = update_unit_attack(attacker, 0.1)
    
    # Should switch to moving state to chase
    assert attacker.state == "moving"
    assert effect is None
    
    # Test case 3: Unit attacking with cooldown
    attacker = MockUnit(x=0, y=0, unit_id=4, attack_range=50, attack_cooldown=1.0)
    attacker.state = "attacking"
    attacker.current_attack_cooldown = 0.5  # Not ready yet
    target = MockUnit(x=40, y=0, unit_id=5) # In range
    attacker.move_target = target
    
    effect = update_unit_attack(attacker, 0.1)
    
    # No attack yet, just cooldown decrease
    assert target.damaged_by is None
    assert attacker.current_attack_cooldown == 0.4
    assert effect is None
    
    # Test case 4: Unit ready to attack
    attacker = MockUnit(x=0, y=0, unit_id=6, attack_range=50, attack_cooldown=1.0)
    attacker.state = "attacking"
    attacker.current_attack_cooldown = 0.0  # Ready to attack
    target = MockUnit(x=40, y=0, unit_id=7) # In range
    attacker.move_target = target
    
    effect = update_unit_attack(attacker, 0.1)
    
    # Should attack
    assert target.damaged_by == attacker
    assert attacker.current_attack_cooldown == 1.0
    assert isinstance(effect, AttackEffect)
