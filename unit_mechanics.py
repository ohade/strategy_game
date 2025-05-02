"""Module for unit-specific mechanics including movement and combat functions."""

import math
import random
from typing import Any, Optional

# These will be used for attack effect color (copied from game_logic.py)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

def update_unit_attack(unit: Any, dt: float) -> Optional[Any]:
    """Update unit's attack state, handling target validity, range, cooldown, and attacks.
    
    Args:
        unit: The unit to update attack for (must have state, move_target attributes)
        dt: Delta time in seconds
        
    Returns:
        Optional[AttackEffect]: An attack effect if one was generated, None otherwise
    """
    # Skip if no target or unit is not in attacking state
    if unit.state != "attacking" or not hasattr(unit, "move_target") or unit.move_target is None:
        return None
    
    # Cast the target for clarity
    target = unit.move_target
    
    # First, verify target still exists and has health
    if not hasattr(target, "hp") or target.hp <= 0:
        unit.move_target = None
        unit.state = "idle"
        return None
    
    # Check if in range to attack
    distance = math.hypot(target.world_x - unit.world_x, target.world_y - unit.world_y)
    
    if distance <= unit.attack_range:
        # We're close enough to attack
        if unit.state != "attacking":
            unit.state = "attacking"
        
        # Handle attack cooldown
        if unit.current_attack_cooldown <= 0:
            # Rotate towards target
            target_angle = calculate_rotation(unit.world_x, unit.world_y, target.world_x, target.world_y)
            unit.rotation = apply_rotation_inertia(unit.rotation, target_angle, 360)  # Fast rotation during attack
            
            # Perform the attack and get any generated effects
            attack_color = BLUE if unit.type == "friendly" else RED
            
            # Reduce target health
            damage_amount = unit.attack_power
            target.take_damage(damage_amount, unit)
            
            # Reset cooldown timer
            unit.current_attack_cooldown = unit.attack_cooldown
            
            # Create an attack line effect if the target is still alive
            if target.hp > 0:
                # This assumes AttackEffect is imported at the top level where this function is called
                # from the correct module to avoid another circular import
                from effects import AttackEffect
                return AttackEffect(
                    (unit.world_x, unit.world_y),  # start_pos as tuple
                    (target.world_x, target.world_y),  # end_pos as tuple
                    attack_color,  # color
                    0.4  # duration in seconds
                )
        else:
            # Cooldown still active, reduce timer
            unit.current_attack_cooldown -= dt
    else:
        # Move closer to target if out of range
        # Store the destination so unit will move toward target
        unit.destination = (target.world_x, target.world_y)
        
        # If state is attacking but we're too far, change to moving
        if unit.state == "attacking":
            unit.state = "moving"
    
    return None  # No attack effect generated this update


def calculate_rotation(start_x: float, start_y: float, target_x: float, target_y: float) -> float:
    """Calculate the rotation angle (in degrees) from start point to target point.
    
    The angle is calculated counterclockwise from the positive x-axis (east).
    
    Args:
        start_x: X-coordinate of the starting point
        start_y: Y-coordinate of the starting point
        target_x: X-coordinate of the target point
        target_y: Y-coordinate of the target point
        
    Returns:
        Angle in degrees (0-360) between the points
    """
    # Get vector from start to target
    dx = target_x - start_x
    dy = target_y - start_y
    
    # Calculate angle in radians, then convert to degrees
    radians = math.atan2(dy, dx)
    degrees = math.degrees(radians)
    
    # Convert from [-180, 180] range to [0, 360]
    if degrees < 0:
        degrees += 360
        
    return degrees


