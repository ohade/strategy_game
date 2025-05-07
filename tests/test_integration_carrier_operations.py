"""
Integration test for carrier operations including movement restrictions during launch and landing.

This test verifies that carrier movement restrictions are properly applied during
launch and landing operations, and that the carrier behaves consistently with
the expectations set in the unit tests.
"""
import unittest
import sys
import os
import pygame
import math
from unittest.mock import MagicMock, patch

# Add parent directory to path to import game modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from carrier import Carrier
from units import FriendlyUnit, Unit
from game_logic import update_unit_movement, update_targeting
from unit_mechanics import smooth_movement

class TestCarrierOperationsIntegration(unittest.TestCase):
    """Integration test for carrier operations including movement restrictions."""
    
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
        self.fighters = [FriendlyUnit(100, 100) for _ in range(3)]
        for fighter in self.fighters:
            self.carrier.store_fighter(fighter)
    
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
    
    def simulate_game_loop(self, dt, iterations=1):
        """Simulate the game loop for a specified number of iterations."""
        for _ in range(iterations):
            # Process the carrier's launch queue
            self.carrier.process_launch_queue(self.all_units)
            
            # Update all units
            for unit in self.all_units:
                effect = unit.update(dt)
                if effect:
                    self.effects.append(effect)
                
                # Update targeting
                update_targeting(unit, self.friendly_units, self.enemy_units)
    
    def test_carrier_movement_restrictions_during_launch(self):
        """Test that carrier movement is restricted during launch operations."""
        # Set initial position
        initial_x, initial_y = self.carrier.world_x, self.carrier.world_y
        
        # Command carrier to move to a new position
        target_x, target_y = 600, 400
        self.carrier.move_to_point(target_x, target_y)
        
        # Verify carrier is in moving state
        self.assertEqual(self.carrier.state, "moving")
        self.assertEqual(self.carrier.move_target, (target_x, target_y))
        
        # Simulate a few updates to start moving
        self.simulate_game_loop(0.1, iterations=5)
        
        # Verify carrier has started moving
        self.assertNotEqual(self.carrier.world_x, initial_x)
        self.assertNotEqual(self.carrier.world_y, initial_y)
        
        # Store current position
        moving_x, moving_y = self.carrier.world_x, self.carrier.world_y
        
        # Queue a launch request
        self.carrier.queue_launch_request()
        
        # Verify launch queue has a fighter
        self.assertEqual(len(self.carrier.launch_queue), 1)
        
        # Simulate a few updates to process the launch
        self.simulate_game_loop(0.1, iterations=5)
        
        # Verify carrier is now in launching state
        self.assertTrue(self.carrier.is_launching)
        
        # Verify movement is restricted
        self.assertTrue(self.carrier.movement_restricted)
        
        # Command carrier to move to a different position
        new_target_x, new_target_y = 200, 200
        self.carrier.move_to_point(new_target_x, new_target_y)
        
        # Simulate a few more updates
        self.simulate_game_loop(0.1, iterations=5)
        
        # Verify carrier position hasn't changed significantly during launch
        # (allowing for small movement due to inertia)
        distance_moved = math.sqrt(
            (self.carrier.world_x - moving_x)**2 + 
            (self.carrier.world_y - moving_y)**2
        )
        
        # The carrier should have slowed down significantly or stopped
        self.assertLess(distance_moved, 50, 
                        "Carrier should move very little during launch operations")
        
        # Verify carrier speed is reduced
        self.assertLess(self.carrier.max_speed, 100, 
                        "Carrier speed should be reduced during launch")
    
    def test_carrier_movement_restrictions_during_landing(self):
        """Test that carrier movement is restricted during landing operations."""
        # Create a fighter outside the carrier
        fighter = FriendlyUnit(500, 300)
        self.friendly_units.append(fighter)
        self.all_units.append(fighter)
        
        # Set initial position
        initial_x, initial_y = self.carrier.world_x, self.carrier.world_y
        
        # Command carrier to move to a new position
        target_x, target_y = 600, 400
        self.carrier.move_to_point(target_x, target_y)
        
        # Simulate a few updates to start moving
        self.simulate_game_loop(0.1, iterations=5)
        
        # Verify carrier has started moving
        self.assertNotEqual(self.carrier.world_x, initial_x)
        self.assertNotEqual(self.carrier.world_y, initial_y)
        
        # Store current position
        moving_x, moving_y = self.carrier.world_x, self.carrier.world_y
        
        # Command fighter to return to carrier
        fighter.target_carrier = self.carrier
        fighter.is_returning_to_carrier = True
        fighter.landing_stage = "approach"
        
        # Add fighter to landing queue
        self.carrier.queue_landing_request(fighter)
        
        # Verify landing queue has a fighter
        self.assertEqual(len(self.carrier.landing_queue), 1)
        
        # Simulate a few updates to process the landing
        self.simulate_game_loop(0.1, iterations=5)
        
        # Verify carrier is now in landing state
        self.assertTrue(self.carrier.is_landing_sequence_active)
        
        # Verify movement is restricted
        self.assertTrue(self.carrier.movement_restricted)
        
        # Command carrier to move to a different position
        new_target_x, new_target_y = 200, 200
        self.carrier.move_to_point(new_target_x, new_target_y)
        
        # Simulate a few more updates
        self.simulate_game_loop(0.1, iterations=5)
        
        # Verify carrier position hasn't changed significantly during landing
        # (allowing for small movement due to inertia)
        distance_moved = math.sqrt(
            (self.carrier.world_x - moving_x)**2 + 
            (self.carrier.world_y - moving_y)**2
        )
        
        # The carrier should have slowed down significantly or stopped
        self.assertLess(distance_moved, 50, 
                        "Carrier should move very little during landing operations")
        
        # Verify carrier speed is reduced
        self.assertLess(self.carrier.max_speed, 100, 
                        "Carrier speed should be reduced during landing")
    
    def test_emergency_move_overrides_restrictions(self):
        """Test that emergency move overrides movement restrictions."""
        # Queue a launch request to trigger movement restrictions
        self.carrier.queue_launch_request()
        
        # Simulate a few updates to process the launch
        self.simulate_game_loop(0.1, iterations=5)
        
        # Verify carrier is now in launching state with movement restricted
        self.assertTrue(self.carrier.is_launching)
        self.assertTrue(self.carrier.movement_restricted)
        
        # Store current position
        initial_x, initial_y = self.carrier.world_x, self.carrier.world_y
        
        # Set emergency move flag
        self.carrier.emergency_move = True
        
        # Command carrier to move to a new position
        target_x, target_y = 600, 400
        self.carrier.move_to_point(target_x, target_y)
        
        # Simulate more updates to give the carrier time to move
        self.simulate_game_loop(0.1, iterations=20)
        
        # Verify carrier has moved despite restrictions
        distance_moved = math.sqrt(
            (self.carrier.world_x - initial_x)**2 + 
            (self.carrier.world_y - initial_y)**2
        )
        
        # The carrier should have moved significantly
        self.assertGreater(distance_moved, 15, 
                          "Carrier should move during emergency despite restrictions")

if __name__ == '__main__':
    unittest.main()
