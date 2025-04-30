"""Tests for the effect update functionality in game_logic.py."""

import pytest
from unittest.mock import MagicMock
import sys
import os

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_logic import update_effects
from effects import AttackEffect, ExplosionEffect, DestinationIndicator

class TestEffectUpdates:
    def test_update_effects_removes_expired_effects(self):
        """Test that update_effects removes effects that have expired."""
        # Create mock effects
        effect1 = MagicMock(spec=AttackEffect)
        effect1.is_expired.return_value = True  # This effect is expired
        
        effect2 = MagicMock(spec=ExplosionEffect)
        effect2.is_finished.return_value = True  # This effect is finished
        
        effect3 = MagicMock(spec=AttackEffect)
        effect3.is_expired.return_value = False  # This effect is not expired
        
        # Create a list of effects
        effects = [effect1, effect2, effect3]
        
        # Call the update_effects function
        dt = 0.016  # Sample delta time
        updated_effects = update_effects(effects, dt)
        
        # Check that expired effects were removed
        assert len(updated_effects) == 1
        assert updated_effects[0] == effect3
        
        # Verify update was called on all effects
        effect1.update.assert_called_once_with(dt)
        effect2.update.assert_called_once_with(dt)
        effect3.update.assert_called_once_with(dt)
    
    def test_update_effects_handles_different_is_finished_methods(self):
        """Test that update_effects handles different 'is_finished' method names."""
        # Create effects with different method names for checking completion
        attack_effect = MagicMock(spec=AttackEffect)
        attack_effect.is_expired.return_value = False
        
        explosion_effect = MagicMock(spec=ExplosionEffect)
        explosion_effect.is_finished.return_value = False
        
        destination_indicator = MagicMock(spec=DestinationIndicator)
        destination_indicator.is_alive.return_value = True  # is_alive returns True if active
        
        # Create a list of effects
        effects = [attack_effect, explosion_effect, destination_indicator]
        
        # Call the update_effects function
        dt = 0.016
        updated_effects = update_effects(effects, dt)
        
        # All effects should remain
        assert len(updated_effects) == 3
        assert attack_effect in updated_effects
        assert explosion_effect in updated_effects
        assert destination_indicator in updated_effects
        
        # Verify update was called on all effects
        attack_effect.update.assert_called_once_with(dt)
        explosion_effect.update.assert_called_once_with(dt)
        destination_indicator.update.assert_called_once_with(dt)
    
    def test_update_effects_empty_list(self):
        """Test that update_effects handles an empty list properly."""
        effects = []
        dt = 0.016
        
        # Call update_effects with an empty list
        updated_effects = update_effects(effects, dt)
        
        # Should return an empty list
        assert updated_effects == []
