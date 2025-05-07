"""Script to generate laser beam animation frames."""
import pygame
import math
import random

# Initialize pygame
pygame.init()

# Set the dimensions
SIZE = (128, 32)  # Rectangular shape for a laser beam
FRAMES = 3  # Number of frames in the laser animation

# Colors
BLUE = (20, 120, 255)
LIGHT_BLUE = (150, 200, 255)
WHITE = (255, 255, 255)

def generate_laser_frame(index, max_frames):
    """Generate a single laser beam frame."""
    # Create a surface with alpha channel
    frame = pygame.Surface(SIZE, pygame.SRCALPHA)
    
    # Calculate the intensity for this frame (pulsing effect)
    progress = index / max_frames
    # Use sine wave to create a pulsing effect
    pulse_factor = 0.7 + 0.3 * math.sin(progress * math.pi)
    
    # Core width and opacity vary with the pulse
    core_width = max(1, int(SIZE[1] * 0.3 * pulse_factor))
    core_opacity = int(250 * pulse_factor)
    
    # Draw the laser beam
    
    # Outer glow
    for i in range(SIZE[1] // 2, 0, -2):
        # Calculate alpha based on distance from center and pulse
        alpha = int(150 * (i / (SIZE[1] / 2)) * pulse_factor)
        # Reduce alpha near the edges
        if i < SIZE[1] // 6:
            alpha = int(alpha * (i / (SIZE[1] // 6)))
            
        # Draw horizontal lines for the glow effect
        y_pos = SIZE[1] // 2 - i
        pygame.draw.line(frame, (*BLUE[:3], alpha), (0, y_pos), (SIZE[0], y_pos), 1)
        y_pos = SIZE[1] // 2 + i
        pygame.draw.line(frame, (*BLUE[:3], alpha), (0, y_pos), (SIZE[0], y_pos), 1)
    
    # Bright core
    y_start = SIZE[1] // 2 - core_width // 2
    pygame.draw.rect(frame, (*LIGHT_BLUE[:3], core_opacity), 
                     (0, y_start, SIZE[0], core_width))
    
    # Central bright line
    pygame.draw.line(frame, (*WHITE[:3], core_opacity), 
                     (0, SIZE[1] // 2), (SIZE[0], SIZE[1] // 2), 1)
    
    # Add random energy particles
    num_particles = 10 + int(10 * pulse_factor)
    for _ in range(num_particles):
        x = random.randint(0, SIZE[0])
        y = random.randint(max(0, SIZE[1]//2 - SIZE[1]//4), 
                          min(SIZE[1], SIZE[1]//2 + SIZE[1]//4))
        size = random.randint(1, 2)
        alpha = random.randint(150, 255)
        
        if random.random() > 0.5:
            color = (*LIGHT_BLUE[:3], alpha)
        else:
            color = (*WHITE[:3], alpha)
            
        pygame.draw.circle(frame, color, (x, y), size)
    
    return frame

# Generate and save each frame
for i in range(FRAMES):
    frame = generate_laser_frame(i, FRAMES - 1)
    filename = f"laser_{i}.png"
    pygame.image.save(frame, filename)
    print(f"Created laser frame {i} as {filename}")

print(f"Generated {FRAMES} laser animation frames")
