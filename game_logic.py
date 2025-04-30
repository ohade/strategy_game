"""Module for handling core game logic and state updates."""

import math
from typing import List, Tuple, Optional, Union, Any


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
    if not hasattr(unit, 'state') or unit.state != "idle":
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
