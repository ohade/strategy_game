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
- [ ] **Targeting/Attack Logic:** (Placeholder)
    - [ ] Define tests.
    - [ ] Extract logic.
    - [ ] Refactor `main.py`.
    - [ ] Run tests.
- [ ] **Effect Updates:** (Placeholder)
    - [ ] Define tests.
    - [ ] Extract logic.
    - [ ] Refactor `main.py`.
    - [ ] Run tests.

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
