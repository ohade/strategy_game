import math
from enum import Enum, auto
from typing import List
# Import type checking only
from typing import TYPE_CHECKING

import numpy as np
import pygame

if TYPE_CHECKING:
    from units import FriendlyUnit, EnemyUnit

class VisibilityState(Enum):
    """Enum representing the visibility state of a grid cell."""
    UNSEEN = auto()         # Never seen by any friendly unit
    PREVIOUSLY_SEEN = auto() # Was visible before, but not currently
    VISIBLE = auto()         # Currently visible by at least one friendly unit

class VisibilityGrid:
    """Manages the fog of war grid for the game."""
    
    def __init__(self, width: int, height: int, cell_size: int = 10):
        """Initialize the visibility grid.
        
        Args:
            width: Width of the game world in pixels
            height: Height of the game world in pixels
            cell_size: Size of each grid cell in pixels
        """
        self.world_width = width
        self.world_height = height
        self.cell_size = cell_size
        
        # Calculate grid dimensions
        self.grid_width = math.ceil(width / cell_size)
        self.grid_height = math.ceil(height / cell_size)
        
        # Initialize visibility grid with all cells UNSEEN
        # Using numpy for memory and performance efficiency
        # 0 = UNSEEN, 1 = PREVIOUSLY_SEEN, 2 = VISIBLE
        self.grid = np.zeros((self.grid_width, self.grid_height), dtype=np.uint8)
        
        # Shadow grid to track current frame visibility before updating main grid
        self.current_visibility = np.zeros((self.grid_width, self.grid_height), dtype=np.bool_)
    
    def get_cell_state(self, grid_x: int, grid_y: int) -> VisibilityState:
        """Get the visibility state of a cell in the grid.
        
        Args:
            grid_x: X coordinate in the grid
            grid_y: Y coordinate in the grid
            
        Returns:
            VisibilityState enum value for the cell
        """
        # Check bounds
        if not (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
            return VisibilityState.UNSEEN
        
        # Convert numeric value to enum
        value = self.grid[grid_x, grid_y]
        if value == 0:
            return VisibilityState.UNSEEN
        elif value == 1:
            return VisibilityState.PREVIOUSLY_SEEN
        else:  # value == 2
            return VisibilityState.VISIBLE
    
    def update_visibility(self, friendly_units: List['FriendlyUnit'], 
                          enemy_units: List['EnemyUnit']) -> List['EnemyUnit']:
        """Update the visibility grid based on friendly unit positions.
        
        Args:
            friendly_units: List of friendly units with vision
            enemy_units: List of enemy units to check visibility for
            
        Returns:
            List of enemy units that are currently visible to friendly units
        """
        # Reset current visibility
        self.current_visibility.fill(False)
        
        # Update visibility for each friendly unit
        for unit in friendly_units:
            # Get vision radius (default to 100 if not set)
            vision_radius = getattr(unit, 'vision_radius', 100)
            
            # Calculate grid coordinates for unit position
            unit_grid_x = int(unit.world_x / self.cell_size)
            unit_grid_y = int(unit.world_y / self.cell_size)
            
            # Calculate radius in grid cells
            radius_in_cells = math.ceil(vision_radius / self.cell_size)
            
            # Mark cells within vision radius as visible
            self._mark_cells_in_radius(unit_grid_x, unit_grid_y, radius_in_cells)
        
        # Determine which enemies are visible
        visible_enemies = []
        for enemy in enemy_units:
            enemy_grid_x = int(enemy.world_x / self.cell_size)
            enemy_grid_y = int(enemy.world_y / self.cell_size)
            
            # Check if enemy position is within the grid boundaries
            if 0 <= enemy_grid_x < self.grid_width and 0 <= enemy_grid_y < self.grid_height:
                # If the cell containing the enemy is visible
                if self.current_visibility[enemy_grid_x, enemy_grid_y]:
                    visible_enemies.append(enemy)
        
        # Update the main grid based on current visibility
        # Where currently visible, set to VISIBLE (2)
        self.grid[self.current_visibility] = 2
        
        # Where was previously visible but not now, set to PREVIOUSLY_SEEN (1)
        # Only if it's not already UNSEEN (0)
        self.grid[(~self.current_visibility) & (self.grid == 2)] = 1
        
        return visible_enemies
    
    def _mark_cells_in_radius(self, center_x: int, center_y: int, radius: int):
        """Mark all cells within radius as visible.
        
        Args:
            center_x: X coordinate of center cell
            center_y: Y coordinate of center cell
            radius: Radius in grid cells
        """
        # Calculate bounds to check, clamped to grid dimensions
        min_x = max(0, center_x - radius)
        max_x = min(self.grid_width - 1, center_x + radius)
        min_y = max(0, center_y - radius)
        max_y = min(self.grid_height - 1, center_y + radius)
        
        # Use vectorized operations for speed
        y_indices, x_indices = np.ogrid[min_y:max_y+1, min_x:max_x+1]
        distances = np.sqrt((x_indices - center_x)**2 + (y_indices - center_y)**2)
        mask = distances <= radius
        
        # Apply the mask to the current visibility
        self.current_visibility[min_x:max_x+1, min_y:max_y+1] |= mask.T
    
    def is_position_visible(self, world_x: float, world_y: float) -> bool:
        """Check if a specific world position is currently visible.
        
        Args:
            world_x: X coordinate in world space
            world_y: Y coordinate in world space
            
        Returns:
            True if the position is visible, False otherwise
        """
        grid_x = int(world_x / self.cell_size)
        grid_y = int(world_y / self.cell_size)
        
        # Check bounds
        if not (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
            return False
        
        return self.get_cell_state(grid_x, grid_y) == VisibilityState.VISIBLE
    
    def draw_fog_of_war(self, surface: pygame.Surface, camera) -> None:
        """Draw the fog of war on the given surface.
        
        Args:
            surface: Pygame surface to draw on
            camera: Camera object for coordinate translation
        """
        fog_color = (0, 0, 0, 255)  # Black for unseen
        fog_color_seen = (0, 0, 0, 150)  # Semi-transparent black for previously seen
        
        # Get visible area in grid coordinates
        view_rect = camera.get_world_view()
        min_grid_x = max(0, int(view_rect.left / self.cell_size))
        min_grid_y = max(0, int(view_rect.top / self.cell_size))
        max_grid_x = min(self.grid_width - 1, int(view_rect.right / self.cell_size))
        max_grid_y = min(self.grid_height - 1, int(view_rect.bottom / self.cell_size))
        
        # Create fog surface with per-pixel alpha
        fog_surface = pygame.Surface((view_rect.width, view_rect.height), pygame.SRCALPHA)
        
        # Draw fog for each cell in view
        for grid_x in range(min_grid_x, max_grid_x + 1):
            for grid_y in range(min_grid_y, max_grid_y + 1):
                state = self.get_cell_state(grid_x, grid_y)
                
                if state == VisibilityState.UNSEEN:
                    # Calculate screen coordinates
                    world_x = grid_x * self.cell_size
                    world_y = grid_y * self.cell_size
                    screen_x, screen_y = camera.apply_coords(world_x, world_y)
                    screen_x -= view_rect.left
                    screen_y -= view_rect.top
                    
                    # Draw an unseen fog cell
                    pygame.draw.rect(fog_surface, fog_color, 
                                    pygame.Rect(screen_x, screen_y, self.cell_size, self.cell_size))
                    
                elif state == VisibilityState.PREVIOUSLY_SEEN:
                    # Calculate screen coordinates
                    world_x = grid_x * self.cell_size
                    world_y = grid_y * self.cell_size
                    screen_x, screen_y = camera.apply_coords(world_x, world_y)
                    screen_x -= view_rect.left
                    screen_y -= view_rect.top
                    
                    # Draw a previously seen fog cell (semi-transparent)
                    pygame.draw.rect(fog_surface, fog_color_seen, 
                                    pygame.Rect(screen_x, screen_y, self.cell_size, self.cell_size))
        
        # Blit the fog surface onto the main surface
        surface.blit(fog_surface, (view_rect.left, view_rect.top))
