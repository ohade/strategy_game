# Product Context: Strategy Game

## Project Overview
This is a strategy game project inspired by real-time strategy (RTS) games with a focus on naval/space combat mechanics. The game features units that can move, attack, and interact with each other in a 2D environment. The project is currently undergoing refactoring and feature enhancement.

## Core Components
- **Main Game Loop**: Handles event processing, updates, and rendering
- **Units**: Base class with friendly and enemy subclasses, handles movement, attacks, and states
- **Effects**: Visual effects for attacks, movement destinations, etc.
- **Camera**: Manages view offset and world-to-screen coordinate conversion
- **Background**: Handles the tiled background with parallax scrolling
- **UI**: Interface elements including debug info and carrier controls
- **Input Handler**: Processes user input for unit selection and commands
- **Game Logic**: Handles unit movement, targeting, attacks, and effect updates
- **Renderer**: Manages drawing of all game elements

## Recent Additions
- **Carrier Implementation**: Large capital ships that can store, launch, and recover fighter units
- **Collision System**: Mass-based collision resolution with special handling for carriers
- **Fighter Management**: System for storing, launching, and recovering fighter units
- **Visual Improvements**: Sprite-based rendering, animations, and visual effects

## Project Organization
The codebase follows a modular structure with separate files for different components:
- `main.py`: Main game loop and initialization
- `units.py`: Unit class definitions and behavior
- `effects.py`: Visual effects
- `camera.py`: Camera management
- `background.py`: Background rendering
- `ui.py`: User interface elements
- `input_handler.py`: Input processing
- `game_logic.py`: Game mechanics
- `constants.py`: Game constants
- `carrier.py`: Carrier-specific functionality

## Technical Standards
- Test-Driven Development (TDD) approach
- Comprehensive test coverage
- Structured task tracking in track-work.md
- Modular code organization

[2025-05-07 16:30:30] - Initial creation of product context
