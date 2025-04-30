"""Tests for smart targeting logic with radius-based selection."""

import pytest
import math
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions we'll be implementing
from game_logic import find_enemies_in_radius, get_closest_enemy_to_point

class TestSmartTargeting:
    
    def test_find_enemies_in_radius_returns_empty_list_when_no_enemies(self):
        """Test that find_enemies_in_radius returns an empty list when there are no enemies."""
        click_pos = (100, 100)
        enemy_units = []
        radius = 50
        
        result = find_enemies_in_radius(click_pos, enemy_units, radius)
        
        assert result == []
    
    def test_find_enemies_in_radius_finds_enemies_within_radius(self):
        """Test that find_enemies_in_radius finds enemies within the specified radius."""
        click_pos = (100, 100)
        
        # Create mock enemy units
        enemy1 = MagicMock()
        enemy1.world_x = 120  # Within radius
        enemy1.world_y = 120
        enemy1.get_rect.return_value = MagicMock(centerx=enemy1.world_x, centery=enemy1.world_y)
        
        enemy2 = MagicMock()
        enemy2.world_x = 130  # Within radius
        enemy2.world_y = 110
        enemy2.get_rect.return_value = MagicMock(centerx=enemy2.world_x, centery=enemy2.world_y)
        
        enemy3 = MagicMock()
        enemy3.world_x = 200  # Outside radius
        enemy3.world_y = 200
        enemy3.get_rect.return_value = MagicMock(centerx=enemy3.world_x, centery=enemy3.world_y)
        
        enemy_units = [enemy1, enemy2, enemy3]
        radius = 50
        
        result = find_enemies_in_radius(click_pos, enemy_units, radius)
        
        # Should only find enemy1 and enemy2
        assert len(result) == 2
        assert enemy1 in result
        assert enemy2 in result
        assert enemy3 not in result
    
    def test_find_enemies_in_radius_handles_exact_distance(self):
        """Test that find_enemies_in_radius correctly handles enemies exactly at the radius distance."""
        click_pos = (100, 100)
        
        # Create a mock enemy unit exactly at the radius distance
        enemy = MagicMock()
        enemy.world_x = 150  # Exactly 50 units away in X direction
        enemy.world_y = 100
        enemy.get_rect.return_value = MagicMock(centerx=enemy.world_x, centery=enemy.world_y)
        
        enemy_units = [enemy]
        radius = 50
        
        result = find_enemies_in_radius(click_pos, enemy_units, radius)
        
        # Should find the enemy
        assert len(result) == 1
        assert enemy in result
    
    def test_get_closest_enemy_to_point_returns_none_when_no_enemies(self):
        """Test that get_closest_enemy_to_point returns None when there are no enemies."""
        click_pos = (100, 100)
        enemy_units = []
        
        result = get_closest_enemy_to_point(click_pos, enemy_units)
        
        assert result is None
    
    def test_get_closest_enemy_to_point_finds_closest_enemy(self):
        """Test that get_closest_enemy_to_point returns the enemy closest to the point."""
        click_pos = (100, 100)
        
        # Create mock enemy units at different distances
        enemy1 = MagicMock()
        enemy1.world_x = 120  # Distance: ~28.28
        enemy1.world_y = 120
        enemy1.get_rect.return_value = MagicMock(centerx=enemy1.world_x, centery=enemy1.world_y)
        
        enemy2 = MagicMock()
        enemy2.world_x = 110  # Distance: ~14.14 (closest)
        enemy2.world_y = 110
        enemy2.get_rect.return_value = MagicMock(centerx=enemy2.world_x, centery=enemy2.world_y)
        
        enemy3 = MagicMock()
        enemy3.world_x = 150  # Distance: 50
        enemy3.world_y = 100
        enemy3.get_rect.return_value = MagicMock(centerx=enemy3.world_x, centery=enemy3.world_y)
        
        enemy_units = [enemy1, enemy2, enemy3]
        
        result = get_closest_enemy_to_point(click_pos, enemy_units)
        
        # Should return enemy2 (closest)
        assert result == enemy2
