import pygame
import random
from settings import *
from spells import Spell

class Bot:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 80)
        self.health = 100
        self.max_health = 100
        self.color = (255, 50, 50)
        self.state = "IDLE"
        self.action_cooldown = 0
        self.spells = []

    def update(self, player_rect):
        if self.action_cooldown > 0:
            self.action_cooldown -= 1
        
        # Update internal spells
        for s in self.spells[:]:
            s.update()
            if not s.active:
                self.spells.remove(s)

        # AI Decisions
        dist = player_rect.centerx - self.rect.centerx
        
        # New: Chance to Dodge or stand still to attack
        if self.action_cooldown == 0:
            if abs(dist) < 150 and random.random() < 0.1:
                self.state = "DODGE"
                # Move away from player
                self.rect.x += -3 if dist > 0 else 3
            elif abs(dist) < 300 and random.random() < 0.05:
                self.state = "STAND_ATTACK"
                self._cast_random_spell()
                self.action_cooldown = 80
            else:
                self.state = "CHASE"

        # Movement logic based on state
        if self.state == "CHASE" and abs(dist) > 200:
            self.rect.x += 2 if dist > 0 else -2
        elif self.state == "DODGE":
            self.rect.x += -4 if dist > 0 else 4
            # Boundary check for dodge
            self.rect.x = max(50, min(WIDTH - 100, self.rect.x))

    def _cast_random_spell(self):
        stype = random.choice(["/", "\\", "^"])
        direction = -1 if self.rect.centerx > WIDTH // 2 else 1
        new_spell = Spell(self.rect.left - 30 if direction < 0 else self.rect.right, self.rect.centery, direction, stype)
        self.spells.append(new_spell)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        # Dark eyes
        pygame.draw.rect(surface, (0, 0, 0), (self.rect.x + 10, self.rect.y + 20, 10, 10))
        for s in self.spells:
            s.draw(surface)
