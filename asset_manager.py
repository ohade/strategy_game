"""Asset manager for handling game resource loading and access.

This module provides functionality to load, manage, and access game assets
such as ship sprites, background images, and effect animations.
"""
import os
import random
from typing import Dict, List, Tuple, Optional, Union, Any

import pygame

# Define asset paths relative to the main module
BASE_PATH = os.path.join(os.path.dirname(__file__), 'assets')
SHIPS_PATH = os.path.join(BASE_PATH, 'ships')
BACKGROUNDS_PATH = os.path.join(BASE_PATH, 'backgrounds')
EFFECTS_PATH = os.path.join(BASE_PATH, 'effects')


def load_image(filename: str, scale: float = 1.0) -> pygame.Surface:
    """Load an image and convert it to a format optimized for blitting.
    
    Args:
        filename: Path to the image file
        scale: Scale factor to resize the image (1.0 = original size)
        
    Returns:
        Loaded and prepared pygame.Surface
    
    Raises:
        FileNotFoundError: If the image file doesn't exist
    """
    # Determine the full path based on the filename
    if os.path.isabs(filename):
        filepath = filename
    else:
        # Check in each asset directory
        for path in [SHIPS_PATH, BACKGROUNDS_PATH, EFFECTS_PATH]:
            full_path = os.path.join(path, filename)
            if os.path.exists(full_path):
                filepath = full_path
                break
        else:  # No break occurred, file not found
            filepath = os.path.join(BASE_PATH, filename)
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Image file not found: {filename}")

    # Load the image and convert for optimized blitting
    try:
        image = pygame.image.load(filepath).convert_alpha()
        
        # Scale if needed
        if scale != 1.0:
            new_width = int(image.get_width() * scale)
            new_height = int(image.get_height() * scale)
            image = pygame.transform.smoothscale(image, (new_width, new_height))
            
        return image
    except pygame.error as e:
        raise IOError(f"Error loading image {filepath}: {e}")


def load_animation(pattern: str, frame_count: int, scale: float = 1.0) -> List[pygame.Surface]:
    """Load a sequence of images for animation.
    
    Args:
        pattern: Filename pattern with '{}' placeholder for frame number
        frame_count: Number of frames to load
        scale: Scale factor for the images
        
    Returns:
        List of loaded pygame.Surface objects
    """
    frames = []
    for i in range(frame_count):
        filename = pattern.format(i)
        frames.append(load_image(filename, scale))
    return frames


