"""Module for handling parallax background effects in the game."""
from __future__ import annotations
import pygame
import random
from typing import List, Tuple, Optional

from camera import Camera
from asset_manager import get_background_layer


class ParallaxBackground:
    """Manages multi-layered parallax scrolling background for the game."""

    def __init__(self, map_width: int, map_height: int, num_layers: int = 3, grid_size: int = 200):
        """Initialize the parallax background system.

        Args:
            map_width (int): Width of the game world.
            map_height (int): Height of the game world.
            num_layers (int): Number of parallax layers (from farthest to nearest).
            grid_size (int): Size of grid cells in pixels.
        """
        self.map_width = map_width
        self.map_height = map_height
        self.grid_size = grid_size
        self.num_layers = num_layers
        
        # Background layer images
        self.layers: List[Optional[pygame.Surface]] = []
        
        # Initialize layers with decreasing parallax factor (farthest to nearest)
        self.parallax_factors: List[float] = []
        
        # Try to load the background layers
        try:
            for i in range(num_layers):
                # Load layer image from asset manager
                layer_surface = get_background_layer(i)
                self.layers.append(layer_surface)
                
                # Parallax factor: determines how fast this layer moves relative to camera
                # Farthest layer (index 0) moves the slowest, nearest layer moves fastest
                # Values from 0.1 (very slow, distant stars) to 0.9 (closer nebulae)
                parallax_factor = 0.1 + (i * 0.3)  
                self.parallax_factors.append(parallax_factor)
                
            # If we successfully loaded layers, we don't need stars
            self.using_layers = True
        except Exception as e:
            print(f"Failed to load background layers: {e}. Falling back to star generation.")
            self.using_layers = False
            # Create a starfield background as fallback
            self.stars: list[tuple[int, int, int, int]] = []  # x, y, radius, brightness
            self.generate_stars(300)  # Generate 300 stars
    
    def generate_stars(self, num_stars: int) -> None:
        """Generate random stars for the background as a fallback.
        
        Args:
            num_stars (int): Number of stars to generate.
        """
        self.stars.clear()
        for _ in range(num_stars):
            x = random.randint(0, self.map_width)
            y = random.randint(0, self.map_height)
            radius = random.choice([1, 1, 1, 2, 2, 3])  # Weighted towards smaller stars
            brightness = random.randint(100, 255)
            self.stars.append((x, y, radius, brightness))
            
    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the visible background layers with parallax scrolling.

        Args:
            surface (pygame.Surface): The surface to draw on (the screen).
            camera (Camera): The camera object providing the view offset and zoom.
        """
        if self.using_layers:
            self._draw_parallax_layers(surface, camera)
        else:
            self._draw_stars_and_grid(surface, camera)
    
    def _draw_parallax_layers(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the layered background with parallax effect.
        
        Args:
            surface (pygame.Surface): The surface to draw on.
            camera (Camera): The camera object.
        """
        # Get the visible area in world coordinates
        world_view = camera.get_world_view()
        screen_width, screen_height = surface.get_width(), surface.get_height()
        
        # Draw each layer with its parallax factor
        for i, (layer, factor) in enumerate(zip(self.layers, self.parallax_factors)):
            if layer is None:
                continue
            
            # Calculate parallax offset based on camera position and layer's parallax factor
            # Use floor division to stabilize integer positions and prevent flickering
            # This ensures consistent rounding during zoom operations
            parallax_x = int(-(camera.world_x * factor))
            parallax_y = int(-(camera.world_y * factor))
            
            # Scale the layer based on zoom level to provide better stability
            # This helps prevent flickering during zoom as it maintains proportional scaling
            scaled_layer = layer
            if camera.zoom_level != 1.0:
                # Only scale if zoom level is not default
                # The scaling here helps ensure that layers maintain proper parallax during zoom
                orig_width, orig_height = layer.get_width(), layer.get_height()
                scale_factor = 1.0  # Use a consistent base scale factor to avoid recalculation artifacts
                layer_width = max(1, int(orig_width * scale_factor))
                layer_height = max(1, int(orig_height * scale_factor))
                
                # Avoid scaling if dimensions haven't changed (saves performance)
                if layer_width != orig_width or layer_height != orig_height:
                    scaled_layer = pygame.transform.smoothscale(layer, (layer_width, layer_height))
            
            # Get layer dimensions after potential scaling
            layer_width, layer_height = scaled_layer.get_width(), scaled_layer.get_height()
            
            # Calculate how many times we need to tile to cover the screen with a buffer zone
            # The +3 ensures coverage during scrolling and provides a safety margin
            tiles_x = (screen_width // layer_width) + 3
            tiles_y = (screen_height // layer_height) + 3
            
            # Calculate the starting position for tiling
            # The modulo operation ensures smooth wrapping of the background
            start_x = parallax_x % layer_width
            # Adjust for negative offsets to maintain seamless wrapping
            if start_x > 0:
                start_x -= layer_width
                
            start_y = parallax_y % layer_height
            if start_y > 0:
                start_y -= layer_height
            
            # Draw the tiled background with adjusted positions
            for y in range(tiles_y):
                for x in range(tiles_x):
                    pos_x = start_x + (x * layer_width)
                    pos_y = start_y + (y * layer_height)
                    # Only draw tiles that are visible (optimization)
                    if (-layer_width <= pos_x <= screen_width and
                            -layer_height <= pos_y <= screen_height):
                        surface.blit(scaled_layer, (pos_x, pos_y))
    
    def _draw_stars_and_grid(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the stars and grid as a fallback if layer images are unavailable.
        
        Args:
            surface (pygame.Surface): The surface to draw on.
            camera (Camera): The camera object.
        """
        # Get the visible area in world coordinates
        world_view = camera.get_world_view()

        # Draw stars
        for star in self.stars:
            star_x, star_y, radius, brightness = star
            # Check if the star is within the camera's world view
            if world_view.collidepoint(star_x, star_y):
                # Convert world coords to screen coords using camera
                screen_x, screen_y = camera.apply_coords(star_x, star_y)
                # Simple check if screen coords are within screen bounds (optional redundancy)
                if 0 <= screen_x < surface.get_width() and 0 <= screen_y < surface.get_height():
                    pygame.draw.circle(
                        surface, 
                        (brightness, brightness, brightness), 
                        (screen_x, screen_y), 
                        radius
                    )

        # Draw grid lines (optional, can be performance intensive)
        # Draw vertical lines
        start_x = (world_view.left // self.grid_size) * self.grid_size
        for x in range(int(start_x), int(world_view.right), self.grid_size):
            screen_x1, screen_y1 = camera.apply_coords(x, world_view.top)
            screen_x2, screen_y2 = camera.apply_coords(x, world_view.bottom)
            # Clip lines to screen bounds if necessary
            screen_y1 = max(0, min(screen_y1, surface.get_height()))
            screen_y2 = max(0, min(screen_y2, surface.get_height()))
            if 0 <= screen_x1 < surface.get_width(): # Only draw if visible on screen X
                pygame.draw.line(surface, (40, 40, 40), (screen_x1, screen_y1), (screen_x2, screen_y2), 1)

        # Draw horizontal lines
        start_y = (world_view.top // self.grid_size) * self.grid_size
        for y in range(int(start_y), int(world_view.bottom), self.grid_size):
            screen_x1, screen_y1 = camera.apply_coords(world_view.left, y)
            screen_x2, screen_y2 = camera.apply_coords(world_view.right, y)
            # Clip lines to screen bounds
            screen_x1 = max(0, min(screen_x1, surface.get_width()))
            screen_x2 = max(0, min(screen_x2, surface.get_width()))
            if 0 <= screen_y1 < surface.get_height(): # Only draw if visible on screen Y
                pygame.draw.line(surface, (40, 40, 40), (screen_x1, screen_y1), (screen_x2, screen_y2), 1)
