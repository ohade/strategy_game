"""Script to generate a friendly spaceship sprite."""
import pygame

# Initialize pygame
pygame.init()

# Set the dimensions
WIDTH, HEIGHT = 64, 64

# Create a surface with alpha channel
ship = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Draw a blue/green friendly spaceship
# Main body
pygame.draw.polygon(ship, (30, 120, 200), [
    (48, 32),  # Nose
    (16, 24),  # Upper back
    (8, 32),   # Back center
    (16, 40)   # Lower back
])

# Cockpit
pygame.draw.circle(ship, (120, 220, 255), (38, 32), 6)

# Wings
pygame.draw.polygon(ship, (20, 80, 160), [
    (24, 18),  # Upper tip
    (16, 24),  # Inner upper
    (28, 32)   # Back tip
])
pygame.draw.polygon(ship, (20, 80, 160), [
    (24, 46),  # Lower tip
    (16, 40),  # Inner lower
    (28, 32)   # Back tip
])

# Engine glow
pygame.draw.polygon(ship, (200, 200, 50), [
    (8, 32),   # Engine back center
    (12, 28),  # Upper engine
    (4, 32),   # Engine flame tip
    (12, 36)   # Lower engine
])

# Highlight
pygame.draw.line(ship, (150, 230, 255), (40, 29), (20, 29), 1)
pygame.draw.line(ship, (150, 230, 255), (40, 35), (20, 35), 1)

# Save the image
pygame.image.save(ship, "/assets/ships/friendly_ship.png")

print("Friendly ship sprite created at 'assets/ships/friendly_ship.png'")
