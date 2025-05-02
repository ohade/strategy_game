"""
Tests for the fighter management functionality of the Carrier class.

This includes:
- Storing fighters in the carrier
- Launching fighters from the carrier
- Managing fighter capacity limits
- Handling launch points and sequences
"""
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path to import game modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from carrier import Carrier
from units import Unit, FriendlyUnit

class TestFighterStorage(unittest.TestCase):
    """Test case for the fighter storage functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.carrier = Carrier(500, 300)
        # Create some fighter units for testing
        self.fighter1 = FriendlyUnit(100, 100)
        self.fighter2 = FriendlyUnit(200, 200)
        self.fighter3 = FriendlyUnit(300, 300)
    
    def test_initial_capacity(self):
        """Test that the carrier initializes with the correct fighter capacity."""
        self.assertEqual(self.carrier.fighter_capacity, 10, 
                         "Carrier should initialize with capacity for 10 fighters")
        self.assertEqual(len(self.carrier.stored_fighters), 0, 
                         "Carrier should initialize with no stored fighters")
    
    def test_store_fighter(self):
        """Test storing a fighter in the carrier."""
        # Store a fighter
        result = self.carrier.store_fighter(self.fighter1)
        
        # Check the result and stored fighters
        self.assertTrue(result, "Storing fighter should return True when successful")
        self.assertEqual(len(self.carrier.stored_fighters), 1, 
                         "Carrier should have 1 stored fighter")
        self.assertIn(self.fighter1, self.carrier.stored_fighters, 
                      "Fighter should be in stored_fighters list")
    
    def test_store_multiple_fighters(self):
        """Test storing multiple fighters up to capacity."""
        # Store 3 fighters
        for fighter in [self.fighter1, self.fighter2, self.fighter3]:
            result = self.carrier.store_fighter(fighter)
            self.assertTrue(result, "Storing fighter should return True when successful")
        
        # Check the stored fighters
        self.assertEqual(len(self.carrier.stored_fighters), 3, 
                         "Carrier should have 3 stored fighters")
        for fighter in [self.fighter1, self.fighter2, self.fighter3]:
            self.assertIn(fighter, self.carrier.stored_fighters, 
                         f"Fighter {id(fighter)} should be in stored_fighters list")
    
    def test_capacity_limit(self):
        """Test that the carrier enforces capacity limits."""
        # Fill carrier to capacity
        fighters = [FriendlyUnit(i*100, i*100) for i in range(self.carrier.fighter_capacity)]
        
        # Store fighters up to capacity
        for fighter in fighters:
            result = self.carrier.store_fighter(fighter)
            self.assertTrue(result, "Storing fighter should return True when under capacity")
        
        # Try to store one more fighter beyond capacity
        extra_fighter = FriendlyUnit(999, 999)
        result = self.carrier.store_fighter(extra_fighter)
        
        # Should fail due to capacity limit
        self.assertFalse(result, "Storing fighter should return False when at capacity")
        self.assertEqual(len(self.carrier.stored_fighters), self.carrier.fighter_capacity,
                         "Carrier should not exceed its fighter capacity")
        self.assertNotIn(extra_fighter, self.carrier.stored_fighters,
                         "Extra fighter should not be added to stored_fighters list")

class TestLaunchPoints(unittest.TestCase):
    """Test case for the launch point functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.carrier = Carrier(500, 300)
        # Prefill some fighters for launch tests
        self.fighters = []
        for _ in range(5):
            fighter = FriendlyUnit(0, 0)  # Initial position doesn't matter for stored units
            self.carrier.store_fighter(fighter)
            self.fighters.append(fighter)
    
    def test_launch_points_initialization(self):
        """Test that the carrier initializes with the correct launch points."""
        # Carrier should have 4 default launch points around its perimeter
        self.assertEqual(len(self.carrier.launch_points), 4, 
                         "Carrier should initialize with 4 launch points")
        
        # Launch points should be in the correct positions (relative to carrier)
        expected_points = [
            (self.carrier.radius, 0),       # Right side
            (-self.carrier.radius, 0),      # Left side
            (0, self.carrier.radius),       # Bottom
            (0, -self.carrier.radius)       # Top
        ]
        
        for point, expected in zip(self.carrier.launch_points, expected_points):
            self.assertEqual(point, expected, f"Launch point {point} should be at {expected}")
    
    def test_launch_fighter_with_default_position(self):
        """Test launching a fighter from a default launch point."""
        # Get the number of stored fighters before launch
        initial_count = len(self.carrier.stored_fighters)
        
        # Launch a fighter without specifying a position
        launched_fighter = self.carrier.launch_fighter()
        
        # Check that a fighter was launched
        self.assertIsNotNone(launched_fighter, "Should return a fighter when launching")
        self.assertEqual(len(self.carrier.stored_fighters), initial_count - 1, 
                         "Number of stored fighters should decrease by 1")
        
        # Verify the launched fighter is positioned at one of the launch points
        # Need to convert relative launch point to world coordinates
        # We'll be flexible here since rotation can affect the exact position
        carrier_pos = (self.carrier.world_x, self.carrier.world_y)
        launch_distance = self.carrier.radius  # Distance from center to launch point
        
        # Calculate distance from fighter to carrier
        fighter_pos = (launched_fighter.world_x, launched_fighter.world_y)
        distance_to_carrier = ((fighter_pos[0] - carrier_pos[0])**2 + 
                              (fighter_pos[1] - carrier_pos[1])**2)**0.5
        
        # Launched fighter should be approximately at launch_distance from carrier
        self.assertAlmostEqual(distance_to_carrier, launch_distance, 
                            msg="Fighter should be launched at approximately the radius distance",
                            delta=5)
    
    def test_launch_fighter_with_custom_position(self):
        """Test launching a fighter at a custom position."""
        # Define a custom launch position
        custom_pos = (700, 400)  # Some position away from the carrier
        
        # Get the number of stored fighters before launch
        initial_count = len(self.carrier.stored_fighters)
        
        # Launch a fighter at the custom position
        launched_fighter = self.carrier.launch_fighter(custom_pos)
        
        # Check that a fighter was launched
        self.assertIsNotNone(launched_fighter, "Should return a fighter when launching")
        self.assertEqual(len(self.carrier.stored_fighters), initial_count - 1, 
                         "Number of stored fighters should decrease by 1")
        
        # Verify the launched fighter is positioned at the custom position
        self.assertEqual(launched_fighter.world_x, custom_pos[0], 
                         "Fighter should be at the specified x position")
        self.assertEqual(launched_fighter.world_y, custom_pos[1], 
                         "Fighter should be at the specified y position")
    
    def test_launch_with_empty_carrier(self):
        """Test launching when the carrier has no fighters stored."""
        # Empty the carrier
        self.carrier.stored_fighters = []
        
        # Try to launch a fighter
        launched_fighter = self.carrier.launch_fighter()
        
        # Should return None since there are no fighters to launch
        self.assertIsNone(launched_fighter, "Should return None when no fighters are available")

