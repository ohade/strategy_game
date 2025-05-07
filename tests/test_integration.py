import pytest
import pygame
import sys
import os
sys.path.append('..')

# Import all required modules for integration testing
from visibility import VisibilityGrid
from camera import Camera
from units import FriendlyUnit, EnemyUnit
from main import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT

class TestComponentIntegration:
    """Test proper integration between different game components."""
    
    @pytest.fixture
    def setup_pygame(self):
        """Initialize pygame for testing."""
        pygame.init()
        # Create a small surface for testing
        surface = pygame.Surface((100, 100))
        yield surface
        pygame.quit()
    
    @pytest.fixture
    def camera(self):
        """Create a camera instance for testing."""
        return Camera(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
    
    @pytest.fixture
    def visibility_grid(self):
        """Create a visibility grid for testing."""
        return VisibilityGrid(MAP_WIDTH, MAP_HEIGHT, cell_size=20)
    
    @pytest.fixture
    def friendly_unit(self):
        """Create a friendly unit for testing."""
        unit = FriendlyUnit(500, 500)
        unit.vision_radius = 200
        return unit
    
    @pytest.fixture
    def enemy_unit(self):
        """Create an enemy unit for testing."""
        return EnemyUnit(700, 700)
    
    def test_visibility_camera_integration(self, setup_pygame, camera, visibility_grid, friendly_unit, enemy_unit):
        """Test that the visibility system integrates properly with the camera system."""
        # Update visibility
        visible_enemies = visibility_grid.update_visibility([friendly_unit], [enemy_unit])
        
        # Verify the enemy is not immediately visible (out of vision range)
        assert enemy_unit not in visible_enemies
        
        # Test that the draw_fog_of_war method can be called with a camera instance
        # This will fail if there's an integration issue between Camera and VisibilityGrid
        try:
            visibility_grid.draw_fog_of_war(setup_pygame, camera)
        except AttributeError as e:
            pytest.fail(f"Integration failure between VisibilityGrid and Camera: {e}")
    
    def test_camera_world_view(self, camera):
        """Test that camera.get_world_view() returns a proper Rect object."""
        world_view = camera.get_world_view()
        assert isinstance(world_view, pygame.Rect)
        assert hasattr(world_view, 'left')
        assert hasattr(world_view, 'top')
        assert hasattr(world_view, 'right')
        assert hasattr(world_view, 'bottom')
    
    def test_camera_apply_coords(self, camera):
        """Test that camera's coordinate transformation works as expected."""
        screen_x, screen_y = camera.apply_coords(100, 100)
        assert isinstance(screen_x, int)
        assert isinstance(screen_y, int)
    
    def test_unit_drawing_integration(self, setup_pygame, camera, friendly_unit):
        """Test that units can be drawn with camera transformations."""
        try:
            friendly_unit.draw(setup_pygame, camera)
        except Exception as e:
            pytest.fail(f"Integration failure between Unit.draw and Camera: {e}")
    
    def test_units_with_visibility(self, visibility_grid, friendly_unit, enemy_unit):
        """Test that units properly integrate with the visibility system."""
        # Move the enemy closer to be within vision range
        enemy_unit.world_x = 600
        enemy_unit.world_y = 600
        
        # Update visibility and check if enemy is visible
        visible_enemies = visibility_grid.update_visibility([friendly_unit], [enemy_unit])
        assert enemy_unit in visible_enemies, "Enemy unit should be visible when within vision range"
