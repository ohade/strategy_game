"""Module for handling core game logic and state updates."""

import math
from typing import List, Optional, Any, Tuple

# These will be used for attack effect color
BLUE = (0, 0, 255)
RED = (255, 0, 0)


def update_unit_movement(unit, dt: float) -> None:
    """Updates a unit's position based on its destination and speed.
    
    Args:
        unit: The unit to update (must have world_x, world_y, speed attributes 
              and a destination attribute which is either None or a (x,y) tuple)
        dt: Delta time in seconds
    """
    # Skip if no destination
    if not hasattr(unit, 'destination') or unit.destination is None:
        return
    
    # Get current position and destination
    current_x, current_y = unit.world_x, unit.world_y
    target_x, target_y = unit.destination
    
    # Calculate vector to destination
    vector_x = target_x - current_x
    vector_y = target_y - current_y
    distance = math.hypot(vector_x, vector_y)
    
    # If already at destination (or very close), stop
    if distance < 5:
        return
    
    # Calculate movement vector based on speed and delta time
    speed = unit.speed * dt
    if speed > distance:  # Don't overshoot
        speed = distance
        
    # Move towards destination
    if distance > 0:  # Avoid division by zero
        move_vector_x = (vector_x / distance) * speed
        move_vector_y = (vector_y / distance) * speed
        unit.world_x += move_vector_x
        unit.world_y += move_vector_y


def find_closest_target(unit, potential_targets: List[Any]) -> Optional[Any]:
    """Find the closest target from a list of potential targets.
    
    Args:
        unit: The unit looking for a target (must have world_x and world_y attributes)
        potential_targets: List of potential targets (must have world_x and world_y attributes)
        
    Returns:
        The closest target or None if the list is empty
    """
    if not potential_targets:
        return None
        
    closest_target = None
    closest_distance = float('inf')
    
    for target in potential_targets:
        distance = math.hypot(target.world_x - unit.world_x, target.world_y - unit.world_y)
        if distance < closest_distance:
            closest_target = target
            closest_distance = distance
            
    return closest_target


def update_targeting(unit, friendly_units: List[Any], enemy_units: List[Any]) -> None:
    """Update a unit's target based on its type and nearby units.
    
    Args:
        unit: The unit to update targeting for (must have type attribute)
        friendly_units: List of friendly units
        enemy_units: List of enemy units
    """
    # Skip if unit is not idle
    if unit.state != "idle":
        return
        
    # Determine appropriate targets based on unit type
    if unit.type == 'enemy':
        potential_targets = friendly_units
    elif unit.type == 'friendly':
        potential_targets = enemy_units
    else:
        return  # Unknown unit type
        
    closest_target = find_closest_target(unit, potential_targets)
    
    # If a target was found, set it as the unit's target
    if closest_target and hasattr(unit, 'set_target'):
        unit.set_target(closest_target)


def check_attack_range(attacker: Any, target: Any) -> bool:
    """Check if target is within attacker's attack range.
    
    Args:
        attacker: The attacking unit (must have world_x, world_y, and attack_range attributes)
        target: The target unit (must have world_x and world_y attributes)
        
    Returns:
        bool: True if target is within attack range, False otherwise
    """
    if not hasattr(attacker, 'attack_range'):
        return False
        
    distance = math.hypot(target.world_x - attacker.world_x, 
                          target.world_y - attacker.world_y)
    return distance <= attacker.attack_range


def perform_attack(attacker: Any, target: Any, dt: float) -> Optional[Any]:
    """Perform an attack from one unit to another, applying damage and generating effects.
    
    Args:
        attacker: The attacking unit (must have attack_power, attack_cooldown attributes)
        target: The target unit (must have take_damage method)
        dt: Delta time in seconds
        
    Returns:
        Optional[AttackEffect]: An attack effect if generated, None otherwise
    """
    from effects import AttackEffect  # Import here to avoid circular imports
    
    # Reset attacker's cooldown
    attacker.current_attack_cooldown = attacker.attack_cooldown
    
    # Apply damage to target
    target.take_damage(attacker.attack_power, attacker)
    
    # Create visual effect
    attack_color = BLUE if attacker.type == 'friendly' else RED
    start_pos = (attacker.draw_x, attacker.draw_y)
    end_pos = (target.draw_x, target.draw_y)
    
    return AttackEffect(start_pos, end_pos, color=attack_color, duration=0.15)


def update_unit_attack(unit: Any, dt: float) -> Optional[Any]:
    """Update unit's attack state, handling target validity, range, cooldown, and attacks.
    
    Args:
        unit: The unit to update attack for (must have state, move_target attributes)
        dt: Delta time in seconds
        
    Returns:
        Optional[AttackEffect]: An attack effect if one was generated, None otherwise
    """
    # Only process units in attacking state
    if not hasattr(unit, 'state') or unit.state != "attacking":
        return None
        
    # Make sure target exists and is a valid unit
    if not hasattr(unit, 'move_target') or unit.move_target is None:
        unit.state = "idle"
        return None
        
    target = unit.move_target
    
    # Check if target has been destroyed
    if hasattr(target, 'hp') and target.hp <= 0:
        unit.state = "idle"
        unit.move_target = None
        unit.current_attack_cooldown = 0.0  # Reset cooldown
        return None
        
    # Check if target is in range
    if not check_attack_range(unit, target):
        # Target out of range, start chasing
        unit.state = "moving"
        unit.current_attack_cooldown = 0.0  # Reset cooldown
        return None
        
    # Target in range, handle cooldown
    unit.current_attack_cooldown -= dt
    
    # Ready to attack
    if unit.current_attack_cooldown <= 0:
        return perform_attack(unit, target, dt)
        
    return None
