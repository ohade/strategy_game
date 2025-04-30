"""Tests for sprite-based rendering in the Unit class."""
import unittest
from unittest.mock import MagicMock, patch

import pygame

from units import Unit
from asset_manager import get_ship_sprite


class TestSpriteRendering(unittest.TestCase):
    """Test suite for sprite-based rendering in the Unit class."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        
        # Create a mock surface
        self.screen = MagicMock(spec=pygame.Surface)
        self.camera = MagicMock()
        
        # Mock camera.apply_coords to return a screen position
        self.camera.apply_coords.return_value = (400, 300)
    
    def tearDown(self):
        """Tear down test fixtures."""
        pygame.quit()
    
    @patch('pygame.draw.polygon')
    @patch('pygame.draw.rect')
    @patch('pygame.transform.rotate')
    @patch('units.get_ship_sprite')
    def test_unit_uses_sprite_for_rendering(self, mock_get_ship_sprite, mock_rotate, mock_draw_rect, mock_draw_polygon):
        """Test that Unit.draw uses sprites from the asset manager."""
        # Create a mock sprite
        mock_sprite = MagicMock(spec=pygame.Surface)
        mock_get_ship_sprite.return_value = mock_sprite
        
        # Setup the rotate mock to return another mock surface
        rotated_sprite = MagicMock(spec=pygame.Surface)
        rotated_sprite.get_rect.return_value = pygame.Rect(0, 0, 30, 30)
        mock_rotate.return_value = rotated_sprite
        
        # Create a unit
        unit = Unit(100, 100, "friendly")
        
        # Call the draw method
        unit.draw(self.screen, self.camera)
        
        # Verify that get_ship_sprite was called with the unit's type
        mock_get_ship_sprite.assert_called_once_with("friendly")
        
        # Verify that the sprite was drawn to the screen (blit was called)
        self.screen.blit.assert_called()
    
    @patch('pygame.draw.polygon')
    @patch('pygame.draw.rect')
    @patch('pygame.transform.rotate')
    @patch('units.get_ship_sprite')
    def test_unit_rotates_sprite_when_drawing(self, mock_get_ship_sprite, mock_rotate, mock_draw_rect, mock_draw_polygon):
        """Test that Unit.draw rotates the sprite based on unit's rotation."""
        # Create a mock sprite
        mock_sprite = MagicMock(spec=pygame.Surface)
        mock_sprite.get_rect.return_value = pygame.Rect(0, 0, 30, 30)
        mock_get_ship_sprite.return_value = mock_sprite
        
        # Setup the rotate mock to return another mock surface
        rotated_sprite = MagicMock(spec=pygame.Surface)
        rotated_sprite.get_rect.return_value = pygame.Rect(0, 0, 30, 30)
        mock_rotate.return_value = rotated_sprite
        
        # Create a unit with non-zero rotation
        unit = Unit(100, 100, "friendly")
        unit.rotation = 45.0  # 45 degrees rotation
        
        # Call the draw method
        unit.draw(self.screen, self.camera)
        
        # Verify that the sprite was rotated with the unit's rotation value
        mock_rotate.assert_called_once()
        rotation_arg = mock_rotate.call_args[0][1]  # Get the rotation argument
        
        # The rotation should be negative in pygame (it rotates counter-clockwise)
        self.assertEqual(rotation_arg, -45.0)
        
        # Verify that the rotated sprite was drawn to the screen
        self.screen.blit.assert_called()
    
    @patch('pygame.draw.polygon')
    @patch('pygame.draw.rect')
    @patch('pygame.transform.rotate')
    @patch('units.get_ship_sprite')
    def test_enemy_unit_uses_enemy_sprite(self, mock_get_ship_sprite, mock_rotate, mock_draw_rect, mock_draw_polygon):
        """Test that enemy units use the enemy sprite."""
        # Create a mock sprite
        mock_sprite = MagicMock(spec=pygame.Surface)
        mock_get_ship_sprite.return_value = mock_sprite
        
        # Setup the rotate mock to return another mock surface
        rotated_sprite = MagicMock(spec=pygame.Surface)
        rotated_sprite.get_rect.return_value = pygame.Rect(0, 0, 30, 30)
        mock_rotate.return_value = rotated_sprite
        
        # Create an enemy unit
        unit = Unit(100, 100, "enemy")
        
        # Call the draw method
        unit.draw(self.screen, self.camera)
        
        # Verify that get_ship_sprite was called with "enemy"
        mock_get_ship_sprite.assert_called_once_with("enemy")


if __name__ == "__main__":
    unittest.main()
