import pytest
from unittest.mock import MagicMock, patch
import sys
import os
import pygame
import math

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialize pygame for testing
pygame.init()

from units import Unit, FriendlyUnit
from carrier import Carrier
from game_logic import detect_unit_collision, resolve_collision_with_mass

class TestCarrierCollisions:
    def test_mass_based_collision_resolution(self):
        """Test that collision resolution takes unit mass into account.
        
        Larger mass units should push smaller units more during collisions.
        """
        # Create a carrier (high mass) and regular unit
        carrier = Carrier(world_x=100, world_y=100)
        small_unit = FriendlyUnit(world_x=101, world_y=101)
        
        # Store original positions
        carrier_original_x, carrier_original_y = carrier.world_x, carrier.world_y
        small_unit_original_x, small_unit_original_y = small_unit.world_x, small_unit.world_y
        
        # Check if they're in collision
        assert detect_unit_collision(carrier, small_unit), "Units should be in collision based on their proximity"
        
        # Test with actual collision resolution
        # Set explicit masses for the test
        carrier.mass = 10.0
        small_unit.mass = 1.0
        
        # Apply collision resolution
        resolve_collision_with_mass(carrier, small_unit, use_mass=True)
        
        # Calculate movement amounts for each unit
        carrier_dx = abs(carrier.world_x - carrier_original_x)
        carrier_dy = abs(carrier.world_y - carrier_original_y)
        small_unit_dx = abs(small_unit.world_x - small_unit_original_x)
        small_unit_dy = abs(small_unit.world_y - small_unit_original_y)
        
        # The small unit should move more than the carrier
        assert small_unit_dx > carrier_dx or small_unit_dy > carrier_dy, \
            "Small unit should move more than carrier in collision resolution"
    
    def test_small_unit_avoidance_behavior(self):
        """Test that small units attempt to avoid the carrier when getting too close."""
        # Test the carrier avoidance function directly
        # Create a carrier and a small unit
        carrier = Carrier(world_x=100, world_y=100)
        small_unit = FriendlyUnit(world_x=120, world_y=100)
        
        # Set the unit to move through the carrier
        small_unit.state = "moving"
        small_unit.move_target = (80, 100)  # This would go through the carrier
        
        # Test the avoidance function directly
        from game_logic import check_carrier_proximity_avoidance
        
        # Call the avoidance function
        adjusted_target = check_carrier_proximity_avoidance(small_unit, [carrier])
        
        # If the unit's path would intersect with the carrier, should return an adjusted path
        assert adjusted_target is not None, "Should return an adjusted path to avoid carrier"
        
        # The adjusted target should still be headed generally west (negative x) but
        # offset in the y direction to avoid the carrier
        adjusted_x, adjusted_y = adjusted_target
        assert adjusted_x < small_unit.world_x, "Should still move generally west"
        assert adjusted_y != 100, "Y coordinate should be adjusted to avoid carrier"
    
    def test_proximity_awareness_indicator(self):
        """Test that there's a visual indicator when units are too close to a carrier."""
        # Create a carrier and small unit
        carrier = Carrier(world_x=100, world_y=100)
        small_unit = FriendlyUnit(world_x=150, world_y=100)  # Within proximity but not colliding
        
        # Test the proximity check directly
        with patch.object(carrier, 'proximity_radius', 60):
            # Manually calculate distance (50) and compare to the mocked proximity_radius (60)
            is_close = carrier.check_proximity_to_unit(small_unit)
            assert is_close, "Should detect unit in carrier proximity awareness range"
            
            # Move the unit outside proximity range
            small_unit.world_x = 200  # Now distance is 100, outside proximity_radius of 60
            is_close = carrier.check_proximity_to_unit(small_unit)
            assert not is_close, "Should not detect unit outside proximity range"

    def test_carrier_imminent_collision_indicator(self):
        """Test that the carrier shows visual indicators for imminent collisions."""
        # Create a carrier and a unit on collision course
        carrier = Carrier(world_x=100, world_y=100)
        unit = FriendlyUnit(world_x=150, world_y=100)
        unit.velocity_x = -50  # Moving toward carrier
        
        # Test the collision prediction directly
        # Should predict collision since the unit is moving toward the carrier
        is_imminent = carrier.predict_collision(unit)
        assert is_imminent, "Should detect imminent collision"
        
        # Check that the unit was added to collision warnings list
        assert unit in carrier.collision_warnings, "Unit should be in collision warnings list"
        
        # Test with a unit moving away
        unit2 = FriendlyUnit(world_x=150, world_y=100)
        unit2.velocity_x = 50  # Moving away from carrier
        is_imminent = carrier.predict_collision(unit2)
        assert not is_imminent, "Should not detect collision for unit moving away"
