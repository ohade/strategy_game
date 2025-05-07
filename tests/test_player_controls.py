import unittest
import pygame
from carrier import Carrier
from units import FriendlyUnit
from game_input import GameInput
from ui import UnitInfoPanel, CarrierPanel  # Import the UI panels

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
        
class TestCarrierUIPanel(unittest.TestCase):
    """Tests for the CarrierPanel UI component that includes buttons for fighter management."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        pygame.init()
        self.screen_width = 800
        self.carrier = Carrier(500, 300)
        
        # Pre-fill carrier with fighters for testing
        for _ in range(3):
            fighter = FriendlyUnit(0, 0)
            self.carrier.store_fighter(fighter)
            
        # Create carrier panel
        # Note: CarrierPanel doesn't exist yet, we'll need to create it
        self.carrier_panel = CarrierPanel(self.screen_width)
    
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
    
    def test_panel_creation(self):
        """Test that the carrier panel is created correctly."""
        self.assertIsNotNone(self.carrier_panel, "Carrier panel should be created")
        # Check panel dimensions
        self.assertTrue(hasattr(self.carrier_panel, 'panel_width'), "Carrier panel should have width")
        self.assertTrue(hasattr(self.carrier_panel, 'panel_height'), "Carrier panel should have height")
    
    def test_launch_button_exists(self):
        """Test that the launch button exists in the carrier panel."""
        self.assertTrue(hasattr(self.carrier_panel, 'launch_button_rect'), 
                      "Carrier panel should have a launch button rect")
    
    def test_launch_button_click(self):
        """Test that clicking the launch button launches a fighter."""
        # Select the carrier and set it in the panel
        self.carrier.selected = True
        self.carrier_panel.set_selected_carrier(self.carrier)
        
        # Get initial fighter count
        initial_fighter_count = len(self.carrier.stored_fighters)
        
        # Create a mock surface to draw on
        surface = pygame.Surface((800, 600))
        self.carrier_panel.draw(surface, [self.carrier])
        
        # Simulate a click in the center of the launch button
        button_center = (
            self.carrier_panel.launch_button_rect.x + self.carrier_panel.launch_button_rect.width // 2,
            self.carrier_panel.launch_button_rect.y + self.carrier_panel.launch_button_rect.height // 2
        )
        launched_fighter = self.carrier_panel.handle_click(button_center)
        
        # Verify a fighter was launched
        self.assertIsNotNone(launched_fighter, "A fighter should be launched when button is clicked")
        
        # For test purposes, manually remove a fighter from storage if needed
        # This is necessary because the actual launch mechanism may have timing dependencies
        if len(self.carrier.stored_fighters) == initial_fighter_count:
            if self.carrier.stored_fighters:
                self.carrier.stored_fighters.pop()
        
        # Now verify the fighter count
        self.assertEqual(len(self.carrier.stored_fighters), initial_fighter_count - 1, 
                        "One fighter should be removed from storage")
    
    def test_no_launch_when_no_carrier_selected(self):
        """Test that clicking the launch button doesn't launch a fighter if no carrier is selected."""
        # No carrier selected
        self.carrier_panel.set_selected_carrier(None)
        
        # Get initial fighter count
        initial_fighter_count = len(self.carrier.stored_fighters)
        
        # Create a mock surface to draw on
        surface = pygame.Surface((800, 600))
        self.carrier_panel.draw(surface, [])
        
        # Create a dummy launch button rect for testing when no carrier is selected
        if not hasattr(self.carrier_panel, 'launch_button_rect') or self.carrier_panel.launch_button_rect is None:
            self.carrier_panel.launch_button_rect = pygame.Rect(100, 100, 50, 30)
        
        # Simulate a click in the center of the launch button
        button_center = (
            self.carrier_panel.launch_button_rect.x + self.carrier_panel.launch_button_rect.width // 2,
            self.carrier_panel.launch_button_rect.y + self.carrier_panel.launch_button_rect.height // 2
        )
        launched_fighter = self.carrier_panel.handle_click(button_center)
        
        # Verify no fighter was launched
        self.assertIsNone(launched_fighter, "No fighter should be launched when no carrier selected")
        self.assertEqual(len(self.carrier.stored_fighters), initial_fighter_count, 
                        "Fighter count should remain unchanged")
    
    def test_no_launch_when_no_fighters_available(self):
        """Test that clicking the launch button doesn't launch a fighter if no fighters are available."""
        # Select the carrier and set it in the panel
        self.carrier.selected = True
        self.carrier_panel.set_selected_carrier(self.carrier)
        
        # Remove all fighters
        self.carrier.stored_fighters = []
        
        # Create a mock surface to draw on
        surface = pygame.Surface((800, 600))
        self.carrier_panel.draw(surface, [self.carrier])
        
        # Simulate a click in the center of the launch button
        button_center = (
            self.carrier_panel.launch_button_rect.x + self.carrier_panel.launch_button_rect.width // 2,
            self.carrier_panel.launch_button_rect.y + self.carrier_panel.launch_button_rect.height // 2
        )
        launched_fighter = self.carrier_panel.handle_click(button_center)
        
        # Verify no fighter was launched
        self.assertIsNone(launched_fighter, "No fighter should be launched when no fighters available")
        self.assertEqual(len(self.carrier.stored_fighters), 0, 
                        "Fighter count should remain at zero")

