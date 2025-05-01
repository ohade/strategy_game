"""Tests for the InputHandler module/class."""

from unittest.mock import MagicMock, patch

import pygame
import pytest

from camera import Camera
from input_handler import InputHandler
from units import Unit


class MockInfoPanel:
    """Minimal mock for UI panel."""
    def handle_click(self, pos): return False # Assume click miss
    def update(self, selected_units): pass

@pytest.fixture
def game_state():
    """Provides a common game state dictionary for tests, now using MagicMock for units."""
    mock_camera = MagicMock(spec=Camera)
    mock_camera.width = 1280
    mock_camera.height = 600
    mock_camera.zoom_level = 1.0
    mock_camera.screen_to_world_coords.side_effect = lambda sx, sy: (float(sx), float(sy))
    mock_camera.apply_coords.side_effect = lambda wx, wy: (int(wx), int(wy))
    mock_camera.apply.side_effect = lambda rect: rect # Pass-through for screen rect calculation

    # Create MagicMock units with spec=Unit
    mock_unit1 = MagicMock(spec=Unit)
    mock_unit1.id = 1
    mock_unit1.world_x = 100.0
    mock_unit1.world_y = 100.0
    mock_unit1.radius = 15
    # Mock the get_rect method based on the mock's attributes
    mock_unit1.get_rect.return_value = pygame.Rect(int(mock_unit1.world_x) - mock_unit1.radius,
                                                  int(mock_unit1.world_y) - mock_unit1.radius,
                                                  mock_unit1.radius * 2, mock_unit1.radius * 2)
    mock_unit1.unit_type = 'friendly' # Add unit_type
    mock_unit1.type = 'friendly' # Add type attribute to match Unit class

    mock_unit2 = MagicMock(spec=Unit)
    mock_unit2.id = 2
    mock_unit2.world_x = 150.0
    mock_unit2.world_y = 150.0
    mock_unit2.radius = 15
    mock_unit2.get_rect.return_value = pygame.Rect(int(mock_unit2.world_x) - mock_unit2.radius,
                                                  int(mock_unit2.world_y) - mock_unit2.radius,
                                                  mock_unit2.radius * 2, mock_unit2.radius * 2)
    mock_unit2.unit_type = 'friendly' # Add unit_type
    mock_unit2.type = 'friendly' # Add type attribute to match Unit class
    
    # Add a mock enemy unit
    mock_enemy_unit = MagicMock(spec=Unit)
    mock_enemy_unit.id = 3
    mock_enemy_unit.world_x = 800.0
    mock_enemy_unit.world_y = 400.0
    mock_enemy_unit.radius = 20
    mock_enemy_unit.get_rect.return_value = pygame.Rect(int(mock_enemy_unit.world_x) - mock_enemy_unit.radius,
                                                      int(mock_enemy_unit.world_y) - mock_enemy_unit.radius,
                                                      mock_enemy_unit.radius * 2, mock_enemy_unit.radius * 2)
    mock_enemy_unit.unit_type = 'enemy' # Set unit_type to enemy
    mock_enemy_unit.type = 'enemy' # Add type attribute to match Unit class
    mock_enemy_unit.move_to_point = MagicMock() # Ensure mock method exists for spec check

    state = {
        'camera': mock_camera,
        'all_units': [mock_unit1, mock_unit2, mock_enemy_unit], # Include enemy unit
        'selected_units': [],
        'unit_info_panel': MockInfoPanel(),
        'destination_indicators': [],
        'keys': {key: False for key in range(512)}, # Helper for static key state
        'dt': 0.016, # Example delta time
        'mouse_pos': (0, 0)
    }
    return state

def test_left_click_select_unit(game_state):
    """Test selecting a single friendly unit with a left click."""
    handler = InputHandler()
    
    # Target a friendly unit
    unit_to_select = next(u for u in game_state['all_units'] if u.unit_type == 'friendly')
    unit_world_rect = unit_to_select.get_rect()
    screen_click_pos = unit_world_rect.center

    # Mock Pygame event
    mock_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen_click_pos)
    mock_keys = {key: False for key in range(512)} # All keys up
    mock_mods = pygame.KMOD_NONE

    with patch('pygame.key.get_mods', return_value=mock_mods):
        running, game_state['selected_units'], game_state['destination_indicators'], \
        handler.is_dragging, handler.drag_start_pos, handler.drag_current_pos = \
            handler.process_input(
                [mock_event],
                mock_keys,
                screen_click_pos,
                game_state['dt'],
                game_state['camera'],
                game_state['all_units'],
                game_state['selected_units'], # Initially empty
                game_state['unit_info_panel'],
                game_state['destination_indicators']
            )

    assert len(game_state['selected_units']) == 1
    assert game_state['selected_units'][0] is unit_to_select # Check identity with mock object
    # Assert camera methods weren't called unexpectedly for panning
    game_state['camera'].handle_zoom.assert_not_called()

