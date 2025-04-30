# MVP PRD: Core Strategy Game Mechanics

**Goal:** Create a minimal playable 2D simulation using Pygame where the player can command friendly units (green dots) to attack static enemy units (red dots) on a navigable map with a minimap, inspired by Homeworld's look and feel where applicable.

## Core Features:

1.  **Game Window:**
    *   A Pygame display window (e.g., 1280x720 resolution).

2.  **Map:**
    *   A 2D game world larger than the screen view.
    *   **Navigation:**
        *   Implement camera panning using keyboard keys (WASD or Arrows).
        *   Optional (Post-MVP): Mouse panning (e.g., middle-mouse drag or edge scrolling).
    *   **Background:** Simple static background (e.g., dark space texture or solid color).
    *   **Zoom:** Optional (Post-MVP): Mouse wheel zoom.

3.  **Units:**
    *   **Representation:**
        *   Friendly units: Solid green circles.
        *   Enemy units: Solid red circles.
    *   **Stats (Initial):**
        *   Health Points (HP): e.g., 100 HP.
        *   Movement Speed: Fixed pixels per frame/second.
        *   Attack Range: Fixed pixel radius.
        *   Attack Power: HP damage per second/attack cycle.
    *   **Placement:** Define starting positions for a few friendly and enemy units.

4.  **Minimap:**
    *   **Display:** A small, fixed rectangle overlay (e.g., bottom-right corner).
    *   **Content:** Shows a scaled-down representation of the entire map area.
    *   **Indicators:** Displays simplified dots (green/red) for all units' relative positions.
    *   Optional (Post-MVP): Show the current camera view rectangle on the minimap.

5.  **Player Control:**
    *   **Selection:**
        *   Left-click on a friendly unit (green dot) to select it.
        *   Only single-unit selection for MVP.
        *   Indicate selection visually (e.g., white outline/circle around the selected green dot).
    *   **Attack Command:**
        *   With a friendly unit selected, right-click on an enemy unit (red dot).
        *   This commands the selected unit to move towards and attack the target.

6.  **Unit Behavior:**
    *   **Movement:**
        *   Selected friendly units move in a straight line towards their targeted enemy unit at their defined speed.
        *   Movement stops when the unit enters attack range.
    *   **Combat (Simplified):**
        *   When a friendly unit is within its `Attack Range` of its target:
            *   It begins 'attacking'.
            *   The target enemy unit's `HP` decreases by the friendly unit's `Attack Power` per unit of time.
            *   No projectiles needed visually for MVP.
        *   **Destruction:** When a unit's HP reaches 0, it is removed from the game (disappears).
        *   **Enemy AI (MVP):** Static targets. They do not move or attack back initially.

7.  **Technology:**
    *   **Language:** Python
    *   **Library:** Pygame

## Look and Feel Notes (Homeworld Inspired):

*   Clean, minimalist UI elements.
*   Use of simple geometric shapes (dots) for units initially.
*   Focus on clear visual feedback for selection and commands.
*   Dark space background theme.

## MVP Milestones (Suggested Order):

1.  Setup Pygame project structure.
2.  Create the game window and basic game loop.
3.  Implement map rendering and camera panning (keyboard).
4.  Implement unit representation (drawing dots) at static positions.
5.  Implement minimap rendering (static dots).
6.  Implement unit selection (click, visual indicator).
7.  Implement movement logic (moving towards a point).
8.  Implement attack command (right-click targeting).
9.  Implement basic combat logic (range check, HP reduction, destruction).
10. Integrate minimap updates with unit movement.
