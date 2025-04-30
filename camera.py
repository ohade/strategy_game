import pygame
from typing import Tuple

class Camera:
    """Manages the game view's offset (scrolling) and zoom."""
    def __init__(self, width: int, height: int, map_width: int = 4000, map_height: int = 3000) -> None:
        """Initialize the camera.

        Args:
            width (int): Width of the camera's view (screen width).
            height (int): Height of the camera's view (screen height).
            map_width (int): Width of the game world/map.
            map_height (int): Height of the game world/map.

        Attributes:
            zoom_level (float): Current zoom level (1.0 = normal).
            min_zoom (float): Minimum allowed zoom level.
            max_zoom (float): Maximum allowed zoom level.
        """
        self.width = width
        self.height = height
        self.pan_speed = 500 # Pixels per second
        self.map_width = map_width
        self.map_height = map_height

        # Zoom attributes
        self.zoom_level = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 4.0

        # Camera position represents the top-left corner in world coordinates
        self.world_x = 0.0
        self.world_y = 0.0

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Update camera position based on keyboard input.

        Args:
            dt (float): Delta time (time since last frame in seconds).
            keys (pygame.key.ScancodeWrapper): Current state of all keyboard keys.
        """
        move_x = 0
        move_y = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= self.pan_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += self.pan_speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= self.pan_speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += self.pan_speed * dt

        # Adjust movement speed based on zoom (optional, might feel weird)
        # move_x /= self.zoom_level
        # move_y /= self.zoom_level

        self.world_x += move_x
        self.world_y += move_y

        # Add bounds checking to prevent camera from going outside the map
        self._apply_bounds()

    def _apply_bounds(self) -> None:
        """Ensure the camera view stays within the map boundaries."""
        # Calculate the visible world dimensions based on zoom
        visible_world_width = self.width / self.zoom_level
        visible_world_height = self.height / self.zoom_level

        # Ensure left edge doesn't go left of map edge (0)
        self.world_x = max(0.0, self.world_x)
        # Ensure top edge doesn't go above map edge (0)
        self.world_y = max(0.0, self.world_y)

        # Ensure right edge doesn't go beyond map's right edge
        if self.world_x + visible_world_width > self.map_width:
            self.world_x = self.map_width - visible_world_width
        # Ensure bottom edge doesn't go beyond map's bottom edge
        if self.world_y + visible_world_height > self.map_height:
            self.world_y = self.map_height - visible_world_height

        # Re-check bounds in case map is smaller than visible area at low zoom
        self.world_x = max(0.0, self.world_x)
        self.world_y = max(0.0, self.world_y)

    def apply(self, entity_rect: pygame.Rect) -> pygame.Rect:
        """Adjust an entity's screen position and size based on camera offset and zoom.

        Args:
            entity_rect (pygame.Rect): The entity's rect in world coordinates.

        Returns:
            pygame.Rect: The entity's rect adjusted for screen drawing.
        """

        # Scale position and size
        screen_x = (entity_rect.left - self.world_x) * self.zoom_level
        screen_y = (entity_rect.top - self.world_y) * self.zoom_level
        screen_width = entity_rect.width * self.zoom_level
        screen_height = entity_rect.height * self.zoom_level

        # Only return integer coords/sizes for the Rect
        return pygame.Rect(int(screen_x), int(screen_y), max(1, int(screen_width)), max(1, int(screen_height)))


    def apply_coords(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Adjust world coordinates to screen coordinates, considering zoom.

        Args:
            world_x (float): World x-coordinate.
            world_y (float): World y-coordinate.

        Returns:
            Tuple[int, int]: Screen coordinates.
        """

        screen_x = (world_x - self.world_x) * self.zoom_level
        screen_y = (world_y - self.world_y) * self.zoom_level
        return int(screen_x), int(screen_y)

    def apply_radius(self, radius: float) -> int:
        """Adjust a world radius to a screen radius based on zoom."""
        return max(1, int(radius * self.zoom_level))

    def screen_to_world_coords(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates back to world coordinates."""
        if self.zoom_level == 0: # Avoid division by zero
             return self.world_x, self.world_y
        world_x = (screen_x / self.zoom_level) + self.world_x
        world_y = (screen_y / self.zoom_level) + self.world_y
        return world_x, world_y

    def handle_zoom(self, scroll_y: int, mouse_pos: Tuple[int, int]) -> None:
        """Adjust zoom level based on mouse scroll, zooming towards the mouse cursor."""
        zoom_speed = 0.1
        old_zoom = self.zoom_level

        # Get world coordinates under mouse before zoom
        mouse_world_before_x, mouse_world_before_y = self.screen_to_world_coords(*mouse_pos)

        # Adjust zoom level
        if scroll_y > 0: # Zoom in
            self.zoom_level = min(self.max_zoom, self.zoom_level * (1 + zoom_speed))
        elif scroll_y < 0: # Zoom out
            self.zoom_level = max(self.min_zoom, self.zoom_level * (1 - zoom_speed))

        # If zoom didn't change, no need to adjust position
        if self.zoom_level == old_zoom:
            return

        # Get world coordinates under mouse after zoom (if camera didn't move)
        mouse_world_after_x, mouse_world_after_y = self.screen_to_world_coords(*mouse_pos)

        # Adjust camera position to keep the world point under the mouse stationary
        delta_x = mouse_world_before_x - mouse_world_after_x
        delta_y = mouse_world_before_y - mouse_world_after_y
        self.world_x += delta_x
        self.world_y += delta_y

        # Apply bounds after zoom adjustment
        self._apply_bounds()

    def get_world_view(self) -> pygame.Rect:
        """Return the rectangle representing the camera's view in world coordinates."""
        if self.zoom_level == 0: # Avoid division by zero
             # Return a minimal rect at the current position if zoom is zero
             return pygame.Rect(self.world_x, self.world_y, 1, 1)
        visible_width = self.width / self.zoom_level
        visible_height = self.height / self.zoom_level
        return pygame.Rect(int(self.world_x), int(self.world_y), int(visible_width), int(visible_height))
