"""Script to generate explosion animation frames."""
import pygame
import math
import random

# Initialize pygame
pygame.init()

# Set the dimensions
SIZE = 128  # Larger size for explosion effect
FRAMES = 5  # Number of frames in the explosion animation

# Colors
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
RED = (255, 50, 20)
SMOKE = (80, 80, 80)

def generate_explosion_frame(index, max_frames):
    """Generate a single explosion frame."""
    # Create a surface with alpha channel
    frame = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    
    # Calculate the size and opacity for this frame
    progress = index / max_frames
    radius = int(10 + (SIZE/2 - 10) * progress)
    opacity = 255 - int(200 * progress)  # Fade out
    
    # Create explosion center
    center = (SIZE // 2, SIZE // 2)
    
    # Draw outer explosion glow
    glow_radius = radius + int(radius * 0.4)
    for r in range(glow_radius, radius, -2):
        alpha = max(0, min(opacity - 50, 255) * (r - radius) / glow_radius)
        pygame.draw.circle(frame, (*ORANGE[:3], int(alpha)), center, r)
    
    # Main explosion circle
    pygame.draw.circle(frame, (*ORANGE[:3], opacity), center, radius)
    
    # Inner bright part
    inner_radius = int(radius * 0.7)
    pygame.draw.circle(frame, (*YELLOW[:3], opacity), center, inner_radius)
    
    # Add random debris/particles for later frames
    if index > 0:
        num_particles = 15 + index * 5
        for _ in range(num_particles):
            angle = random.random() * math.pi * 2
            distance = random.random() * radius * 0.9
            size = random.randint(1, 3 + index)
            x = int(center[0] + math.cos(angle) * distance)
            y = int(center[1] + math.sin(angle) * distance)
            
            # Random color for particles
            if random.random() > 0.7:
                color = (*YELLOW[:3], random.randint(100, 200))
            elif random.random() > 0.5:
                color = (*ORANGE[:3], random.randint(100, 200))
            else:
                color = (*RED[:3], random.randint(100, 200))
                
            pygame.draw.circle(frame, color, (x, y), size)
    
    # Add smoke for later frames
    if index > 1:
        for _ in range(5 + index * 3):
            angle = random.random() * math.pi * 2
            distance = random.random() * radius * 1.2
            smoke_size = random.randint(3, 6 + index * 2)
            x = int(center[0] + math.cos(angle) * distance)
            y = int(center[1] + math.sin(angle) * distance)
            smoke_alpha = random.randint(30, 100)
            
            pygame.draw.circle(frame, (*SMOKE[:3], smoke_alpha), (x, y), smoke_size)
    
    return frame

# Generate and save each frame
for i in range(FRAMES):
    frame = generate_explosion_frame(i, FRAMES - 1)
    filename = f"/Users/ohadedelstein/projects/playground/strategy_game/assets/effects/explosion_{i}.png"
    pygame.image.save(frame, filename)
    print(f"Created explosion frame {i} at {filename}")

print(f"Generated {FRAMES} explosion animation frames")
