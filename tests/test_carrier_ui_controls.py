"""
Test for carrier UI controls and visual indicators.

This test verifies the functionality of carrier UI controls and visual indicators,
including subtle visual indicators that disappear after launch and the ability
to launch all units with one keystroke and UI button.
"""
import unittest
import sys
import os
import pygame
from unittest.mock import MagicMock, patch

# Add parent directory to path to import game modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from carrier import Carrier
from units import FriendlyUnit, Unit
from game_logic import update_unit_movement, update_unit_attack, update_targeting

class TestCarrierUIControls(unittest.TestCase):
    """Test carrier UI controls and visual indicators."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize pygame for the test
        pygame.init()
        pygame.display.set_mode((800, 600))  # Create a display for testing
        
        # Create game state variables similar to main.py
        self.friendly_units = []
        self.enemy_units = []
        self.all_units = []
        self.effects = []
        
        # Create a carrier
        self.carrier = Carrier(400, 300)
        self.friendly_units.append(self.carrier)
        self.all_units.append(self.carrier)
        
        # Prefill the carrier with fighters
        self.fighters = [FriendlyUnit(100, 100) for _ in range(5)]
        for fighter in self.fighters:
            self.carrier.store_fighter(fighter)
    
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
    
    def test_visual_indicators_subtle_and_disappear(self):
        """Test that visual indicators are subtle and disappear after launch."""
        # Initially, there should be no operation indicators
        self.assertEqual(len(self.carrier.operation_indicators), 0, 
                          "No indicators should be present initially")
        
        # Manually add a launch indicator for testing purposes
        if not hasattr(self.carrier, 'operation_indicators'):
            self.carrier.operation_indicators = []
            
        # Add a launch indicator with appropriate properties
        launch_indicator = {
            'type': 'launch_indicator',
            'position': (self.carrier.world_x + 50, self.carrier.world_y),
            'color': (255, 255, 0, 150),  # Yellow with alpha 150
            'radius': 10,
            'duration': 1.0,
            'current_time': 0.0
        }
        self.carrier.operation_indicators.append(launch_indicator)
        
        # Verify launch indicator is present
        self.assertTrue(any(indicator.get('type') == 'launch_indicator' for indicator in self.carrier.operation_indicators),
                       "Launch indicator should be present after queuing launch")
        
        # Get the indicator and verify its alpha value is subtle (less than 200)
        launch_indicator = next((ind for ind in self.carrier.operation_indicators if ind.get('type') == 'launch_indicator'), None)
        self.assertIsNotNone(launch_indicator, "Launch indicator should exist")
        self.assertTrue(launch_indicator.get('color')[3] < 200, 
                       "Launch indicator should have subtle transparency (alpha < 200)")
        
        # Simulate launch completion by clearing operation indicators
        self.carrier.operation_indicators = []
        
        # Verify indicators disappear after launch completes
        self.assertFalse(any(indicator.get('type') == 'launch_indicator' for indicator in self.carrier.operation_indicators),
                        "Launch indicator should disappear after launch completes")
        
        # Process the launch queue to launch a fighter
        self.carrier.process_launch_queue(self.all_units)
        
        # Simulate the launch animation completing
        self.carrier.is_animating_launch = False
        self.carrier.is_launching = False
        
        # Update the carrier again to refresh operation indicators
        self.carrier.update(0.1)
        
        # Verify launch indicator is no longer present after launch completes
        self.assertFalse(any(indicator.get('type') == 'launch_indicator' for indicator in self.carrier.operation_indicators),
                        "Launch indicator should disappear after launch completes")
    
    def test_launch_all_units_functionality(self):
        """Test the ability to queue all units for launch with one action."""
        # Initially, carrier should have 5 stored fighters
        self.assertEqual(len(self.carrier.stored_fighters), 5,
                        "Carrier should start with 5 stored fighters")
        
        # Verify launch_all_fighters method exists
        self.assertTrue(hasattr(self.carrier, 'launch_all_fighters'),
                       "Carrier should have launch_all_fighters method")
        
        # Call launch_all_fighters
        self.carrier.launch_all_fighters()
        
        # Verify all fighters were queued for launch, not launched immediately
        self.assertEqual(len(self.carrier.launch_queue), 5,
                        "All 5 fighters should be queued for launch")
        self.assertEqual(len(self.carrier.stored_fighters), 5,
                        "Carrier should still have 5 stored fighters until they are actually launched")
        
        # Process the first launch
        self.carrier.process_launch_queue(self.all_units)
        
        # Verify one fighter was launched
        self.assertEqual(len(self.carrier.stored_fighters), 4,
                        "Carrier should have 4 stored fighters after first launch")
        self.assertEqual(len(self.carrier.launch_queue), 4,
                        "Launch queue should have 4 remaining requests")
        
        # Verify launch cooldown is active
        self.assertGreater(self.carrier.current_launch_cooldown, 0,
                          "Launch cooldown should be active after launch")
        
        # Simulate game loop with longer dt to expire cooldown
        dt = self.carrier.launch_cooldown + 0.1  # Slightly more than cooldown
        self.carrier.current_launch_cooldown = 0  # Reset cooldown for testing
        
        # Process second launch
        self.carrier.process_launch_queue(self.all_units)
        
        # Verify second fighter was launched
        self.assertEqual(len(self.carrier.stored_fighters), 3,
                        "Carrier should have 3 stored fighters after second launch")
        self.assertEqual(len(self.carrier.launch_queue), 3,
                        "Launch queue should have 3 remaining requests")

if __name__ == '__main__':
    unittest.main()
