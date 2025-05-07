from __future__ import annotations

from typing import List, Tuple, Optional, Callable

import pygame

from units import Unit, FriendlyUnit
from carrier import Carrier


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
        health_text = f"HP: {unit.hp}/{unit.hp_max}"
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
        max_total_hp = sum(unit.hp_max for unit in units)
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
            health_text = f"HP: {unit.hp}/{unit.hp_max}"
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


class CarrierPanel:
    """Specialized panel for carrier units with fighter launch controls."""
    
    def __init__(self, screen_width: int, panel_height: int = 180):
        """Initialize the carrier control panel.
        
        Args:
            screen_width (int): Width of the game screen for positioning.
            panel_height (int): Height of the panel.
        """
        self.screen_width = screen_width
        self.panel_width = screen_width // 3  # Take up 1/3 of the screen width
        self.panel_height = panel_height  # Increased to 180 for more space
        
        # Panel appearance
        self.panel_color = (20, 35, 50, 200)  # Dark blue-gray with transparency
        self.border_color = (100, 150, 200)  # Light blue
        self.text_color = (200, 200, 220)  # Light blue-white
        self.title_color = (160, 200, 255)  # Light blue
        
        # Button appearance
        self.button_color = (50, 90, 150)  # Medium blue
        self.button_hover_color = (70, 120, 200)  # Brighter blue
        self.button_disabled_color = (50, 50, 80)  # Darker gray blue
        self.button_text_color = (240, 240, 240)  # White
        self.button_disabled_text_color = (150, 150, 150)  # Gray
        
        # Prepare surface
        self.panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        
        # Prepare fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 28)
        self.info_font = pygame.font.Font(None, 24)
        self.button_font = pygame.font.Font(None, 24)
        
        # Launch button properties
        self.launch_button_rect: Optional[pygame.Rect] = None
        self.button_width = 130  # Narrower for better fit
        self.button_height = 35  # Slightly smaller height
        
        # Panel position
        self.panel_rect: Optional[pygame.Rect] = None
        
        # Currently selected carrier
        self.selected_carrier: Optional[Carrier] = None
        
    def set_selected_carrier(self, carrier: Optional[Carrier]) -> None:
        """Set the carrier being displayed in the panel.
        
        Args:
            carrier: The carrier to display in the panel, or None if no carrier is selected.
        """
        self.selected_carrier = carrier
        
    def draw(self, surface: pygame.Surface, carriers: List[Carrier]) -> None:
        """Draw the carrier control panel with fighter launch button.
        
        Args:
            surface (pygame.Surface): The screen surface to draw on.
            carriers (List[Carrier]): List of carriers in the game (for reference).
        """
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if we have a selected carrier to display
        if not self.selected_carrier:
            return  # Don't draw if no carrier is selected
        
        # Calculate panel position at right center of screen
        panel_x = surface.get_width() - self.panel_width - 10  # Right aligned with padding
        panel_y = 10  # Top aligned with padding
        self.panel_rect = pygame.Rect(panel_x, panel_y, self.panel_width, self.panel_height)
        
        # Create panel surface
        self.panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        self.panel_surface.fill(self.panel_color)
        
        # Draw border
        pygame.draw.rect(self.panel_surface, self.border_color, 
                         pygame.Rect(0, 0, self.panel_width, self.panel_height), 2)
        
        # Panel content
        padding = 20
        y_offset = 20  # Start with more padding from the top
        
        # Title
        title_text = "Carrier Control"
        title_surface = self.title_font.render(title_text, True, self.title_color)
        self.panel_surface.blit(title_surface, (padding, y_offset))
        y_offset += 40  # More spacing after title
        
        # Fighter status
        fighters_text = f"Fighters: {len(self.selected_carrier.stored_fighters)}/{self.selected_carrier.fighter_capacity}"
        fighters_surface = self.info_font.render(fighters_text, True, self.text_color)
        self.panel_surface.blit(fighters_surface, (padding, y_offset))
        y_offset += 35  # More spacing between items
        
        # Cooldown status
        cooldown_text = "Launch Ready" if self.selected_carrier.current_launch_cooldown <= 0 else f"Cooldown: {self.selected_carrier.current_launch_cooldown:.1f}s"
        cooldown_color = (0, 200, 0) if self.selected_carrier.current_launch_cooldown <= 0 else (200, 200, 0)
        cooldown_surface = self.info_font.render(cooldown_text, True, cooldown_color)
        self.panel_surface.blit(cooldown_surface, (padding, y_offset))
        y_offset += 45  # Much more space before the button
        
        # Launch button
        button_x = (self.panel_width - self.button_width) // 2
        button_y = y_offset
        button_rect = pygame.Rect(button_x, button_y, self.button_width, self.button_height)
        
        # Determine button state (enabled/disabled)
        can_launch = self.selected_carrier.can_launch_fighter()
        button_hover = button_rect.collidepoint(mouse_pos[0] - panel_x, mouse_pos[1] - panel_y)
        
        # Draw button with appropriate state
        if not can_launch:
            button_color = self.button_disabled_color
            text_color = self.button_disabled_text_color
        elif button_hover:
            button_color = self.button_hover_color
            text_color = self.button_text_color
        else:
            button_color = self.button_color
            text_color = self.button_text_color
        
        pygame.draw.rect(self.panel_surface, button_color, button_rect, 0, border_radius=5)
        pygame.draw.rect(self.panel_surface, self.border_color, button_rect, 2, border_radius=5)
        
        # Button text
        button_text = "Launch Fighter"
        button_text_surface = self.button_font.render(button_text, True, text_color)
        text_rect = button_text_surface.get_rect(center=button_rect.center)
        self.panel_surface.blit(button_text_surface, text_rect)
        
        # Store the launch button rect in screen coordinates for click detection
        self.launch_button_rect = pygame.Rect(
            button_rect.x + panel_x, button_rect.y + panel_y,
            button_rect.width, button_rect.height
        )
        
        # Draw the panel to the screen
        surface.blit(self.panel_surface, self.panel_rect)
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[FriendlyUnit]:
        """Handle mouse clicks on the carrier panel and launch fighter if needed.
        
        Args:
            mouse_pos (Tuple[int, int]): The mouse position when clicked.
            
        Returns:
            Optional[FriendlyUnit]: The launched fighter if successful, None otherwise.
        """
        if not self.selected_carrier or not self.panel_rect or not self.panel_rect.collidepoint(mouse_pos):
            return None  # No carrier selected or click was outside the panel
        
        # Check if click was on launch button
        if (self.launch_button_rect and 
            self.launch_button_rect.collidepoint(mouse_pos) and 
            self.selected_carrier.can_launch_fighter()):
            
            # Queue a launch request instead of directly launching
            success = self.selected_carrier.queue_launch_request()
            if success:
                # Create a dummy fighter to return so the UI knows a launch was queued
                # This will be replaced by the actual launched fighter in the game loop
                dummy = FriendlyUnit(0, 0)  # Position doesn't matter, this is just a signal
                dummy.is_dummy = True  # Mark as dummy so we can identify it later
                return dummy
        
            return None  # No fighter launched