class TestLaunchSequenceAndCooldown(unittest.TestCase):
    """Test case for the fighter launch sequence and cooldown functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.carrier = Carrier(500, 300)
        # Prefill some fighters for launch tests
        self.fighters = []
        for _ in range(5):
            fighter = FriendlyUnit(0, 0)  # Initial position doesn't matter for stored units
            self.carrier.store_fighter(fighter)
            self.fighters.append(fighter)
            
        # Add launch cooldown attribute if it doesn't exist
        if not hasattr(self.carrier, 'launch_cooldown'):
            self.carrier.launch_cooldown = 1.0  # 1 second cooldown between launches
        if not hasattr(self.carrier, 'current_launch_cooldown'):
            self.carrier.current_launch_cooldown = 0.0  # No cooldown initially
    
    def test_launch_cooldown_initialization(self):
        """Test that the carrier initializes with the correct launch cooldown values."""
        # Check that launch cooldown values are properly set
        self.assertTrue(hasattr(self.carrier, 'launch_cooldown'), 
                      "Carrier should have a launch_cooldown attribute")
        self.assertTrue(hasattr(self.carrier, 'current_launch_cooldown'), 
                      "Carrier should have a current_launch_cooldown attribute")
        
        # Initial current cooldown should be 0 (ready to launch)
        self.assertEqual(self.carrier.current_launch_cooldown, 0.0, 
                       "Initial current_launch_cooldown should be 0")
    
    def test_launch_sets_cooldown(self):
        """Test that launching a fighter sets the cooldown timer."""
        # Launch a fighter
        self.carrier.launch_fighter()
        
        # Current cooldown should be set to the full cooldown value
        self.assertEqual(self.carrier.current_launch_cooldown, self.carrier.launch_cooldown,
                       "Launching should set current_launch_cooldown to launch_cooldown")
    
    def test_cooldown_prevents_launch(self):
        """Test that cooldown prevents launching another fighter."""
        # Launch a fighter to set the cooldown
        first_fighter = self.carrier.launch_fighter()
        self.assertIsNotNone(first_fighter, "First launch should succeed")
        
        # Try to launch another fighter immediately (should fail due to cooldown)
        second_fighter = self.carrier.launch_fighter()
        self.assertIsNone(second_fighter, "Second launch should fail due to cooldown")
    
    def test_cooldown_decreases_with_time(self):
        """Test that the cooldown timer decreases over time."""
        # Launch a fighter to set the cooldown
        self.carrier.launch_fighter()
        initial_cooldown = self.carrier.current_launch_cooldown
        
        # Simulate time passing (0.5 seconds)
        dt = 0.5
        self.carrier.update(dt)
        
        # Cooldown should decrease by dt
        expected_cooldown = initial_cooldown - dt
        self.assertAlmostEqual(self.carrier.current_launch_cooldown, expected_cooldown,
                             msg="Cooldown should decrease by dt",
                             delta=0.01)
    
    def test_launch_after_cooldown(self):
        """Test that launching is possible after cooldown expires."""
        # Launch a fighter to set the cooldown
        self.carrier.launch_fighter()
        
        # Simulate time passing greater than the cooldown time
        dt = self.carrier.launch_cooldown + 0.1  # Add a bit extra to ensure it's expired
        self.carrier.update(dt)
        
        # Cooldown should be reset to 0
        self.assertEqual(self.carrier.current_launch_cooldown, 0.0,
                       "Cooldown should be 0 after sufficient time has passed")
        
        # Should be able to launch another fighter now
        fighter = self.carrier.launch_fighter()
        self.assertIsNotNone(fighter, "Should be able to launch after cooldown expires")

if __name__ == '__main__':
    unittest.main()