class AssetManager:
    """Manages all game assets including sprites, backgrounds, and animations."""
    
    def __init__(self) -> None:
        """Initialize the asset manager with empty collections."""
        self.ship_sprites: Dict[str, pygame.Surface] = {}
        self.background_layers: List[Dict[str, Any]] = []
        self.effect_animations: Dict[str, List[pygame.Surface]] = {}
        
        # Flag to track initialization state
        self._initialized = False
    
    def initialize(self) -> None:
        """Load all game assets."""
        if self._initialized:
            return
            
        self.load_ship_sprites()
        self.load_background_layers()
        self.load_effect_animations()
        
        self._initialized = True
    
    def load_ship_sprites(self) -> None:
        """Load ship sprites for different unit types."""
        # Load ship sprites
        try:
            self.ship_sprites['friendly'] = load_image('friendly_ship.png', scale=1.0)
            self.ship_sprites['enemy'] = load_image('enemy_ship.png', scale=1.0)
        except FileNotFoundError:
            # Use placeholder graphics if files don't exist yet
            print("Ship sprite files not found, using placeholder graphics")
            self._create_placeholder_sprites()
    
    def _create_placeholder_sprites(self) -> None:
        """Create placeholder sprites for development."""
        # Create surfaces for the ships
        friendly_ship = pygame.Surface((30, 30), pygame.SRCALPHA)
        enemy_ship = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        # Draw a green triangle for friendly ships
        pygame.draw.polygon(friendly_ship, (0, 255, 0), [(30, 15), (0, 0), (0, 30)])
        
        # Draw a red triangle for enemy ships
        pygame.draw.polygon(enemy_ship, (255, 0, 0), [(0, 15), (30, 0), (30, 30)])
        
        # Store the placeholder sprites
        self.ship_sprites['friendly'] = friendly_ship
        self.ship_sprites['enemy'] = enemy_ship
    
    def load_background_layers(self) -> None:
        """Load background layers for parallax scrolling effect."""
        try:
            # Load background layers with different parallax factors
            # Layer 0: Stars (furthest, slowest)
            stars = load_image('stars.png', scale=1.0)
            self.background_layers.append({
                'surface': stars,
                'parallax_factor': 0.2,  # Moves at 20% of camera speed
                'repeat_x': True,
                'repeat_y': True
            })
            
            # Layer 1: Nebula
            nebula = load_image('nebula.png', scale=1.0)
            self.background_layers.append({
                'surface': nebula,
                'parallax_factor': 0.4,  # Moves at 40% of camera speed
                'repeat_x': True,
                'repeat_y': False
            })
            
            # Layer 2: Planets (closest, fastest)
            planets = load_image('planets.png', scale=1.0)
            self.background_layers.append({
                'surface': planets,
                'parallax_factor': 0.6,  # Moves at 60% of camera speed
                'repeat_x': False,
                'repeat_y': False
            })
            
        except FileNotFoundError:
            # Use placeholder background if files don't exist yet
            print("Background layer files not found, using placeholder graphics")
            self._create_placeholder_backgrounds()
    
    def _create_placeholder_backgrounds(self) -> None:
        """Create placeholder background layers for development."""
        # Create surfaces with different colors
        screen_width, screen_height = 1600, 1200  # Large enough to cover screen
        
        # Layer 0: Stars (black with white dots)
        stars = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        stars.fill((0, 0, 20, 255))  # Dark blue
        
        # Add random stars in a much simpler way - REDUCED DENSITY
        for _ in range(150):  # Reduced from 500 stars to 150
            # Simply use random positions across the screen
            x = int(random.random() * screen_width)
            y = int(random.random() * screen_height)
            
            # Vary star size and brightness
            size = int(random.random() * 1.5) + 1  # Slightly smaller stars
            brightness = int(random.random() * 35) + 180  # Less bright
            color = (brightness, brightness, brightness)
            
            pygame.draw.circle(stars, color, (x, y), size)
        
        self.background_layers.append({
            'surface': stars,
            'parallax_factor': 0.2,
            'repeat_x': True,
            'repeat_y': True
        })
        
        # Layer 1: Nebula (blue/purple clouds) - REDUCED DENSITY
        nebula = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        for _ in range(8):  # Reduced from 20 to 8
            # Create cloud-like shapes with transparency
            cloud_size = int(random.random() * 250) + 80  # Slightly smaller
            x = int(random.random() * screen_width)
            y = int(random.random() * screen_height)
            
            # Random blue/purple hue - more subtle
            r = int(random.random() * 50)  # Less red
            g = int(random.random() * 30)  # Less green
            b = int(random.random() * 100) + 80  # Less intense blue
            alpha = int(random.random() * 15) + 5  # More transparent
            
            cloud_surf = pygame.Surface((cloud_size, cloud_size), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud_surf, (r, g, b, alpha), (0, 0, cloud_size, cloud_size))
            nebula.blit(cloud_surf, (x - cloud_size//2, y - cloud_size//2))
        
        self.background_layers.append({
            'surface': nebula,
            'parallax_factor': 0.4,
            'repeat_x': True,
            'repeat_y': False
        })
        
        # Layer 2: Planets - REDUCED DENSITY
        planets = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        # Reduce number of planets for less visual noise
        for _ in range(1):  # Just one planet to reduce visual noise
            # Create smaller planets
            planet_size = int(random.random() * 80) + 30  # Reduced size
            
            # Position planets away from the edges to reduce flickering during zoom
            margin = planet_size * 2
            x = int(random.random() * (screen_width - 2 * margin)) + margin
            y = int(random.random() * (screen_height - 2 * margin)) + margin
            
            # More muted colors
            r = int(random.random() * 180)
            g = int(random.random() * 180)
            b = int(random.random() * 180)
            
            # Add some transparency to the planet
            pygame.draw.circle(planets, (r, g, b, 200), (x, y), planet_size)
            
            # Less chance of rings
            if random.random() > 0.7:  # 30% chance instead of 50%
                ring_width = int(planet_size * 0.5)  # Thinner rings
                pygame.draw.ellipse(planets, (r//2, g//2, b//2, 80), 
                                   (x - planet_size - ring_width//2, 
                                    y - planet_size//3,
                                    planet_size*2 + ring_width, 
                                    planet_size*2//3), 
                                   width=max(1, ring_width//4))  # Thinner lines
        
        self.background_layers.append({
            'surface': planets,
            'parallax_factor': 0.6,
            'repeat_x': False,
            'repeat_y': False
        })
    
    def load_effect_animations(self) -> None:
        """Load effect animations (explosions, lasers, etc.)."""
        try:
            # Load explosion animation
            self.effect_animations['explosion'] = load_animation(
                'explosion_{}.png', 5, scale=1.0
            )
            
            # Load laser animation
            self.effect_animations['laser'] = load_animation(
                'laser_{}.png', 3, scale=1.0
            )
            
        except FileNotFoundError:
            # Use placeholder animations if files don't exist yet
            print("Effect animation files not found, using placeholder graphics")
            self._create_placeholder_animations()
    
    def _create_placeholder_animations(self) -> None:
        """Create placeholder animations for development."""
        # Create explosion animation frames
        explosion_frames = []
        for i in range(5):
            size = 30 + i * 10  # Increasing size
            frame = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Orange/yellow circle with decreasing opacity
            opacity = 255 - i * 40
            pygame.draw.circle(frame, (255, 165, 0, opacity), (size//2, size//2), size//2)
            
            explosion_frames.append(frame)
        
        self.effect_animations['explosion'] = explosion_frames
        
        # Create laser animation frames
        laser_frames = []
        for i in range(3):
            frame = pygame.Surface((30, 5), pygame.SRCALPHA)
            
            # Alternate blue colors
            if i % 2 == 0:
                color = (0, 0, 255, 200)
            else:
                color = (100, 100, 255, 200)
                
            pygame.draw.rect(frame, color, (0, 0, 30, 5))
            laser_frames.append(frame)
            
        self.effect_animations['laser'] = laser_frames


# Global instance for easy access
_asset_manager = AssetManager()


def get_asset_manager() -> AssetManager:
    """Get the global asset manager instance.
    
    Returns:
        The global AssetManager instance
    """
    global _asset_manager
    if not _asset_manager._initialized:
        _asset_manager.initialize()
    return _asset_manager


def get_ship_sprite(unit_type: str) -> pygame.Surface:
    """Get a ship sprite for the specified unit type.
    
    Args:
        unit_type: Type of unit ('friendly' or 'enemy')
        
    Returns:
        The appropriate ship sprite
        
    Raises:
        ValueError: If the unit type is not recognized
    """
    manager = get_asset_manager()
    
    if unit_type not in manager.ship_sprites:
        raise ValueError(f"Unknown unit type: {unit_type}")
        
    return manager.ship_sprites[unit_type]


def get_background_layers() -> List[Dict[str, Any]]:
    """Get the background layers for parallax scrolling.
    
    Returns:
        List of background layers with their properties
    """
    return get_asset_manager().background_layers


def get_background_layer(layer_index: int) -> pygame.Surface:
    """Get a specific background layer by index.
    
    Args:
        layer_index: The index of the background layer to retrieve
        
    Returns:
        The background layer surface
        
    Raises:
        IndexError: If the layer index is out of range
    """
    manager = get_asset_manager()
    
    if layer_index < 0 or layer_index >= len(manager.background_layers):
        # If we don't have enough layers, create a placeholder
        color = (10, 10, 30)  # Very dark blue
        if layer_index == 0:  # Farthest layer (stars)
            color = (0, 0, 20)  # Almost black
        elif layer_index == 1:  # Middle layer (nebulae)
            color = (20, 10, 40)  # Dark purple
        elif layer_index == 2:  # Closest layer (planets/asteroids)
            color = (30, 30, 50)  # Medium dark blue
            
        # Create a placeholder surface
        surface = pygame.Surface((800, 600), pygame.SRCALPHA)
        surface.fill(color)
        
        # Add some random dots
        for _ in range(50 + layer_index * 20):
            x = pygame.time.get_ticks() % 800  # Use time for "random" but deterministic positions
            y = (pygame.time.get_ticks() * (layer_index + 1)) % 600
            radius = 1 if layer_index == 0 else 2 if layer_index == 1 else 3
            brightness = 100 + layer_index * 50
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), radius)
            
        return surface
        
    return manager.background_layers[layer_index]['surface']


def get_effect_animation(effect_type: str) -> List[pygame.Surface]:
    """Get the animation frames for an effect type.
    
    Args:
        effect_type: Type of effect ('explosion', 'laser', etc.)
        
    Returns:
        List of animation frames
        
    Raises:
        ValueError: If the effect type is not recognized
    """
    manager = get_asset_manager()
    
    if effect_type not in manager.effect_animations:
        raise ValueError(f"Unknown effect type: {effect_type}")
        
    return manager.effect_animations[effect_type]
