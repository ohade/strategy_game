import sys
import math
import pygame
from camera import Camera
from units import Unit
from background import Background
from ui import UnitInfoPanel
from effects import AttackEffect, DestinationIndicator, ExplosionEffect # Import the effect classes
from constants import * # Import all constants
from input_handler import InputHandler # Import the new handler
from game_logic import update_unit_movement, update_targeting

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
    
    # --- Create Input Handler ---
    input_handler = InputHandler()

    # --- Create Units ---
    friendly_units: list[Unit] = [
        Unit(300, 300, 'friendly', attack_range=100),
        Unit(350, 350, 'friendly', attack_range=100),
        Unit(350, 350, 'friendly', attack_range=100),
        Unit(300, 300, 'friendly', attack_range=100),
        Unit(350, 350, 'friendly', attack_range=100),
        Unit(350, 350, 'friendly', attack_range=100),
        Unit(350, 350, 'friendly', attack_range=100)
    ]
    enemy_units: list[Unit] = [
        Unit(800, 400, 'enemy'),
        Unit(900, 500, 'enemy'),
        Unit(800, 400, 'enemy'),
        Unit(900, 500, 'enemy'),
        Unit(800, 400, 'enemy'),
        Unit(900, 500, 'enemy'),
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
    drag_current_pos: tuple[int, int] | None = None # Keep track for drawing

    while running:
        # --- Delta Time Calculation ---
        # dt = time difference between frames in seconds. Crucial for frame-rate independent movement.
        dt: float = clock.tick(FPS) / 1000.0

        # --- Event Handling (Moved to InputHandler) ---
        events = pygame.event.get()
        keys = pygame.key.get_pressed() # Get current key states
        mouse_pos = pygame.mouse.get_pos()
        
        # Call the input handler to process events and update state
        running, selected_units, destination_indicators, \
        is_dragging, drag_start_pos, drag_current_pos = \
            input_handler.process_input(
                events,
                keys,
                mouse_pos,
                dt,
                camera,
                all_units,
                selected_units,
                unit_info_panel,
                destination_indicators
            )
        
        # Exit loop if running is set to False
        if not running:
            break

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

            # Use game_logic module for unit targeting
            update_targeting(unit, friendly_units, enemy_units)

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
