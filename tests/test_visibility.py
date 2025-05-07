import pytest
import pygame
import sys
import numpy as np
from typing import List, Tuple
sys.path.append('..')

# Import the module we'll be testing (to be created)
from visibility import VisibilityGrid, VisibilityState

# Import other necessary modules
from units import FriendlyUnit, EnemyUnit


class TestVisibilityGrid:
    
    @pytest.fixture
    def visibility_grid(self):
        """Create a visibility grid instance for testing."""
        # Initialize a 100x100 cell grid with 10x10 cell size
        return VisibilityGrid(width=1000, height=1000, cell_size=10)
    
    def test_grid_initialization(self, visibility_grid):
        """Test that the grid is properly initialized with all cells unseen."""
        # Grid should have 100x100 cells
        assert visibility_grid.grid_width == 100
        assert visibility_grid.grid_height == 100
        
        # All cells should initially be in UNSEEN state
        for x in range(visibility_grid.grid_width):
            for y in range(visibility_grid.grid_height):
                assert visibility_grid.get_cell_state(x, y) == VisibilityState.UNSEEN
    
    def test_unit_visibility_circle(self, visibility_grid):
        """Test that a unit makes cells visible within its vision radius."""
        # Create a friendly unit
        unit = FriendlyUnit(500, 500)  # Center of the map
        unit.vision_radius = 100  # Vision radius of 100 pixels
        
        # Calculate visibility
        visibility_grid.update_visibility([unit], [])
        
        # Check cells within vision radius are visible
        center_grid_x = 500 // visibility_grid.cell_size
        center_grid_y = 500 // visibility_grid.cell_size
        
        # Sample a few points that should be visible
        assert visibility_grid.get_cell_state(center_grid_x, center_grid_y) == VisibilityState.VISIBLE
        
        # Check a cell near the edge of visibility
        radius_in_cells = 100 // visibility_grid.cell_size
        assert visibility_grid.get_cell_state(center_grid_x + radius_in_cells - 1, center_grid_y) == VisibilityState.VISIBLE
        
        # Check a cell outside visibility radius
        far_cell_x = center_grid_x + radius_in_cells + 5
        far_cell_y = center_grid_y
        # Ensure it's within grid bounds
        if far_cell_x < visibility_grid.grid_width:
            assert visibility_grid.get_cell_state(far_cell_x, far_cell_y) == VisibilityState.UNSEEN
    
    def test_previously_seen_state(self, visibility_grid):
        """Test that cells transition to PREVIOUSLY_SEEN when no longer visible."""
        # Create a friendly unit
        unit = FriendlyUnit(500, 500)
        unit.vision_radius = 100
        
        # Make some cells visible
        visibility_grid.update_visibility([unit], [])
        
        # Move the unit away
        unit.world_x = 800
        unit.world_y = 800
        
        # Update visibility again
        visibility_grid.update_visibility([unit], [])
        
        # Cells near the original position should now be PREVIOUSLY_SEEN
        center_grid_x = 500 // visibility_grid.cell_size
        center_grid_y = 500 // visibility_grid.cell_size
        
        assert visibility_grid.get_cell_state(center_grid_x, center_grid_y) == VisibilityState.PREVIOUSLY_SEEN
    
    def test_enemy_unit_visibility(self, visibility_grid):
        """Test that enemy units are only visible when within friendly vision."""
        # Create a friendly unit and an enemy unit
        friendly = FriendlyUnit(500, 500)
        friendly.vision_radius = 100
        
        enemy_inside_vision = EnemyUnit(550, 550)  # Inside vision radius
        enemy_outside_vision = EnemyUnit(700, 700)  # Outside vision radius
        
        # Update visibility
        visible_enemies = visibility_grid.update_visibility([friendly], [enemy_inside_vision, enemy_outside_vision])
        
        # Check that only the enemy within vision radius is returned
        assert enemy_inside_vision in visible_enemies
        assert enemy_outside_vision not in visible_enemies
    
    def test_carrier_has_larger_vision(self, visibility_grid):
        """Test that carriers have larger vision radius than regular units."""
        # Create a mock carrier by extending the vision radius of a friendly unit
        carrier = FriendlyUnit(500, 500)
        carrier.vision_radius = 250  # Larger vision radius
        
        regular_unit = FriendlyUnit(500, 500)
        regular_unit.vision_radius = 100  # Standard vision radius
        
        # Update visibility with carrier
        visibility_grid.update_visibility([carrier], [])
        carrier_visible_count = self._count_visible_cells(visibility_grid)
        
        # Reset grid
        reset_grid = VisibilityGrid(width=1000, height=1000, cell_size=10)
        
        # Update visibility with regular unit
        reset_grid.update_visibility([regular_unit], [])
        regular_visible_count = self._count_visible_cells(reset_grid)
        
        # Carrier should reveal more cells
        assert carrier_visible_count > regular_visible_count
    
    def test_combined_visibility(self, visibility_grid):
        """Test that multiple units combine their visibility."""
        # Create two friendly units with non-overlapping vision
        unit1 = FriendlyUnit(300, 300)
        unit1.vision_radius = 100
        
        unit2 = FriendlyUnit(700, 700)
        unit2.vision_radius = 100
        
        # Update visibility with both units
        visibility_grid.update_visibility([unit1, unit2], [])
        
        # Check that cells near both units are visible
        grid_x1 = 300 // visibility_grid.cell_size
        grid_y1 = 300 // visibility_grid.cell_size
        grid_x2 = 700 // visibility_grid.cell_size
        grid_y2 = 700 // visibility_grid.cell_size
        
        assert visibility_grid.get_cell_state(grid_x1, grid_y1) == VisibilityState.VISIBLE
        assert visibility_grid.get_cell_state(grid_x2, grid_y2) == VisibilityState.VISIBLE
    
    def _count_visible_cells(self, visibility_grid):
        """Helper method to count the number of visible cells in the grid."""
        count = 0
        for x in range(visibility_grid.grid_width):
            for y in range(visibility_grid.grid_height):
                if visibility_grid.get_cell_state(x, y) == VisibilityState.VISIBLE:
                    count += 1
        return count
