# Attribute & Method Error Prevention Guide

This guide explains how to use type checking tools to catch attribute and method errors before they appear at runtime, following Google's Python Style Guide.

## Preventing Common Errors

### 1. Static Analysis with mypy

Static analysis helps catch errors during development:

```bash
# Run type checking on a specific file
.venv/bin/mypy units.py

# Run checks on the entire codebase
.venv/bin/mypy .
```

The `mypy.ini` configuration specifies type checking rules. We've set up a gradual approach that will catch major errors without being too restrictive.

### 2. Runtime Validation with Pydantic

The `pydantic_models.py` file contains schema definitions that ensure all required attributes exist with correct types.

```python
# To validate a Unit instance
from pydantic_models import validate_unit_attributes

# This will raise an error if any required attributes are missing
validate_unit_attributes(my_unit)
```

### 3. IDE Integration

Configure your IDE to show type errors in real time:

- **VS Code**: Install the Pylance extension and enable type checking
- **PyCharm**: Type checking is enabled by default

## Implementation Strategies

### Option 1: Type Hints + Dataclasses (Preferred)

Use Python's dataclasses with type hints to define clear attribute structures:

```python
from dataclasses import dataclass
from typing import Optional, List, Tuple

@dataclass
class Unit:
    world_x: float  # Required field
    world_y: float  # Required field
    hp: int = 100   # Field with default value
    
    # ... other attributes with type hints
```

Benefits:
- Clear structure
- IDE completion support
- Static analysis catches errors
- Follows Google style guide recommendations

### Option 2: Pydantic Models

For more complex validation needs, use Pydantic models:

```python
from pydantic import BaseModel

class Unit(BaseModel):
    world_x: float
    world_y: float
    hp: int = 100
    
    # ... other attributes with type hints
```

Benefits:
- Automatic validation
- Schema generation
- Serialization/deserialization

## Recommended Approach for This Project

1. **Use dataclasses with complete type annotations** for all new classes
2. **Run mypy before commits** to catch type errors early
3. **Add Pydantic validation** in critical paths or for complex data structures

## Common Error Patterns to Avoid

1. **Inconsistent attribute naming**
   - Bad: `max_hp` in one place, `hp_max` in another
   - Good: Use consistent naming everywhere

2. **Accessing attributes without checking existence**
   - Bad: `unit.target.hp` (crashes if target is None)
   - Good: `if unit.target: unit.target.hp`

3. **Missing initialization**
   - Bad: Using attributes that aren't initialized in `__init__`
   - Good: Initialize all attributes in `__init__` or use dataclass

## Example: Refactoring for Type Safety

Before (error-prone):
```python
class Unit:
    def __init__(self, x, y):
        self.world_x = x
        self.world_y = y
        # Oops, forgot to initialize hp!
        
    def take_damage(self, amount):
        self.hp -= amount  # Error: 'hp' doesn't exist!
```

After (type-safe):
```python
@dataclass
class Unit:
    world_x: float
    world_y: float
    hp: int = 100
    
    def take_damage(self, amount: int) -> None:
        self.hp -= amount  # Works correctly
```
