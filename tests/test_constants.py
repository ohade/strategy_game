"""Tests for constants defined in the game."""

import pytest
import constants # Import from the new constants module

def test_screen_constants_exist_and_type():
    """Test screen-related constants."""
    assert hasattr(constants, 'SCREEN_WIDTH')
    assert isinstance(constants.SCREEN_WIDTH, int)
    assert hasattr(constants, 'SCREEN_HEIGHT')
    assert isinstance(constants.SCREEN_HEIGHT, int)
    assert hasattr(constants, 'WINDOW_TITLE')
    assert isinstance(constants.WINDOW_TITLE, str)
    assert hasattr(constants, 'BACKGROUND_COLOR')
    assert isinstance(constants.BACKGROUND_COLOR, tuple)
    assert len(constants.BACKGROUND_COLOR) == 3
    assert all(isinstance(c, int) for c in constants.BACKGROUND_COLOR)
    assert hasattr(constants, 'FPS')
    assert isinstance(constants.FPS, int)

def test_map_constants_exist_and_type():
    """Test map-related constants."""
    assert hasattr(constants, 'MAP_WIDTH')
    assert isinstance(constants.MAP_WIDTH, int)
    assert hasattr(constants, 'MAP_HEIGHT')
    assert isinstance(constants.MAP_HEIGHT, int)

def test_minimap_constants_exist_and_type():
    """Test minimap-related constants."""
    assert hasattr(constants, 'MINIMAP_WIDTH')
    assert isinstance(constants.MINIMAP_WIDTH, int)
    assert hasattr(constants, 'MINIMAP_HEIGHT')
    assert isinstance(constants.MINIMAP_HEIGHT, int)
    assert hasattr(constants, 'MINIMAP_X')
    assert isinstance(constants.MINIMAP_X, int)
    assert hasattr(constants, 'MINIMAP_Y')
    assert isinstance(constants.MINIMAP_Y, int)
    assert hasattr(constants, 'MINIMAP_BG_COLOR')
    assert isinstance(constants.MINIMAP_BG_COLOR, tuple)
    assert len(constants.MINIMAP_BG_COLOR) == 4
    assert all(isinstance(c, int) for c in constants.MINIMAP_BG_COLOR)
    assert hasattr(constants, 'MINIMAP_BORDER_COLOR')
    assert isinstance(constants.MINIMAP_BORDER_COLOR, tuple)
    assert len(constants.MINIMAP_BORDER_COLOR) == 3
    assert all(isinstance(c, int) for c in constants.MINIMAP_BORDER_COLOR)
    assert hasattr(constants, 'MINIMAP_UNIT_SIZE')
    assert isinstance(constants.MINIMAP_UNIT_SIZE, int)

def test_scaling_constants_exist_and_type():
    """Test scaling factor constants."""
    assert hasattr(constants, 'MINIMAP_SCALE_X')
    assert isinstance(constants.MINIMAP_SCALE_X, float)
    assert hasattr(constants, 'MINIMAP_SCALE_Y')
    assert isinstance(constants.MINIMAP_SCALE_Y, float)

# It might be good to test the *values* if they are critical and unlikely to change
# For now, just testing existence and type is sufficient for refactoring.
