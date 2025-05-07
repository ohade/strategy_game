"""Tests for the asset_manager module."""
import os
import unittest
from unittest.mock import patch, MagicMock

import pygame

# Import the module we'll be testing (to be created)
# from asset_manager import AssetManager, load_image, load_animation, get_ship_sprite


class TestAssetManager(unittest.TestCase):
    """Test suite for the asset_manager module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for the tests
        pygame.init()
        
        # Define test paths
        self.base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        self.ship_path = os.path.join(self.base_path, 'ships')
        self.bg_path = os.path.join(self.base_path, 'backgrounds')
        self.effects_path = os.path.join(self.base_path, 'effects')
        
        # Ensure directories exist
        for path in [self.base_path, self.ship_path, self.bg_path, self.effects_path]:
            os.makedirs(path, exist_ok=True)
    
    def tearDown(self):
        """Tear down test fixtures."""
        pygame.quit()
    
    @patch('pygame.transform.smoothscale')
    @patch('os.path.exists')
    @patch('pygame.image.load')
    def test_load_image(self, mock_load, mock_exists, mock_scale):
        """Test loading a single image with proper scaling."""
        from asset_manager import load_image
        
        # Setup mocks
        mock_exists.return_value = True  # Pretend file exists
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_load.return_value = mock_surface
        mock_surface.convert_alpha.return_value = mock_surface
        mock_surface.get_width.return_value = 100
        mock_surface.get_height.return_value = 100
        
        # Mock the scaling function to return the same surface
        mock_scale.return_value = mock_surface
        
        # Call function with test data
        result = load_image('test_ship.png', scale=0.5)
        
        # Assertions
        mock_load.assert_called_once()
        mock_surface.convert_alpha.assert_called_once()
        self.assertEqual(result, mock_surface)
    
    @patch('asset_manager.load_image')
    def test_load_animation(self, mock_load_image):
        """Test loading an animation sequence."""
        from asset_manager import load_animation
        
        # Setup mock
        mock_images = [MagicMock(spec=pygame.Surface) for _ in range(3)]
        mock_load_image.side_effect = mock_images
        
        # Call function with test data
        frames = load_animation('test_anim_{}.png', 3, scale=1.0)
        
        # Assertions
        self.assertEqual(len(frames), 3)
        self.assertEqual(mock_load_image.call_count, 3)
        
        # Verify each call with proper filename format
        # Using any_order=True since the exact parameter ordering might vary
        mock_load_image.assert_any_call('test_anim_0.png', 1.0)
        mock_load_image.assert_any_call('test_anim_1.png', 1.0)
        mock_load_image.assert_any_call('test_anim_2.png', 1.0)
    
    def test_asset_manager_initialization(self):
        """Test AssetManager initializes properly."""
        from asset_manager import AssetManager
        
        manager = AssetManager()
        
        # Check manager has the expected attributes
        self.assertTrue(hasattr(manager, 'ship_sprites'))
        self.assertTrue(hasattr(manager, 'background_layers'))
        self.assertTrue(hasattr(manager, 'effect_animations'))
        
        # Collections should be empty initially
        self.assertEqual(len(manager.ship_sprites), 0)
        self.assertEqual(len(manager.background_layers), 0)
        self.assertEqual(len(manager.effect_animations), 0)
    
    @patch('asset_manager.load_image')
    def test_load_ship_sprites(self, mock_load_image):
        """Test loading ship sprites."""
        from asset_manager import AssetManager
        
        # Setup mock
        mock_friendly_ship = MagicMock(spec=pygame.Surface)
        mock_enemy_ship = MagicMock(spec=pygame.Surface)
        mock_carrier_ship = MagicMock(spec=pygame.Surface)
        mock_load_image.side_effect = [mock_friendly_ship, mock_enemy_ship, mock_carrier_ship]
        
        # Call the function
        manager = AssetManager()
        manager.load_ship_sprites()
        
        # Assertions
        self.assertEqual(mock_load_image.call_count, 3)  # Updated to 3 for carrier
        self.assertEqual(len(manager.ship_sprites), 3)  # Updated to 3 for carrier
        self.assertIn('friendly', manager.ship_sprites)
        self.assertIn('enemy', manager.ship_sprites)
        self.assertIn('carrier', manager.ship_sprites)  # Added carrier assertion
    
    @patch('asset_manager.load_image')
    def test_load_background_layers(self, mock_load_image):
        """Test loading background layers for parallax effect."""
        from asset_manager import AssetManager
        
        # Setup mock
        mock_bg_layers = [MagicMock(spec=pygame.Surface) for _ in range(3)]
        mock_load_image.side_effect = mock_bg_layers
        
        # Call the function
        manager = AssetManager()
        manager.load_background_layers()
        
        # Should have loaded at least 3 layers (stars, nebula, planets)
        self.assertGreaterEqual(mock_load_image.call_count, 3)
        self.assertGreaterEqual(len(manager.background_layers), 3)
        
        # First layer should be the furthest/slowest
        self.assertIn('parallax_factor', manager.background_layers[0])
    
    @patch('asset_manager.load_animation')
    def test_load_effect_animations(self, mock_load_animation):
        """Test loading effect animations."""
        from asset_manager import AssetManager
        
        # Setup mock
        mock_explosion = [MagicMock(spec=pygame.Surface) for _ in range(5)]
        mock_laser = [MagicMock(spec=pygame.Surface) for _ in range(3)]
        mock_load_animation.side_effect = [mock_explosion, mock_laser]
        
        # Call the function
        manager = AssetManager()
        manager.load_effect_animations()
        
        # Assertions
        self.assertEqual(mock_load_animation.call_count, 2)
        self.assertIn('explosion', manager.effect_animations)
        self.assertIn('laser', manager.effect_animations)
        
        # Check animation frames were loaded
        self.assertEqual(len(manager.effect_animations['explosion']), 5)
        self.assertEqual(len(manager.effect_animations['laser']), 3)
    
    @patch('asset_manager._asset_manager')
    def test_get_ship_sprite(self, mock_manager):
        """Test getting a ship sprite by type."""
        from asset_manager import get_ship_sprite
        
        # Setup mock
        mock_friendly_ship = MagicMock(spec=pygame.Surface)
        mock_enemy_ship = MagicMock(spec=pygame.Surface)
        
        # Configure the mock manager
        mock_manager._initialized = True
        mock_manager.ship_sprites = {
            'friendly': mock_friendly_ship,
            'enemy': mock_enemy_ship
        }
        
        # Call the function
        friendly_sprite = get_ship_sprite('friendly')
        enemy_sprite = get_ship_sprite('enemy')
        
        # Assertions
        self.assertEqual(friendly_sprite, mock_friendly_ship)
        self.assertEqual(enemy_sprite, mock_enemy_ship)
        
        # Test invalid type
        with self.assertRaises(ValueError):
            get_ship_sprite('invalid_type')


if __name__ == "__main__":
    unittest.main()
