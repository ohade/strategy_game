import unittest
import math
import pygame
from carrier import Carrier
from units import FriendlyUnit

class TestCarrierRotation(unittest.TestCase):
    """Test case for the carrier's rotation mechanism."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        pygame.init()
        self.carrier = Carrier(500, 300)
        self.initial_x = self.carrier.world_x
        self.initial_y = self.carrier.world_y
        
    def test_rotation_point_is_at_aft(self):
        """Test that the carrier rotates around its aft (back) end, not its center."""
        # Store the initial position
        initial_x = self.carrier.world_x
        initial_y = self.carrier.world_y
        initial_rotation = self.carrier.rotation
        
        # The carrier sprite has the front to the right, so aft would be to the left
        # Assuming sprite is facing right (0 degrees), aft is at negative x offset
        aft_offset_x = -self.carrier.sprite_width / 2  # Approximate aft position
        
        # Calculate expected position of the aft in world coordinates
        aft_world_x = initial_x + aft_offset_x * math.cos(math.radians(initial_rotation))
        aft_world_y = initial_y + aft_offset_x * math.sin(math.radians(initial_rotation))
        
        # Apply a 45-degree rotation
        self.carrier.set_rotation(initial_rotation + 45)
        
        # After rotation, the aft position should remain mostly the same
        # Calculate current aft position in world coordinates
        current_aft_offset_x = -self.carrier.sprite_width / 2
        current_aft_world_x = self.carrier.world_x + current_aft_offset_x * math.cos(math.radians(self.carrier.rotation))
        current_aft_world_y = self.carrier.world_y + current_aft_offset_x * math.sin(math.radians(self.carrier.rotation))
        
        # The aft position should be approximately the same before and after rotation
        self.assertAlmostEqual(aft_world_x, current_aft_world_x, delta=2.0)
        self.assertAlmostEqual(aft_world_y, current_aft_world_y, delta=2.0)
        
    def test_rotation_preserves_aft_position_during_movement(self):
        """Test that the aft position is preserved during rotation and movement."""
        # Store initial position and calculate initial aft position
        self.carrier.rotation = 0  # Start with carrier facing right
        initial_x = self.carrier.world_x
        initial_y = self.carrier.world_y
        aft_offset_x = -self.carrier.sprite_width / 2
        
        # Calculate initial aft position
        initial_aft_x = initial_x + aft_offset_x
        initial_aft_y = initial_y
        
        # Rotate by 90 degrees (now facing down) and update carrier position
        target_rotation = 90
        self.carrier.set_rotation(target_rotation)
        
        # The rotation should maintain the aft position but move the center
        # Calculate new aft position
        current_aft_offset_x = -self.carrier.sprite_width / 2 * math.cos(math.radians(target_rotation))
        current_aft_offset_y = -self.carrier.sprite_width / 2 * math.sin(math.radians(target_rotation))
        
        current_aft_x = self.carrier.world_x + current_aft_offset_x
        current_aft_y = self.carrier.world_y + current_aft_offset_y
        
        # The aft position should be approximately preserved
        self.assertAlmostEqual(initial_aft_x, current_aft_x, delta=2.0)
        self.assertAlmostEqual(initial_aft_y, current_aft_y, delta=2.0)
        
    def test_aft_rotation_during_turn_sequence(self):
        """Test that a sequence of small rotations maintains aft position."""
        # Initial setup - carrier facing right (0 degrees)
        self.carrier.rotation = 0
        initial_x = self.carrier.world_x
        initial_y = self.carrier.world_y
        aft_offset_x = -self.carrier.sprite_width / 2
        
        # Calculate initial aft position
        initial_aft_x = initial_x + aft_offset_x
        initial_aft_y = initial_y
        
        # Simulate a turning sequence with small increments (10 degrees each)
        for _ in range(9):  # 9 steps of 10 degrees = 90 degree total turn
            current_rotation = self.carrier.rotation
            # Rotate by 10 more degrees
            self.carrier.set_rotation(current_rotation + 10)
        
        # After a 90 degree turn, check if aft position is maintained
        final_rotation = self.carrier.rotation  # Should be ~90 degrees
        
        # Calculate final aft position
        final_aft_offset_x = -self.carrier.sprite_width / 2 * math.cos(math.radians(final_rotation))
        final_aft_offset_y = -self.carrier.sprite_width / 2 * math.sin(math.radians(final_rotation))
        
        final_aft_x = self.carrier.world_x + final_aft_offset_x
        final_aft_y = self.carrier.world_y + final_aft_offset_y
        
        # The aft position should be approximately preserved through the entire turn sequence
        self.assertAlmostEqual(initial_aft_x, final_aft_x, delta=2.0)
        self.assertAlmostEqual(initial_aft_y, final_aft_y, delta=2.0)

if __name__ == '__main__':
    unittest.main()
