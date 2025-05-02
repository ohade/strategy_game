"""
Game input handler for strategy game.
Handles player inputs including keyboard and mouse commands.
"""
import pygame
from typing import List, Optional
from carrier import Carrier
from units import FriendlyUnit

class GameInput:
    """
    Handles all player input for the game including keyboard and mouse actions.
    Provides methods to process input for specific game elements like carriers.
    """
    
    def __init__(self):
        """Initialize the input handler."""
        # Define key mappings
        self.carrier_launch_key = pygame.K_l  # 'L' key for launching fighters
        self.carrier_recall_key = pygame.K_r  # 'R' key for recalling fighters
    
    def process_carrier_key_command(self, event: pygame.event.Event, carriers: List[Carrier]) -> Optional[FriendlyUnit]:
        """
        Process keyboard commands for carrier operations.
        
        Args:
            event: The pygame event to process
            carriers: List of carrier objects in the game
            
        Returns:
            Optional[FriendlyUnit]: The launched fighter if a launch was triggered, None otherwise
        """
        # Only process KEYDOWN events
        if event.type != pygame.KEYDOWN:
            return None
        
        # Check for launch key
        if event.key == self.carrier_launch_key:
            # Find the first selected carrier
            for carrier in carriers:
                if carrier.selected:
                    # Attempt to launch a fighter
                    return carrier.launch_fighter()
        
        # No fighter was launched
        return None
    
    def process_return_to_carrier_command(self, selected_units: List[FriendlyUnit], carrier: Carrier, target_pos: tuple) -> bool:
        """
        Process command to return selected fighters to carrier when right-clicking on a carrier.
        
        Args:
            selected_units: List of currently selected units (fighters)
            carrier: The carrier that was clicked on
            target_pos: The world position that was clicked (carrier position)
            
        Returns:
            bool: True if the return command was successful for any unit, False otherwise
        """
        # Check if carrier has capacity for at least one fighter
        available_capacity = carrier.fighter_capacity - len(carrier.stored_fighters)
        if available_capacity <= 0:
            return False
            
        # Count how many fighters will be returning to this carrier
        returning_fighters = []
        
        # Mark each selected fighter to return to this carrier
        for unit in selected_units:
            # Only friendly units can be ordered to return to carrier
            if isinstance(unit, FriendlyUnit):
                # Add target_carrier attribute to the fighter
                unit.target_carrier = carrier
                unit.is_returning_to_carrier = True
                # Set the approach point (slightly in front of carrier based on its orientation)
                approach_distance = carrier.radius * 2
                approach_x = carrier.world_x + approach_distance * carrier.get_direction_x()
                approach_y = carrier.world_y + approach_distance * carrier.get_direction_y()
                unit.move_to_point(approach_x, approach_y)
                
                # Add to our tracking list
                returning_fighters.append(unit)
                
                # Stop targeting enemies when returning to carrier
                unit.target = None
        
        # Return True if any fighters were commanded to return
        return len(returning_fighters) > 0
    
    def process_input(self, event: pygame.event.Event, game_objects: dict) -> dict:
        """
        Process all game input events and update game state accordingly.
        
        Args:
            event: The pygame event to process
            game_objects: Dictionary containing all game objects by category
            
        Returns:
            dict: Actions resulting from input processing
        """
        results = {
            'launched_fighter': None,
            'command_processed': False,
            'returning_fighters': False
        }
        
        # Process carrier-specific commands if carriers exist
        if 'carriers' in game_objects and game_objects['carriers']:
            fighter = self.process_carrier_key_command(event, game_objects['carriers'])
            if fighter:
                results['launched_fighter'] = fighter
                results['command_processed'] = True
        
        return results
