"""
Tests for the fighter launch mechanics to ensure proper behavior.

This test suite focuses on three specific issues:
1. Fighters should launch from the green arrow location (front of the carrier)
2. Fighters should not push the carrier (carrier should be much heavier)
3. Fighters should stop moving after reaching their patrol point
"""
import unittest
import sys
import os
import math
import pygame
from unittest.mock import MagicMock, patch

# Add parent directory to path to import game modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from carrier import Carrier
from units import FriendlyUnit, Unit
from game_logic import detect_unit_collision, resolve_collision_with_mass

class TestFighterLaunchPosition(unittest.TestCase):
    """Test that fighters launch from the front of the carrier (green arrow location)."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize pygame for the test
        pygame.init()
        pygame.display.set_mode((800, 600))  # Create a display for testing
        
        # Create a carrier at position (400, 300) with rotation 0 (facing right)
        self.carrier = Carrier(400, 300)
        self.carrier.rotation = 0  # Ensure carrier is facing right
        
        # Store a fighter in the carrier
        self.fighter = FriendlyUnit(100, 100)
        self.carrier.store_fighter(self.fighter)
    
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
    
    def test_fighter_launches_from_front(self):
        """Test that fighter launches from the front of the carrier."""
        # Launch a fighter
        launched_fighter = self.carrier.launch_fighter()
        
        # Calculate where the front of the carrier should be
        # The front should be at the right side when rotation is 0
        expected_x = self.carrier.world_x + self.carrier.radius * 1.2  # Front position
        expected_y = self.carrier.world_y  # Same Y position as carrier
        
        # Check that the fighter was launched at the front of the carrier
        self.assertAlmostEqual(launched_fighter.world_x, expected_x, delta=5,
                              msg="Fighter should be launched from the front of the carrier")
        self.assertAlmostEqual(launched_fighter.world_y, expected_y, delta=5,
                              msg="Fighter should be launched from the front of the carrier")
        
    def test_fighter_launches_from_front_when_rotated(self):
        """Test that fighter launches from the front of the carrier when rotated."""
        # Rotate the carrier 90 degrees (facing down)
        self.carrier.rotation = 90
        
        # Launch a fighter
        launched_fighter = self.carrier.launch_fighter()
        
        # Calculate where the front of the carrier should be when rotated 90 degrees
        # The front should be at the bottom when rotation is 90
        expected_x = self.carrier.world_x  # Same X position as carrier
        expected_y = self.carrier.world_y + self.carrier.radius * 1.2  # Front position
        
        # Check that the fighter was launched at the front of the carrier
        self.assertAlmostEqual(launched_fighter.world_x, expected_x, delta=5,
                              msg="Fighter should be launched from the front of the carrier when rotated")
        self.assertAlmostEqual(launched_fighter.world_y, expected_y, delta=5,
                              msg="Fighter should be launched from the front of the carrier when rotated")


class TestCarrierMass(unittest.TestCase):
    """Test that the carrier has much higher mass than fighters and is not pushed by them."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize pygame for the test
        pygame.init()
        pygame.display.set_mode((800, 600))  # Create a display for testing
        
        # Create a carrier and a fighter
        self.carrier = Carrier(400, 300)
        self.fighter = FriendlyUnit(400 + self.carrier.radius + 5, 300)  # Position fighter near carrier
    
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
    
    def test_carrier_has_higher_mass(self):
        """Test that the carrier has much higher mass than fighters."""
        # Check that carrier mass is significantly higher than fighter mass
        self.assertGreater(self.carrier.mass, self.fighter.mass * 5,
                          msg="Carrier should have much higher mass than fighters")
    
    def test_carrier_not_pushed_by_fighter(self):
        """Test that the carrier is not significantly pushed by a fighter during collision."""
        # Record carrier's initial position
        initial_carrier_x = self.carrier.world_x
        initial_carrier_y = self.carrier.world_y
        
        # Simulate a collision between carrier and fighter
        # Position fighter to overlap with carrier
        self.fighter.world_x = self.carrier.world_x + self.carrier.radius * 0.5
        self.fighter.world_y = self.carrier.world_y
        
        # Resolve the collision
        resolve_collision_with_mass(self.carrier, self.fighter)
        
        # Calculate how much the carrier moved
        carrier_movement = math.hypot(
            self.carrier.world_x - initial_carrier_x,
            self.carrier.world_y - initial_carrier_y
        )
        
        # The carrier should barely move due to its high mass
        self.assertLess(carrier_movement, 5.0,
                       msg="Carrier should not be significantly pushed by a fighter")


class TestFighterPatrolBehavior(unittest.TestCase):
    """Test that fighters stop moving after reaching their patrol point."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize pygame for the test
        pygame.init()
        pygame.display.set_mode((800, 600))  # Create a display for testing
        
        # Create a carrier and a fighter
        self.carrier = Carrier(400, 300)
        self.fighter = FriendlyUnit(100, 100)
        
        # Store and launch the fighter
        self.carrier.store_fighter(self.fighter)
        self.launched_fighter = self.carrier.launch_fighter()
    
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
    
    def test_fighter_has_patrol_timer(self):
        """Test that launched fighters have a patrol timer set."""
        # Check that the launched fighter has a patrol timer set
        self.assertTrue(hasattr(self.launched_fighter, 'patrol_timer'),
                       msg="Launched fighter should have a patrol_timer attribute")
        self.assertGreater(self.launched_fighter.patrol_timer, 0,
                          msg="Launched fighter should have a positive patrol timer")
    
    def test_fighter_stops_after_patrol_timer(self):
        """Test that fighters stop moving after their patrol timer expires."""
        # Set the fighter's patrol timer to a small value
        self.launched_fighter.patrol_timer = 0.1
        
        # Set the fighter to moving state with a target
        self.launched_fighter.set_state("moving")
        self.launched_fighter.move_target = (500, 300)
        
        # Update the fighter with a time delta larger than the patrol timer
        self.launched_fighter.update(0.2)
        
        # Check that the fighter has stopped moving
        self.assertEqual(self.launched_fighter.state, "idle",
                        msg="Fighter should stop moving after patrol timer expires")
        self.assertIsNone(self.launched_fighter.move_target,
                         msg="Fighter should clear its move target after patrol timer expires")


if __name__ == '__main__':
    unittest.main()
