"""Module for handling animated sprite effects in the game."""
from typing import List, Tuple, Optional

import pygame

from camera import Camera
from asset_manager import get_effect_animation


class AnimatedSprite:
    """A class to handle sprite-based animations with frame sequences."""
    
    def __init__(self, world_x: float, world_y: float, 
                 effect_type: str, duration: float = 1.0, 
                 scale: float = 1.0, loop: bool = False,
                 rotation: float = 0.0):
        """Initialize an animated sprite effect.
        
        Args:
            world_x (float): World x-coordinate
            world_y (float): World y-coordinate
            effect_type (str): Type of effect ('explosion', 'laser', etc.)
            duration (float): Total duration of the animation in seconds
            scale (float): Size scale factor
            loop (bool): Whether the animation should loop
            rotation (float): Rotation angle in degrees
        """
        self.world_x = world_x
        self.world_y = world_y
        self.effect_type = effect_type
        self.duration = max(0.1, duration)  # Minimum duration to avoid division by zero
        self.scale = scale
        self.loop = loop
        self.rotation = rotation
        
        # Get frame sequence from asset manager
        try:
            self.frames = get_effect_animation(effect_type)
            self.total_frames = len(self.frames)
        except ValueError:
            # Fallback to a simple colored rectangle if animation not found
            print(f"Animation '{effect_type}' not found, using fallback")
            self.frames = [self._create_fallback_frame()]
            self.total_frames = 1
        
        self.timer = 0.0
        self.current_frame_index = 0
        self.finished = False
    
    def _create_fallback_frame(self) -> pygame.Surface:
        """Create a fallback animation frame when the requested type isn't available."""
        size = 32  # Default size for fallback
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw a simple colored rectangle based on effect type
        if self.effect_type == 'explosion':
            color = (255, 100, 0, 200)  # Orange
        elif self.effect_type == 'laser':
            color = (0, 100, 255, 200)  # Blue
        else:
            color = (255, 255, 255, 200)  # White
            
        pygame.draw.rect(surface, color, (0, 0, size, size))
        return surface
    
    def update(self, dt: float) -> None:
        """Update the animation state.
        
        Args:
            dt (float): Time delta in seconds
        """
        if self.finished:
            return
            
        self.timer += dt
        
        # Check if animation is complete
        if self.timer >= self.duration:
            if self.loop:
                # Loop back to start
                self.timer %= self.duration
            else:
                self.finished = True
                return
        
        # Calculate current frame index based on time progress
        progress = self.timer / self.duration
        self.current_frame_index = min(
            int(progress * self.total_frames), 
            self.total_frames - 1
        )
    
    def is_finished(self) -> bool:
        """Check if the animation has finished playing.
        
        Returns:
            bool: True if animation is finished, False otherwise
        """
        return self.finished
    
    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the current animation frame.
        
        Args:
            surface (pygame.Surface): The surface to draw on
            camera (Camera): The camera for coordinate transformation
        """
        if self.finished or self.current_frame_index >= len(self.frames):
            return
            
        # Get current frame
        frame = self.frames[self.current_frame_index]
        
        # Scale if needed
        if self.scale != 1.0:
            original_size = (frame.get_width(), frame.get_height())
            new_size = (int(original_size[0] * self.scale), int(original_size[1] * self.scale))
            frame = pygame.transform.smoothscale(frame, new_size)
        
        # Rotate if needed
        if self.rotation != 0:
            frame = pygame.transform.rotate(frame, self.rotation)
        
        # Get frame dimensions
        frame_width = frame.get_width()
        frame_height = frame.get_height()
        
        # Convert world coordinates to screen coordinates
        screen_x, screen_y = camera.apply_coords(int(self.world_x), int(self.world_y))
        
        # Center the frame on the coordinates
        dest_x = screen_x - frame_width // 2
        dest_y = screen_y - frame_height // 2
        
        # Draw the frame
        surface.blit(frame, (dest_x, dest_y))
