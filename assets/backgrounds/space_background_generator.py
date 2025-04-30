"""Script to generate space background layers for parallax effect."""
import pygame
import random
import math

# Initialize pygame
pygame.init()

# Set the dimensions for background layers
WIDTH, HEIGHT = 1024, 768

def create_far_background():
    """Create the distant star field background layer."""
    # Create a dark blue surface
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    surface.fill((5, 8, 20))
    
    # Add stars - sparse and small
    for _ in range(200):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        brightness = random.randint(120, 255)
        size = random.random()
        if size > 0.95:  # Occasional larger star
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), 1)
        else:  # Most stars are just pixels
            surface.set_at((x, y), (brightness, brightness, brightness))
    
    return surface

def create_mid_background():
    """Create the nebula background layer."""
    # Create a transparent surface
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Add some subtle nebula clouds
    for _ in range(5):
        # Create a nebula with a random color
        cloud_size = random.randint(300, 500)
        cloud_surface = pygame.Surface((cloud_size, cloud_size), pygame.SRCALPHA)
        
        # Random nebula color - blue, purple, or red hues
        color_choice = random.choice(['blue', 'purple', 'red'])
        if color_choice == 'blue':
            color = (30, 50, 120)
        elif color_choice == 'purple':
            color = (60, 20, 90)
        else:  # red
            color = (90, 20, 40)
        
        # Create a radial gradient
        for radius in range(cloud_size // 2, 0, -1):
            alpha = int(30 * (radius / (cloud_size / 2)))
            pygame.draw.circle(cloud_surface, (*color, alpha), 
                              (cloud_size // 2, cloud_size // 2), radius)
        
        # Add the nebula to the surface at a random position
        x = random.randint(-cloud_size // 3, WIDTH - cloud_size // 3 * 2)
        y = random.randint(-cloud_size // 3, HEIGHT - cloud_size // 3 * 2)
        surface.blit(cloud_surface, (x, y))
    
    return surface

def create_near_background():
    """Create the foreground celestial objects layer."""
    # Create a transparent surface
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Add 1-2 distant planets or large objects
    num_objects = random.randint(1, 2)
    for _ in range(num_objects):
        # Size and position
        size = random.randint(60, 100)
        # Place away from edges
        margin = size
        x = random.randint(margin, WIDTH - margin)
        y = random.randint(margin, HEIGHT - margin)
        
        # Planet colors - more muted and realistic
        base_color = (
            random.randint(30, 180),
            random.randint(30, 180),
            random.randint(30, 180)
        )
        
        # Draw the planet with some atmospheric gradient
        for r in range(size, 0, -2):
            factor = r / size
            color = (
                int(base_color[0] * factor),
                int(base_color[1] * factor),
                int(base_color[2] * factor),
                180  # Semi-transparent
            )
            pygame.draw.circle(surface, color, (x, y), r)
        
        # 30% chance to add rings
        if random.random() < 0.3:
            ring_width = size // 2
            ring_color = (*base_color, 100)  # Semi-transparent
            
            # Draw an elliptical ring
            rect = (
                x - size - ring_width // 2,
                y - size // 3,
                size * 2 + ring_width,
                size * 2 // 3
            )
            pygame.draw.ellipse(surface, ring_color, rect, ring_width // 3)
    
    return surface

# Generate and save the backgrounds
backgrounds = [
    ("far", create_far_background()),
    ("mid", create_mid_background()),
    ("near", create_near_background())
]

for name, surface in backgrounds:
    filename = f"/Users/ohadedelstein/projects/playground/strategy_game/assets/backgrounds/bg_{name}.png"
    pygame.image.save(surface, filename)
    print(f"Created background layer '{name}' at {filename}")

print("Generated all background layers for parallax effect")
