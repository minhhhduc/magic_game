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
            self.color = (255, 60, 0) # Fire (Vibrant Red-Orange)
        elif type == "\\": 
            self.color = (240, 240, 240) # Normal (Bright White/Silver)
        elif type == "|":
            self.color = (0, 120, 255) # Block (Electric Blue)
            self.speed = 5 * direction
        elif type == "O":
            self.color = (0, 255, 180) # Freeze (Mint Ice)
        else:
            self.color = (255, 255, 255)

    def update(self, particle_system=None):
        self.rect.x += self.speed
        if particle_system:
            # Emit trail particles
            ptype = "circle"
            count = 1
            if self.type == "/": 
                ptype = "spark"
                count = 2
            particle_system.emit(self.rect.centerx, self.rect.centery, self.color, count=count, ptype=ptype)

        if self.rect.x < -50 or self.rect.x > WIDTH + 50:
            self.active = False

    def draw(self, surface):
        # Main projectile body
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        
        # Inner core (lighter color)
        core_color = [min(255, c + 100) for c in self.color]
        core_rect = self.rect.inflate(-8, -8)
        pygame.draw.rect(surface, core_color, core_rect, border_radius=5)

        # Glow effect
        glow_size = 20
        glow_surf = pygame.Surface((self.rect.width + glow_size, self.rect.height + glow_size), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (*self.color, 60), (0, 0, glow_surf.get_width(), glow_surf.get_height()))
        surface.blit(glow_surf, (self.rect.x - glow_size//2, self.rect.y - glow_size//2))
