# Future Enhancements & Tasks

List of desired features and improvements beyond the initial MVP:

- [x] **1. Implement Map Boundaries:**
    - [x] Modify `Camera.update` to clamp `camera_rect` within the `MAP_WIDTH` and `MAP_HEIGHT` defined in `main.py`.

- [x] **2. Implement Move-to-Point Command:**
    - [x] Modify right-click logic in `main.py`: If the click is not on an enemy unit, calculate the target world coordinates.
    - [x] Add a new state or modify `Unit.set_target` to handle moving to coordinates instead of a target unit.
    - [x] Update `Unit.update` to handle movement towards a point and transition to `idle` upon arrival.

- [x] **3. Implement Multi-Unit Selection (Box Select):**
    - [x] In `main.py`, detect mouse button down (left) to start drag.
    - [x] While dragging, draw a selection rectangle on screen.
    - [x] On mouse button up, determine the world coordinates spanned by the screen rectangle.
    - [x] Select all friendly units whose `get_rect()` intersects with the world coordinate rectangle.
    - [x] Manage the list of selected units (previously `selected_unit` needs to become `selected_units: list[Unit]`).

- [x] **4. Enhance Map Visuals:**
    - [x] **Background:** Created a starfield background with varied star sizes and brightness levels.
    - [x] **Grid:** Implemented a coordinate grid that adjusts based on camera position and shows only visible grid lines.

- [x] **5. Implement Unit Info Display (Homeworld Inspired):**
    - [x] Design a UI panel location (bottom of the screen).
    - [x] When one or more units are selected, draw this panel.
    - [x] Display relevant info: Unit type, count (if multiple), HP/health percentage, current state(s).
    - [x] Added visual elements with clean text display and panel styling.

- [x] **6. Refine Combat Mechanics:**
    - [x] Added `attack_power: int` attribute to `Unit` class `__init__`.
    - [x] Added `attack_cooldown: float` attribute (1.0 seconds default).
    - [x] Added `current_attack_cooldown: float` attribute, initialized to 0.
    - [x] In `Unit.update` (state `attacking`):
        - [x] Check if `target_unit` still exists and is in `attack_range`.
        - [x] If yes, decrement `current_attack_cooldown` by `dt`.
        - [x] If cooldown <= 0: 
            - [x] Call `take_damage(amount)` method on the `target_unit`.
            - [x] Reset `current_attack_cooldown` to `attack_cooldown`.
    - [x] Added `take_damage(self, amount: int)` method to `Unit` class:
        - [x] Subtract `amount` from `self.hp`.
        - [x] Check if `self.hp <= 0`. If so, handle unit removal.
    - [x] In `main.py`, implemented filtering to remove destroyed units from all relevant lists.
    - [x] **Visual HP:** Added health bar above units that shows current HP as a proportion of max HP.

- [x] **7. Enhance Minimap with Camera View Indicator:**
    - [x] Draw a rectangle on the minimap representing the current camera view boundaries.
    - [x] Update the rectangle position as the camera moves.
    - [x] Style the rectangle to be visible but not obtrusive (white outline).

- [x] **8. Improve Multi-unit Selection UI:**
    - [x] Reorganize the unit info panel to support showing detailed stats for multiple units.
    - [x] Implement a collapsible/expandable section for multi-unit details.
    - [x] Display a summary (e.g., average health, unit counts) when collapsed.
    - [x] Show a scrollable list or truncated list of individual units when expanded.

- [ ] **9. Add Movement Animations:**
    - [x] Create sprite sheets or individual frames for unit movement (different directions if needed). -> *Used interpolation instead of sprites.* 
    - [x] Implement smooth transitions for unit movement instead of direct position updates.
    - [x] Add a visual motion trail effect behind units.
    - [x] Add optional visual indicators showing movement path or destination.
    - [ ] Consider adding small rotation/orientation changes as units move in different directions.

- [ ] **10. Add Shooting Animations:**
    - [x] Add basic line effect for shooting (Done). 
    - [x] Implement fading effect for shooting line (Done).
    - [ ] Improve projectile visuals (e.g., thicker line, actual sprite, particle effect).
    - [ ] Add sound effects for shooting.

- [ ] **11. Improve Targeting for Moving Units:**
    - [ ] Research/Implement Predictive Aiming: Calculate target's future position based on its velocity and projectile speed to improve hit rate against moving targets (like Homeworld).
    - [ ] Adjust unit turning speed/behavior when acquiring/tracking moving targets.

- [ ] **12. Add Unit Destruction Animations:**
    - [ ] Implement a short explosion or disintegration effect when units are destroyed.
    - [ ] Add particle effects that dissipate after the destruction.
    - [ ] Consider adding small debris that remains briefly on the map.

## Gameplay Features & Enhancements

- [ ] **1. Basic Resource System:**
