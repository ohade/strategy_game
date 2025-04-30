from typing import Tuple

import pygame

from camera import Camera

BRIGHT_YELLOW = (255, 255, 100)
WHITE = (255, 255, 255)

class AttackEffect:
    """Represents a temporary visual effect for an attack (e.g., a laser line)."""
    def __init__(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], 
                 color: Tuple[int, int, int] = BRIGHT_YELLOW, duration: float = 0.15, 
                 thickness: int = 3):
        """Initialize the attack effect.

        Args:
            start_pos (Tuple[float, float]): World coordinates of the effect start.
            end_pos (Tuple[float, float]): World coordinates of the effect end.
            color (Tuple[int, int, int]): Color of the effect line.
            duration (float): How long the effect should last in seconds.
            thickness (int): Thickness of the line effect.
        """
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.duration = duration
        self.timer = duration # Countdown timer
        self.thickness = thickness

    def update(self, dt: float) -> None:
        """Update the effect's timer."""
        self.timer -= dt

    def is_expired(self) -> bool:
        """Check if the effect's timer has run out."""
        return self.timer <= 0

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the attack effect (layered beam)."""
        # Convert world coordinates to screen coordinates
        screen_start = camera.apply_coords(int(self.start_pos[0]), int(self.start_pos[1]))
        screen_end = camera.apply_coords(int(self.end_pos[0]), int(self.end_pos[1]))

        # Calculate alpha based on remaining time (fade out quickly)
        if self.duration <= 0: # Avoid division by zero
            alpha = 0
        else:
            # Square the ratio to make it fade faster towards the end
            time_left_ratio = max(0.0, self.timer / self.duration)
            alpha = max(0, min(255, int((time_left_ratio ** 2) * 255)))

        if alpha <= 0:
            return # Don't draw if fully faded

        # Define thicknesses
        outer_thickness = int(self.thickness * 2.5) # Make outer glow noticeably thicker
        inner_thickness = self.thickness
        max_thickness = outer_thickness # For bounding box calculation

        # Create a temporary surface for alpha blending
        # Determine bounds needed for the thickest line
        min_x = min(screen_start[0], screen_end[0]) - max_thickness
        max_x = max(screen_start[0], screen_end[0]) + max_thickness
        min_y = min(screen_start[1], screen_end[1]) - max_thickness
        max_y = max(screen_start[1], screen_end[1]) + max_thickness
        width = max(1, int(max_x - min_x))
        height = max(1, int(max_y - min_y))

        beam_surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # Calculate line points relative to the surface
        surf_start = (screen_start[0] - min_x, screen_start[1] - min_y)
        surf_end = (screen_end[0] - min_x, screen_end[1] - min_y)

        # Draw Outer Glow (thicker, base color)
        outer_color = (*self.color[:3], int(alpha * 0.8)) # Slightly less alpha for glow
        pygame.draw.line(beam_surf, outer_color, surf_start, surf_end, outer_thickness)
        
        # Draw Inner Core (thinner, bright color)
        inner_color = (*WHITE[:3], alpha) # Bright white core
        pygame.draw.line(beam_surf, inner_color, surf_start, surf_end, inner_thickness)

        # Blit the temporary surface onto the main screen
        surface.blit(beam_surf, (min_x, min_y))


# --- Destination Indicator --- 

class DestinationIndicator:
    """Represents a visual indicator for a move destination point."""

    def __init__(self, world_x: float, world_y: float, color: Tuple[int, int, int] = (255, 255, 255), duration: float = 0.75, radius: int = 10):
        """Initialize the destination indicator.

        Args:
            world_x (float): World x-coordinate for the indicator.
            world_y (float): World y-coordinate for the indicator.
            color (Tuple[int, int, int]): Initial color of the indicator circle.
            duration (float): How long the indicator lasts in seconds.
            radius (int): The radius of the indicator circle.
        """
        self.world_x = world_x
        self.world_y = world_y
        self.initial_color = color
        self.duration = duration
        self.radius = radius

        self.timer = self.duration

    def update(self, dt: float) -> None:
        """Update the indicator's timer."""
        self.timer -= dt

    def is_alive(self) -> bool:
        """Check if the indicator's timer has expired."""
        return self.timer > 0

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the fading indicator circle onto the surface."""
        if not self.is_alive():
            return

        # Calculate alpha based on remaining time (fades out)
        life_ratio = max(0.0, self.timer / self.duration) # Ensure float division
        current_alpha = int(255 * life_ratio)

        # Create color with current alpha
        fade_color = (*self.initial_color, current_alpha)

        # Convert world coordinates to screen coordinates using camera offset
        screen_x, screen_y = camera.apply_coords(int(self.world_x), int(self.world_y))

        # Create a temporary surface for alpha blending
        temp_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, fade_color, (self.radius, self.radius), self.radius)

        # Blit the temporary surface onto the main surface
        surface.blit(temp_surface, (screen_x - self.radius, screen_y - self.radius))


# --- Explosion Effect --- 

class ExplosionEffect:
    """Represents a simple expanding circle explosion effect."""

    def __init__(self, world_x: float, world_y: float, 
                 max_radius: int = 50, duration: float = 0.5, 
                 start_color: Tuple[int, int, int] = (255, 150, 0), # Orange
                 end_color: Tuple[int, int, int] = (100, 100, 100) # Grey
                ):
        """Initialize the explosion effect.

        Args:
            world_x (float): World x-coordinate for the explosion center.
            world_y (float): World y-coordinate for the explosion center.
            max_radius (int): The maximum radius the explosion reaches.
            duration (float): How long the explosion effect lasts in seconds.
            start_color (Tuple[int, int, int]): Color at the start of the explosion.
            end_color (Tuple[int, int, int]): Color at the end of the explosion (fades to this).
        """
        self.world_x = world_x
        self.world_y = world_y
        self.max_radius = max_radius
        self.duration = max(duration, 0.01) # Avoid division by zero
        self.start_color = start_color
        self.end_color = end_color

        self.timer = self.duration # Countdown timer
        self.current_radius = 0

    def update(self, dt: float) -> None:
        """Update the explosion's timer and radius."""
        self.timer -= dt
        # Interpolate radius from 0 to max_radius based on time
        if self.duration > 0:
            time_ratio = (self.duration - self.timer) / self.duration
            self.current_radius = int(self.max_radius * time_ratio)
        else:
            self.current_radius = self.max_radius # Instantaneous if duration is 0

    def is_finished(self) -> bool:
        """Check if the explosion effect's timer has expired."""
        return self.timer <= 0

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the expanding and fading explosion circle."""
        if self.is_finished():
            return

        # Calculate progress ratio (0 = start, 1 = end)
        progress_ratio = (self.duration - self.timer) / self.duration
        progress_ratio = max(0.0, min(1.0, progress_ratio)) # Clamp between 0 and 1

        # Interpolate color
        current_color = (
            int(self.start_color[0] + (self.end_color[0] - self.start_color[0]) * progress_ratio),
            int(self.start_color[1] + (self.end_color[1] - self.start_color[1]) * progress_ratio),
            int(self.start_color[2] + (self.end_color[2] - self.start_color[2]) * progress_ratio)
        )

        # Calculate alpha (fades out towards the end)
        alpha = int(255 * (1.0 - progress_ratio))
        alpha = max(0, min(255, alpha)) # Clamp alpha

        # Final color with alpha
        draw_color = (*current_color, alpha)

        # Convert world coordinates to screen coordinates
        screen_x, screen_y = camera.apply_coords(int(self.world_x), int(self.world_y))

        # Draw the circle on a temporary surface for alpha blending
        radius = max(1, int(self.current_radius))
        if radius * 2 <= 0:
            return # Avoid zero-size surface
            
        temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, draw_color, (radius, radius), radius)

        # Blit onto the main surface
        surface.blit(temp_surface, (screen_x - radius, screen_y - radius))
