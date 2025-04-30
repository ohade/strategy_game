import pygame

class Camera:
    """Manages the game view's offset (scrolling)."""
    def __init__(self, width: int, height: int, map_width: int = 4000, map_height: int = 3000) -> None:
        """Initialize the camera.

        Args:
            width (int): Width of the camera's view (screen width).
            height (int): Height of the camera's view (screen height).
            map_width (int): Width of the game world/map.
            map_height (int): Height of the game world/map.
        """
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.pan_speed = 500 # Pixels per second
        self.map_width = map_width
        self.map_height = map_height

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

        self.camera_rect.move_ip(int(move_x), int(move_y))

        # Add bounds checking to prevent camera from going outside the map
        # Ensure left edge of camera doesn't go left of map edge (0)
        self.camera_rect.left = max(0, self.camera_rect.left)
        # Ensure top edge of camera doesn't go above map edge (0)
        self.camera_rect.top = max(0, self.camera_rect.top)
        # Ensure right edge doesn't go beyond map's right edge
        if self.camera_rect.right > self.map_width:
            self.camera_rect.right = self.map_width
        # Ensure bottom edge doesn't go beyond map's bottom edge
        if self.camera_rect.bottom > self.map_height:
            self.camera_rect.bottom = self.map_height

    def apply(self, entity_rect: pygame.Rect) -> pygame.Rect:
        """Adjust an entity's screen position based on the camera offset.

        Args:
            entity_rect (pygame.Rect): The entity's rect in world coordinates.

        Returns:
            pygame.Rect: The entity's rect adjusted for screen drawing.
        """
        return entity_rect.move(-self.camera_rect.left, -self.camera_rect.top)

    def apply_coords(self, x: int, y: int) -> tuple[int, int]:
        """Adjust world coordinates to screen coordinates.

        Args:
            x (int): World x-coordinate.
            y (int): World y-coordinate.

        Returns:
            tuple[int, int]: Screen coordinates.
        """
        return x - self.camera_rect.left, y - self.camera_rect.top
