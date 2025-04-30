# Type Stubs for Strategy Game

This directory contains type stub files (`.pyi`) that define the expected interfaces for classes across the project. Type stubs help catch attribute and method errors at "compile time" through static analysis tools like mypy.

## How Type Stubs Help

Type stubs clearly define what attributes and methods a class should have, allowing static analysis tools to catch:

1. **Missing attributes**: Detect attempts to access class attributes that don't exist
2. **Missing methods**: Catch calls to methods that aren't implemented
3. **Type errors**: Identify incompatible types in assignments or function calls
4. **API consistency**: Ensure consistent interfaces across the codebase

## Creating Type Stubs

For critical classes, create a `.pyi` file with the same name as the module. For example:

```python
# units.pyi
from typing import Protocol, List, Tuple, Optional, Union

class Unit(Protocol):
    world_x: float
    world_y: float
    unit_type: str
    type: str
    hp: int
    hp_max: int
    
    def move_to_point(self, x: float, y: float) -> None: ...
    def attack(self, target: 'Unit') -> None: ...
    def take_damage(self, amount: int, attacker: Optional['Unit'] = None) -> None: ...
```

This defines what attributes and methods a Unit must have, allowing mypy to catch errors where these are missing.
