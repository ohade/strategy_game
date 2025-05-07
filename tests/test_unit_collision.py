"""Tests for unit collision detection and handling in game_logic.py."""

import unittest
import math
from unittest.mock import MagicMock
import sys
import os

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We'll be implementing this function in game_logic.py
from game_logic import detect_unit_collision, resolve_collision_with_mass

class TestUnitCollision(unittest.TestCase):
    
    def test_detect_unit_collision_detects_overlapping_units(self):
        """Test that detect_unit_collision returns True when units are overlapping."""
        # Create two units at the same position (overlapping)
        unit1 = MagicMock()
        unit1.world_x = 100
        unit1.world_y = 100
        unit1.radius = 15
        
        unit2 = MagicMock()
        unit2.world_x = 105  # Close enough to collide
        unit2.world_y = 105
        unit2.radius = 15
        
        # Distance between centers is 7.07 (sqrt(5^2 + 5^2)),
        # Combined radii is 30, so they are overlapping
        assert detect_unit_collision(unit1, unit2) is True
    
    def test_detect_unit_collision_returns_false_for_distant_units(self):
        """Test that detect_unit_collision returns False when units are far apart."""
        unit1 = MagicMock()
        unit1.world_x = 100
        unit1.world_y = 100
        unit1.radius = 15
        
        unit2 = MagicMock()
        unit2.world_x = 150  # Far enough to avoid collision
        unit2.world_y = 150
        unit2.radius = 15
        
        # Distance is 70.7, which is greater than combined radii (30)
        self.assertFalse(detect_unit_collision(unit1, unit2))
    
    def test_detect_unit_collision_handles_edge_case(self):
        """Test that detect_unit_collision correctly handles the edge case where units are just touching."""
        unit1 = MagicMock()
        unit1.world_x = 100
        unit1.world_y = 100
        unit1.radius = 15
        
        unit2 = MagicMock()
        unit2.world_x = 130  # Distance exactly equals sum of radii
        unit2.world_y = 100
        unit2.radius = 15
        
        # Units are exactly touching (distance = combined radii)
        assert detect_unit_collision(unit1, unit2) is True
    
    def test_resolve_collision_with_mass_moves_units_apart(self):
        """Test that resolve_collision_with_mass separates overlapping units."""
        # Create two overlapping units
        unit1 = MagicMock()
        unit1.world_x = 100
        unit1.world_y = 100
        unit1.radius = 15
        
        unit2 = MagicMock()
        unit2.world_x = 120  # Overlapping by 10 units
        unit2.world_y = 100
        unit2.radius = 15
        
        # Units start overlapping
        assert detect_unit_collision(unit1, unit2) is True
        
        # Resolve the collision
        resolve_collision_with_mass(unit1, unit2)
        
        # Calculate distance after resolution
        distance = math.hypot(unit2.world_x - unit1.world_x, unit2.world_y - unit1.world_y)
        
        # Units should now be at least at a distance equal to the sum of their radii
        self.assertGreaterEqual(distance, (unit1.radius + unit2.radius))
    
    def test_resolve_collision_with_mass_distributes_movement_evenly(self):
        """Test that resolve_collision_with_mass distributes movement evenly between units."""
        # Store original positions
        x1, y1 = 100, 100
        x2, y2 = 120, 100
        
        # Create two overlapping units
        unit1 = MagicMock()
        unit1.world_x = x1
        unit1.world_y = y1
        unit1.radius = 15
        
        unit2 = MagicMock()
        unit2.world_x = x2
        unit2.world_y = y2
        unit2.radius = 15
        
        # Resolve the collision
        resolve_collision_with_mass(unit1, unit2)
        
        # Calculate how much each unit moved
        unit1_movement = math.hypot(unit1.world_x - x1, unit1.world_y - y1)
        unit2_movement = math.hypot(unit2.world_x - x2, unit2.world_y - y2)
        
        # The difference in movement should be small (allowing for floating point precision)
        self.assertLess(abs(unit1_movement - unit2_movement), 0.001)
