"""
Carrier class implementation for the strategy game.

This module provides the Carrier class, which represents a large capital ship
that can store and launch fighter units. The visual design is inspired by
Battlestar Galactica.
"""
from __future__ import annotations
import pygame
import math
import random
import os
from typing import Optional, Tuple, Union, List, Dict, Any

from units import FriendlyUnit, Unit
from effects import AttackEffect
from camera import Camera
from constants import SCREEN_WIDTH, SCREEN_HEIGHT  # Import screen dimensions for scaling
from asset_manager import load_image  # Import the image loading function

def get_carrier_sprite() -> pygame.Surface:
    """Load a high-detailed Battlestar Galactica-inspired carrier sprite.
    
    Returns:
        A pygame Surface with the carrier's appearance, properly sized and oriented
    """
    # Try to load the high-detailed carrier PNG
    try:
        # Load the carrier image from the assets/ships directory with 70% reduced size (scale=0.3)
        sprite = load_image(os.path.join('ships', 'carrier.png'), scale=0.3)
        return sprite
    except (FileNotFoundError, IOError) as e:
        # If the image can't be loaded, generate a fallback sprite
        print(f"Warning: Could not load carrier image: {e}")
        return generate_fallback_carrier_sprite()

def generate_fallback_carrier_sprite() -> pygame.Surface:
    """Generate a fallback sprite that resembles Battlestar Galactica if the PNG is not available.
    
    Returns:
        A pygame Surface with the carrier's appearance
    """
    # Create a base surface for the carrier
    # Battlestar Galactica has an elongated rectangular shape with details
    width, height = 240, 80  # Larger carrier dimensions
    
    # Create a surface with per-pixel alpha
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Main hull color - dark gray with slight blue tint
    hull_color = (70, 75, 80, 255)
    
    # Draw the main hull (elongated shape)
    pygame.draw.polygon(surface, hull_color, [
        (10, height//2),             # Front point
        (25, height//4),             # Upper front edge
        (width-30, height//4),       # Upper rear edge
        (width-20, height//8),       # Upper rear point
        (width-5, height//3),        # Upper engine section
        (width-5, height*2//3),      # Lower engine section
        (width-20, height*7//8),     # Lower rear point
        (width-30, height*3//4),     # Lower rear edge
        (25, height*3//4),           # Lower front edge
    ])
    
    # Command center (conning tower) - inspired by Galactica's raised section
    command_color = (60, 65, 70, 255)
    pygame.draw.polygon(surface, command_color, [
        (width//3, height//4),       # Front top
        (width*2//3, height//4),     # Rear top
        (width*2//3, height//8),     # Rear upper
        (width//3, height//8),       # Front upper
    ])
    
    # Flight pods (two rectangular sections on sides)
    pod_color = (80, 85, 90, 255)
    
    # Upper flight pod
    pygame.draw.rect(surface, pod_color, 
                    (width//4, height//8 - 10, width//2, 8))
    
    # Lower flight pod
    pygame.draw.rect(surface, pod_color, 
                    (width//4, height*7//8 + 2, width//2, 8))
    
    # Add details - windows, lights, etc.
    
    # Small windows along the hull
    window_color = (180, 200, 220, 200)
    for i in range(8):
        x_pos = width//4 + i * width//16
        # Upper windows
        pygame.draw.rect(surface, window_color, (x_pos, height//3, 2, 1))
        # Lower windows
        pygame.draw.rect(surface, window_color, (x_pos, height*2//3, 2, 1))
    
    # Engine glow
    engine_color = (100, 150, 255, 150)
    pygame.draw.rect(surface, engine_color, 
                    (width-8, height//3 + 2, 3, height//3 - 4))
    
    # Flight deck lights
    light_color = (255, 255, 200, 200)
    for i in range(5):
        # Upper flight deck lights
        pygame.draw.rect(surface, light_color, 
                        (width//4 + i * width//10, height//8 - 6, 3, 2))
        # Lower flight deck lights
        pygame.draw.rect(surface, light_color, 
                        (width//4 + i * width//10, height*7//8 + 4, 3, 2))
    
    # Add some random small details for texture
    detail_color = (90, 95, 100, 255)
    for _ in range(15):
        x = random.randint(width//5, width-20)
        y = random.randint(height//4 + 2, height*3//4 - 2)
        size = random.randint(1, 3)
        pygame.draw.rect(surface, detail_color, (x, y, size, size))
    
    return surface

class Carrier(FriendlyUnit):
    """A large capital ship that can store and launch fighter units.
    
    The Carrier is based on the Battlestar Galactica design and has
    extended capabilities compared to regular units, including higher
    health, more momentum, and the ability to store fighter units.
    """
    
    def __init__(self, world_x: int, world_y: int):
        """Initialize a carrier unit.
        
        Args:
            world_x: X position in world coordinates
            world_y: Y position in world coordinates
        """
        super().__init__(world_x, world_y)
        
        # Override basic Unit properties with carrier-specific values
        
        # Size and health - reduced by 90%
        self.radius = 50  # Reduced size (was 100, reduced by 90% = 10, but keep a bit larger than regular units)
        self.hp = 500     # Health still higher than regular units
        self.hp_max = 500
        
        # Combat attributes
        self.attack_range = 300    # Longer range weapons
        self.attack_power = 40     # Stronger attacks
        self.attack_cooldown = 2.0  # Slower firing rate
        
        # Physics and movement (slower, more momentum)
        self.mass = 10.0           # Mass for collision calculations
        self.max_speed = 50        # Slower than regular units
        self.acceleration = 50     # Less acceleration
        self.max_rotation_speed = 45  # Slower rotation
        
        # Carrier-specific attributes
        self.fighter_capacity = 10  # Maximum number of fighters it can hold
        self.stored_fighters = []   # List to track stored fighters
        self.launch_points = [      # Points where fighters launch from (relative to carrier)
            (self.radius, 0),       # Right side
            (-self.radius, 0),      # Left side
            (0, self.radius),       # Bottom
            (0, -self.radius)       # Top
        ]
        
        # Carrier state tracking
        self.is_launching = False
        self.is_recovering = False
        self.current_operation = None  # Track current launch/recover operation
        
        # Custom sprite flag
        self.has_custom_sprite = True
    
    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the carrier with its custom sprite.
        
        Args:
            surface: The pygame surface to draw on
            camera: The game camera for coordinate conversion
        """
        # Calculate screen position
        screen_pos = camera.apply_coords(int(self.draw_x), int(self.draw_y))
        
        # Get or generate the carrier sprite
        sprite = get_carrier_sprite()
        
        # Calculate the rotation for the sprite
        # Add 180 degrees to the rotation because the ship's front is to the right
        # This makes the movement direction match the ship's actual orientation
        adjusted_rotation = -self.rotation + 180
        rotated_sprite = pygame.transform.rotate(sprite, adjusted_rotation)
        
        # Get the rect for the rotated sprite to center it properly
        sprite_rect = rotated_sprite.get_rect(center=screen_pos)
        
        # Draw the sprite
        surface.blit(rotated_sprite, sprite_rect)
        
        # Draw selection indicator if selected
        if self.selected:
            pygame.draw.circle(surface, (0, 255, 0), screen_pos, self.radius + 5, 2)
        elif self.preview_selected:
            pygame.draw.circle(surface, (0, 200, 0), screen_pos, self.radius + 5, 1)
        
        # Draw health bar
        health_bar_width = self.radius * 2
        health_bar_height = 6
        health_percent = self.hp / self.hp_max
        
        bar_top = screen_pos[1] + self.radius + 10
        
        # Background (black/dark gray)
        pygame.draw.rect(surface, (50, 50, 50), 
                        (screen_pos[0] - health_bar_width//2, 
                         bar_top, 
                         health_bar_width, 
                         health_bar_height))
        
        # Health remaining (green)
        pygame.draw.rect(surface, (0, 200, 0), 
                        (screen_pos[0] - health_bar_width//2, 
                         bar_top, 
                         int(health_bar_width * health_percent), 
                         health_bar_height))
        
        # Draw fighter capacity indicator
        if self.fighter_capacity > 0:
            capacity_bar_top = bar_top + health_bar_height + 2
            fighter_percent = len(self.stored_fighters) / self.fighter_capacity
            
            # Background (dark blue)
            pygame.draw.rect(surface, (20, 20, 80), 
                            (screen_pos[0] - health_bar_width//2, 
                             capacity_bar_top, 
                             health_bar_width, 
                             health_bar_height))
            
            # Fighters stored (light blue)
            pygame.draw.rect(surface, (50, 100, 255), 
                            (screen_pos[0] - health_bar_width//2, 
                             capacity_bar_top, 
                             int(health_bar_width * fighter_percent), 
                             health_bar_height))
    
    def update(self, dt: float) -> Optional[AttackEffect]:
        """Update carrier state and return any effects generated.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            AttackEffect or None
        """
        # Use the parent class update method for base unit functionality
        attack_effect = super().update(dt)
        
        # Carrier-specific update logic could go here
        # For now, we're just using the base Unit behavior
        
        # In our case, the carrier's sprite has the front to the right (opposite from normal units)
        # So we need to adjust the rotation by 180 degrees for movement to match the sprite orientation
        # Note: This doesn't change the actual rotation value used in game logic, just visually
        
        return attack_effect
    
    def store_fighter(self, fighter: Unit) -> bool:
        """Store a fighter unit in the carrier if there's capacity.
        
        Args:
            fighter: The fighter unit to store
            
        Returns:
            bool: True if successful, False if at capacity
        """
        if len(self.stored_fighters) < self.fighter_capacity:
            self.stored_fighters.append(fighter)
            # Could set the fighter to an "inactive" state here
            return True
        return False
    
    def launch_fighter(self, position: Optional[Tuple[float, float]] = None) -> Optional[Unit]:
        """Launch a stored fighter at the specified position.
        
        Args:
            position: Optional world position to launch the fighter at
                     If None, launches from a default launch point
                     
        Returns:
            The launched fighter unit or None if no fighters available
        """
        if not self.stored_fighters:
            return None
            
        fighter = self.stored_fighters.pop()
        
        # Determine launch position
        if position:
            fighter.world_x, fighter.world_y = position
        else:
            # Use one of the launch points
            launch_idx = len(self.stored_fighters) % len(self.launch_points)
            offset_x, offset_y = self.launch_points[launch_idx]
            
            # Convert from relative to world coordinates
            angle_rad = math.radians(self.rotation)
            rotated_x = offset_x * math.cos(angle_rad) - offset_y * math.sin(angle_rad)
            rotated_y = offset_x * math.sin(angle_rad) + offset_y * math.cos(angle_rad)
            
            fighter.world_x = self.world_x + rotated_x
            fighter.world_y = self.world_y + rotated_y
            
            # Set initial direction to match carrier's rotation
            fighter.rotation = self.rotation
        
        # Reactivate the fighter (in case we had deactivated it)
        fighter.set_state("idle")
        
        return fighter