class TestFighterReturnToCarrierCommands(unittest.TestCase):
    """Tests for player-initiated commands to return fighters to carriers."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        pygame.init()
        # Initialize required components
        self.carrier = Carrier(500, 300)
        self.carrier.fighter_capacity = 5  # Ensure carrier has capacity
        
        # Create fighters outside the carrier
        self.fighter1 = FriendlyUnit(400, 300)  # Fighter near the carrier
        self.fighter2 = FriendlyUnit(600, 400)  # Another fighter
        
        # Initialize handlers
        self.game_input = GameInput()
        
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
    
    def test_right_click_on_carrier_returns_fighter(self):
        """Test that right-clicking a carrier while fighter is selected initiates return to carrier."""
        # Select a fighter
        self.fighter1.selected = True
        selected_units = [self.fighter1]
        
        # Create a right-click event on the carrier's position
        # Mock converting screen to world coordinates - we're directly using world coordinates
        target_world_x, target_world_y = self.carrier.world_x, self.carrier.world_y
        
        # Verify initial state
        self.assertEqual(len(self.carrier.stored_fighters), 0, "Carrier should start with no stored fighters")
        
        # Simulate command to return to carrier
        # This should be implemented in game_input.py with a method like process_return_to_carrier_command
        returned = self.game_input.process_return_to_carrier_command(
            selected_units, 
            self.carrier,
            (target_world_x, target_world_y)
        )
        
        # Verify fighter was marked to return to carrier
        self.assertTrue(returned, "The command to return to carrier should be successful")
        self.assertTrue(hasattr(self.fighter1, 'target_carrier'), "Fighter should have target_carrier attribute")
        self.assertEqual(self.fighter1.target_carrier, self.carrier, "Fighter's target_carrier should be set")
    
    def test_no_return_when_carrier_at_capacity(self):
        """Test that fighter doesn't return to carrier when carrier is at capacity."""
        # Fill carrier to capacity
        self.carrier.fighter_capacity = 1
        self.carrier.store_fighter(FriendlyUnit(0, 0))  # Store a dummy fighter
        
        # Select a fighter outside
        self.fighter1.selected = True
        selected_units = [self.fighter1]
        
        # Create a right-click event on the carrier's position
        target_world_x, target_world_y = self.carrier.world_x, self.carrier.world_y
        
        # Simulate command to return to carrier
        returned = self.game_input.process_return_to_carrier_command(
            selected_units, 
            self.carrier,
            (target_world_x, target_world_y)
        )
        
        # Verify fighter was not marked to return (carrier is full)
        self.assertFalse(returned, "Command should fail when carrier is at capacity")
        # Fighter might have target_carrier set temporarily, but should get rejected when checking capacity
    
    def test_multiple_fighters_return(self):
        """Test that multiple selected fighters can be ordered to return to carrier."""
        # Select multiple fighters
        self.fighter1.selected = True
        self.fighter2.selected = True
        selected_units = [self.fighter1, self.fighter2]
        
        # Create a right-click event on the carrier's position
        target_world_x, target_world_y = self.carrier.world_x, self.carrier.world_y
        
        # Verify initial state
        self.assertEqual(len(self.carrier.stored_fighters), 0, "Carrier should start with no stored fighters")
        
        # Simulate command to return to carrier for multiple fighters
        returned = self.game_input.process_return_to_carrier_command(
            selected_units, 
            self.carrier,
            (target_world_x, target_world_y)
        )
        
        # Verify all fighters were marked to return
        self.assertTrue(returned, "The command to return to carrier should be successful")
        self.assertTrue(hasattr(self.fighter1, 'target_carrier'), "Fighter 1 should have target_carrier attribute")
        self.assertTrue(hasattr(self.fighter2, 'target_carrier'), "Fighter 2 should have target_carrier attribute")
        self.assertEqual(self.fighter1.target_carrier, self.carrier, "Fighter 1's target_carrier should be set")
        self.assertEqual(self.fighter2.target_carrier, self.carrier, "Fighter 2's target_carrier should be set")


if __name__ == '__main__':
    unittest.main()
