import pytest
from unittest.mock import MagicMock, patch
import sys
import os
import pygame

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialize pygame for testing
pygame.init()

from units import Unit, FriendlyUnit
from carrier import Carrier, get_carrier_sprite

class TestCarrier:
    def test_carrier_inheritance(self):
        """Test that Carrier inherits from FriendlyUnit and has expected base properties."""
        carrier = Carrier(world_x=100, world_y=100)
        
        # Test inheritance
        assert isinstance(carrier, FriendlyUnit)
        assert isinstance(carrier, Unit)
        
        # Test carrier type
        assert carrier.unit_type == 'friendly'
        assert carrier.type == 'friendly'
        
    def test_carrier_extended_properties(self):
        """Test that Carrier has extended properties beyond the base Unit class."""
        carrier = Carrier(world_x=100, world_y=100)
        
        # Test carrier-specific properties
        assert carrier.hp > 100  # Carrier should have more HP than regular units
        assert carrier.hp_max > 100
        assert carrier.radius > 15  # Carrier should be larger than regular units
        assert carrier.mass > 1.0  # Carrier should have more mass than regular units
        assert hasattr(carrier, 'fighter_capacity')  # Should have capacity for fighters
        assert carrier.fighter_capacity > 0  # Should be able to store fighters
        
    def test_carrier_movement_properties(self):
        """Test that Carrier has appropriate movement properties (slower, more momentum)."""
        carrier = Carrier(world_x=100, world_y=100)
        regular_unit = FriendlyUnit(world_x=100, world_y=100)
        
        # Carrier should be slower than regular units
        assert carrier.max_speed < regular_unit.max_speed
        assert carrier.acceleration < regular_unit.acceleration
        assert carrier.max_rotation_speed < regular_unit.max_rotation_speed
        
    def test_carrier_sprite_generation(self):
        """Test that Carrier generates appropriate sprites that resemble Battlestar Galactica."""
        # First test the sprite generator function directly
        sprite = get_carrier_sprite()
        assert isinstance(sprite, pygame.Surface)
        assert sprite.get_width() > 0
        assert sprite.get_height() > 0
        
        # Test the carrier draw method with properly configured mocks
        carrier = Carrier(world_x=100, world_y=100)
        
        # Create mock screen surface
        mock_surface = pygame.Surface((100, 100))
        
        # Create a properly configured camera mock that returns a tuple for screen position
        mock_camera = MagicMock()
        mock_camera.apply_coords.return_value = (50, 50)  # Return a proper screen position
        
        # Test with actual sprite but mocked camera
        with patch('carrier.get_carrier_sprite', return_value=sprite):
            # This should now draw without errors
            carrier.draw(mock_surface, mock_camera)
            
            # Verify the camera was called with expected parameters
            mock_camera.apply_coords.assert_called_once_with(100, 100)  # The carrier's position
