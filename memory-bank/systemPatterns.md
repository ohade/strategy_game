# System Patterns

## Code Architecture Patterns

### Component-Based Structure
- Each major game component is separated into its own module
- Components communicate through well-defined interfaces
- Main game loop orchestrates component interactions

### Inheritance Hierarchy
- Base `Unit` class with `FriendlyUnit` and `EnemyUnit` subclasses
- `Carrier` extends `FriendlyUnit` with additional functionality
- Common properties and methods defined in base classes

### State Machine Pattern
- Units use state machine pattern (`idle`, `moving`, `attacking`, `destroyed`)
- Landing sequence uses multi-stage state machine (approach, align, land, secure)
- State transitions trigger appropriate animations and behaviors

### Observer Pattern
- Game objects observe and react to state changes in other objects
- Effects are created in response to unit actions
- UI updates in response to game state changes

## Development Patterns

### Test-Driven Development
- Tests are written before implementation
- Each feature begins with test definition
- Implementation follows to satisfy tests
- Tests must pass before task is considered complete

### Task Tracking
- All tasks are documented in track-work.md
- Tasks include creation and completion dates
- Completed tasks are marked with checkmarks
- Work logs document accomplishments, challenges, and solutions

### Refactoring Approach
- Incremental refactoring of main game loop
- Extract functionality into specialized modules
- Maintain test coverage during refactoring
- Ensure backward compatibility

## Visual Design Patterns

### Visual Feedback
- Selection indicators (green outlines)
- Attack effects (fading lines)
- Movement indicators (fading circles)
- Motion trails for moving units

### UI Elements
- Debug information panel
- Carrier status display
- Fighter bay status
- Command feedback indicators

[2025-05-07 16:30:30] - Initial documentation of system patterns
