from __future__ import annotations

from typing import List, Tuple

import pygame

from units import Unit


class UnitInfoPanel:
    """Panel displaying information about currently selected units."""
    
    def __init__(self, screen_width: int, panel_height: int = 80, expanded_height: int = 200):
        """Initialize the unit info panel.
        
        Args:
            screen_width (int): Width of the game screen for positioning.
            panel_height (int): Height of the panel when collapsed.
            expanded_height (int): Height of the panel when expanded.
        """
        self.screen_width = screen_width
        self.panel_width = screen_width // 2 # Occupy half the screen width
        self.collapsed_height = panel_height
        self.expanded_height = expanded_height
        self.current_height = self.collapsed_height
        self.is_expanded = False
        
        self.panel_color = (20, 20, 35, 200)  # Dark blue with transparency
        self.border_color = (100, 100, 160)  # Light blue-gray
        self.text_color = (200, 200, 200)  # Light gray
        self.health_text_color = (0, 200, 0)  # Green for health
        self.title_color = (160, 160, 255)  # Light blue
        
        # Prepare panel surface with alpha for transparency
        self.panel_surface = pygame.Surface((self.panel_width, self.current_height), pygame.SRCALPHA)
        
        # Prepare fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 28)
        self.info_font = pygame.font.Font(None, 24)
        
        # Clickable area for expanding/collapsing
        self.toggle_button_rect: pygame.Rect | None = None
        
    def draw(self, surface: pygame.Surface, selected_units: List[Unit], mouse_pos: Tuple[int, int]) -> None:
        """Draw the unit info panel.
        
        Args:
            surface (pygame.Surface): The screen surface to draw on.
            selected_units (List[Unit]): Currently selected units.
            mouse_pos (Tuple[int, int]): Current mouse position for potential mouse-over effects.
        """
        if not selected_units:
            return  # Don't draw if no units selected
            
        # Calculate panel position at bottom center of screen
        panel_x = (self.screen_width - self.panel_width) // 2 # Center horizontally
        panel_rect = pygame.Rect(panel_x, surface.get_height() - self.current_height, 
                               self.panel_width, self.current_height)
        
        # Create panel surface with correct height
        self.panel_surface = pygame.Surface((self.panel_width, self.current_height), pygame.SRCALPHA)
        
        # Draw panel background
        self.panel_surface.fill(self.panel_color)
        
        # Draw top border line
        pygame.draw.line(self.panel_surface, self.border_color, 
                        (0, 0), (self.panel_width, 0), 2)
        
        # Panel content
        padding = 15
        y_offset = 10
        
        # Title - show count of selected units and types
        friendly_count = len(selected_units)
        title_text = f"Selected Units: {friendly_count}"
        title_surface = self.title_font.render(title_text, True, self.title_color)
        self.panel_surface.blit(title_surface, (padding, y_offset))
        y_offset += 30
        
        # Determine if we should show the expand/collapse button
        can_expand = len(selected_units) > 1
        toggle_symbol = "[+]" if not self.is_expanded else "[-]"
        
        if can_expand:
            toggle_text = f"Details {toggle_symbol}"
            toggle_surface = self.info_font.render(toggle_text, True, self.title_color)
            toggle_rect_local = toggle_surface.get_rect(topright=(self.panel_width - padding, 5)) # Relative to panel top-right
            self.panel_surface.blit(toggle_surface, toggle_rect_local)
            
            # Store the button rect in screen coordinates for click detection
            self.toggle_button_rect = pygame.Rect(toggle_rect_local.x + panel_rect.x, 
                                               toggle_rect_local.y + panel_rect.y,
                                               toggle_rect_local.width,
                                               toggle_rect_local.height)
        else:
            self.toggle_button_rect = None # No button if only one unit selected
        
        # Unit details
        if len(selected_units) == 1:
            # Single unit - show detailed info (always expanded implicitly)
            unit = selected_units[0]
            self.draw_single_unit_details(self.panel_surface, unit, padding, y_offset)
            
        elif self.is_expanded and can_expand:
            # Multiple units, expanded view - show list
            self.draw_multi_unit_details_expanded(self.panel_surface, selected_units, padding, y_offset)
        else:
            # Multiple units, collapsed view - show summary
            self.draw_multi_unit_summary(self.panel_surface, selected_units, padding, y_offset)
            
        # Blit the panel surface onto the main surface
        surface.blit(self.panel_surface, (panel_rect.x, panel_rect.y))

    def draw_single_unit_details(self, surface: pygame.Surface, unit: Unit, x_offset: int, y_offset: int) -> None:
        """Draw details for a single selected unit."""
        # Health
        health_text = f"HP: {unit.hp}/{unit.max_hp}"
        health_surface = self.info_font.render(health_text, True, self.health_text_color)
        surface.blit(health_surface, (x_offset, y_offset))
        
        # Status
        status_text = f"Status: {unit.state.capitalize()}"
        status_surface = self.info_font.render(status_text, True, self.text_color)
        surface.blit(status_surface, (x_offset + 140, y_offset))
        
        # Attack power
        atk_text = f"ATK: {unit.attack_power}"
        atk_surface = self.info_font.render(atk_text, True, self.text_color)
        surface.blit(atk_surface, (x_offset + 320, y_offset))
        
        # Position
        pos_text = f"POS: ({int(unit.world_x)}, {int(unit.world_y)})"
        pos_surface = self.info_font.render(pos_text, True, self.text_color)
        surface.blit(pos_surface, (x_offset + 450, y_offset))
        
    def draw_multi_unit_summary(self, surface: pygame.Surface, units: List[Unit], x_offset: int, y_offset: int) -> None:
        """Draw summary information for multiple selected units (collapsed view)."""
        # Calculate average HP
        total_hp = sum(unit.hp for unit in units)
        max_total_hp = sum(unit.max_hp for unit in units)
        avg_hp_percent = int((total_hp / max_total_hp) * 100) if max_total_hp > 0 else 0
        
        health_text = f"Avg Health: {avg_hp_percent}%"
        health_surface = self.info_font.render(health_text, True, self.health_text_color)
        surface.blit(health_surface, (x_offset, y_offset))
        
        # Count units by state
        states = {}
        for unit in units:
            state_key = unit.state.capitalize()
            states[state_key] = states.get(state_key, 0) + 1
                
        # Display state counts
        state_text_parts = [f"{state}: {count}" for state, count in states.items()]
        state_text = "States: " + ", ".join(state_text_parts)
        # TODO: Might need to wrap this text or reduce info if panel is too narrow
        state_surface = self.info_font.render(state_text, True, self.text_color)
        surface.blit(state_surface, (x_offset + 220, y_offset))
        
    def draw_multi_unit_details_expanded(self, surface: pygame.Surface, units: List[Unit], x_offset: int, y_offset: int) -> None:
        """Draw detailed list for multiple selected units (expanded view), mimicking single-unit style."""
        
        # Define column x-offsets relative to the main x_offset
        col_offsets = {
            'hp': 0,
            'status': 140,
            'atk': 320,
            'pos': 450
        }
        
        # Check if offsets exceed panel width and adjust if necessary (simple scaling example)
        max_required_width = x_offset + col_offsets['pos'] + 100 # Estimate width needed for POS text
        if max_required_width > self.panel_width:
            scale_factor = (self.panel_width - x_offset - 20) / (col_offsets['pos'] + 100) # Leave some padding
            col_offsets = {key: int(val * scale_factor) for key, val in col_offsets.items()}
        
        line_height = 25 # Vertical space per unit entry
        max_units_to_display = (self.expanded_height - y_offset - 10) // line_height
        
        for i, unit in enumerate(units[:max_units_to_display]):
            current_y = y_offset + i * line_height
            
            # Draw Unit Number
            # unit_num_text = f"Unit {i+1}:"
            # unit_num_surface = self.info_font.render(unit_num_text, True, self.title_color) # Use title color for emphasis
            # surface.blit(unit_num_surface, (x_offset, current_y))
            # current_y += 20 # Add space after unit number
            
            # Health (reuse single unit logic/colors)
            health_text = f"HP: {unit.hp}/{unit.max_hp}"
            health_surface = self.info_font.render(health_text, True, self.health_text_color)
            surface.blit(health_surface, (x_offset + col_offsets['hp'], current_y))
            
            # Status
            status_text = f"Status: {unit.state.capitalize()}"
            status_surface = self.info_font.render(status_text, True, self.text_color)
            surface.blit(status_surface, (x_offset + col_offsets['status'], current_y))
            
            # Attack power
            atk_text = f"ATK: {unit.attack_power}"
            atk_surface = self.info_font.render(atk_text, True, self.text_color)
            surface.blit(atk_surface, (x_offset + col_offsets['atk'], current_y))
            
            # Position
            pos_text = f"POS: ({int(unit.world_x)}, {int(unit.world_y)})"
            pos_surface = self.info_font.render(pos_text, True, self.text_color)
            surface.blit(pos_surface, (x_offset + col_offsets['pos'], current_y))
        
        if len(units) > max_units_to_display:
            more_y = y_offset + max_units_to_display * line_height
            more_text = f"... and {len(units) - max_units_to_display} more units."
            more_surface = self.info_font.render(more_text, True, self.text_color)
            surface.blit(more_surface, (x_offset, more_y))

    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if the click toggles the expand/collapse state.

        Args:
            mouse_pos (Tuple[int, int]): The screen coordinates of the mouse click.

        Returns:
            bool: True if the click was handled by the panel (consumed), False otherwise.
        """
        if self.toggle_button_rect and self.toggle_button_rect.collidepoint(mouse_pos):
            self.is_expanded = not self.is_expanded
            if self.is_expanded:
                self.current_height = self.expanded_height
            else:
                self.current_height = self.collapsed_height
            return True # Click consumed
            
        return False # Click not on button
