# Static Type Checking with mypy

This project now uses mypy for static type checking to catch attribute errors, method calls, and other type-related issues at "compile time" rather than runtime.

## Benefits of Static Type Checking

- **Catch Errors Early**: Find attribute/method errors before running the code
- **Better IDE Support**: Get better code completion and documentation
- **Self-Documenting Code**: Types serve as documentation
- **Safer Refactoring**: Catch issues when renaming or changing attributes

## How to Run Type Checking

```bash
# Run type checking on the entire project
.venv/bin/mypy .

# Run type checking on a specific file
.venv/bin/mypy units.py
```

## Pre-Commit Hook

A pre-commit hook has been set up to run mypy automatically before each commit. This helps catch type errors before they make it into the codebase.

## Type Checking Configuration

The `mypy.ini` file contains the configuration for type checking with the following settings:

- Strict optional checking
- Disallow untyped function definitions
- Warning about any return values
- Warning about redundant casts
- Warning about unreachable code

## Best Practices for Type Annotations

1. **Use Python's type hints for all function parameters and return values**:
   ```python
   def function_name(param1: str, param2: int) -> bool:
       # ...
   ```

2. **Use Optional for values that might be None**:
   ```python
   from typing import Optional
   
   def find_item(id: int) -> Optional[Item]:
       # ...
   ```

3. **Use Union for values that could be multiple types**:
   ```python
   from typing import Union
   
   def process_input(value: Union[str, int]) -> None:
       # ...
   ```

4. **Use ClassVar for class variables**:
   ```python
   from typing import ClassVar
   
   class MyClass:
       class_constant: ClassVar[int] = 42
   ```

5. **Use dataclasses for structured data with predefined attributes**:
   ```python
   from dataclasses import dataclass
   
   @dataclass
   class Point:
       x: float
       y: float
   ```

By following these practices, we can catch many common errors at "compile time" rather than runtime, making our codebase more robust and maintainable.
