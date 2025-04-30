"""Game constants."""

# Constants
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
WINDOW_TITLE: str = "Strategy Game MVP"
BACKGROUND_COLOR: tuple[int, int, int] = (0, 0, 20) # Dark blue space-like
FPS: int = 60

# --- Map and Minimap Constants ---
MAP_WIDTH: int = 4000
MAP_HEIGHT: int = 3000
MINIMAP_WIDTH: int = 200
MINIMAP_HEIGHT: int = 150 # Maintain aspect ratio of map (4000/3000 = 4/3)
MINIMAP_X: int = SCREEN_WIDTH - MINIMAP_WIDTH - 10 # 10px padding from right edge
MINIMAP_Y: int = SCREEN_HEIGHT - MINIMAP_HEIGHT - 10 # 10px padding from bottom edge
MINIMAP_BG_COLOR: tuple[int, int, int, int] = (50, 50, 50, 150) # Semi-transparent dark grey
MINIMAP_BORDER_COLOR: tuple[int, int, int] = (100, 100, 100)
MINIMAP_UNIT_SIZE: int = 2 # Size of dots on minimap

# --- Scaling Factors ---
MINIMAP_SCALE_X: float = MINIMAP_WIDTH / MAP_WIDTH
MINIMAP_SCALE_Y: float = MINIMAP_HEIGHT / MAP_HEIGHT
