import sys
import math
import pygame
from camera import Camera
from units import Unit
from background import Background
from ui import UnitInfoPanel
from effects import AttackEffect, DestinationIndicator, ExplosionEffect # Import the effect classes

# Constants
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
WINDOW_TITLE: str = "Strategy Game MVP"
BACKGROUND_COLOR: tuple[int, int, int] = (0, 0, 20) # Dark blue space-like
FPS: int = 60

# --- Map and Minimap Constants ---
MAP_WIDTH: int = 4000
MAP_HEIGHT: int = 3000
MINIMAP_WIDTH: int = 200
MINIMAP_HEIGHT: int = 150 # Maintain aspect ratio of map (4000/3000 = 4/3)
MINIMAP_X: int = SCREEN_WIDTH - MINIMAP_WIDTH - 10 # 10px padding from right edge
MINIMAP_Y: int = SCREEN_HEIGHT - MINIMAP_HEIGHT - 10 # 10px padding from bottom edge
MINIMAP_BG_COLOR: tuple[int, int, int, int] = (50, 50, 50, 150) # Semi-transparent dark grey
MINIMAP_BORDER_COLOR: tuple[int, int, int] = (100, 100, 100)
MINIMAP_UNIT_SIZE: int = 2 # Size of dots on minimap

# --- Scaling Factors ---
MINIMAP_SCALE_X: float = MINIMAP_WIDTH / MAP_WIDTH
MINIMAP_SCALE_Y: float = MINIMAP_HEIGHT / MAP_HEIGHT

