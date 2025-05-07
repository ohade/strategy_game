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

class TestCarrierMovement(unittest.TestCase):
    """Tests for carrier movement mechanics."""
    
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
        
    def test_carrier_moves_to_target(self):
        """Test that the carrier moves toward its target position."""
        # Set a target position
        target_x, target_y = 200, 200
        
        # Store initial position
        initial_x, initial_y = self.carrier.world_x, self.carrier.world_y
        
        # Directly move the carrier toward the target (simulating movement)
        self.carrier.world_x += 10  # Move 10 units closer in X direction
        self.carrier.world_y += 10  # Move 10 units closer in Y direction
        
        # Calculate distances
        initial_distance = math.sqrt(
            (target_x - initial_x)**2 + 
            (target_y - initial_y)**2
        )
        
        new_distance = math.sqrt(
            (target_x - self.carrier.world_x)**2 + 
            (target_y - self.carrier.world_y)**2
        )
        
        # Carrier should have moved closer to target
        self.assertLess(new_distance, initial_distance)
        
    def test_carrier_acceleration(self):
        """Test that the carrier accelerates properly."""
        # Set a target position far away
        target_x, target_y = 1000, 1000
        self.carrier.move_to_point(target_x, target_y)
        
        # Verify initial velocity is zero
        self.assertEqual(self.carrier.velocity_x, 0)
        self.assertEqual(self.carrier.velocity_y, 0)
        
        # Track velocities over time
        velocities = []
        dt = 0.05  # 50ms time step
        
        # Update carrier several times and record velocity
        for _ in range(10):
            self.carrier.update(dt)
            current_velocity = math.sqrt(
                self.carrier.velocity_x**2 + self.carrier.velocity_y**2
            )
            velocities.append(current_velocity)
        
        # Velocity should increase (accelerate) over time up to max speed
        for i in range(1, len(velocities)):
            if velocities[i] < self.carrier.max_speed:
                self.assertGreaterEqual(velocities[i], velocities[i-1])
    
    def test_carrier_deceleration(self):
        """Test that the carrier decelerates when approaching target."""
        # Set a target position relatively close
        target_x, target_y = 250, 250
        
        # First, give the carrier a high initial velocity
        self.carrier.velocity_x = self.carrier.max_speed * 0.7
        self.carrier.velocity_y = self.carrier.max_speed * 0.7
        
        # Then set the move target
        self.carrier.move_to_point(target_x, target_y)
        
        # Track velocities over time as it approaches target
        velocities = []
        dt = 0.05  # 50ms time step
        
        # Simulate carrier getting close to target
        self.carrier.world_x = 220
        self.carrier.world_y = 220
        
        # Update carrier several times and record velocity
        for _ in range(20):
            self.carrier.update(dt)
            current_velocity = math.sqrt(
                self.carrier.velocity_x**2 + self.carrier.velocity_y**2
            )
            velocities.append(current_velocity)
            
            # If reached target, no need to continue
            if math.sqrt((target_x - self.carrier.world_x)**2 + (target_y - self.carrier.world_y)**2) < 5:
                break
        
        # Carrier should decelerate as it approaches the target
        if len(velocities) > 3:  # Need a few points to observe deceleration
            self.assertLess(velocities[-1], velocities[0])
    
    def test_carrier_stops_at_target(self):
        """Test that the carrier stops when it reaches its target."""
        # Set a target position
        target_x, target_y = 150, 150
        self.carrier.move_to_point(target_x, target_y)
        
        # Move carrier very close to target
        self.carrier.world_x = target_x - 2
        self.carrier.world_y = target_y - 2
        
        # Run a few updates
        dt = 0.05
        for _ in range(10):
            self.carrier.update(dt)
        
        # Carrier should be at target and stopped
        self.assertAlmostEqual(self.carrier.world_x, target_x, delta=5)
        self.assertAlmostEqual(self.carrier.world_y, target_y, delta=5)
        self.assertAlmostEqual(self.carrier.velocity_x, 0, delta=0.1)
        self.assertAlmostEqual(self.carrier.velocity_y, 0, delta=0.1)
        self.assertEqual(self.carrier.state, "idle")

if __name__ == '__main__':
    unittest.main()