def apply_rotation_inertia(current_angle: float, target_angle: float, max_rotation_speed: float) -> float:
    """Gradually rotate from current angle towards target angle with inertia.
    
    This function limits rotation speed to simulate realistic turning.
    It takes the shortest path around the circle (clockwise or counterclockwise).
    
    Args:
        current_angle: Current rotation angle in degrees
        target_angle: Target rotation angle in degrees
        max_rotation_speed: Maximum rotation speed in degrees per update
        
    Returns:
        New rotation angle after applying inertia
    """
    # Normalize angles to [0, 360) range
    current_angle = current_angle % 360
    target_angle = target_angle % 360
    
    # Calculate angle difference, considering the shorter path
    diff = (target_angle - current_angle) % 360
    if diff > 180:
        diff = diff - 360  # Take shorter path (negative value = clockwise)
    
    # Apply speed limit to rotation
    if abs(diff) <= max_rotation_speed:
        # If we can reach target in this update, go there directly
        return target_angle
    else:
        # Move at max speed towards target
        direction = 1 if diff > 0 else -1
        new_angle = (current_angle + (direction * max_rotation_speed)) % 360
        return new_angle


def smooth_movement(unit: Any, target_x: float, target_y: float, dt: float) -> None:
    """Apply smooth movement with rotation inertia and acceleration/deceleration.
    
    This function updates a unit's position, rotation, and velocity to move towards
    a target position in a realistic way, considering inertia and gradual turning.
    
    Args:
        unit: The unit to move (must have appropriate attributes)
        target_x: X-coordinate of the target position
        target_y: Y-coordinate of the target position
        dt: Delta time in seconds
    """
    # Calculate target rotation based on direction to target
    target_angle = calculate_rotation(unit.world_x, unit.world_y, target_x, target_y)
    
    # Initialize velocity components if they don't exist
    if not hasattr(unit, 'velocity_x'):
        unit.velocity_x = 0.0
    if not hasattr(unit, 'velocity_y'):
        unit.velocity_y = 0.0
        
    # Define rotation speed (degrees per second)
    if not hasattr(unit, 'max_rotation_speed'):
        max_rotation_speed = 180.0  # Default: 180 degrees per second
    else:
        max_rotation_speed = unit.max_rotation_speed
        
    # Apply rotation with inertia, scaled by time
    max_rotation_this_frame = max_rotation_speed * dt
    unit.rotation = apply_rotation_inertia(unit.rotation, target_angle, max_rotation_this_frame)
    
    # Calculate distance to target
    distance_to_target = math.hypot(target_x - unit.world_x, target_y - unit.world_y)
    
    # Define acceleration and max speed
    if not hasattr(unit, 'acceleration'):
        acceleration = 200.0  # Default: 200 units per second^2
    else:
        acceleration = unit.acceleration
        
    if not hasattr(unit, 'max_speed'):
        max_speed = 100.0  # Default: 100 units per second
    else:
        max_speed = unit.max_speed
    
    # If close to target, start slowing down
    braking_distance = (max_speed * max_speed) / (2 * acceleration)
    
    # Calculate forward vector based on current rotation
    forward_x = math.cos(math.radians(unit.rotation))
    forward_y = math.sin(math.radians(unit.rotation))
    
    # Adjust velocity based on alignment with forward direction
    alignment = forward_x * (target_x - unit.world_x) + forward_y * (target_y - unit.world_y)
    alignment = max(-1.0, min(1.0, alignment / max(0.1, distance_to_target)))  # Normalize
    
    # Calculate acceleration scaled by alignment and time
    accel_value = acceleration * dt
    if distance_to_target < braking_distance:
        # Slow down when approaching target
        accel_value = -accel_value
    
    # Apply acceleration in the forward direction
    unit.velocity_x += forward_x * accel_value * alignment
    unit.velocity_y += forward_y * accel_value * alignment
    
    # Apply velocity limits
    current_speed = math.hypot(unit.velocity_x, unit.velocity_y)
    if current_speed > max_speed:
        # Scale back to max speed
        scale_factor = max_speed / current_speed
        unit.velocity_x *= scale_factor
        unit.velocity_y *= scale_factor
    
    # Apply damping when not aligned with target (simulates sideways drag)
    damping = 1.0 - (0.8 * dt * (1.0 - abs(alignment)))
    unit.velocity_x *= damping
    unit.velocity_y *= damping
    
    # Update position based on velocity
    unit.world_x += unit.velocity_x * dt
    unit.world_y += unit.velocity_y * dt
