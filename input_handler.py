"""Handles user input (mouse, keyboard) for the game."""

from typing import List, Tuple, Dict, Any, Optional
import pygame

from camera import Camera
from effects import DestinationIndicator
from game_logic import find_enemies_in_radius, get_closest_enemy_to_point
from game_input import GameInput  # Import the new GameInput class
from ui import UnitInfoPanel
from units import Unit, FriendlyUnit
from carrier import Carrier  # Explicitly import Carrier


class InputHandler:
    """Processes Pygame events and keyboard/mouse states."""

    def __init__(self):
        # Store persistent state related to input if needed, e.g., drag state
        self.is_dragging: bool = False
        self.drag_start_pos: Optional[Tuple[int, int]] = None
        self.drag_current_pos: Optional[Tuple[int, int]] = None
        
        # Initialize the game input handler for specialized operations
        self.game_input = GameInput()

    def process_input(
        self,
        events: List[pygame.event.Event],
        keys: Dict[int, bool], # Result of pygame.key.get_pressed()
        mouse_pos: Tuple[int, int],
        dt: float,
        camera: Camera,
        all_units: List[Unit],
        selected_units: List[Unit],
        unit_info_panel: UnitInfoPanel,
        destination_indicators: List[DestinationIndicator]
    ) -> Tuple[bool, List[Unit], List[DestinationIndicator], bool, Optional[Tuple[int, int]], Optional[Tuple[int, int]], Optional[Unit]]:
        """Processes all input events for a single frame.

        Args:
            events: List of pygame events from pygame.event.get().
            keys: Dictionary representing the state of all keyboard keys.
            mouse_pos: Current mouse position on the screen.
            dt: Delta time (time since last frame in seconds).
            camera: The game camera object.
            all_units: List of all Unit objects in the game.
            selected_units: List of currently selected Unit objects.
            unit_info_panel: The UI panel for unit info.
            destination_indicators: List of active destination indicators.

        Returns:
            A tuple containing:
            - running (bool): False if the game should quit.
            - selected_units (List[Unit]): Updated list of selected units.
            - destination_indicators (List[DestinationIndicator]): Updated list.
            - is_dragging (bool): Current drag state.
            - drag_start_pos (Optional[Tuple[int, int]]): Drag start position.
            - drag_current_pos (Optional[Tuple[int, int]]): Drag current position.
            - launched_fighter (Optional[Unit]): A fighter unit launched via keyboard shortcut, if any.
        """
        running = True
        launched_fighter = None  # Track if a fighter was launched this frame
        
        # --- Update Camera Panning (based on keys pressed this frame) --- #
        # This logic is now handled below within the continuous key check
        # camera.update_panning(keys, dt) # Incorrect call - remove

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # --- Mouse Wheel for Zoom ---    
            elif event.type == pygame.MOUSEWHEEL:
                camera.handle_zoom(event.y, mouse_pos)
                 
            # --- Mouse Button Down Events --- 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Use the position from the event for click detection
                click_screen_pos = event.pos
                
                # --- Left Click --- 
                if event.button == 1: 
                    # Check UI first
                    if unit_info_panel.handle_click(event.pos):
                        continue # Click handled by UI
                    
                    # Start potential drag
                    self.is_dragging = True
                    self.drag_start_pos = click_screen_pos # Use event pos for drag start
                    self.drag_current_pos = click_screen_pos # Initialize
                    
                    # Reset preview_selected flag for all units at the start of drag
                    for unit in all_units:
                        unit.preview_selected = False

                    mods = pygame.key.get_mods()
                    shift_pressed = mods & pygame.KMOD_SHIFT
                    
                    clicked_on_unit = False
                    newly_selected_units = []
                    for unit in all_units:
                        # Get world rect, then convert to screen rect using camera
                        world_rect = unit.get_rect()
                        unit_screen_rect = camera.apply(world_rect)
                        # Only consider friendly units for selection
                        if unit.type == 'friendly' and unit_screen_rect.collidepoint(click_screen_pos):
                            clicked_on_unit = True
                            # If shift is held, add to selection, otherwise select only this one
                            if shift_pressed:
                                if unit not in selected_units:
                                    newly_selected_units.append(unit)
                            else:
                                # Regular click: select only this unit
                                newly_selected_units = [unit]
                    if newly_selected_units:
                        # If not shift-selecting, first deselect all currently selected units
                        if not shift_pressed:
                            for unit in selected_units:
                                unit.selected = False
                            selected_units = newly_selected_units
                        else:
                            # For shift-select, simply extend the selection
                            selected_units.extend(newly_selected_units)
                            
                        # Set selected flag for all newly selected units
                        for unit in newly_selected_units:
                            unit.selected = True

                    if not clicked_on_unit and not shift_pressed:
                        # When clicking on empty space, deselect all units
                        for unit in selected_units:
                            unit.selected = False
                        selected_units.clear()

                # --- Right Click ---    
                elif event.button == 3 and selected_units:
                    print("OHAD!!! Right click")
                    target_world_x, target_world_y = camera.screen_to_world_coords(click_screen_pos[0], click_screen_pos[1])
                    destination_indicators.clear() # Clear previous indicators
                    
                    # Check if clicked on a carrier to return fighters
                    clicked_carrier = None
                    for unit in all_units:
                        if isinstance(unit, Carrier):
                            # Get world rect and check if clicked point is inside
                            world_rect = unit.get_rect()
                            if world_rect.collidepoint((target_world_x, target_world_y)):
                                clicked_carrier = unit
                                break
                    print(f"OHAD!!! Clicked carrier: {clicked_carrier}")
                    print(f"OHAD!!! Selected units: {selected_units}")
                    # If clicked on a carrier, check if selected units should return to it
                    if clicked_carrier and all(isinstance(unit, FriendlyUnit) for unit in selected_units):

                        # Process fighter return command using game_input
                        target_world_pos = (target_world_x, target_world_y)
                        return_successful = self.game_input.process_return_to_carrier_command(
                            selected_units, 
                            clicked_carrier,
                            target_world_pos
                        )
                        
                        if return_successful:
                            # Add a visual indicator on the carrier
                            indicator = DestinationIndicator(clicked_carrier.world_x, clicked_carrier.world_y, color=(0, 200, 200))  # Cyan indicator for return
                            destination_indicators.append(indicator)
                            continue  # Skip the regular command processing below
                    
                    # Check for enemies near the click point using smart targeting
                    # Define targeting radius
                    TARGETING_RADIUS = 50
                    
                    # Find enemies within the targeting radius
                    enemy_units = [unit for unit in all_units if unit.type == 'enemy']
                    target_world_pos = (target_world_x, target_world_y)
                    nearby_enemies = find_enemies_in_radius(target_world_pos, enemy_units, TARGETING_RADIUS)
                    
                    # Get the closest enemy if any were found
                    clicked_enemy = get_closest_enemy_to_point(target_world_pos, nearby_enemies) if nearby_enemies else None
                    
                    for i, unit in enumerate(selected_units):
                        # Ensure only friendly units receive commands
                        if unit.type == 'friendly':
                            # Reset carrier return flags when giving a new command
                            if hasattr(unit, 'is_returning_to_carrier') and unit.is_returning_to_carrier:
                                unit.is_returning_to_carrier = False
                                unit.target_carrier = None
                                
                            if clicked_enemy:  # If clicked on enemy, attack it
                                unit.attack(clicked_enemy)
                                # Add a visual indicator on the enemy
                                indicator = DestinationIndicator(clicked_enemy.world_x, clicked_enemy.world_y, color=(255, 0, 0))  # Red indicator for attack
                                destination_indicators.append(indicator)
                            else:  # Otherwise, move to the clicked location
                                # Simple formation: Offset positions slightly for multiple units
                                offset_x = (i % 3 - 1) * 30 # Example offset
                                offset_y = (i // 3 - 1) * 30 # Example offset
                                unit.move_to_point(target_world_x + offset_x, target_world_y + offset_y)
                                
                                # Add a visual indicator
                                indicator = DestinationIndicator(target_world_x + offset_x, target_world_y + offset_y)
                                destination_indicators.append(indicator)
                            
            # --- Mouse Button Up Events ---            
            elif event.type == pygame.MOUSEBUTTONUP and  event.button == 1: # Left mouse button released
                if self.is_dragging and self.drag_start_pos and self.drag_current_pos:
                    # Finalize drag selection
                    drag_rect_screen = pygame.Rect(
                        min(self.drag_start_pos[0], self.drag_current_pos[0]),
                        min(self.drag_start_pos[1], self.drag_current_pos[1]),
                        abs(self.drag_current_pos[0] - self.drag_start_pos[0]),
                        abs(self.drag_current_pos[1] - self.drag_start_pos[1])
                    )

                    # Only select if the box is larger than a small threshold (ignore clicks)
                    if drag_rect_screen.width > 5 or drag_rect_screen.height > 5:
                        mods = pygame.key.get_mods()
                        shift_pressed = mods & pygame.KMOD_SHIFT

                        if not shift_pressed:
                            # Clear previous selection if Shift is not held
                            for unit in all_units:
                                unit.selected = False
                            selected_units.clear() # Make sure to clear the list too

                        for unit in all_units:
                            # Get world rect, then convert to screen rect
                            world_rect = unit.get_rect()
                            unit_screen_rect = camera.apply(world_rect)
                            if drag_rect_screen.colliderect(unit_screen_rect) and unit.type == 'friendly':
                                if unit not in selected_units:
                                    selected_units.append(unit)
                                    unit.selected = True # Make sure to set the selected flag

                # Reset preview_selected for all units when drag selection ends
                for unit in all_units:
                    unit.preview_selected = False
                    
                # Reset drag state
                self.is_dragging = False
                self.drag_start_pos = None
                self.drag_current_pos = None

            # --- Keyboard Events for Carrier Operations ---
            elif event.type == pygame.KEYDOWN:
                # Filter the carrier units from all_units
                carriers = [unit for unit in all_units if isinstance(unit, Carrier)]
                
                # Process carrier keyboard commands
                fighter = self.game_input.process_carrier_key_command(event, carriers, all_units)
                if fighter:
                    launched_fighter = fighter
                    # Add the launched fighter to all_units list if not already added
                    # (launch_all_fighters already adds fighters to all_units)
                    if fighter not in all_units:
                        all_units.append(fighter)
            
            # --- Mouse Motion Events --- 
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    self.drag_current_pos = event.pos
                    
                    # Calculate current drag selection rectangle
                    drag_rect_screen = pygame.Rect(
                        min(self.drag_start_pos[0], self.drag_current_pos[0]),
                        min(self.drag_start_pos[1], self.drag_current_pos[1]),
                        abs(self.drag_current_pos[0] - self.drag_start_pos[0]),
                        abs(self.drag_current_pos[1] - self.drag_start_pos[1])
                    )
                    
                    # Update preview_selected state for all units
                    for unit in all_units:
                        # Only friendly units can be selected
                        if unit.type == 'friendly':
                            # Get world rect, then convert to screen rect
                            world_rect = unit.get_rect()
                            unit_screen_rect = camera.apply(world_rect)
                            
                            # Set preview_selected if unit intersects with the drag rectangle
                            unit.preview_selected = drag_rect_screen.colliderect(unit_screen_rect)
                        else:
                            # Enemy units shouldn't show preview selection
                            unit.preview_selected = False
        
        # Return updated state
        return running, selected_units, destination_indicators, self.is_dragging, self.drag_start_pos, self.drag_current_pos, launched_fighter
