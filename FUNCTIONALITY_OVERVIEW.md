# Strategy Game Functionality Overview

This document outlines the core components and functionality of the strategy game project as of YYYY-MM-DD.

## 1. Core Components

-   **`main.py`**: 
    -   Initializes Pygame and game window.
    -   Sets up core game objects (clock, screen, camera, background, units, UI elements).
    -   Contains the main game loop.
    -   Handles user input events (keyboard and mouse).
    -   Orchestrates updates for all game objects (camera, units, effects, UI).
    -   Manages the drawing order of all visual elements.
-   **`units.py`**: 
    -   Defines the base `Unit` class and subclasses (`FriendlyUnit`, `EnemyUnit`).
    -   Manages unit attributes (HP, speed, attack power, range, state, etc.).
    -   Implements unit state logic (`idle`, `moving`, `attacking`, `destroyed`).
    -   Handles movement logic (towards points or target units) using interpolation.
    -   Handles attack logic (cooldown, applying damage via `take_damage`).
    -   Manages visual aspects like drawing the unit and its health bar.
    -   Includes motion trail logic.
-   **`effects.py`**: 
    -   Defines visual effects classes.
    -   `AttackEffect`: Draws a fading line between attacker and target.
    -   `DestinationIndicator`: Draws a fading circle at a move command location.
    -   Manages the lifecycle (creation, update, drawing, removal) of effects.
-   **`camera.py`**: 
    -   Defines the `Camera` class.
    -   Manages the view offset based on keyboard input (WASD/Arrows).
    -   Provides methods (`apply`, `apply_coords`) to convert world coordinates to screen coordinates for drawing.
    -   Enforces map boundaries to prevent scrolling too far.
-   **`background.py`**: 
    -   Defines the `Background` class.
    -   Loads and manages the background tile image.
    -   Draws the tiled background adjusted for the camera offset.
-   **`ui.py`**: 
    -   Defines UI elements (currently includes a `DebugInfo` panel).
    -   Handles drawing UI components onto the screen (independent of camera). 

## 2. Game Loop (`main.py`)

The main loop performs the following sequence each frame:

1.  **Event Handling:** Processes Pygame events (quit, keyboard presses, mouse clicks).
2.  **Input Processing:** 
    -   Handles unit selection (left-click drag).
    -   Handles move/attack commands (right-click).
3.  **Updates:**
    -   Updates camera position based on keyboard input (`camera.update`).
    -   Updates all active units (`unit.update`), handling state changes, movement, attacks, and generating attack effects.
    -   Updates active visual effects (`effect.update`), managing their timers/lifecycles.
    -   Updates UI elements (`debug_info.update`).
    -   **Unit Removal:** Checks units for `hp <= 0` and schedules them for removal from relevant lists (`all_units`, `friendly_units`, `enemy_units`, `selected_units`). *(Currently suspected to be malfunctioning)*.
    -   Removes completed/expired visual effects.
4.  **Drawing:**
    -   Clears the screen.
    -   Draws the background (`background.draw`).
    -   Draws unit motion trails.
    -   Draws all units (`unit.draw`).
    -   Draws all active visual effects (`effect.draw`, `indicator.draw`).
    -   Draws selection rectangle if active.
    -   Draws UI elements (`debug_info.draw`).
5.  **Display Update:** Flips the Pygame display buffer to show the newly drawn frame.
6.  **Clock Tick:** Controls the frame rate (`clock.tick`).

## 3. Unit Logic (`units.py`)

-   **States:** `idle`, `moving`, `attacking`, `destroyed`.
-   **Movement:** 
    -   Units move towards a `move_target` (either a `(x, y)` tuple or another `Unit`).
    -   Uses linear interpolation (`lerp`) for smooth visual movement (`draw_x`, `draw_y` approach `world_x`, `world_y`).
-   **Targeting:**
    -   Friendly units can be commanded to attack enemy units.
    -   Enemy units (when AI enabled) find the closest friendly unit to attack.
-   **Attacking:**
    -   Transitions to `attacking` state when in range of a target `Unit`.
    -   Uses a cooldown (`current_attack_cooldown`) between attacks.
    -   Calls `target.take_damage()` when attacking.
    -   Generates an `AttackEffect`.
-   **Damage & Destruction:**
    -   `take_damage` method reduces HP.
    -   Sets state to `destroyed` when HP reaches <= 0.
-   **Drawing:** Includes drawing the unit sprite/shape and a health bar.

## 4. Input Handling

-   **Left Mouse Button:**
    -   Click: Selects a single unit.
    -   Drag: Creates a selection rectangle to select multiple units.
-   **Right Mouse Button:**
    -   Click on Ground: Issues a move command (`move_to_point`) to selected units; creates `DestinationIndicator`.
    -   Click on Enemy Unit: Issues an attack command (`set_target`) to selected friendly units.
-   **Keyboard (WASD / Arrow Keys):** Controls camera panning.

## 5. Rendering Order

1.  Background
2.  Unit Motion Trails
3.  Units
4.  Attack Effects / Destination Indicators
5.  Selection Rectangle
6.  UI Elements (Debug Info)

## 6. Visual Effects

-   **Attack Effect:** Fading line projectile.
-   **Destination Indicator:** Fading circle marker.
-   **Motion Trail:** Series of fading circles behind moving units.

---
*This overview should be updated as refactoring progresses.*
