import unittest
import pygame
from carrier import Carrier
from units import FriendlyUnit
from game_input import GameInput  # We'll need to create or modify this

class TestPlayerControlsForCarrier(unittest.TestCase):
    """Tests for player-initiated fighter launches and other carrier operations."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        pygame.init()
        # Initialize required components
        self.carrier = Carrier(500, 300)
        
        # Pre-fill carrier with fighters for testing
        for _ in range(3):
            fighter = FriendlyUnit(0, 0)
            self.carrier.store_fighter(fighter)
            
        # Mock game input handler
        self.game_input = GameInput()
        
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
        
    def test_launch_with_key_press(self):
        """Test that pressing the launch key (default 'L') launches a fighter from selected carrier."""
        # Select the carrier
        self.carrier.selected = True
        
        # Simulate L key press
        key_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_l})
        
        # Before key press, no fighter should be launched
        initial_fighter_count = len(self.carrier.stored_fighters)
        self.assertEqual(initial_fighter_count, 3, "Should have 3 fighters stored initially")
        
        # Process the key press
        launched_fighter = self.game_input.process_carrier_key_command(key_event, [self.carrier])
        
        # Verify a fighter was launched
        self.assertIsNotNone(launched_fighter, "A fighter should be launched")
        self.assertEqual(len(self.carrier.stored_fighters), initial_fighter_count - 1, 
                        "One fighter should be removed from storage")
        
    def test_no_launch_when_carrier_not_selected(self):
        """Test that pressing launch key doesn't launch a fighter if carrier is not selected."""
        # Ensure carrier is not selected
        self.carrier.selected = False
        
        # Simulate L key press
        key_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_l})
        
        # Before key press
        initial_fighter_count = len(self.carrier.stored_fighters)
        
        # Process the key press
        launched_fighter = self.game_input.process_carrier_key_command(key_event, [self.carrier])
        
        # Verify no fighter was launched
        self.assertIsNone(launched_fighter, "No fighter should be launched when carrier not selected")
        self.assertEqual(len(self.carrier.stored_fighters), initial_fighter_count, 
                        "Fighter count should remain unchanged")
        
    def test_no_launch_when_wrong_key_pressed(self):
        """Test that pressing a non-launch key doesn't launch a fighter."""
        # Select the carrier
        self.carrier.selected = True
        
        # Simulate a different key press (e.g. 'K')
        key_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_k})
        
        # Before key press
        initial_fighter_count = len(self.carrier.stored_fighters)
        
        # Process the key press
        launched_fighter = self.game_input.process_carrier_key_command(key_event, [self.carrier])
        
        # Verify no fighter was launched
        self.assertIsNone(launched_fighter, "No fighter should be launched when wrong key pressed")
        self.assertEqual(len(self.carrier.stored_fighters), initial_fighter_count, 
                        "Fighter count should remain unchanged")
        
    def test_no_launch_when_no_fighters_available(self):
        """Test that pressing launch key doesn't launch a fighter if no fighters are available."""
        # Select the carrier
        self.carrier.selected = True
        
        # Remove all fighters
        self.carrier.stored_fighters = []
        
        # Simulate L key press
        key_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_l})
        
        # Process the key press
        launched_fighter = self.game_input.process_carrier_key_command(key_event, [self.carrier])
        
        # Verify no fighter was launched
        self.assertIsNone(launched_fighter, "No fighter should be launched when no fighters available")
        self.assertEqual(len(self.carrier.stored_fighters), 0, 
                        "Fighter count should remain at zero")
        
    def test_no_launch_during_cooldown(self):
        """Test that pressing launch key doesn't launch a fighter during cooldown period."""
        # Select the carrier
        self.carrier.selected = True
        
        # Launch a fighter to trigger cooldown
        first_fighter = self.carrier.launch_fighter()
        self.assertIsNotNone(first_fighter, "First fighter should launch")
        
        # Verify cooldown is active
        self.assertGreater(self.carrier.current_launch_cooldown, 0, 
                          "Cooldown should be active after launch")
        
        # Simulate another L key press during cooldown
        key_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_l})
        
        # Process the key press
        launched_fighter = self.game_input.process_carrier_key_command(key_event, [self.carrier])
        
        # Verify no fighter was launched
        self.assertIsNone(launched_fighter, "No fighter should be launched during cooldown")
        
if __name__ == '__main__':
    unittest.main()
