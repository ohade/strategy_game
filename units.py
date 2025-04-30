from __future__ import annotations
import pygame
import math
import collections
from camera import Camera
from typing import Optional, Tuple, Union
from effects import AttackEffect # Import the new effect class

# Define colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
HEALTH_BAR_RED = (200, 0, 0)
HEALTH_BAR_GREEN = (0, 200, 0)
HEALTH_BAR_BACK = (50, 50, 50)
BLUE = (0, 0, 255) # Example friendly attack color

class Unit:
    """Represents a single game unit (friendly or enemy)."""

    def __init__(self, x: int, y: int, unit_type: str, hp: int = 100, radius: int = 15, speed: int = 150, attack_range: int = 50, attack_power: int = 10, attack_cooldown: float = 1.0):
        """Initialize a unit.

        Args:
            x (int): Initial world x-coordinate.
            y (int): Initial world y-coordinate.
            unit_type (str): 'friendly' or 'enemy'.
            hp (int): Health points.
            radius (int): Visual radius of the unit's circle.
            speed (int): Movement speed in pixels per second.
            attack_range (int): Distance within which the unit can attack.
            attack_power (int): Damage dealt per attack.
            attack_cooldown (float): Time in seconds between attacks.
        """
        self.world_x: float = float(x) # Use float for smoother movement
        self.world_y: float = float(y)
        self.hp = hp
        self.max_hp = hp # Store max HP for drawing health bars later if needed
        self.radius = radius
        self.type = unit_type
        self.color = GREEN if unit_type == 'friendly' else RED
        self.selected = False # For player selection indication

        # Drawing coordinates for smooth animation
        self.draw_x = float(x) 
        self.draw_y = float(y)
        self.last_draw_x = self.draw_x # Store previous position for trail calculation
        self.last_draw_y = self.draw_y
        
        # Trail effect
        self.trail_positions = collections.deque(maxlen=10) # Store last 10 positions
        self.min_trail_dist_sq = 5*5 # Minimum squared distance to add a trail point

        # Movement and Combat related
        self.speed = speed
        self.attack_range = attack_range
        self.move_target: Optional[Union[Unit, Tuple[float, float]]] = None # Can be a Unit or a (x, y) tuple
        self.state: str = "idle"  # Current state: idle, moving, attacking, destroyed
        self.attack_power = attack_power
        self.attack_cooldown = attack_cooldown
        self.current_attack_cooldown: float = 0.0 # Time until next attack is ready

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the unit onto the screen, adjusted by camera view.

        Args:
            surface (pygame.Surface): The screen surface to draw on.
            camera (Camera): The game camera instance.
        """
        # Use interpolated draw coordinates for rendering
        screen_pos = camera.apply_coords(int(self.draw_x), int(self.draw_y))

        # --- Draw Trail --- 
        if self.state == "moving":
            max_len = float(len(self.trail_positions))
            if max_len > 0:
                for i, pos in enumerate(reversed(self.trail_positions)): # Draw newest first
                    # Calculate alpha and size based on age (i)
                    progress = (i + 1) / max_len # Normalized position in trail (0 to 1)
                    alpha = int(progress * 100) + 20 # Fade out (e.g., 20 to 120 alpha)
                    size = int(progress * (self.radius * 0.6)) + 1 # Shrink (e.g., 1 to 60% radius)
                    
                    if size > 0:
                        trail_screen_pos = camera.apply_coords(pos[0], pos[1])
                        # Create a temporary surface for alpha blending
                        trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                        trail_color = (*self.color[:3], alpha) # Use unit color with calculated alpha
                        pygame.draw.circle(trail_surf, trail_color, (size, size), size)
                        surface.blit(trail_surf, (trail_screen_pos[0] - size, trail_screen_pos[1] - size))
                        
        # --- End Draw Trail --- 
        
        # Draw the main unit circle
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)

        # Draw selection indicator if selected
        if self.selected:
            pygame.draw.circle(surface, WHITE, screen_pos, self.radius + 2, 1) # Draw white outline

        # Draw health bar if not at max HP
        if self.hp < self.max_hp:
            bar_width = self.radius * 2
            bar_height = 4
            bar_x = screen_pos[0] - self.radius
            bar_y = screen_pos[1] - self.radius - bar_height - 2 # Position above the unit

            health_percentage = self.hp / self.max_hp
            current_bar_width = int(bar_width * health_percentage)

            # Background rect
            pygame.draw.rect(surface, HEALTH_BAR_BACK, (bar_x, bar_y, bar_width, bar_height))
            # Health rect
            pygame.draw.rect(surface, HEALTH_BAR_GREEN, (bar_x, bar_y, current_bar_width, bar_height))

    def update(self, dt: float) -> Optional[AttackEffect]:
        """Update unit state (movement, state changes, attacking).

        Args:
            dt (float): Delta time.

        Returns:
            Optional[AttackEffect]: An attack effect if one was generated this frame, else None.
        """
        attack_effect_generated: Optional[AttackEffect] = None
        
        # --- Smooth Movement Interpolation --- 
        # Move draw coordinates towards logical world coordinates
        lerp_factor = 10.0 * dt # Adjust this factor to control smoothness (higher = faster catch-up)
        lerp_factor = min(lerp_factor, 1.0) # Clamp to 1.0 to prevent overshooting

        # Store pre-interpolation position
        prev_draw_x, prev_draw_y = self.draw_x, self.draw_y
        
        self.draw_x += (self.world_x - self.draw_x) * lerp_factor
        self.draw_y += (self.world_y - self.draw_y) * lerp_factor
        # --- End Smooth Movement --- 

        # --- Trail Update --- 
        is_moving_state = self.state == "moving"

        if is_moving_state:
            # Append the position *before* the current interpolation step, every frame during move
            self.trail_positions.append((int(prev_draw_x), int(prev_draw_y)))
        elif len(self.trail_positions) > 0:
            # Clear trail if not moving
            self.trail_positions.clear()
        # --- End Trail Update --- 
 
        # --- Movement Logic ---
        if self.state == "moving" and self.move_target is not None:
            target_x: float
            target_y: float

            # Determine target coordinates based on move_target type
            if isinstance(self.move_target, Unit):
                # Check if target unit is still valid
                if self.move_target.hp <= 0:
                    self.move_target = None
                    self.set_state("idle")
                    return attack_effect_generated # Early exit if target gone
                target_x, target_y = self.move_target.world_x, self.move_target.world_y
            elif isinstance(self.move_target, tuple):
                target_x, target_y = self.move_target
            else: # Should not happen, but good practice
                 self.move_target = None
                 self.set_state("idle")
                 return attack_effect_generated # Early exit

            vector_x = target_x - self.world_x
            vector_y = target_y - self.world_y
            distance = math.hypot(vector_x, vector_y)

            # --- Check for arrival / state transition --- 
            # 1. Target is a Unit: Check attack range
            if isinstance(self.move_target, Unit):
                if distance <= self.attack_range:
                    # Target in range, attempt to transition to attacking
                    # Keep the target for attack logic in the 'attacking' state
                    self.set_state("attacking") 
                    return attack_effect_generated # Don't move further this frame

            # 2. Target is a Point: Check if close enough
            elif isinstance(self.move_target, tuple):
                if distance < 5: # Arrival threshold
                    self.world_x, self.world_y = target_x, target_y # Snap to target
                    self.move_target = None
                    self.set_state("idle")
                    return attack_effect_generated # Arrived, stop processing movement

            # --- Apply Movement (if still moving) --- 
            if distance > 0: # Avoid division by zero if already at target
                # Normalize vector
                vector_x /= distance
                vector_y /= distance
                # Move unit
                self.world_x += vector_x * self.speed * dt
                self.world_y += vector_y * self.speed * dt

        elif self.state == "attacking":
            # Check if target still exists and is valid
            # Ensure move_target is a Unit in attack state
            if not isinstance(self.move_target, Unit) or self.move_target.hp <= 0:
                self.set_state("idle")
                self.move_target = None
                self.current_attack_cooldown = 0.0 # Reset cooldown
                return attack_effect_generated

            # Check distance to target
            target_x, target_y = self.move_target.world_x, self.move_target.world_y
            vector_x = target_x - self.world_x
            vector_y = target_y - self.world_y
            distance = math.hypot(vector_x, vector_y)

            if distance > self.attack_range:
                # Target moved out of range, go back to moving state
                self.set_state("moving") # Re-enter moving state to chase
                self.current_attack_cooldown = 0.0 # Reset cooldown if stopped attacking
            else:
                # Target in range, handle attack cooldown
                self.current_attack_cooldown -= dt
                if self.current_attack_cooldown <= 0:
                    # Attack!
                    # Apply damage
                    self.move_target.take_damage(self.attack_power)
                    # Create and store the visual effect for return
                    attack_color = BLUE if self.type == 'friendly' else RED
                    start_pos = (self.draw_x, self.draw_y)
                    end_pos = (self.move_target.draw_x, self.move_target.draw_y)
                    attack_effect_generated = AttackEffect(start_pos, end_pos, color=attack_color, duration=0.15)
                    # Reset cooldown
                    self.current_attack_cooldown = self.attack_cooldown

        return attack_effect_generated # Return effect if created, else None

    def set_target(self, target: Unit) -> None:
        """Set an enemy unit as the target for movement/attack.

        Args:
            target (Unit): The enemy unit to target.
        """
        if target is not None and target.hp > 0 and target != self:
            self.move_target = target
            self.set_state("moving") # Start moving towards the target

    def move_to_point(self, x: float, y: float) -> None:
        """Command the unit to move to a specific point on the map.

        Args:
            x (float): Target world x-coordinate.
            y (float): Target world y-coordinate.
        """
        self.move_target = (x, y)
        self.set_state("moving") # Start moving towards the point

    def take_damage(self, amount: int) -> None:
        """Reduce HP by the given amount and check for destruction."""
        self.hp -= amount
        print(f"DEBUG take_damage: Unit {id(self)} took {amount} damage. New HP: {self.hp}") # DEBUG
        if self.hp <= 0:
            self.hp = 0
            print(f"DEBUG take_damage: Unit {id(self)} HP <= 0. Setting state to destroyed.") # DEBUG
            # Unit is destroyed - state change or flag could be set here if needed
            # For now, main loop will check hp directly.
            self.set_state("destroyed")

    def get_rect(self) -> pygame.Rect:
        """Get the unit's bounding rectangle in world coordinates.

        Used for collision detection or selection checks.
        Rect's top-left is calculated from the center (world_x, world_y) and radius.
        """
        # Use int coords for Rect
        return pygame.Rect(int(self.world_x) - self.radius, int(self.world_y) - self.radius,
                         self.radius * 2, self.radius * 2)

    def set_state(self, new_state: str) -> None:
        """Set the unit's state and handle transitions (like clearing trail)."""
        if self.state != new_state:
            self.state = new_state
            # Clear trail if not in a moving state
            if self.state != "moving": 
                self.trail_positions.clear()
                
    def move_to(self, target_pos: Tuple[float, float]) -> None:
        """Set a movement target position."""
        self.move_target_pos = target_pos
        self.move_target = None # Clear attack target when moving to point
        self.set_state("moving") # Use set_state

class FriendlyUnit(Unit):
    def __init__(self, world_x: int, world_y: int):
        super().__init__(world_x, world_y, unit_type='friendly')

class EnemyUnit(Unit):
    def __init__(self, world_x: int, world_y: int):
        super().__init__(world_x, world_y, unit_type='enemy')
