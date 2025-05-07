from __future__ import annotations
import pygame
import math
import collections
import random
from typing import Optional, Tuple, Union, List, TYPE_CHECKING
from dataclasses import dataclass, field
from effects import AttackEffect # Import the new effect class
from unit_mechanics import update_unit_attack, smooth_movement
from camera import Camera
from asset_manager import get_ship_sprite  # Import the ship sprite getter

# To avoid circular imports
if TYPE_CHECKING:
    from carrier import Carrier

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
    mass: float = 1.0  # Mass for collision resolution (carrier will have much higher mass)
    
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
    
    # Visibility properties
    vision_radius: int = 150  # Default vision radius for fog of war
    
    # Transparency effect (255 = fully opaque, 0 = invisible)
    opacity: int = 255
    # Animation properties
    fade_in_duration: float = 1.0  # Time in seconds for unit to fully appear
    current_fade_time: float = 0.0  # Current progress of fade animation
    
    # Flight behavior attributes
    straight_flight_timer: float = 0.0  # Timer for straight flight behavior
    is_straight_flight: bool = False  # Flag to indicate the unit is in straight flight mode
    
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
            # Increase fade time based on dt, but accelerate for better visibility
            self.current_fade_time = min(self.fade_in_duration, self.current_fade_time + dt * 2.0)  # Double speed
            # Calculate opacity based on current fade progress
            fade_progress = self.current_fade_time / self.fade_in_duration
            # Start with a minimum opacity of 100 to ensure immediate visibility
            min_opacity = 100
            fade_opacity = min(255, int(min_opacity + (255 - min_opacity) * fade_progress))
            self.opacity = max(self.opacity, fade_opacity)  # Never decrease opacity
            
            # If unit has launch_origin and is still launching, use a smooth emergence animation
            if hasattr(self, 'launch_origin') and fade_progress < 1.0:
                # Calculate how far the unit should have emerged by now
                angle_rad = math.radians(self.rotation)
                
                # Use a non-linear easing function for smoother emergence
                # Quadratic ease-in: makes the movement start slow and accelerate
                eased_progress = fade_progress * fade_progress
                
                # Start position is slightly inside the carrier, then move to edge and beyond
                # This creates the illusion of emerging from inside the carrier
                # Use a longer emergence distance for more visible movement
                start_offset = -self.radius * 0.5  # Start half a radius inside the carrier
                end_offset = self.radius * 0.5     # End half a radius outside the carrier
                
                # Calculate current offset using eased progress
                current_offset = start_offset + (end_offset - start_offset) * eased_progress
                
                # Apply the offset in the direction the unit is facing
                emergence_x = math.cos(angle_rad) * current_offset
                emergence_y = math.sin(angle_rad) * current_offset
                
                # Adjust position to create smooth emerging effect
                self.world_x = self.launch_origin[0] + emergence_x
                self.world_y = self.launch_origin[1] + emergence_y
                
                # Also adjust draw coordinates for immediate visual effect
                self.draw_x = self.world_x
                self.draw_y = self.world_y
        
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
            # Check if this is a unit in straight flight mode
            if self.is_straight_flight:
                # Update position based on current velocity
                self.world_x += self.velocity_x * dt
                self.world_y += self.velocity_y * dt
                
                # Decrease the straight flight timer
                self.straight_flight_timer -= dt
                
                # Debug output
                if self.straight_flight_timer <= 0:
                    print(f"DEBUG: Fighter straight flight completed, transitioning to normal movement")
                    # When timer expires, transition to normal movement
                    self.is_straight_flight = False
                
                # Continue with normal movement logic after updating position

            # Check if this is a FriendlyUnit on patrol mission
            if hasattr(self, 'is_patrolling') and self.is_patrolling:
                # If we have a patrol timer, decrease it
                if hasattr(self, 'patrol_timer') and self.patrol_timer > 0:
                    self.patrol_timer -= dt
                    
                # Calculate distance to target if we have one
                if isinstance(self.move_target, tuple):
                    target_x, target_y = self.move_target
                    dist_to_target = math.hypot(self.world_x - target_x, self.world_y - target_y)
                    
                    # If we're close to target or timer expired, stop patrolling and hover
                    if dist_to_target < 10 or (hasattr(self, 'patrol_timer') and self.patrol_timer <= 0):
                        self.set_state("idle")
                        self.move_target = None
                        self.is_patrolling = False  # End patrol mission
                        # Gradually slow down when stopping
                        self.velocity_x *= 0.8
                        self.velocity_y *= 0.8
                        return attack_effect_generated
                
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
            
        # Handle carrier return behavior with a more robust simplified approach
        # Only apply to fighter units (FriendlyUnit instances that are not Carrier instances)
        if isinstance(self, FriendlyUnit) and not hasattr(self, 'fighter_capacity') and self.is_returning_to_carrier and self.target_carrier:
            # Calculate distance to carrier
            distance_to_carrier = math.hypot(
                self.world_x - self.target_carrier.world_x,
                self.world_y - self.target_carrier.world_y
            )
            
            print(f"DEBUG: Fighter {id(self)} returning to carrier {id(self.target_carrier)}")
            print(f"DEBUG: Distance to carrier: {distance_to_carrier:.1f}, carrier radius: {self.target_carrier.radius}")
            print(f"DEBUG: Fighter state: {self.state}, move_target: {self.move_target}")
            
            # CRITICAL FIX: Make sure we continue movement until we're very close to carrier
            landing_distance = self.target_carrier.radius * 1.0  # Tighter distance requirement
            
            # Check if close enough to land directly
            if distance_to_carrier <= landing_distance:
                print(f"DEBUG: Fighter {id(self)} close enough to carrier, attempting direct landing")
                
                # Forcibly stop movement to ensure clean landing
                self.velocity_x = 0
                self.velocity_y = 0
                self.move_target = None
                self.state = "idle"
                
                # Try to land directly - with extra safety checks
                if hasattr(self.target_carrier, 'direct_land_fighter'):
                    landing_success = self.target_carrier.direct_land_fighter(self)
                    print(f"DEBUG: Landing attempt result: {landing_success}")
                    
                    if landing_success:
                        # Extra safeguard - make sure fighter is marked for removal
                        self.opacity = 0
                        self.landing_complete = True
                        print(f"DEBUG: Fighter {id(self)} successfully landed and marked for removal")
                    else:
                        print(f"DEBUG: Fighter {id(self)} could not land - carrier may be at capacity")
                        # Reset returning state but move away from carrier
                        self.is_returning_to_carrier = False
                        self.target_carrier = None
                        
                        # Move away to prevent immediate re-landing attempts
                        offset_x = random.uniform(-100, 100)
                        offset_y = random.uniform(-100, 100)
                        self.move_to_point(self.world_x + offset_x, self.world_y + offset_y)
                else:
                    print(f"ERROR: Target carrier doesn't have direct_land_fighter method!")

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
        # Friendly units have good vision
        self.vision_radius = 200  # Enhanced vision radius for friendly units
        # Carrier-related attributes
        self.target_carrier = None  # Reference to carrier this fighter is returning to
        self.is_returning_to_carrier = False  # Flag to indicate return mode
        self.landing_stage = "idle"  # idle, approach, align, land, store
        self.landing_timer = 0.0  # Timer for landing sequence phases
        self.landing_complete = False  # Flag to indicate fighter has landed and should be removed
        self.patrol_timer = 0.0  # Timer for patrol behavior - when expires, fighter stops at current position
        self.is_patrolling = False  # Flag to indicate the fighter is on a patrol mission
        self.collision_enabled = True  # Flag to control collision detection
        
    def get_direction_x(self) -> float:
        """Get the X component of the unit's direction vector based on rotation.
        
        Returns:
            float: X component of direction vector (normalized)
        """
        return math.cos(math.radians(self.rotation))
        
    def get_direction_y(self) -> float:
        """Get the Y component of the unit's direction vector based on rotation.
        
        Returns:
            float: Y component of direction vector (normalized)
        """
        return math.sin(math.radians(self.rotation))
        
    def update_carrier_return(self, dt: float) -> None:
        """Update the fighter's return-to-carrier behavior.
        
        This method handles the different stages of returning to a carrier:
        - Approach: Move to a point near the carrier
        - Align: Rotate to match carrier's orientation
        - Land: Move onto the carrier's deck
        - Store: Add fighter to carrier's stored_fighters list
        
        Args:
            dt: Time delta in seconds
        """
        if not self.is_returning_to_carrier or not self.target_carrier:
            return
            
        # Check if we've reached the carrier during any stage
        distance_to_carrier = math.hypot(
            self.world_x - self.target_carrier.world_x,
            self.world_y - self.target_carrier.world_y
        )
        
        # Debug output to help troubleshoot landing sequence (less verbose)
        if random.random() < 0.05:  # Only print debug info occasionally to reduce spam
            print(f"Fighter {id(self)} is {distance_to_carrier:.1f} units from carrier {id(self.target_carrier)}, in stage: {self.landing_stage}")
        
        # Override normal state for landing sequence
        self.state = "landing"  # This prevents normal movement logic from interfering
        
        # Add visual indicator for landing sequence - pulsing opacity effect
        if self.landing_stage in ["approach", "align"]:
            # Create a pulsing effect for visibility
            pulse_rate = 5.0  # Speed of pulse
            pulse_min = 180   # Minimum opacity
            pulse_max = 255   # Maximum opacity
            pulse_range = pulse_max - pulse_min
            
            # Calculate pulsing opacity based on sine wave
            pulse_factor = (math.sin(self.landing_timer * pulse_rate) + 1) / 2  # 0 to 1
            self.opacity = int(pulse_min + pulse_factor * pulse_range)
            
            # Update landing timer for animation effects
            self.landing_timer += dt
        
        # Update based on landing stage
        if self.landing_stage == "approach":
            # Keep collision detection enabled during approach
            self.collision_enabled = True
            
            # Calculate approach point - slightly offset from carrier center
            # This creates a more realistic approach path
            carrier_direction_x = self.target_carrier.get_direction_x()
            carrier_direction_y = self.target_carrier.get_direction_y()
            
            # Approach point is behind the carrier (for landing from behind)
            approach_distance = self.target_carrier.radius * 3.0
            approach_point_x = self.target_carrier.world_x - carrier_direction_x * approach_distance
            approach_point_y = self.target_carrier.world_y - carrier_direction_y * approach_distance
            
            # Calculate direction to approach point
            direct_x = approach_point_x - self.world_x
            direct_y = approach_point_y - self.world_y
            distance_to_approach = math.hypot(direct_x, direct_y)
            
            # Use smooth approach speed with easing
            # Faster when far away, slower as we get closer
            base_speed = self.max_speed
            distance_factor = min(1.0, distance_to_approach / (approach_distance * 2))
            approach_speed = (base_speed * 0.5 + base_speed * 0.5 * distance_factor) * dt
            
            if distance_to_approach > 0:  # Avoid division by zero
                self.world_x += (direct_x / distance_to_approach) * approach_speed
                self.world_y += (direct_y / distance_to_approach) * approach_speed
            
            # Gradually rotate toward carrier's opposite direction during approach
            target_rotation = (self.target_carrier.rotation + 180) % 360
            rotation_diff = (target_rotation - self.rotation + 180) % 360 - 180
            
            # Rotate at half speed during approach (full speed during align stage)
            rotation_step = min(self.max_rotation_speed * dt * 2.5, abs(rotation_diff))
            if rotation_diff > 0:
                self.rotation += rotation_step
            else:
                self.rotation -= rotation_step
                
            # Keep rotation in 0-360 range
            self.rotation = self.rotation % 360
            
            # Check if we're close enough to the approach point
            if distance_to_approach <= self.radius * 2 or distance_to_carrier <= self.target_carrier.radius * 2.5:
                print(f"Fighter {id(self)} reached approach point, moving to align stage")
                self.landing_stage = "align"
                self.landing_timer = 0.0
                # Stop normal movement - we're now in landing mode
                self.move_target = None
                # Reduce velocity for more controlled movement
                self.velocity_x *= 0.5
                self.velocity_y *= 0.5
                
        elif self.landing_stage == "align":
            # Keep collision detection enabled during alignment
            self.collision_enabled = True
            
            # Align with carrier orientation (opposite direction to match docking)
            target_rotation = (self.target_carrier.rotation + 180) % 360
            rotation_diff = (target_rotation - self.rotation + 180) % 360 - 180
            
            # Less verbose debug output
            if random.random() < 0.05:  # Only print occasionally
                print(f"Fighter {id(self)} aligning - current: {self.rotation:.1f}°, target: {target_rotation:.1f}°, diff: {rotation_diff:.1f}°")
            
            # Rotate smoothly toward target rotation with easing
            # Faster rotation when difference is large, slower as we get closer
            rotation_factor = min(1.0, abs(rotation_diff) / 90)  # 0-1 based on difference
            rotation_step = min(self.max_rotation_speed * dt * (3 + rotation_factor * 3), abs(rotation_diff))
            
            if rotation_diff > 0:
                self.rotation += rotation_step
            else:
                self.rotation -= rotation_step
                
            # Keep rotation in 0-360 range
            self.rotation = self.rotation % 360
            
            # Maintain position relative to carrier during alignment
            # This creates a more stable alignment phase
            carrier_direction_x = self.target_carrier.get_direction_x()
            carrier_direction_y = self.target_carrier.get_direction_y()
            
            # Hold position behind carrier during alignment
            hold_distance = self.target_carrier.radius * 2.0
            target_x = self.target_carrier.world_x - carrier_direction_x * hold_distance
            target_y = self.target_carrier.world_y - carrier_direction_y * hold_distance
            
            # Move toward hold position with dampening
            hold_speed = 80 * dt
            self.world_x += (target_x - self.world_x) * hold_speed * 0.1
            self.world_y += (target_y - self.world_y) * hold_speed * 0.1
            
            # Gradually reduce velocity during alignment
            self.velocity_x *= 0.95
            self.velocity_y *= 0.95
            
            # Check if we're aligned within tolerance
            # Use tighter tolerance for more precise alignment
            alignment_tolerance = 10  # 10 degree tolerance
            if abs(rotation_diff) < alignment_tolerance:
                # Count time spent in aligned state
                if not hasattr(self, 'alignment_hold_timer'):
                    self.alignment_hold_timer = 0.0
                
                self.alignment_hold_timer += dt
                
                # Only proceed after maintaining alignment for a short period
                # This prevents premature transition if we're just passing through alignment
                if self.alignment_hold_timer >= 0.5:  # Half second of stable alignment
                    print(f"Fighter {id(self)} aligned with carrier, moving to land stage")
                    self.landing_stage = "land"
                    self.landing_timer = 0.0
                    
                    # Disable collision detection during landing phase
                    self.collision_enabled = False
                    print(f"Fighter {id(self)} disabled collision detection for landing")
            else:
                # Reset alignment timer if we're not aligned
                if hasattr(self, 'alignment_hold_timer'):
                    self.alignment_hold_timer = 0.0
                
        elif self.landing_stage == "land":
            # Calculate landing path - smooth curve to carrier center
            # Start with direct vector to carrier
            direct_x = self.target_carrier.world_x - self.world_x
            direct_y = self.target_carrier.world_y - self.world_y
            
            # Add carrier's direction vector to create a curved approach
            carrier_direction_x = self.target_carrier.get_direction_x()
            carrier_direction_y = self.target_carrier.get_direction_y()
            
            # Blend between direct approach and carrier direction based on distance
            # This creates a curved landing path that aligns with carrier direction
            curve_factor = min(1.0, distance_to_carrier / (self.target_carrier.radius * 2))
            approach_x = direct_x - carrier_direction_x * self.target_carrier.radius * curve_factor
            approach_y = direct_y - carrier_direction_y * self.target_carrier.radius * curve_factor
            
            # Normalize and apply landing speed with easing
            # Slower as we get closer to create smooth deceleration
            approach_distance = math.hypot(approach_x, approach_y)
            distance_factor = min(1.0, distance_to_carrier / (self.target_carrier.radius * 1.5))
            landing_speed = (80 + 80 * distance_factor) * dt  # Variable speed based on distance
            
            if approach_distance > 0:  # Avoid division by zero
                self.world_x += (approach_x / approach_distance) * landing_speed
                self.world_y += (approach_y / approach_distance) * landing_speed
            
            # Set velocity for visual effects (engine flare)
            # Blend between approach vector and carrier direction
            self.velocity_x = -carrier_direction_x * 30 * (1 - distance_factor) + direct_x * 0.2 * distance_factor
            self.velocity_y = -carrier_direction_y * 30 * (1 - distance_factor) + direct_y * 0.2 * distance_factor
            
            # Apply carrier velocity to match speed
            self.velocity_x += self.target_carrier.velocity_x
            self.velocity_y += self.target_carrier.velocity_y
            
            # Create smooth fade-out effect based on distance
            # Faster fade as we get closer to carrier
            fade_progress = 1.0 - min(1.0, distance_to_carrier / (self.target_carrier.radius * 1.2))
            target_opacity = int(255 * (1.0 - fade_progress * fade_progress))  # Quadratic easing
            
            # Smooth transition to target opacity
            opacity_change = int(255 * dt * 2.0)  # Cap the rate of change
            if self.opacity > target_opacity:
                self.opacity = max(target_opacity, self.opacity - opacity_change)
            else:
                self.opacity = min(target_opacity, self.opacity + opacity_change)
            
            # Less verbose debug output
            if random.random() < 0.05:  # Only print occasionally
                print(f"Fighter {id(self)} landing - distance: {distance_to_carrier:.1f}, opacity: {self.opacity}")
            
            # Check if close enough to carrier to be stored
            # Use distance or opacity thresholds
            if distance_to_carrier <= self.target_carrier.radius * 0.6 or self.opacity <= 30:
                print(f"Fighter {id(self)} close enough to carrier, moving to store stage")
                self.landing_stage = "store"
                
        elif self.landing_stage == "store":
            # Keep collision detection disabled during storage
            self.collision_enabled = False
            
            # Make sure fighter is completely invisible before storing
            self.opacity = 0
            
            print(f"Fighter {id(self)} attempting to store in carrier {id(self.target_carrier)}")
            # Try to store the fighter in the carrier
            store_success = self.target_carrier.store_fighter(self)
            print(f"Fighter storage attempt result: {store_success}")
            
            if store_success:
                # Reset state since the fighter is now stored
                self.is_returning_to_carrier = False
                self.target_carrier = None
                self.landing_stage = "idle"  # Reset to idle state
                self.opacity = 0  # Completely invisible
                self.landing_complete = True  # Mark for removal from active units
                print(f"Fighter {id(self)} has been stored in carrier, ready for removal")
                # Main loop will need to remove this fighter from the active units list
            else:
                print(f"WARNING: Failed to store fighter in carrier - may be at capacity")
                # If storage failed (carrier at capacity), cancel return
                self.is_returning_to_carrier = False
                self.target_carrier = None
                self.landing_stage = "idle"
                self.opacity = 255  # Make visible again
                # Re-enable collision detection
                self.collision_enabled = True
                # Move away from carrier to prevent collision
                self.move_to_point(self.world_x + 100, self.world_y + 100)

class EnemyUnit(Unit):
    def __init__(self, world_x: int, world_y: int):
        super().__init__(world_x, world_y, unit_type='enemy')
        # Enemy units have limited vision
        self.vision_radius = 80  # Reduced vision radius for enemy units
