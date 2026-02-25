import pygame
from settings import *

class Spell:
    def __init__(self, x, y, direction, type):
        self.rect = pygame.Rect(x, y, 30, 10)
        self.direction = direction
        self.type = type # "/", "\", "^"
        self.speed = 10 * direction
        self.active = True
        
        # Color based on type
        if type == "/": self.color = (0, 255, 255) # Cyan
        elif type == "\\": self.color = (255, 0, 255) # Magenta
        else: self.color = (255, 255, 0) # Yellow

    def update(self):
        self.rect.x += self.speed
        if self.rect.x < 0 or self.rect.x > WIDTH:
            self.active = False

    def draw(self, surface):
        # Draw with a slight glow
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        # Simple glow
        glow_rect = self.rect.inflate(10, 10)
        s = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.color, 100), s.get_rect(), border_radius=10)
        surface.blit(s, glow_rect.topleft)
