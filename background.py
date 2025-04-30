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
        """Draw the visible stars and grid lines based on camera position.

        Args:
            surface (pygame.Surface): The surface to draw on (the screen).
            camera (Camera): The camera object providing the view offset and zoom.
        """
        # Get the visible area in world coordinates
        world_view = camera.get_world_view()

        # Draw stars
        for star in self.stars:
            star_x, star_y, _, brightness = star
            # Check if the star is within the camera's world view
            if world_view.collidepoint(star_x, star_y):
                # Convert world coords to screen coords using camera
                screen_x, screen_y = camera.apply_coords(star_x, star_y)
                # Simple check if screen coords are within screen bounds (optional redundancy)
                if 0 <= screen_x < surface.get_width() and 0 <= screen_y < surface.get_height():
                    pygame.draw.circle(surface, (brightness, brightness, brightness), (screen_x, screen_y), star[2])

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
