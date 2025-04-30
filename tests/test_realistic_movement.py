"""Tests for realistic unit movement with gradual rotation and inertia."""

import pytest
import math
from unittest.mock import MagicMock
import sys
import os

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions we'll be implementing
from game_logic import calculate_rotation, apply_rotation_inertia, smooth_movement

class TestRealisticMovement:
    
    def test_calculate_rotation_returns_correct_angle(self):
        """Test that calculate_rotation returns the correct angle between two points."""
        start_x, start_y = 0, 0
        target_x, target_y = 10, 10  # 45 degrees
        
        angle = calculate_rotation(start_x, start_y, target_x, target_y)
        
        assert math.isclose(angle, 45, abs_tol=0.1)
        
        # Test another angle
        target_x, target_y = 0, 10  # 90 degrees
        angle = calculate_rotation(start_x, start_y, target_x, target_y)
        
        assert math.isclose(angle, 90, abs_tol=0.1)
    
    def test_calculate_rotation_handles_all_quadrants(self):
        """Test that calculate_rotation works in all quadrants."""
        start_x, start_y = 0, 0
        
        # First quadrant
        target_x, target_y = 10, 10
        angle = calculate_rotation(start_x, start_y, target_x, target_y)
        assert math.isclose(angle, 45, abs_tol=0.1)
        
        # Second quadrant
        target_x, target_y = -10, 10
        angle = calculate_rotation(start_x, start_y, target_x, target_y)
        assert math.isclose(angle, 135, abs_tol=0.1)
        
        # Third quadrant
        target_x, target_y = -10, -10
        angle = calculate_rotation(start_x, start_y, target_x, target_y)
        assert math.isclose(angle, 225, abs_tol=0.1)
        
        # Fourth quadrant
        target_x, target_y = 10, -10
        angle = calculate_rotation(start_x, start_y, target_x, target_y)
        assert math.isclose(angle, 315, abs_tol=0.1)
    
    def test_apply_rotation_inertia_gradually_rotates_towards_target(self):
        """Test that apply_rotation_inertia gradually rotates a unit towards the target angle."""
        # Setup a mock unit
        unit = MagicMock()
        unit.rotation = 0  # Current rotation angle
        target_angle = 90  # Target rotation angle
        max_rotation_speed = 45  # Max degrees per update
        
        # First update (should rotate by max speed)
        new_rotation = apply_rotation_inertia(unit.rotation, target_angle, max_rotation_speed)
        assert math.isclose(new_rotation, 45, abs_tol=0.1)
        
        # Second update (should rotate by max speed again)
        unit.rotation = new_rotation
        new_rotation = apply_rotation_inertia(unit.rotation, target_angle, max_rotation_speed)
        assert math.isclose(new_rotation, 90, abs_tol=0.1)
        
        # Third update (already at target, should not change)
        unit.rotation = new_rotation
        new_rotation = apply_rotation_inertia(unit.rotation, target_angle, max_rotation_speed)
        assert math.isclose(new_rotation, 90, abs_tol=0.1)
    
    def test_apply_rotation_inertia_handles_angle_wrapping(self):
        """Test that apply_rotation_inertia correctly handles angle wrapping (0-360 degrees)."""
        # Setup
        current_angle = 350
        target_angle = 10
        max_rotation_speed = 30
        
        # Should rotate clockwise by the smaller angle (20 degrees)
        new_rotation = apply_rotation_inertia(current_angle, target_angle, max_rotation_speed)
        # Expected: 350° + 20° = 370° (which wraps to 10°)
        # But since our max speed is 30°, we can reach the target directly
        assert math.isclose(new_rotation, target_angle, abs_tol=0.1)
        
        # Now test counter-clockwise
        current_angle = 10
        target_angle = 350
        
        # Should rotate counter-clockwise (smaller angle)
        new_rotation = apply_rotation_inertia(current_angle, target_angle, max_rotation_speed)
        # Since angle difference is only 20° and max speed is 30°, we should reach target directly
        assert math.isclose(new_rotation, target_angle, abs_tol=0.1)
    
    def test_smooth_movement_applies_inertia(self):
        """Test that smooth_movement applies inertia to movement."""
        # Create a proper test object with all required attributes
        class TestUnit:
            def __init__(self):
                self.world_x = 0
                self.world_y = 0
                self.velocity_x = 0  # Initial velocity
                self.velocity_y = 0
                self.rotation = 0  # Facing right
                self.max_speed = 5
                self.acceleration = 200
                self.max_rotation_speed = 180
                
        unit = TestUnit()
        
        target_x, target_y = 100, 0  # Target directly to the right
        dt = 0.1  # Smaller time step for more realistic testing
        
        # First update (should accelerate)
        smooth_movement(unit, target_x, target_y, dt)
        assert unit.velocity_x > 0  # Should have positive x velocity
        assert unit.velocity_x <= unit.acceleration * dt  # Should not exceed acceleration
        
        # Save position after first update
        pos_after_first = (unit.world_x, unit.world_y)
        
        # Several updates to reach max speed
        for _ in range(5):
            smooth_movement(unit, target_x, target_y, dt)
        
        # Should now be at or near max speed
        assert unit.velocity_x > 0
        
        # Now change direction to test deceleration
        target_x, target_y = 0, 100  # Target upward
        
        # Position before changing direction
        pos_before_turn = (unit.world_x, unit.world_y)
        
        # First update in new direction
        smooth_movement(unit, target_x, target_y, dt)
        
        # Should start adjusting velocity components
        assert unit.velocity_y > 0  # Should start moving upward
