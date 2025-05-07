import sys

import pygame

from parallax_background import ParallaxBackground
from camera import Camera
from constants import *  # Import all constants
from effects import DestinationIndicator, ExplosionEffect  # Import the effect classes
from game_logic import update_targeting, update_effects, detect_unit_collision, resolve_collision_with_mass
from input_handler import InputHandler  # Import the new handler
from ui import UnitInfoPanel, CarrierPanel  # Import both UI panels
from units import Unit, FriendlyUnit, EnemyUnit  # Import all unit classes for type checking
from carrier import Carrier  # Import our new Carrier class
from visibility import VisibilityGrid, VisibilityState  # Import the fog of war system and states


def main() -> None:
    """Main game function."""
    pygame.init()

    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock: pygame.time.Clock = pygame.time.Clock()

    # Create camera instance
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
    
    # Create parallax background with 3 layers
    background = ParallaxBackground(MAP_WIDTH, MAP_HEIGHT, num_layers=3)
    
    # Initialize fog of war visibility system
    visibility_grid = VisibilityGrid(MAP_WIDTH, MAP_HEIGHT, cell_size=20)  # 20px cell size for performance
    
    # Create UI components
    unit_info_panel = UnitInfoPanel(SCREEN_WIDTH)
    carrier_panel = CarrierPanel(SCREEN_WIDTH)
    effects: list = [] # List to hold all active effects (attack, explosion, etc.)
    
    # --- Create Input Handler ---
    input_handler = InputHandler()

    # --- Create Units ---
    
    # Create a carrier with one fighter inside it
    carrier = Carrier(500, 300)  # Create carrier at position 500, 300

    for i in range(10):
        fighter_for_carrier = Unit(0, 0, 'friendly', attack_range=100)
        carrier.store_fighter(fighter_for_carrier)

    # Store the fighter in the carrier
    
    friendly_units: list[Unit] = [
        # Add the carrier
        carrier,
        # Regular friendly units
        # Unit(300, 300, 'friendly', attack_range=100),
        # Unit(350, 350, 'friendly', attack_range=100),
        # Unit(400, 350, 'friendly', attack_range=100),
        # Unit(300, 400, 'friendly', attack_range=100),
        # Unit(400, 300, 'friendly', attack_range=100),
        Unit(450, 350, 'friendly', attack_range=100)
    ]
    enemy_units: list[Unit] = [
        # Unit(1800, 1400, 'enemy'),
        # Unit(900, 500, 'enemy'),
        # Unit(850, 450, 'enemy'),
        # Unit(950, 550, 'enemy'),
        Unit(750, 350, 'enemy'),
        Unit(870, 470, 'enemy'),
        Unit(930, 430, 'enemy')
    ]
    all_units: list[Unit] = friendly_units + enemy_units

    destination_indicators: list[DestinationIndicator] = [] # List for destination indicators

    running: bool = True
    selected_units: list[Unit] = [] # Track all currently selected units
    control_groups: dict[int, list[Unit]] = {} # Map number keys (1-9) to groups of units
    
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
        
        # Update fog of war visibility based on friendly unit positions
        # Get list of visible enemy units
        visible_enemies = visibility_grid.update_visibility(friendly_units, enemy_units)
        
        # Update carrier panel's selected carrier if carrier is in selected units
        selected_carrier = None
        for unit in selected_units:
            if isinstance(unit, Carrier):
                selected_carrier = unit
                carrier_panel.set_selected_carrier(unit)
                break
                
        # Process UI panel clicks without consuming keyboard events
        ui_consumed_click = False
        for event in events:
            # Only process mouse clicks here, leave keyboard events for input handler
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                # Check if we have a selected carrier and the click is on the panel
                if selected_carrier:
                    # Check if carrier panel was clicked
                    launched_fighter = carrier_panel.handle_click(event.pos)
                    if launched_fighter:
                        # If it's a dummy fighter, it means a launch was queued
                        if hasattr(launched_fighter, 'is_dummy') and launched_fighter.is_dummy:
                            # Check if this is a launch_all request
                            if hasattr(launched_fighter, 'is_launch_all') and launched_fighter.is_launch_all:
                                # Queue all fighters for sequential launch
                                success = selected_carrier.launch_all_fighters()
                                if success:
                                    print(f"DEBUG: Queued all fighters for sequential launch with UI button")
                            # Don't add the dummy to the game units
                            ui_consumed_click = True
                            print("DEBUG: Launch request queued from UI")
                        else:
                            # This is a real fighter (direct launch), add it to the game units
                            friendly_units.append(launched_fighter)
                            all_units.append(launched_fighter)
                            ui_consumed_click = True
        
        # Call the input handler to process events and update state if UI didn't consume the click
        running, selected_units, destination_indicators, \
        is_dragging, drag_start_pos, drag_current_pos, launched_fighter = \
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
            
        # Handle newly launched fighter (from direct keyboard launch)
        if launched_fighter and launched_fighter not in friendly_units:
            friendly_units.append(launched_fighter)
            print(f"DEBUG: Added directly launched fighter to friendly_units")
        
        # Exit loop if running is set to False
        if not running:
            break

        # --- Game Logic Update ---
        camera.update(dt, keys) # Update camera based on key presses and dt
        
        # --- Process Carrier Launch Queues ---
        # Find all carriers and process their launch queues
        for unit in all_units:
            if isinstance(unit, Carrier) and unit.launch_queue:
                # Process the launch queue
                launched_fighter = unit.process_launch_queue(all_units)
                
                # If a fighter was launched, add it to friendly_units and create launch effect
                if launched_fighter:
                    # Add to friendly units if not already there
                    if launched_fighter not in friendly_units:
                        friendly_units.append(launched_fighter)
                        print(f"DEBUG: Added newly launched fighter to friendly_units")
                    
                    # Create an explosion effect at the fighter's position
                    launch_explosion = ExplosionEffect(
                        world_x=launched_fighter.world_x,
                        world_y=launched_fighter.world_y,
                        max_radius=launched_fighter.radius * 2,
                        duration=0.4,
                        start_color=(100, 200, 255),  # Blue-ish
                        end_color=(200, 230, 255)     # Light blue
                    )
                    effects.append(launch_explosion)
                    print(f"DEBUG: Created launch explosion at ({launched_fighter.world_x}, {launched_fighter.world_y})")
                
                # Check for any other newly added fighters
                for game_unit in all_units:
                    if isinstance(game_unit, FriendlyUnit) and game_unit not in friendly_units:
                        friendly_units.append(game_unit)
                        print(f"DEBUG: Added newly launched fighter to friendly_units")
        
        # --- Process Carrier Landing Queues ---
        # Find all carriers and process their landing queues
        for unit in all_units:
            if isinstance(unit, Carrier) and hasattr(unit, 'landing_queue') and unit.landing_queue:
                # Process the landing queue
                unit.process_landing_queue(all_units)
        
        # --- Update Effects ---
        # Use game_logic.update_effects to update and clean up expired effects
        effects = update_effects(effects, dt)

        # --- Update Destination Indicators ---
        destination_indicators = update_effects(destination_indicators, dt)
        
        # --- Update Units --- 
        units_to_remove = []
        for unit in all_units:
            effect = unit.update(dt)
            if effect: # If unit update returned an effect (e.g., attack)
                effects.append(effect)
                
            # Check if fighter has completed landing and been stored in a carrier
            if isinstance(unit, FriendlyUnit) and hasattr(unit, 'landing_complete'):
                # If the fighter has completed landing and marked for removal
                if unit.landing_complete:
                    # Mark the fighter for removal from the active units list
                    if unit not in units_to_remove:
                        print(f"DEBUG: Fighter {id(unit)} has landed on carrier and will be removed")
                        units_to_remove.append(unit)
                        
                        # Also remove from friendly_units list to ensure proper cleanup
                        if unit in friendly_units:
                            friendly_units.remove(unit)

            # Use game_logic module for unit targeting
            update_targeting(unit, friendly_units, enemy_units)

            for unit_other in all_units:
                # Check if unit's HP dropped to zero or below AFTER update
                if unit_other.hp <= 0:
                    print(f"DEBUG: Condition unit.hp <= 0 met for unit {id(unit_other)}. Adding to removal list.") # DEBUG
                    if unit_other not in units_to_remove:
                        units_to_remove.append(unit_other)
        
        # --- Handle Unit Collisions ---
        # Detect and resolve collisions between all units to prevent overlap
        for i, unit1 in enumerate(all_units):
            for unit2 in all_units[i+1:]:  # Only check each pair once
                if detect_unit_collision(unit1, unit2):
                    resolve_collision_with_mass(unit1, unit2)
 
         # Handle destroyed units
        if units_to_remove:
            print(f"DEBUG Removing units: {[id(u) for u in units_to_remove]}") # DEBUG
        for unit in units_to_remove:
            print(f"DEBUG Attempting to remove unit {id(unit)}...") # DEBUG
            
            # Create an explosion effect at the unit's position
            explosion = ExplosionEffect(
                world_x=unit.world_x,
                world_y=unit.world_y,
                max_radius=unit.radius * 3,  # Make explosion larger than the unit
                duration=0.8,  # Longer duration for better visibility
                start_color=(255, 165, 0),  # Orange
                end_color=(100, 20, 20)  # Dark red
            )
            effects.append(explosion)
            
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
        
        # --- Draw Fog of War (before units and effects) ---
        visibility_grid.draw_fog_of_war(screen, camera)

        # --- Draw Units ---
        # Draw all friendly units
        for unit in friendly_units:
            unit.draw(screen, camera)
            
        # Draw only visible enemy units
        for unit in visible_enemies:
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
            
            # --- Draw Carrier Panel (if a carrier is selected) ---
            for unit in selected_units:
                if isinstance(unit, Carrier):
                    carrier_panel.draw(screen, friendly_units)
                    break
            
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
        
        # Draw fog of war on minimap
        fog_overlay = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA)
        
        # Draw areas in fog based on visibility grid
        for grid_x in range(visibility_grid.grid_width):
            for grid_y in range(visibility_grid.grid_height):
                # Get cell state (0=unseen, 1=previously seen, 2=visible)
                state = visibility_grid.get_cell_state(grid_x, grid_y)
                
                # Calculate minimap position for this cell
                cell_world_x = grid_x * visibility_grid.cell_size
                cell_world_y = grid_y * visibility_grid.cell_size
                mini_x = int((cell_world_x / MAP_WIDTH) * MINIMAP_WIDTH)
                mini_y = int((cell_world_y / MAP_HEIGHT) * MINIMAP_HEIGHT)
                mini_cell_size = max(1, int((visibility_grid.cell_size / MAP_WIDTH) * MINIMAP_WIDTH))
                
                # Draw different fog colors based on visibility state
                if state == VisibilityState.UNSEEN:
                    # Completely black for unseen
                    pygame.draw.rect(fog_overlay, (0, 0, 0, 255), 
                                    pygame.Rect(mini_x, mini_y, mini_cell_size, mini_cell_size))
                elif state == VisibilityState.PREVIOUSLY_SEEN:
                    # Semi-transparent for previously seen
                    pygame.draw.rect(fog_overlay, (0, 0, 0, 150), 
                                    pygame.Rect(mini_x, mini_y, mini_cell_size, mini_cell_size))
        
        # Draw friendly units on minimap (always visible)
        for unit in friendly_units:
            mini_x = int((unit.world_x / MAP_WIDTH) * MINIMAP_WIDTH)
            mini_y = int((unit.world_y / MAP_HEIGHT) * MINIMAP_HEIGHT)
            pygame.draw.circle(minimap_surface, unit.color, (mini_x, mini_y), 2)
            
        # Draw enemy units on minimap only if visible
        for unit in visible_enemies:
            mini_x = int((unit.world_x / MAP_WIDTH) * MINIMAP_WIDTH)
            mini_y = int((unit.world_y / MAP_HEIGHT) * MINIMAP_HEIGHT)
            pygame.draw.circle(minimap_surface, unit.color, (mini_x, mini_y), 2)
            
        # Apply fog of war to minimap
        minimap_surface.blit(fog_overlay, (0, 0))

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
        
        # Fog of war is now drawn before UI elements and after background

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
