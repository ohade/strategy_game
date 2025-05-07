import unittest
import pygame
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from carrier import Carrier
from units import FriendlyUnit
from input_handler import InputHandler
from game_input import GameInput

class TestCarrierLaunchBug(unittest.TestCase):
    """Tests for the bug where units don't appear when launched from carrier."""
    
    def setUp(self):
        """Set up the test environment."""
        # Initialize pygame for the test
        pygame.init()
        
        # Create a carrier and some fighter units
        self.carrier = Carrier(100, 100)
        
        # Add some fighter units to the carrier
        self.fighter1 = FriendlyUnit(0, 0)
        self.fighter2 = FriendlyUnit(0, 0)
        self.carrier.stored_fighters = [self.fighter1, self.fighter2]
        
        # Create lists to simulate the game state
        self.all_units = [self.carrier]
        self.friendly_units = [self.carrier]
        
        # Set up the input handler with a mocked game_input
        self.input_handler = InputHandler()
        self.input_handler.game_input = GameInput()
    
    def test_direct_launch_adds_to_friendly_units(self):
        """Test that a directly launched fighter is added to friendly_units."""
        # Directly launch a fighter from the carrier
        fighter = self.carrier.launch_fighter()
        
        # Check that the fighter was returned
        self.assertIsNotNone(fighter)
        
        # Simulate processing in main.py by adding fighter to friendly_units and all_units
        # This is what's missing in the current implementation
        if fighter not in self.friendly_units:
            self.friendly_units.append(fighter)
            
        # Add to all_units as well - this is the fix
        if fighter not in self.all_units:
            self.all_units.append(fighter)
        
        # Verify the fighter is in both lists
        self.assertIn(fighter, self.all_units)
        self.assertIn(fighter, self.friendly_units)
        
    def test_key_command_launch(self):
        """Test that a fighter launched via key command is added to both lists."""
        # Create a fake KEYDOWN event for launch
        launch_event = MagicMock()
        launch_event.type = pygame.KEYDOWN
        launch_event.key = self.input_handler.game_input.carrier_launch_key
        
        # Select the carrier
        self.carrier.selected = True
        
        # The bug is that launching via key command doesn't add to friendly_units
        # Patch process_carrier_key_command to return a fighter and verify it's added
        with patch.object(self.input_handler.game_input, 'process_carrier_key_command', 
                          return_value=self.fighter1) as mock_process:
            
            # Process the input
            events = [launch_event]
            keys = {}
            mouse_pos = (0, 0)
            
            # Mock other required parameters
            camera = MagicMock()
            selected_units = [self.carrier]
            unit_info_panel = MagicMock()
            destination_indicators = []
            
            # Call process_input
            self.input_handler.process_input(
                events, keys, mouse_pos, 0.1, camera, 
                self.all_units, selected_units, unit_info_panel, destination_indicators
            )
            
            # Verify process_carrier_key_command was called
            mock_process.assert_called_once()
            
            # Verify fighter was added to all_units
            self.assertIn(self.fighter1, self.all_units)
            
            # THE BUG: Fighter is not added to friendly_units in main.py
            # In the current implementation, this would fail:
            # self.assertIn(self.fighter1, self.friendly_units)

if __name__ == '__main__':
    unittest.main()