def test_left_click_select_enemy_unit(game_state):
    """Test left-clicking an enemy unit does not select it."""
    handler = InputHandler()
    
    # Target an enemy unit
    enemy_unit = next(u for u in game_state['all_units'] if u.unit_type == 'enemy')
    unit_world_rect = enemy_unit.get_rect()
    screen_click_pos = unit_world_rect.center

    # Mock Pygame event
    mock_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen_click_pos)
    mock_keys = {key: False for key in range(512)} # All keys up
    mock_mods = pygame.KMOD_NONE

    with patch('pygame.key.get_mods', return_value=mock_mods):
        running, game_state['selected_units'], game_state['destination_indicators'], \
        handler.is_dragging, handler.drag_start_pos, handler.drag_current_pos = \
            handler.process_input(
                [mock_event],
                mock_keys,
                screen_click_pos,
                game_state['dt'],
                game_state['camera'],
                game_state['all_units'],
                game_state['selected_units'], # Initially empty
                game_state['unit_info_panel'],
                game_state['destination_indicators']
            )

    assert len(game_state['selected_units']) == 0 # Enemy unit should not be selected
    # Assert camera methods weren't called unexpectedly for panning
    game_state['camera'].handle_zoom.assert_not_called()

def test_left_click_empty_deselects(game_state):
    """Test clicking empty space deselects units."""
    handler = InputHandler() 
    game_state['selected_units'] = [game_state['all_units'][0]] # Pre-select a unit

    # Simulate click position missing units
    screen_click_pos = (500, 500)
    mock_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen_click_pos)
    mock_keys = {key: False for key in range(512)} # All keys up
    mock_mods = pygame.KMOD_NONE

    with patch('pygame.key.get_mods', return_value=mock_mods):
         running, game_state['selected_units'], game_state['destination_indicators'], \
        handler.is_dragging, handler.drag_start_pos, handler.drag_current_pos = \
            handler.process_input(
                [mock_event], 
                mock_keys, 
                screen_click_pos, 
                game_state['dt'],
                game_state['camera'], 
                game_state['all_units'],
                game_state['selected_units'], 
                game_state['unit_info_panel'], 
                game_state['destination_indicators']
            )

    assert len(game_state['selected_units']) == 0
    # Assert camera methods weren't called unexpectedly for panning
    game_state['camera'].handle_zoom.assert_not_called()

def test_shift_left_click_adds_to_selection(game_state):
    """Test shift-clicking adds a unit to the current selection."""
    handler = InputHandler()
    unit1 = game_state['all_units'][0]
    unit2 = game_state['all_units'][1]
    game_state['selected_units'] = [unit1] # Pre-select unit 1

    # Simulate shift-click on unit 2
    unit2_world_rect = unit2.get_rect()
    screen_click_pos = unit2_world_rect.center
    mock_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen_click_pos)
    mock_keys = {key: False for key in range(512)} # All keys up
    mock_mods = pygame.KMOD_SHIFT # Shift key down

    with patch('pygame.key.get_mods', return_value=mock_mods):
        running, game_state['selected_units'], game_state['destination_indicators'], \
        handler.is_dragging, handler.drag_start_pos, handler.drag_current_pos = \
            handler.process_input(
                [mock_event],
                mock_keys,
                screen_click_pos,
                game_state['dt'],
                game_state['camera'],
                game_state['all_units'],
                game_state['selected_units'],
                game_state['unit_info_panel'],
                game_state['destination_indicators']
            )

    assert len(game_state['selected_units']) == 2
    assert unit1 in game_state['selected_units'] # Check membership
    assert unit2 in game_state['selected_units'] # Check membership
    # Assert camera methods weren't called unexpectedly for panning
    game_state['camera'].handle_zoom.assert_not_called()

