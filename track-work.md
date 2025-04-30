# Refactoring main.py

## Goal
Refactor `main.py` to improve modularity, readability, and maintainability by extracting constants, breaking down the main loop, and separating concerns into different modules. Follow Test-Driven Development (TDD).

## Tasks

### Phase 1: Setup & Constants
- [x] Create `track-work.md` (This file)
- [x] Create `tests/` directory and `__init__.py`.
- [x] Write test for constants (`tests/test_constants.py`).
- [x] Create `constants.py`.
- [x] Move constants from `main.py` to `constants.py`.
- [x] Update `main.py` to import constants from `constants.py`.
- [x] Run `test_constants.py` and ensure it passes.

### Phase 2: Input Handling
- [x] Write tests for input handling logic (e.g., unit selection, camera movement) (`tests/test_input_handler.py`).
- [x] Create `input_handler.py`.
- [x] Move event processing and input-related logic from `main.py` loop into `input_handler.py` (potentially as a class or functions).
- [x] Refactor `main.py` to use the `InputHandler`.
- [x] Run `test_input_handler.py` and ensure tests pass.

### Phase 3: Game Logic / State Update

- [x] **Unit Movement:**
    - [x] Write tests for unit movement towards a destination (`tests/test_game_logic.py`).
    - [x] Create `game_logic.py`.
    - [x] Extract unit movement logic from `main.py` into `game_logic.py`.
    - [x] Refactor `main.py` to call the new game logic functions for movement.
    - [x] Run movement tests and ensure they pass.
- [x] **Targeting/Attack Logic:**
    - [x] Define tests for targeting and attack logic in `tests/test_game_logic.py` and `tests/test_units.py`.
    - [x] Extract attack logic into `game_logic.py` (check_attack_range, perform_attack, update_unit_attack).
    - [x] Add missing Unit.set_target method for enemy AI targeting.
    - [x] Refactor `main.py` to use the new game logic functions for targeting and attacks.
    - [x] Run tests and ensure all pass.
- [x] **Effect Updates:**
    - [x] Define tests for effect updates in `tests/test_effect_updates.py`.
    - [x] Extract effect update logic into `game_logic.py` (update_effects function).
    - [x] Refactor `main.py` to use the new game logic function for effect updates.
    - [x] Run tests and ensure all pass.

### Phase 4: Rendering / Drawing
- [ ] Write tests for rendering logic (where feasible, e.g., minimap calculations) (`tests/test_renderer.py`).
- [ ] Create `renderer.py`.
- [ ] Move all drawing calls (background, units, effects, UI, minimap, selection box) from `main.py` loop into `renderer.py`.
- [ ] Refactor `main.py` to use the `Renderer`.
- [ ] Run `test_renderer.py` and ensure tests pass.

### Phase 5: Final Main Loop Refinement
- [ ] Review `main.py`'s main loop - it should now be significantly smaller, orchestrating calls to input handling, game logic updates, and rendering.
- [ ] Add any necessary tests for the main loop orchestration.
- [ ] Ensure all existing tests pass.
- [ ] Run linters/formatters (`black`, `pylint`, `mypy`) if configured.

## Bug Fixes

- [x] **Player Control:** Prevent player from selecting or commanding enemy units.
- [x] **Friendly Fire:** Prevent units from targeting or attacking units of the same type (friendly vs. friendly, enemy vs. enemy).
- [ ] **Background Rendering:** Background does not cover the entire map area, leaving empty spaces at the edges when zoomed out or panned.

## Feature Enhancements

### Phase 6: Unit Collision and Smart Targeting ✅
- [x] **Unit Collision:**
    - [x] Write tests for unit collision detection and handling.
    - [x] Implement collision detection system to prevent units from occupying the same space.
    - [x] Create unit separation behavior to realistically handle collisions.
    - [x] Run tests and ensure they pass.
    
- [x] **Smart Targeting:**
    - [x] Write tests for improved targeting logic with radius-based selection.
    - [x] Implement configurable radius targeting to detect enemy units near click location.
    - [x] Add "lock-on" functionality to prioritize enemy ships within targeting radius.
    - [x] Update input handler to properly interpret player intent when clicking near enemies.
    - [x] Run tests and ensure they pass.

### Phase 7: Realistic Movement and Visual Improvements
- [x] **Realistic Unit Movement:**
    - [x] Write tests for gradual rotation and movement physics.
    - [x] Implement rotation mechanics so units turn realistically when changing direction.
    - [x] Add momentum/inertia to unit movement for more natural motion.
    - [x] Create smooth transitions between movement states.
    - [x] Run tests and ensure they pass.
    
- [ ] **Visual Assets Integration:**
    - [ ] Create an assets module to handle loading and managing visual assets.
    - [ ] Design or source appropriate ship/unit graphics.
    - [ ] Implement sprite/image rendering to replace geometric shapes.
    - [ ] Add rotation and animation support for sprites.
    - [ ] Create visual feedback for different unit states (moving, attacking, damaged).
    - [ ] Update rendering to properly handle new visual assets.
    - [ ] Enhanced space background with images of planets, nebulae, and comets.
    - [ ] Implement parallax scrolling for multi-layered background effects.
    - [ ] Run tests and ensure the game looks and performs well with new assets.

### Phase 8: Code Quality and Safety Improvements
- [ ] **Static Type Checking with mypy:**
    - [ ] Add type annotations to all core modules (game_logic.py, camera.py, ui.py, etc.)
    - [ ] Fix existing type errors identified by mypy
    - [ ] Create comprehensive type stubs (.pyi files) for critical interfaces
    - [ ] Enable stricter mypy settings incrementally
    - [ ] Set up CI integration to run type checking on all pull requests

- [ ] **Code Refactoring and Optimization:**
    - [ ] Review and optimize critical game loops for performance
    - [ ] Implement consistent error handling throughout the codebase
    - [ ] Add comprehensive logging for debugging
    - [ ] Standardize code style with auto-formatting tools
    - [ ] Run profiling and address performance bottlenecks
