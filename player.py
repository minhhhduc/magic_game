import pygame
from settings import *
from spells import Spell

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 80)
        self.vel_y = 0
        self.health = 100
        self.max_health = 100
        self.color = (0, 200, 255)
        self.on_ground = False
        self.spells = []
        self.cooldown = 0

    def update(self):
        # Cooldown
        if self.cooldown > 0:
            self.cooldown -= 1

        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # Floor collision (Centered vertically)
        floor_y = HEIGHT // 2 + 80
        if self.rect.bottom > floor_y:
            self.rect.bottom = floor_y
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Update internal spells
        for s in self.spells[:]:
            s.update()
            if not s.active:
                self.spells.remove(s)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        # Draw some "eyes" to indicate direction
        pygame.draw.rect(surface, (255, 255, 255), (self.rect.x + 30, self.rect.y + 20, 10, 10))
        for s in self.spells:
            s.draw(surface)

    def cast_spell(self, gesture):
        if self.cooldown > 0: return
        
        new_spell = Spell(self.rect.right, self.rect.centery, 1, gesture)
        self.spells.append(new_spell)
        self.cooldown = 40 # Cast cooldown