def test_right_click_selected_creates_destination(game_state):
    """Test right-clicking with selected friendly units creates destination indicators and calls move_to_point."""
    handler = InputHandler()
    friendly_unit = next(u for u in game_state['all_units'] if u.unit_type == 'friendly')
    game_state['selected_units'] = [friendly_unit] # Pre-select friendly unit

    # Simulate right-click
    screen_click_pos = (600, 600)
    # Get corresponding world position using mocked camera
    target_world_x, target_world_y = game_state['camera'].screen_to_world_coords(*screen_click_pos)
    
    mock_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=screen_click_pos)
    mock_keys = {key: False for key in range(512)}
    mock_mods = pygame.KMOD_NONE
    
    with patch('pygame.key.get_mods', return_value=mock_mods):
        running, game_state['selected_units'], game_state['destination_indicators'], \
        handler.is_dragging, handler.drag_start_pos, handler.drag_current_pos = \
            handler.process_input(
                [mock_event],
                mock_keys,
                screen_click_pos,
                game_state['dt'],
                game_state['camera'],
                game_state['all_units'],
                game_state['selected_units'],
                game_state['unit_info_panel'],
                game_state['destination_indicators']
            )

    assert len(game_state['destination_indicators']) == 1 # One indicator for one unit
    # Assert camera methods weren't called unexpectedly for panning
    game_state['camera'].handle_zoom.assert_not_called()
    
    # Assert the correct method was called on the unit mock
    # Note: Offsets are hardcoded in input_handler, so we expect them here
    expected_dest_x = target_world_x + (0 % 3 - 1) * 30 # i=0 offset
    expected_dest_y = target_world_y + (0 // 3 - 1) * 30 # i=0 offset
    friendly_unit.move_to_point.assert_called_once_with(expected_dest_x, expected_dest_y)
    # TODO: Check indicator position matches click world coords more accurately

def test_right_click_does_not_command_enemy_units(game_state):
    """Test right-clicking does not command enemy units, even if selected (defensive test)."""
    handler = InputHandler()
    friendly_unit = next(u for u in game_state['all_units'] if u.unit_type == 'friendly')
    enemy_unit = next(u for u in game_state['all_units'] if u.unit_type == 'enemy')
    # Manually add both to selection for this specific test scenario
    game_state['selected_units'] = [friendly_unit, enemy_unit]

    # Simulate right-click
    screen_click_pos = (700, 700)
    target_world_x, target_world_y = game_state['camera'].screen_to_world_coords(*screen_click_pos)
    
    mock_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=screen_click_pos)
    mock_keys = {key: False for key in range(512)}
    mock_mods = pygame.KMOD_NONE
    
    with patch('pygame.key.get_mods', return_value=mock_mods):
        running, game_state['selected_units'], game_state['destination_indicators'], \
        handler.is_dragging, handler.drag_start_pos, handler.drag_current_pos = \
            handler.process_input(
                [mock_event],
                mock_keys,
                screen_click_pos,
                game_state['dt'],
                game_state['camera'],
                game_state['all_units'],
                game_state['selected_units'],
                game_state['unit_info_panel'],
                game_state['destination_indicators']
            )

    # Assert move_to_point was called on the friendly unit
    expected_dest_x_friendly = target_world_x + (0 % 3 - 1) * 30 # i=0 offset
    expected_dest_y_friendly = target_world_y + (0 // 3 - 1) * 30 # i=0 offset
    friendly_unit.move_to_point.assert_called_once_with(expected_dest_x_friendly, expected_dest_y_friendly)

    # Assert move_to_point was NOT called on the enemy unit
    enemy_unit.move_to_point.assert_not_called()
    
    assert len(game_state['destination_indicators']) == 1 # Only one indicator for the friendly unit

def test_camera_zoom_with_wheel(game_state):
    """Test camera zooms correctly with mouse wheel."""
    handler = InputHandler()
    mock_camera = game_state['camera']
    dt = 0.1
    mouse_pos = (mock_camera.width // 2, mock_camera.height // 2)
    mock_keys = {key: False for key in range(512)} # No keys pressed
    
    # Simulate Mouse Wheel Up event
    mock_event_up = pygame.event.Event(pygame.MOUSEWHEEL, y=1)
    
    handler.process_input([mock_event_up], mock_keys, mouse_pos, dt, mock_camera, 
                        game_state['all_units'], game_state['selected_units'], 
                        game_state['unit_info_panel'], game_state['destination_indicators'])

    # Expect camera.handle_zoom to be called for zooming IN
    mock_camera.handle_zoom.assert_called_once_with(1, mouse_pos)
    # mock_camera.move.assert_not_called() # InputHandler doesn't call move
    
    # Reset mock for next call check
    mock_camera.reset_mock()
    
    # Simulate Mouse Wheel Down event
    mock_event_down = pygame.event.Event(pygame.MOUSEWHEEL, y=-1)
    
    handler.process_input([mock_event_down], mock_keys, mouse_pos, dt, mock_camera, 
                        game_state['all_units'], game_state['selected_units'], 
                        game_state['unit_info_panel'], game_state['destination_indicators'])
                        
    # Expect camera.handle_zoom to be called for zooming OUT
    mock_camera.handle_zoom.assert_called_once_with(-1, mouse_pos)
    # mock_camera.move.assert_not_called() # InputHandler doesn't call move

def test_drag_selection_preview(game_state):
    """Test that units get preview_selected when mouse drags over them."""
    handler = InputHandler()
    
    # We'll simulate a drag that starts in empty space and covers unit1
    mock_unit1 = game_state['all_units'][0]
    
    # Start drag at empty space
    drag_start_pos = (50, 50)  # Some point away from all units
    mock_mousedown = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=drag_start_pos)
    mock_keys = {key: False for key in range(512)}  # No keys pressed
    
    # Process the MOUSEBUTTONDOWN event to start dragging
    with patch('pygame.key.get_mods', return_value=pygame.KMOD_NONE):
        running, game_state['selected_units'], game_state['destination_indicators'], \
        handler.is_dragging, handler.drag_start_pos, handler.drag_current_pos = \
            handler.process_input(
                [mock_mousedown],
                mock_keys,
                drag_start_pos,
                game_state['dt'],
                game_state['camera'],
                game_state['all_units'],
                game_state['selected_units'],
                game_state['unit_info_panel'],
                game_state['destination_indicators']
            )
    
    # Verify drag was initiated
    assert handler.is_dragging
    assert handler.drag_start_pos == drag_start_pos
    
    # Now simulate mouse motion that creates a selection rectangle covering unit1
    # Get unit1's center for this test - we'll drag to a point beyond it
    unit1_center = mock_unit1.get_rect().center
    drag_current_pos = (unit1_center[0] + 20, unit1_center[1] + 20)  # Point beyond unit1
    
    # Reset preview_selected for test clarity
    for unit in game_state['all_units']:
        unit.preview_selected = False
    
    # Process a MOUSEMOTION event
    mock_motion = pygame.event.Event(pygame.MOUSEMOTION, pos=drag_current_pos, rel=(0, 0), buttons=(1, 0, 0))
    
    handler.process_input(
        [mock_motion],
        mock_keys,
        drag_current_pos,
        game_state['dt'],
        game_state['camera'],
        game_state['all_units'],
        game_state['selected_units'],
        game_state['unit_info_panel'],
        game_state['destination_indicators']
    )
    
    # Check unit1 is preview_selected since it's in the drag area
    assert mock_unit1.preview_selected
    
    # Check units outside the selection area are not preview_selected
    assert not any(unit.preview_selected for unit in game_state['all_units'][1:])
    
    # Now simulate mouse up to finalize selection
    mock_mouseup = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=drag_current_pos)
    
    with patch('pygame.key.get_mods', return_value=pygame.KMOD_NONE):
        running, game_state['selected_units'], game_state['destination_indicators'], \
        handler.is_dragging, handler.drag_start_pos, handler.drag_current_pos = \
            handler.process_input(
                [mock_mouseup],
                mock_keys,
                drag_current_pos,
                game_state['dt'],
                game_state['camera'],
                game_state['all_units'],
                game_state['selected_units'],
                game_state['unit_info_panel'],
                game_state['destination_indicators']
            )
    
    # Verify drag ended
    assert not handler.is_dragging
    assert handler.drag_start_pos is None
    
    # Check unit1 is now selected (not just preview)
    assert mock_unit1 in game_state['selected_units']
    
    # Check all preview_selected flags are reset after drag is complete
    assert not any(unit.preview_selected for unit in game_state['all_units'])

# TODO:
# - Add tests for camera panning via mouse at screen edge (this IS handled by InputHandler).
# - Add tests for clicking UI panel toggle (requires MockInfoPanel update).
# - Add tests for Camera.update() method separately (in test_camera.py or similar).
