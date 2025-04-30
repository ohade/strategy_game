"""Script to generate an enemy spaceship sprite."""
import pygame

# Initialize pygame
pygame.init()

# Set the dimensions
WIDTH, HEIGHT = 64, 64

# Create a surface with alpha channel
ship = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Draw a red/orange enemy spaceship
# Main body
pygame.draw.polygon(ship, (200, 50, 30), [
    (48, 32),  # Nose
    (20, 18),  # Upper back
    (12, 32),  # Back center
    (20, 46)   # Lower back
])

# Angular details to make it look more aggressive
pygame.draw.polygon(ship, (160, 30, 20), [
    (36, 32),  # Middle point
    (30, 24),  # Upper point
    (30, 40)   # Lower point
])

# Cockpit - darker and more angled
pygame.draw.polygon(ship, (120, 30, 40), [
    (42, 32),  # Front
    (34, 27),  # Upper
    (34, 37)   # Lower
])

# Wings - more angular
pygame.draw.polygon(ship, (180, 40, 20), [
    (28, 12),  # Upper tip
    (20, 18),  # Inner upper
    (30, 28)   # Back tip
])
pygame.draw.polygon(ship, (180, 40, 20), [
    (28, 52),  # Lower tip
    (20, 46),  # Inner lower
    (30, 36)   # Back tip
])

# Engine glow - orange/red
pygame.draw.polygon(ship, (255, 120, 0), [
    (12, 32),  # Engine back center
    (16, 27),  # Upper engine
    (8, 32),   # Engine flame tip
    (16, 37)   # Lower engine
])

# Highlights
pygame.draw.line(ship, (255, 150, 100), (40, 28), (24, 22), 1)
pygame.draw.line(ship, (255, 150, 100), (40, 36), (24, 42), 1)

# Save the image
pygame.image.save(ship, "/Users/ohadedelstein/projects/playground/strategy_game/assets/ships/enemy_ship.png")

print("Enemy ship sprite created at 'assets/ships/enemy_ship.png'")
