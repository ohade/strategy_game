"""Module for handling core game logic and state updates."""

import math
from typing import List, Any, Tuple, Optional

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


def update_effects(effects: List[Any], dt: float) -> List[Any]:
    """Update all effects and remove those that have expired.
    
    This function handles updating and cleaning up visual effects. It properly detects
    different types of effects by checking for their specific completion methods 
    (is_expired, is_finished, or is_alive).
    
    Args:
        effects: List of effect objects (must have update method and one of: 
                is_expired, is_finished, or is_alive methods)
        dt: Delta time in seconds
        
    Returns:
        List of effects that are still active after updates
    """
    if not effects:
        return []
        
    active_effects = []
    
    for effect in effects:
        # Update the effect
        effect.update(dt)
        
        # Check if effect should be removed based on its completion state
        # Different effect types might have different methods to check completion
        if hasattr(effect, 'is_expired') and effect.is_expired():
            continue  # Skip adding this effect to active list
        elif hasattr(effect, 'is_finished') and effect.is_finished():
            continue  # Skip adding this effect to active list
        elif hasattr(effect, 'is_alive') and not effect.is_alive():
            continue  # Skip adding this effect to active list (note inverted logic)
            
        active_effects.append(effect)
        
    return active_effects


def detect_unit_collision(unit1: Any, unit2: Any) -> bool:
    """Detect if two units are colliding/overlapping.
    
    Units are considered colliding if the distance between their centers is less than
    or equal to the sum of their radii. This implements a simple circle-circle
    collision detection.
    
    Args:
        unit1: First unit (must have world_x, world_y, and radius attributes)
        unit2: Second unit (must have world_x, world_y, and radius attributes)
        
    Returns:
        bool: True if units are colliding, False otherwise
    """
    # Calculate distance between unit centers
    distance = math.hypot(unit2.world_x - unit1.world_x, unit2.world_y - unit1.world_y)
    
    # Determine combined radius (collision threshold)
    combined_radius = unit1.radius + unit2.radius
    
    # Collision occurs when distance <= combined radius
    return distance <= combined_radius


def resolve_unit_collision(unit1: Any, unit2: Any) -> None:
    """Resolve collision between two units by moving them apart.
    
    This function pushes overlapping units away from each other along their
    center-to-center axis. Movement is distributed evenly between both units.
    
    Args:
        unit1: First unit (must have world_x, world_y, and radius attributes)
        unit2: Second unit (must have world_x, world_y, and radius attributes)
    """
    # Calculate current distance and direction vector
    dx = unit2.world_x - unit1.world_x
    dy = unit2.world_y - unit1.world_y
    distance = math.hypot(dx, dy)
    
    # Handle the case where units are exactly at the same position
    if distance < 0.1:  # Small epsilon to avoid division by zero
        # Move in a random direction if directly on top of each other
        dx, dy = 1.0, 0.0  # Default to moving along x-axis
        distance = 0.1
    
    # Calculate minimum distance needed (sum of radii)
    min_distance = unit1.radius + unit2.radius
    
    # If units are already separated, do nothing
    if distance >= min_distance:
        return
    
    # Calculate how much overlap there is
    overlap = min_distance - distance
    
    # Normalize direction vector
    dx /= distance
    dy /= distance
    
    # Calculate movement per unit (distribute evenly)
    move_per_unit = overlap / 2.0
    
    # Move unit1 away from unit2
    unit1.world_x -= dx * move_per_unit
    unit1.world_y -= dy * move_per_unit
    
    # Move unit2 away from unit1
    unit2.world_x += dx * move_per_unit
    unit2.world_y += dy * move_per_unit


def find_enemies_in_radius(click_pos: Tuple[float, float], enemy_units: List[Any], radius: float) -> List[Any]:
    """Find all enemy units within a specified radius of a point.
    
    This function finds all enemy units whose centers are within the specified
    radius of the click point. This allows for radius-based targeting.
    
    Args:
        click_pos: The world coordinates (x, y) of the click point
        enemy_units: List of enemy units to check
        radius: The radius within which to find enemy units
        
    Returns:
        List of enemy units within the radius
    """
    if not enemy_units:
        return []
    
    click_x, click_y = click_pos
    units_in_radius = []
    
    for enemy in enemy_units:
        # Get the center position of the enemy unit
        enemy_rect = enemy.get_rect()
        enemy_center_x = enemy.world_x
        enemy_center_y = enemy.world_y
        
        # Calculate distance from click point to enemy center
        distance = math.hypot(enemy_center_x - click_x, enemy_center_y - click_y)
        
        # If within radius, add to result list
        if distance <= radius:
            units_in_radius.append(enemy)
    
    return units_in_radius


def get_closest_enemy_to_point(click_pos: Tuple[float, float], enemy_units: List[Any]) -> Optional[Any]:
    """Get the enemy unit closest to a specific point.
    
    This function finds the enemy unit whose center is closest to the specified
    point. Used for "lock-on" targeting functionality.
    
    Args:
        click_pos: The world coordinates (x, y) of the point
        enemy_units: List of enemy units to check
        
    Returns:
        The closest enemy unit, or None if no enemies are available
    """
    if not enemy_units:
        return None
    
    click_x, click_y = click_pos
    closest_enemy = None
    min_distance = float('inf')
    
    for enemy in enemy_units:
        # Get the center position of the enemy unit
        enemy_rect = enemy.get_rect()
        enemy_center_x = enemy.world_x
        enemy_center_y = enemy.world_y
        
        # Calculate distance from click point to enemy center
        distance = math.hypot(enemy_center_x - click_x, enemy_center_y - click_y)
        
        # Update closest enemy if this one is closer
        if distance < min_distance:
            min_distance = distance
            closest_enemy = enemy
    
    return closest_enemy


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
    # Calculate direction vector
    dx = target_x - start_x
    dy = target_y - start_y
    
    # Calculate angle in radians, then convert to degrees
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    
    # Convert to 0-360 range (atan2 returns -180 to 180)
    if angle_deg < 0:
        angle_deg += 360
        
    return angle_deg


def apply_rotation_inertia(current_angle: float, target_angle: float, max_rotation_speed: float) -> float:
    """Gradually rotate from current angle towards target angle with inertia.
    
    This function limits rotation speed to simulate realistic turning.
    It takes the shortest path around the circle (clockwise or counterclockwise).
    
    Args:
        current_angle: Current rotation angle in degrees (0-360)
        target_angle: Target rotation angle in degrees (0-360)
        max_rotation_speed: Maximum rotation speed in degrees per update
        
    Returns:
        New rotation angle after applying inertia
    """
    # Normalize angles to 0-360 range
    current_angle = current_angle % 360
    target_angle = target_angle % 360
    
    # Calculate the direct difference between angles
    angle_diff = target_angle - current_angle
    
    # Handle wrapping around 360 degrees (find shortest path)
    if angle_diff > 180:
        angle_diff -= 360
    elif angle_diff < -180:
        angle_diff += 360
    
    # Apply speed limit
    if abs(angle_diff) <= max_rotation_speed:
        # If we can reach the target in this step, go directly to it
        return target_angle
    elif angle_diff > 0:
        # Rotate clockwise by max speed
        new_angle = current_angle + max_rotation_speed
        return new_angle
    else:
        # Rotate counterclockwise by max speed
        new_angle = current_angle - max_rotation_speed
        # Handle wrapping for negative angles
        if new_angle < 0:
            new_angle += 360
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
