import pytest
from unittest.mock import MagicMock
import sys
import os

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from units import Unit, FriendlyUnit, EnemyUnit

class TestUnit:
    def test_set_target_calls_attack_with_valid_target(self):
        """Test that set_target calls attack method with valid target."""
        # Create a test unit and a mock target
        unit = Unit(x=100, y=100, unit_type='friendly')
        target = Unit(x=200, y=200, unit_type='enemy')
        target.hp = 100  # Ensure target has health
        
        # Mock the attack method
        unit.attack = MagicMock()
        
        # Call set_target
        unit.set_target(target)
        
        # Verify that attack was called with the target
        unit.attack.assert_called_once_with(target)
    
    def test_set_target_ignores_invalid_target(self):
        """Test that set_target doesn't call attack with invalid target."""
        # Create a test unit and a mock target
        unit = Unit(x=100, y=100, unit_type='friendly')
        
        # Case 1: None target
        unit.attack = MagicMock()
        unit.set_target(None)
        unit.attack.assert_not_called()
        
        # Case 2: Target with 0 HP
        dead_target = Unit(x=200, y=200, unit_type='enemy')
        dead_target.hp = 0
        
        unit.attack = MagicMock()
        unit.set_target(dead_target)
        unit.attack.assert_not_called()
