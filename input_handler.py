"""Handles user input (mouse, keyboard) for the game."""

import pygame
from typing import Any, List, Tuple, Dict, Optional
from camera import Camera
from units import Unit
from ui import UnitInfoPanel
from effects import DestinationIndicator

class InputHandler:
    """Processes Pygame events and keyboard/mouse states."""

    def __init__(self):
        # Store persistent state related to input if needed, e.g., drag state
        self.is_dragging: bool = False
        self.drag_start_pos: Optional[Tuple[int, int]] = None
        self.drag_current_pos: Optional[Tuple[int, int]] = None

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
    ) -> Tuple[bool, List[Unit], List[DestinationIndicator], bool, Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
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
        """
        running = True
        
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

                    mods = pygame.key.get_mods()
                    add_to_selection = mods & pygame.KMOD_SHIFT
                    
                    clicked_on_unit = False
                    for unit in all_units:
                        # Get world rect, then convert to screen rect using camera
                        world_rect = unit.get_rect()
                        unit_screen_rect = camera.apply(world_rect)
                        if unit_screen_rect.collidepoint(click_screen_pos): # Use event pos for collision
                            clicked_on_unit = True
                            if add_to_selection:
                                if unit not in selected_units:
                                    selected_units.append(unit)
                                else:
                                    # Shift-clicking an already selected unit deselects it
                                    selected_units.remove(unit)
                            else:
                                # Regular click: select only this unit
                                selected_units.clear()
                                selected_units.append(unit)
                            break # Stop after finding the first unit under the click
                        else:
                            pass
                            
                    if not clicked_on_unit and not add_to_selection:
                        selected_units.clear()

                # --- Right Click ---    
                elif event.button == 3: 
                    if selected_units: # Only act if units are selected
                        target_world_x, target_world_y = camera.screen_to_world_coords(*click_screen_pos) # Use event pos
                        
                        # Clear previous indicators for these units
                        # More complex logic might be needed if multiple groups move
                        destination_indicators.clear() 
                        
                        for i, unit in enumerate(selected_units):
                            # Simple formation: Offset positions slightly for multiple units
                            # TODO: Implement better formation logic
                            offset_x = (i % 3 - 1) * 30 # Example offset
                            offset_y = (i // 3 - 1) * 30 # Example offset
                            unit.move_to_point(target_world_x + offset_x, target_world_y + offset_y)
                            
                            # Add a visual indicator
                            indicator = DestinationIndicator(target_world_x + offset_x, target_world_y + offset_y)
                            destination_indicators.append(indicator)
                            
            # --- Mouse Button Up Events ---            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # Left mouse button released
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
                            add_to_selection = mods & pygame.KMOD_SHIFT
                            
                            if not add_to_selection:
                                selected_units.clear()
                                
                            for unit in all_units:
                                # Get world rect, then convert to screen rect
                                world_rect = unit.get_rect()
                                unit_screen_rect = camera.apply(world_rect)
                                if drag_rect_screen.colliderect(unit_screen_rect):
                                    if unit not in selected_units:
                                        selected_units.append(unit)
                                        
                        # Reset drag state AFTER processing selection
                        self.is_dragging = False
                        self.drag_start_pos = None
                        self.drag_current_pos = None
                    else:
                        # If not dragging (simple click release), ensure drag state is reset
                        self.is_dragging = False
                        self.drag_start_pos = None
                        self.drag_current_pos = None

            # --- Mouse Motion Events --- 
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    self.drag_current_pos = event.pos
        
        # Return updated state
        return running, selected_units, destination_indicators, self.is_dragging, self.drag_start_pos, self.drag_current_pos
