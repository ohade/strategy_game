import unittest
import pygame
import sys
import os
import math
from unittest.mock import MagicMock, patch

# Add parent directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from carrier import Carrier
from constants import *

class TestCarrierMovementRestrictions(unittest.TestCase):
    """Tests for carrier movement restrictions during operations."""
    
    def setUp(self):
        """Set up the test environment."""
        # Initialize pygame for the test
        pygame.init()
        
        # Create a carrier at a known position
        self.carrier = Carrier(100, 100)
        
        # Reset carrier state
        self.carrier.velocity_x = 0
        self.carrier.velocity_y = 0
        self.carrier.state = "idle"
        self.carrier.move_target = None
        
        # Store original speeds for comparison
        self.original_max_speed = self.carrier.max_speed
        self.original_max_rotation_speed = self.carrier.max_rotation_speed
        
    def test_speed_reduction_during_launching(self):
        """Test that carrier speed is reduced during launch operations."""
        # Set a launching state
        self.carrier.is_launching = True
        
        # Update movement restrictions
        dt = 0.05
        self.carrier._update_movement_restrictions(dt)
        
        # Verify that speed is reduced to 30% of original
        self.assertAlmostEqual(self.carrier.max_speed, self.original_max_speed * 0.3, delta=0.01)
        
        # Verify that rotation speed is reduced to 50% of original
        self.assertAlmostEqual(self.carrier.max_rotation_speed, self.original_max_rotation_speed * 0.5, delta=0.01)
        
        # Verify that movement_restricted flag is set
        self.assertTrue(self.carrier.movement_restricted)
        
        # Verify that rotation_restricted flag is set
        self.assertTrue(self.carrier.rotation_restricted)
        
        # Verify reason is set
        self.assertEqual(self.carrier.restriction_reason, "Active launch operations")
        
    def test_speed_reduction_during_landing(self):
        """Test that carrier speed is reduced during landing operations."""
        # Set a landing state
        self.carrier.is_landing_sequence_active = True
        
        # Update movement restrictions
        dt = 0.05
        self.carrier._update_movement_restrictions(dt)
        
        # Verify that speed is reduced to 30% of original
        self.assertAlmostEqual(self.carrier.max_speed, self.original_max_speed * 0.3, delta=0.01)
        
        # Verify that rotation speed is reduced to 50% of original
        self.assertAlmostEqual(self.carrier.max_rotation_speed, self.original_max_rotation_speed * 0.5, delta=0.01)
        
        # Verify that movement_restricted flag is set
        self.assertTrue(self.carrier.movement_restricted)
        
        # Verify that rotation_restricted flag is set
        self.assertTrue(self.carrier.rotation_restricted)
        
        # Verify reason is set
        self.assertEqual(self.carrier.restriction_reason, "Active landing operations")
        
    def test_queue_based_restrictions(self):
        """Test that carrier speed is reduced when queues are not empty."""
        # Set non-empty queues
        self.carrier.launch_queue = ["fighter1"]
        
        # Update movement restrictions
        dt = 0.05
        self.carrier._update_movement_restrictions(dt)
        
        # Verify that speed is reduced
        self.assertAlmostEqual(self.carrier.max_speed, self.original_max_speed * 0.3, delta=0.01)
        
        # Reset and test landing queue
        self.carrier.launch_queue = []
        self.carrier.max_speed = self.original_max_speed
        self.carrier.max_rotation_speed = self.original_max_rotation_speed
        self.carrier.movement_restricted = False
        self.carrier.rotation_restricted = False
        
        # Set landing queue
        self.carrier.landing_queue = ["fighter2"]
        
        # Update movement restrictions
        self.carrier._update_movement_restrictions(dt)
        
        # Verify that speed is reduced
        self.assertAlmostEqual(self.carrier.max_speed, self.original_max_speed * 0.3, delta=0.01)
        
    def test_emergency_override(self):
        """Test that emergency movement overrides restrictions."""
        # Set a launching state
        self.carrier.is_launching = True
        
        # Set emergency override
        self.carrier.emergency_move = True
        
        # Update movement restrictions
        dt = 0.05
        self.carrier._update_movement_restrictions(dt)
        
        # Verify that speed is NOT reduced despite launch operation
        self.assertEqual(self.carrier.max_speed, self.original_max_speed)
        
        # Verify that rotation speed is NOT reduced
        self.assertEqual(self.carrier.max_rotation_speed, self.original_max_rotation_speed)
        
        # Verify that movement_restricted flag is not set
        self.assertFalse(self.carrier.movement_restricted)
        
        # Verify that rotation_restricted flag is not set
        self.assertFalse(self.carrier.rotation_restricted)
        
    def test_restrictions_reset(self):
        """Test that restrictions are reset when operations end."""
        # First apply restrictions
        self.carrier.is_launching = True
        self.carrier._update_movement_restrictions(0.05)
        
        # Verify restrictions are applied
        self.assertTrue(self.carrier.movement_restricted)
        
        # Now end operations
        self.carrier.is_launching = False
        self.carrier._update_movement_restrictions(0.05)
        
        # Verify restrictions are reset
        self.assertFalse(self.carrier.movement_restricted)
        self.assertEqual(self.carrier.max_speed, self.original_max_speed)
        self.assertEqual(self.carrier.max_rotation_speed, self.original_max_rotation_speed)
        self.assertEqual(self.carrier.restriction_reason, "")

if __name__ == '__main__':
    unittest.main()
