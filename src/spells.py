import pygame
from settings import *

class Spell:
    def __init__(self, x, y, direction, type):
        self.rect = pygame.Rect(x, y, 30, 20)
        self.direction = direction
        self.type = type # "/", "\", "|", "O"
        self.speed = 12 * direction
        self.active = True
        
        # Color based on type
        if type == "/": 
            self.color = (255, 50, 0) # Fire Red
        elif type == "\\": 
            self.color = (240, 240, 240) # Normal White
        elif type == "|":
            self.color = (50, 120, 255) # Block Blue
            self.speed = 5 * direction
        elif type == "O":
            self.color = (0, 255, 255) # Ice Cyan
            self.speed = 15 * direction # Fast freeze
        else:
            self.color = (200, 200, 200)

    def update(self, particle_system=None):
        self.rect.x += self.speed
        if particle_system:
            # Emit intense trail
            ptype = "circle"
            count = 2
            if self.type == "/": 
                ptype = "spark"
                count = 4
            elif self.type == "O":
                count = 3
            particle_system.emit(self.rect.centerx, self.rect.centery, self.color, count=count, ptype=ptype)

        if self.rect.x < -100 or self.rect.x > WIDTH + 100:
            self.active = False

    def draw(self, surface):
        # projectile body
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        
        # Inner core (white-ish)
        core_rect = self.rect.inflate(-10, -10)
        pygame.draw.rect(surface, (255, 255, 255), core_rect, border_radius=5)

        # Large Glow effect
        glow_size = 30
        glow_surf = pygame.Surface((self.rect.width + glow_size, self.rect.height + glow_size), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (*self.color, 40), (0, 0, glow_surf.get_width(), glow_surf.get_height()))
        surface.blit(glow_surf, (self.rect.x - glow_size//2, self.rect.y - glow_size//2))
