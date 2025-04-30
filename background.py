from __future__ import annotations
import pygame
import random
from camera import Camera

class Background:
    """Manages the game background visuals (starfield and grid)."""

    def __init__(self, map_width: int, map_height: int, grid_size: int = 200):
        """Initialize the background.

        Args:
            map_width (int): Width of the game world.
            map_height (int): Height of the game world.
            grid_size (int): Size of grid cells in pixels.
        """
        self.map_width = map_width
        self.map_height = map_height
        self.grid_size = grid_size
        
        # Create a starfield background
        self.stars: list[tuple[int, int, int, int]] = []  # x, y, radius, brightness
        self.generate_stars(300)  # Generate 300 stars
        
    def generate_stars(self, num_stars: int) -> None:
        """Generate random stars for the background.
        
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
        """Draw the background elements.
        
        Args:
            surface (pygame.Surface): Surface to draw on.
            camera (Camera): Camera for position calculations.
        """
        # Draw visible stars
        for star_x, star_y, radius, brightness in self.stars:
            # Check if star is in the currently visible area
            if (camera.camera_rect.left <= star_x <= camera.camera_rect.right and 
                camera.camera_rect.top <= star_y <= camera.camera_rect.bottom):
                
                # Convert to screen coordinates
                screen_x, screen_y = camera.apply_coords(star_x, star_y)
                
                # Draw the star
                color = (brightness, brightness, brightness)
                pygame.draw.circle(surface, color, (screen_x, screen_y), radius)
        
        # Draw grid
        self.draw_grid(surface, camera)
                
    def draw_grid(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw a coordinate grid.
        
        Args:
            surface (pygame.Surface): Surface to draw on.
            camera (Camera): Camera for position calculations.
        """
        # Calculate the visible area of the map
        visible_left = camera.camera_rect.left
        visible_top = camera.camera_rect.top
        visible_right = camera.camera_rect.right
        visible_bottom = camera.camera_rect.bottom
        
        # Find the grid lines that are visible
        start_x = (visible_left // self.grid_size) * self.grid_size
        start_y = (visible_top // self.grid_size) * self.grid_size
        
        # Grid colors
        grid_color = (40, 40, 40)  # Dark gray
        
        # Draw vertical grid lines
        x = start_x
        while x <= visible_right:
            start_screen_x, start_screen_y = camera.apply_coords(x, visible_top)
            end_screen_x, end_screen_y = camera.apply_coords(x, visible_bottom)
            pygame.draw.line(surface, grid_color, (start_screen_x, start_screen_y), 
                           (end_screen_x, end_screen_y), 1)
            x += self.grid_size
            
        # Draw horizontal grid lines
        y = start_y
        while y <= visible_bottom:
            start_screen_x, start_screen_y = camera.apply_coords(visible_left, y)
            end_screen_x, end_screen_y = camera.apply_coords(visible_right, y)
            pygame.draw.line(surface, grid_color, (start_screen_x, start_screen_y), 
                           (end_screen_x, end_screen_y), 1)
            y += self.grid_size
