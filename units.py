from __future__ import annotations
import pygame
import math
import collections
import random
from typing import Optional, Tuple, Union, List
from dataclasses import dataclass, field
from effects import AttackEffect # Import the new effect class
from unit_mechanics import update_unit_attack, smooth_movement
from camera import Camera
from asset_manager import get_ship_sprite  # Import the ship sprite getter

# Define colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
HEALTH_BAR_RED = (200, 0, 0)
HEALTH_BAR_GREEN = (0, 200, 0)
HEALTH_BAR_BACK = (50, 50, 50)
BLUE = (0, 0, 255) # Example friendly attack color
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

@dataclass
class Unit:
    """Represents a single game unit (friendly or enemy)."""
    # World position and basic properties
    world_x: float  # X position in world coordinates
    world_y: float  # Y position in world coordinates
    unit_type: str  # Type of unit ("friendly" or "enemy")
    type: str = field(init=False)  # Synonym for unit_type, used for targeting and command logic
    color: Tuple[int, int, int] = field(init=False)  # RGB color based on unit type
    hp: int = 100
    hp_max: int = 100
    radius: int = 15
    
    # Combat attributes
    attack_range: int = 150
    attack_power: int = 20  # Damage dealt per attack
    attack_cooldown: float = 1.0  # 1 second between attacks
    current_attack_cooldown: float = 0.0  # Time until next attack is ready
    attack_target: Optional[Unit] = None
    
    # Movement attributes
    speed: int = 100
    state: str = "idle"  # idle, moving, attacking, destroyed
    move_target: Optional[Union[Tuple[float, float], Unit]] = None
    
    # Physics-based movement attributes
    rotation: float = 0  # Current angle in degrees (0-360)
    velocity_x: float = 0
    velocity_y: float = 0
    max_speed: float = 100
    acceleration: float = 200
    max_rotation_speed: float = 180  # degrees per second
    
    # Visual interpolation
    draw_x: float = field(init=False)
    draw_y: float = field(init=False)
    last_draw_x: float = field(init=False)
    last_draw_y: float = field(init=False)
    
    # Visual effects
    trail_positions: List[Tuple[int, int]] = field(default_factory=list)
    max_trail_length: int = 15
    min_trail_dist_sq: int = 100  # Minimum squared distance to create a new trail point
    flare_flicker: float = 1.0
    selected: bool = False  # For player selection indication
    preview_selected: bool = False  # For selection preview during rectangle drag
    
    # Transparency effect (255 = fully opaque, 0 = invisible)
    opacity: int = 255
    # Animation properties
    fade_in_duration: float = 1.0  # Time in seconds for unit to fully appear
    current_fade_time: float = 0.0  # Current progress of fade animation
    
    def __post_init__(self) -> None:
        """Initialize derived attributes after dataclass initialization."""
        self.type = self.unit_type
        self.color = GREEN if self.unit_type == "friendly" else RED
        self.draw_x = self.world_x
        self.draw_y = self.world_y
        self.last_draw_x = self.world_x
        self.last_draw_y = self.world_y

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the unit onto the screen, adjusted by camera view.

        Args:
            surface (pygame.Surface): The screen surface to draw on.
            camera (Camera): The game camera instance.
        """
        # Use interpolated draw coordinates for rendering
        screen_pos = camera.apply_coords(int(self.draw_x), int(self.draw_y))

        # --- Draw Engine Flare (Modified Trail) --- 
        if self.state == "moving":
            # Convert rotation from degrees to radians for trigonometric calculations
            angle_rad = math.radians(self.rotation)
            
            # Calculate the back position of the ship based on rotation
            back_offset_x = -self.radius * math.cos(angle_rad)
            back_offset_y = -self.radius * math.sin(angle_rad)
            flare_base_x = self.draw_x + back_offset_x
            flare_base_y = self.draw_y + back_offset_y
            
            num_flares = random.randint(2, 4) # Draw a few flickering particles
            for _ in range(num_flares):
                # Vary size and position slightly
                flicker_size = self.radius * 0.5 * self.flare_flicker * random.uniform(0.7, 1.3)
                flicker_offset_rad = angle_rad + random.uniform(-0.3, 0.3) # Slight angle variation
                flicker_dist = self.radius * random.uniform(0.1, 0.5) # Distance behind ship
                
                flare_center_x = flare_base_x - flicker_dist * math.cos(angle_rad)
                flare_center_y = flare_base_y - flicker_dist * math.sin(angle_rad)
                
                flare_screen_pos = camera.apply_coords(int(flare_center_x), int(flare_center_y))
                
                if flicker_size >= 1:
                    # Choose color randomly between yellow and orange
                    flare_color = random.choice([YELLOW, ORANGE]) 
                    alpha = random.randint(150, 255) # Random alpha
                    final_color = (*flare_color, alpha)

                    # Draw small flare polygon (e.g., triangle)
                    flare_points = [
                        (0, -flicker_size * 0.8), # Tip
                        (-flicker_size * 0.5, flicker_size * 0.5),
                        (flicker_size * 0.5, flicker_size * 0.5)
                    ]
                    # Rotate flare points
                    rotated_flare_points = []
                    # Point flare backwards (180 degrees from ship direction)
                    flare_angle_deg = (self.rotation + 180) % 360
                    flare_angle_rad = math.radians(flare_angle_deg)
                    cos_a = math.cos(flare_angle_rad)
                    sin_a = math.sin(flare_angle_rad)
                    for px, py in flare_points:
                        rot_x = px * cos_a - py * sin_a
                        rot_y = px * sin_a + py * cos_a
                        rotated_flare_points.append((flare_screen_pos[0] + rot_x, flare_screen_pos[1] + rot_y))
                        
                    # Draw on temp surface for alpha
                    min_x = min(p[0] for p in rotated_flare_points)
                    max_x = max(p[0] for p in rotated_flare_points)
                    min_y = min(p[1] for p in rotated_flare_points)
                    max_y = max(p[1] for p in rotated_flare_points)
                    width = max(1, int(max_x - min_x))
                    height = max(1, int(max_y - min_y))
                    
                    temp_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                    local_points = [(p[0] - min_x, p[1] - min_y) for p in rotated_flare_points]
                    pygame.draw.polygon(temp_surf, final_color, local_points)
                    surface.blit(temp_surf, (min_x, min_y))

        # --- Draw Ship Sprite --- 
        # Get the appropriate sprite for this unit type
        
        try:
            # Get and rotate the sprite based on unit's rotation
            ship_sprite = get_ship_sprite(self.unit_type)
            rotated_sprite = pygame.transform.rotate(ship_sprite, -self.rotation) # Counter-clockwise
            
            # Apply opacity to sprite if not fully opaque
            if self.opacity < 255:
                # Create a copy with per-pixel alpha
                sprite_with_alpha = rotated_sprite.copy().convert_alpha()
                # Apply the opacity value to all pixels
                sprite_with_alpha.fill((255, 255, 255, self.opacity), None, pygame.BLEND_RGBA_MULT)
                rotated_sprite = sprite_with_alpha
            
            sprite_rect = rotated_sprite.get_rect(center=screen_pos)
            
            # Draw the rotated sprite
            surface.blit(rotated_sprite, sprite_rect.topleft)
            
            # Draw selection indicator if selected or preview-selected
            if self.selected or self.preview_selected:
                # Try to use mask for accurate outline that follows sprite shape
                try:
                    mask = pygame.mask.from_surface(rotated_sprite)
                    outline_points = mask.outline()
                    
                    # Translate outline points to the sprite's position on screen
                    translated_points = [(p[0] + sprite_rect.left, p[1] + sprite_rect.top) for p in outline_points]
                    
                    # Draw the outline using lines
                    if len(translated_points) > 1:
                        # Use green for both selection and preview
                        outline_color = GREEN
                        pygame.draw.lines(surface, outline_color, True, translated_points, 2) # Closed loop, 2px thick
                    else:
                        # Fallback if mask outline fails
                        outline_rect = sprite_rect.inflate(4, 4) # Slightly larger than the sprite
                        pygame.draw.rect(surface, GREEN, outline_rect, 2)
                except Exception as e:
                    # Fallback to simple rectangle if mask creation fails
                    outline_rect = sprite_rect.inflate(4, 4)
                    pygame.draw.rect(surface, GREEN, outline_rect, 2)
                    
        except Exception as e:
            # Fallback to geometric rendering if sprites can't be loaded
            print(f"Falling back to geometric rendering: {e}")
            
            # Define base points for a triangle
            p1 = (self.radius, 0)  # Nose
            p2 = (-self.radius * 0.8, self.radius * 0.7)  # Back left wing
            p3 = (-self.radius * 0.8, -self.radius * 0.7)  # Back right wing
            base_points = [p1, p2, p3]

            # Rotate points based on self.rotation (in degrees)
            angle_rad = math.radians(self.rotation)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            rotated_points = []
            for x, y in base_points:
                rotated_x = x * cos_a - y * sin_a
                rotated_y = x * sin_a + y * cos_a
                rotated_points.append((screen_pos[0] + rotated_x, screen_pos[1] + rotated_y))

            # Draw the polygon
            pygame.draw.polygon(surface, self.color, rotated_points)

            # Draw selection indicator if selected or preview_selected
            if self.selected or self.preview_selected:
                # Draw outline around the polygon
                pygame.draw.polygon(surface, GREEN, rotated_points, 2)

        # Draw health bar if not at max HP
        if self.hp < self.hp_max:
            bar_width = self.radius * 2
            bar_height = 4
            bar_x = screen_pos[0] - self.radius
            bar_y = screen_pos[1] - self.radius - bar_height - 2 # Position above the unit

            health_percentage = self.hp / self.hp_max
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
        
        # Update opacity fade-in effect if unit is not fully opaque
        if self.opacity < 255:
            # Increase fade time based on dt
            self.current_fade_time = min(self.fade_in_duration, self.current_fade_time + dt)
            # Calculate opacity based on current fade progress
            fade_progress = self.current_fade_time / self.fade_in_duration
            self.opacity = min(255, int(255 * fade_progress))
        
        # --- Smooth Movement Interpolation --- 
        # Move draw coordinates towards logical world coordinates
        lerp_factor = min(1.0, dt * 10) # Adjust lerp speed as needed
        self.draw_x += (self.world_x - self.draw_x) * lerp_factor
        self.draw_y += (self.world_y - self.draw_y) * lerp_factor
        
        # Update trail
        if self.state == "moving":
            dist_sq = (self.draw_x - self.last_draw_x)**2 + (self.draw_y - self.last_draw_y)**2
            if dist_sq > self.min_trail_dist_sq:
                 self.trail_positions.append((int(self.last_draw_x), int(self.last_draw_y))) # Store previous int position
                 self.last_draw_x = self.draw_x
                 self.last_draw_y = self.draw_y
                 
        attack_effect_generated = None # Initialize return value

        # Movement logic
        if self.state == "moving":
            target_pos = None
            if isinstance(self.move_target, Unit):
                # Target is another unit
                if self.move_target.hp <= 0: # Check if target is destroyed
                    self.set_state("idle")
                    self.move_target = None
                else:
                    target_pos = (self.move_target.world_x, self.move_target.world_y)
            elif isinstance(self.move_target, tuple):
                # Target is a point
                target_pos = self.move_target

            if target_pos:
                # Calculate distance to target
                vector_x = target_pos[0] - self.world_x
                vector_y = target_pos[1] - self.world_y
                distance = math.hypot(vector_x, vector_y)
                
                # Update engine flare flicker effect
                self.flare_flicker = max(0.7, min(1.3, self.flare_flicker + random.uniform(-0.1, 0.1)))

                # Check proximity for state change
                stop_distance = 0
                if isinstance(self.move_target, Unit):
                    stop_distance = self.attack_range - 5 # Stop slightly before attack range

                if distance <= stop_distance and isinstance(self.move_target, Unit):
                    # Reached attack target
                    self.set_state("attacking")
                    # Gradually slow down when stopping
                    self.velocity_x *= 0.9
                    self.velocity_y *= 0.9
                elif distance < 5: # Close enough to point target
                    self.set_state("idle")
                    self.move_target = None
                    # Gradually slow down when stopping
                    self.velocity_x *= 0.9
                    self.velocity_y *= 0.9
                else:
                    # Apply realistic movement physics
                    smooth_movement(self, target_pos[0], target_pos[1], dt)
            else:
                 # No valid target position, become idle
                 self.set_state("idle")

        # Use the game_logic module for attack handling instead of inline logic
        if self.state == "attacking":
            attack_effect_generated = update_unit_attack(self, dt)

        return attack_effect_generated # Return effect if created, else None

    def attack(self, target: Unit) -> None:
        """Command the unit to attack another unit.

        Args:
            target (Unit): The enemy unit to target.
        """
        # Check target is not null, has health, is not this unit, and is of opposite type
        if (target is not None and target.hp > 0 and target != self and 
                ((self.type == 'friendly' and target.type == 'enemy') or 
                 (self.type == 'enemy' and target.type == 'friendly'))):
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

    def take_damage(self, amount: int, attacker: Optional['Unit'] = None) -> None:
        """Reduce HP by the given amount and check for destruction.
        
        Args:
            amount (int): The amount of damage to apply
            attacker (Unit, optional): The unit that caused the damage, if any
        """
        self.hp -= amount
        if attacker:
            print(f"DEBUG take_damage: Unit {id(self)} took {amount} damage from {id(attacker)}. New HP: {self.hp}") # DEBUG
        else:
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
        
    def set_target(self, target_unit: 'Unit') -> None:
        """Set a target unit to attack or follow.
        
        This is used by the game's AI system to make units engage with targets.
        Enemy units use this to chase friendly units, and friendly units use this
        to engage enemy units when not directly controlled by the player.
        
        Args:
            target_unit: The Unit to target
        """
        if target_unit and target_unit.hp > 0:
            self.attack(target_unit)

class FriendlyUnit(Unit):
    def __init__(self, world_x: int, world_y: int):
        super().__init__(world_x, world_y, unit_type='friendly')

class EnemyUnit(Unit):
    def __init__(self, world_x: int, world_y: int):
        super().__init__(world_x, world_y, unit_type='enemy')
