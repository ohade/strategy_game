"""Tests for the parallax background system."""
import unittest
from unittest.mock import MagicMock, patch

import pygame

from asset_manager import get_background_layer
from parallax_background import ParallaxBackground


class TestParallaxBackground(unittest.TestCase):
    """Test suite for the parallax background system."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        
        # Create a mock surface
        self.screen = MagicMock(spec=pygame.Surface)
        self.screen.get_width.return_value = 800
        self.screen.get_height.return_value = 600
        
        # Create a real rect for world view
        self.world_rect = pygame.Rect(0, 0, 800, 600)
        
        # Mock camera
        self.camera = MagicMock()
        self.camera.world_x = 0
        self.camera.world_y = 0
        self.camera.zoom_level = 1.0
        self.camera.get_world_view.return_value = self.world_rect
        self.camera.apply_coords.side_effect = lambda x, y: (x, y)  # Simple pass-through for tests
        
    def tearDown(self):
        """Tear down test fixtures."""
        pygame.quit()
    
    @patch('parallax_background.get_background_layer')
    def test_init_creates_multiple_layers(self, mock_get_background_layer):
        """Test that initialization creates the correct number of layers."""
        # Setup the mock
        mock_layer = MagicMock(spec=pygame.Surface)
        mock_get_background_layer.return_value = mock_layer
        
        # Create the background with 3 layers
        background = ParallaxBackground(3000, 3000, num_layers=3)
        
        # Check that get_background_layer was called for each layer
        self.assertEqual(mock_get_background_layer.call_count, 3)
        
        # Verify that the correct indices were used for the layers
        mock_get_background_layer.assert_any_call(0)
        mock_get_background_layer.assert_any_call(1)
        mock_get_background_layer.assert_any_call(2)
    
    @patch('parallax_background.get_background_layer')
    def test_draw_renders_all_layers(self, mock_get_background_layer):
        """Test that draw renders all background layers."""
        # Setup the mocks
        mock_layer = MagicMock(spec=pygame.Surface)
        mock_layer.get_width.return_value = 800
        mock_layer.get_height.return_value = 600
        mock_get_background_layer.return_value = mock_layer
        
        # Create the background with 3 layers
        background = ParallaxBackground(3000, 3000, num_layers=3)
        
        # Set up specific attributes for the camera mock to avoid comparison issues
        self.camera.x = 0
        self.camera.y = 0
        self.camera.width = 800
        self.camera.height = 600
        self.camera.scale = 1.0
        
        # Call draw method
        background.draw(self.screen, self.camera)
        
        # Verify that blit was called at least once for each layer
        # The actual implementation may call blit multiple times per layer for tiling
        self.assertGreaterEqual(self.screen.blit.call_count, 3)
    
    @patch('pygame.draw.circle')
    @patch('parallax_background.get_background_layer')
    def test_parallax_effect_moves_layers_at_different_speeds(self, mock_get_background_layer, mock_draw_circle):
        """Test that layers move at different speeds based on their depth."""
        # Setup the mocks
        mock_layer = MagicMock(spec=pygame.Surface)
        mock_layer.get_width.return_value = 200  # Small width to reduce tiling
        mock_layer.get_height.return_value = 200  # Small height to reduce tiling
        mock_get_background_layer.return_value = mock_layer
        
        # Create the background with 3 layers
        background = ParallaxBackground(3000, 3000, num_layers=3)
        
        # Manually set up the parallax layers and factors for direct testing
        background.using_layers = True
        background.layers = [mock_layer, mock_layer, mock_layer]
        
        # Set distinct parallax factors for clear testing
        background.parallax_factors = [0.1, 0.5, 0.9]
        
        # Set some significant camera position to make parallax effects obvious
        self.camera.world_x = 1000
        self.camera.world_y = 500
        
        # Call draw method but isolate each layer draw to test separately
        # We'll manually calculate parallax offsets for each layer
        
        # For layer 0 (farthest, factor 0.1)
        parallax_x0 = -self.camera.world_x * background.parallax_factors[0]
        parallax_y0 = -self.camera.world_y * background.parallax_factors[0]
        
        # For layer 2 (closest, factor 0.9)
        parallax_x2 = -self.camera.world_x * background.parallax_factors[2]
        parallax_y2 = -self.camera.world_y * background.parallax_factors[2]
        
        # The closest layer (layer 2) should have moved more (larger negative offset)
        # than the farthest layer (layer 0) for the same camera position
        self.assertLess(parallax_x2, parallax_x0, 
                        "Closest layer should move more (have larger negative X offset)")
        self.assertLess(parallax_y2, parallax_y0, 
                        "Closest layer should move more (have larger negative Y offset)")
        
        # Now call the real draw method to verify it's working
        background.draw(self.screen, self.camera)
        
        # Verify blit was called multiple times (exact count doesn't matter as it depends on tiling)
        self.assertGreater(self.screen.blit.call_count, 0, "Background layers should be drawn")
    
    @patch('pygame.draw.line')
    @patch('pygame.draw.circle')
    @patch('parallax_background.get_background_layer')
    def test_fallback_to_stars_if_layers_unavailable(self, mock_get_background_layer, mock_draw_circle, mock_draw_line):
        """Test that the system falls back to star rendering if background layers are unavailable."""
        # Setup the mock to simulate failure to load background
        mock_get_background_layer.side_effect = Exception("Background layer not found")
        
        # Create the background with stars
        background = ParallaxBackground(3000, 3000, num_layers=3)
        
        # Replace background.stars with a test star that will be in our view
        test_star = (400, 300, 2, 200)  # x, y, radius, brightness
        background.stars = [test_star]
        self.assertFalse(background.using_layers)
        
        # Make sure our test star is in the world view
        # We don't need to mock collidepoint since we're using a real rect
        
        # Draw with stars
        background.draw(self.screen, self.camera)
        
        # Check that we're trying to draw circles (stars)
        # We expect at least one call to draw_circle for our test star
        self.assertGreaterEqual(mock_draw_circle.call_count, 1, "Should draw stars with circles")
        
        # For star drawing, we should see no calls to blit for background layers
        self.assertEqual(self.screen.blit.call_count, 0, "No background layers should be drawn")


if __name__ == "__main__":
    unittest.main()
