"""Pydantic models for validating game entities.

This module provides Pydantic models that define expected attributes and types
for the game's core classes. These models serve both as documentation and as
runtime validation.
"""

from typing import List, Tuple, Optional, Union, Dict, Any, Literal, ClassVar
from pydantic import BaseModel, Field, validator


class UnitModel(BaseModel):
    """Pydantic model defining a Unit's expected attributes and types."""
    
    # Core properties
    world_x: float = Field(..., description="X position in world coordinates")
    world_y: float = Field(..., description="Y position in world coordinates")
    unit_type: Literal["friendly", "enemy"] = Field(..., description="Type of unit")
    hp: int = Field(default=100, description="Current health points")
    hp_max: int = Field(default=100, description="Maximum health points")
    radius: int = Field(default=15, description="Unit collision radius")
    
    # Combat attributes
    attack_range: int = Field(default=150, description="Range for attack in world units")
    attack_power: int = Field(default=20, description="Damage dealt per attack")
    attack_cooldown: float = Field(default=1.0, description="Time between attacks in seconds")
    current_attack_cooldown: float = Field(default=0.0, description="Current cooldown timer")
    
    # Movement attributes
    state: Literal["idle", "moving", "attacking", "destroyed"] = Field(
        default="idle", 
        description="Current unit state"
    )
    rotation: float = Field(default=0.0, description="Rotation in degrees (0-360)")
    velocity_x: float = Field(default=0.0, description="X velocity component")
    velocity_y: float = Field(default=0.0, description="Y velocity component")
    max_speed: float = Field(default=100.0, description="Maximum movement speed")
    acceleration: float = Field(default=200.0, description="Acceleration rate")
    max_rotation_speed: float = Field(default=180.0, description="Maximum rotation speed in degrees/second")
    
    # Visual attributes
    selected: bool = Field(default=False, description="Whether unit is currently selected")
    
    class Config:
        """Pydantic configuration for the UnitModel."""
        
        # Allow extra attributes for flexibility
        extra = "allow"
        
        # Example for documentation
        json_schema_extra = {
            "examples": [
                {
                    "world_x": 500.0,
                    "world_y": 300.0,
                    "unit_type": "friendly",
                    "hp": 100,
                    "attack_range": 150
                }
            ]
        }


def validate_unit_attributes(unit: Any) -> Dict[str, Any]:
    """Validate that a Unit instance has all required attributes with correct types.
    
    Args:
        unit: Any object that should conform to the UnitModel schema
        
    Returns:
        Dict of validated attributes
        
    Raises:
        ValidationError: If unit doesn't have required attributes or they have wrong types
    """
    # Extract all attributes from the unit object
    unit_dict = {
        attr: getattr(unit, attr) 
        for attr in dir(unit) 
        if not attr.startswith('_') and not callable(getattr(unit, attr))
    }
    
    # Validate against the model
    validated_data = UnitModel(**unit_dict).dict()
    return validated_data


# Example of how to use this for validation:
"""
# At the top of units.py:
from pydantic_models import validate_unit_attributes

# In Unit.__post_init__:
def __post_init__(self) -> None:
    # Basic initialization
    self.type = self.unit_type
    self.color = GREEN if self.unit_type == "friendly" else RED
    self.draw_x = self.world_x
    self.draw_y = self.world_y
    self.last_draw_x = self.world_x
    self.last_draw_y = self.world_y
    
    # Validate all attributes (only in debug mode)
    if DEBUG:
        try:
            validate_unit_attributes(self)
        except Exception as e:
            print(f"WARNING: Unit validation failed: {e}")
            # Could log this or raise in stricter environments
"""