def main() -> None:
    """Main game function."""
    pygame.init()

    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock: pygame.time.Clock = pygame.time.Clock()

    # Create camera instance
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
    
    # Create background
    background = Background(MAP_WIDTH, MAP_HEIGHT)
    
    # Create UI components
    unit_info_panel = UnitInfoPanel(SCREEN_WIDTH)
    effects: list = [] # List to hold all active effects (attack, explosion, etc.)

    # --- Create Units ---
    friendly_units: list[Unit] = [
        Unit(300, 300, 'friendly'),
        Unit(350, 350, 'friendly')
    ]
    enemy_units: list[Unit] = [
        Unit(800, 400, 'enemy'),
        Unit(900, 500, 'enemy'),
        Unit(850, 450, 'enemy')
    ]
    all_units: list[Unit] = friendly_units + enemy_units

    destination_indicators: list[DestinationIndicator] = [] # List for destination indicators

    running: bool = True
    selected_units: list[Unit] = [] # Track all currently selected units
    
    # Variables to track drag selection
    is_dragging: bool = False
    drag_start_pos: tuple[int, int] | None = None
    drag_current_pos: tuple[int, int] | None = None

    while running:
        # --- Delta Time Calculation ---
        # dt = time difference between frames in seconds. Crucial for frame-rate independent movement.
        dt: float = clock.tick(FPS) / 1000.0

        # --- Event Handling ---
        keys = pygame.key.get_pressed() # Get current key states
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # --- Mouse Wheel for Zoom ---    
            elif event.type == pygame.MOUSEWHEEL:
                # event.y gives scroll amount (+1 for up/zoom in, -1 for down/zoom out)
                camera.handle_zoom(event.y, pygame.mouse.get_pos()) 
            # --- Mouse Events for Selection --- 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    # Check if the click was on the info panel's toggle button first
                    if unit_info_panel.handle_click(event.pos):
                        continue # Click was handled by the panel, don't process further
                    
                    mouse_screen_pos = event.pos
                    # Convert screen coordinates to world coordinates using the camera
                    mouse_world_x, mouse_world_y = camera.screen_to_world_coords(*mouse_screen_pos)
                    
                    # Check if any keyboard modifiers are pressed (e.g., Shift for adding to selection)
                    mods = pygame.key.get_mods()
                    add_to_selection = mods & pygame.KMOD_SHIFT
                    
                    # Start potential drag operation
                    is_dragging = True
                    drag_start_pos = mouse_screen_pos
                    drag_current_pos = mouse_screen_pos
                    
                    # Check for direct unit click
                    clicked_on_unit = False
                    for unit in friendly_units:
                        if unit.get_rect().collidepoint(mouse_world_x, mouse_world_y):
                            clicked_on_unit = True
                            
                            # If Shift is held, toggle this unit's selection without affecting others
                            if add_to_selection:
                                if unit in selected_units:
                                    # Deselect the unit if already selected
                                    selected_units.remove(unit)
                                    unit.selected = False
                                else:
                                    # Add to selection
                                    selected_units.append(unit)
                                    unit.selected = True
                            else:
                                # Clear previous selection
                                for u in selected_units:
                                    u.selected = False
                                selected_units.clear()
                                
                                # Select just this unit
                                unit.selected = True
                                selected_units.append(unit)
                            break
                    
                    # If clicked on empty space and not adding to selection, deselect all
                    if not clicked_on_unit and not add_to_selection:
                        for unit in selected_units:
                            unit.selected = False
                        selected_units.clear()

            # --- Mouse Move for Drag Selection ---
            elif event.type == pygame.MOUSEMOTION:
                if is_dragging and drag_start_pos:
                    drag_current_pos = event.pos
                    
            # --- Mouse Release to Complete Selection ---
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and is_dragging and drag_start_pos and drag_current_pos:
                    # If the drag distance is significant (prevent accidental tiny drags)
                    drag_distance = math.hypot(
                        drag_start_pos[0] - drag_current_pos[0],
                        drag_start_pos[1] - drag_current_pos[1]
                    )
                    
                    if drag_distance > 5:  # Minimum drag distance threshold
                        # Convert screen coords to world coords
                        start_world_x, start_world_y = camera.screen_to_world_coords(*drag_start_pos)
                        end_world_x, end_world_y = camera.screen_to_world_coords(*drag_current_pos)
                        
                        # Define the selection rectangle in world coordinates
                        selection_world_rect = pygame.Rect(
                            min(start_world_x, end_world_x),
                            min(start_world_y, end_world_y),
                            abs(end_world_x - start_world_x),
                            abs(end_world_y - start_world_y)
                        )
                        
                        # Clear previous selection unless Shift is held
                        mods = pygame.key.get_mods()
                        add_to_selection = mods & pygame.KMOD_SHIFT
                        if not add_to_selection:
                            for unit in selected_units:
                                unit.selected = False
                            selected_units.clear()
                        
                        # Select all friendly units within the selection rectangle
                        for unit in friendly_units:
                            if unit.get_rect().colliderect(selection_world_rect):
                                unit.selected = True
                                if unit not in selected_units:
                                    selected_units.append(unit)
                    
                    # Reset drag state
                    is_dragging = False
                    drag_start_pos = None
                    drag_current_pos = None
                
                elif event.button == 3: # Right mouse button for commands
                    mouse_screen_pos = event.pos
                    # Convert screen coordinates to world coordinates
                    target_world_x, target_world_y = camera.screen_to_world_coords(*mouse_screen_pos)
                    
                    # Clear previous indicators for selected units
                    destination_indicators = [ind for ind in destination_indicators 
                                             if ind.unit not in selected_units]
                    
                    # Check if the right-click hit an enemy unit
                    clicked_enemy: Unit | None = None
                    for enemy in enemy_units:
                        if enemy.get_rect().collidepoint(target_world_x, target_world_y):
                            clicked_enemy = enemy
                            break

                    if clicked_enemy:
                        # Target enemy unit for attack
                        for unit in selected_units:
                            unit.set_target(clicked_enemy)
                    else:
                        # Move to the clicked point on the map
                        # Clamp to map boundaries for safety
                        target_x = min(max(0, target_world_x), MAP_WIDTH)
                        target_y = min(max(0, target_world_y), MAP_HEIGHT)
                        
                        # Issue move command to all selected units
                        for unit in selected_units:
                            unit.move_to_point(target_x, target_y)
                            # Create a destination indicator only if not targeting an enemy
                            if clicked_enemy is None:
                                indicator = DestinationIndicator(target_x, target_y)
                                destination_indicators.append(indicator)

        # --- Game Logic Update ---
        camera.update(dt, keys) # Update camera based on key presses and dt
        
        # --- Update Effects ---
        # Update and remove finished effects
        effects_to_remove = []
        for effect in effects:
            effect.update(dt)
            if hasattr(effect, 'is_finished') and effect.is_finished(): # Check if effect is done
                effects_to_remove.append(effect)
        for effect in effects_to_remove:
            effects.remove(effect)

        # --- Update Destination Indicators ---
        destination_indicators = [ind for ind in destination_indicators if ind.is_alive()]
        for indicator in destination_indicators:
            indicator.update(dt)
        
        # --- Update Units --- 
        units_to_remove = []
        for unit in all_units:
            effect = unit.update(dt)
            if effect: # If unit update returned an effect (e.g., attack)
                effects.append(effect)

            # Basic AI for Enemies (example: attack nearest friendly if idle)
            if isinstance(unit, Unit) and unit.state == "idle":
                closest_friendly = None
                closest_distance = float('inf')
                for friendly in friendly_units:
                    distance = math.hypot(friendly.world_x - unit.world_x, friendly.world_y - unit.world_y)
                    if distance < closest_distance:
                        closest_friendly = friendly
                        closest_distance = distance
                if closest_friendly:
                    unit.set_target(closest_friendly)

            for unit_other in all_units:
                # Check if unit's HP dropped to zero or below AFTER update
                if unit_other.hp <= 0:
                    print(f"DEBUG: Condition unit.hp <= 0 met for unit {id(unit_other)}. Adding to removal list.") # DEBUG
                    units_to_remove.append(unit_other)
                    # Trigger explosion effect
                    explosion = ExplosionEffect(unit_other.world_x, unit_other.world_y)
                    effects.append(explosion)
 
         # Remove destroyed units
        if units_to_remove:
            print(f"DEBUG Removing units: {[id(u) for u in units_to_remove]}") # DEBUG
        for unit in units_to_remove:
            print(f"DEBUG Attempting to remove unit {id(unit)}...") # DEBUG
            # Manually remove from all relevant lists
            if unit in all_units:
                print(f"DEBUG Removing unit {id(unit)} from all_units.") # DEBUG
                all_units.remove(unit)
            if isinstance(unit, Unit) and unit in friendly_units:
                print(f"DEBUG Removing unit {id(unit)} from friendly_units.") # DEBUG
                friendly_units.remove(unit)
            elif isinstance(unit, Unit) and unit in enemy_units:
                print(f"DEBUG Removing unit {id(unit)} from enemy_units.") # DEBUG
                enemy_units.remove(unit)
            # Make sure selected units list is also updated
            if unit in selected_units:
                print(f"DEBUG Removing unit {id(unit)} from selected_units.") # DEBUG
                selected_units.remove(unit)
 
        # --- Drawing ---
        screen.fill(BACKGROUND_COLOR)
        
        # Draw background elements (stars and grid)
        background.draw(screen, camera)

        # --- Draw Units ---
        for unit in all_units:
            unit.draw(screen, camera)
            
        # --- Draw Effects ---
        # Draw all active effects
        for effect in effects:
            effect.draw(screen, camera)

        # --- Draw Destination Indicators ---
        for indicator in destination_indicators:
            indicator.draw(screen, camera)
            
        # --- Draw Unit Info Panel (if units are selected) ---
        if selected_units:
            mouse_pos = pygame.mouse.get_pos()
            unit_info_panel.draw(screen, selected_units, mouse_pos)
            
        # --- Draw Selection Box (if currently dragging) ---
        if is_dragging and drag_start_pos and drag_current_pos:
            select_box_rect = pygame.Rect(
                min(drag_start_pos[0], drag_current_pos[0]),
                min(drag_start_pos[1], drag_current_pos[1]),
                abs(drag_current_pos[0] - drag_start_pos[0]),
                abs(drag_current_pos[1] - drag_start_pos[1])
            )
            
            # Draw selection box with dotted/dashed effect (alternating transparent and solid)
            # First, draw transparent white rectangle
            selection_surface = pygame.Surface((select_box_rect.width, select_box_rect.height), pygame.SRCALPHA)
            selection_surface.fill((255, 255, 255, 30))  # White with alpha (transparency)
            screen.blit(selection_surface, (select_box_rect.x, select_box_rect.y))
            
            # Then, draw the rectangle outline in solid white
            pygame.draw.rect(screen, (255, 255, 255), select_box_rect, 1)  # 1 pixel width border

        # --- Draw Minimap ---
        # Create a surface for the minimap with per-pixel alpha
        minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA)
        minimap_surface.fill(MINIMAP_BG_COLOR)

        # Draw units on minimap surface
        for unit in all_units:
            mini_x = int((unit.world_x / MAP_WIDTH) * MINIMAP_WIDTH)
            mini_y = int((unit.world_y / MAP_HEIGHT) * MINIMAP_HEIGHT)
            pygame.draw.circle(minimap_surface, unit.color, (mini_x, mini_y), 2)

        # Draw camera view rectangle on minimap
        cam_rect_world = camera.get_world_view() # Use the new method
        cam_rect_mini_x = int((cam_rect_world.left * MINIMAP_SCALE_X)) # Use world_view properties and scaling factors
        cam_rect_mini_y = int((cam_rect_world.top * MINIMAP_SCALE_Y))
        cam_rect_mini_width = int((cam_rect_world.width * MINIMAP_SCALE_X))
        cam_rect_mini_height = int((cam_rect_world.height * MINIMAP_SCALE_Y))
        
        camera_view_rect_mini = pygame.Rect(cam_rect_mini_x, cam_rect_mini_y, 
                                          max(1, cam_rect_mini_width), max(1, cam_rect_mini_height)) # Ensure minimum size of 1x1
        pygame.draw.rect(minimap_surface, (255, 255, 255), camera_view_rect_mini, 1) # White outline
            
        # Draw minimap outline
        pygame.draw.rect(minimap_surface, (200, 200, 200), minimap_surface.get_rect(), 1)
        
        # Blit the minimap surface onto the main screen
        screen.blit(minimap_surface, (MINIMAP_X, MINIMAP_Y))

        # --- Debug: Draw Camera Position ---
        font = pygame.font.Font(None, 30) # Default font, size 30
        # Update debug text to show world_x, world_y and zoom_level
        cam_text = font.render(f"World: ({int(camera.world_x)}, {int(camera.world_y)}) Zoom: {camera.zoom_level:.2f}", True, (255, 255, 255))
        screen.blit(cam_text, (10, 10))

        pygame.display.flip() # Update the full screen

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
