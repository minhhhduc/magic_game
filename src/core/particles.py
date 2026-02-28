import pygame
import random
import math
from config.settings import *

PIXEL_SCALE = 3

class ParticleBase:
    def update(self) -> bool: return False
    def draw(self, surface: pygame.Surface, shake_offset=(0, 0)): pass

class Particle(ParticleBase):
    """Pixel-style square particle."""
    def __init__(self, x, y, color, size=None, vx=None, vy=None, decay=None):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.vx = float(vx if vx is not None else random.uniform(-2, 2))
        self.vy = float(vy if vy is not None else random.uniform(-2, 2))
        self.life = 255.0
        self.decay = float(decay if decay is not None else random.uniform(5, 12))
        self.size = int(size if size is not None else random.choice([PIXEL_SCALE, PIXEL_SCALE * 2]))

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface, shake_offset=(0, 0)):
        if self.life <= 0: return
        # Pixel square instead of circle
        draw_x = int(self.x + shake_offset[0])
        draw_y = int(self.y + shake_offset[1])
        pygame.draw.rect(surface, self.color, (draw_x, draw_y, self.size, self.size))
        # Inner bright pixel
        if self.size >= PIXEL_SCALE * 2:
            pygame.draw.rect(surface, (255, 255, 255),
                           (draw_x + PIXEL_SCALE // 2, draw_y + PIXEL_SCALE // 2,
                            PIXEL_SCALE, PIXEL_SCALE))

class Spark(ParticleBase):
    """Pixel-style spark trail."""
    def __init__(self, x, y, color, vx=None, vy=None):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        speed = random.uniform(3, 7)
        self.vx = float(vx if vx is not None else random.uniform(-1, 1) * speed)
        self.vy = float(vy if vy is not None else random.uniform(-1, 1) * speed)
        self.life = 255.0
        self.decay = float(random.uniform(10, 20))
        self.trail = []  # Store previous positions for pixelated trail

    def update(self) -> bool:
        # Save trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 3:
            self.trail.pop(0)
        
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface, shake_offset=(0, 0)):
        if self.life <= 0: return
        # Draw trail as pixel squares
        for i, (tx, ty) in enumerate(self.trail):
            alpha_color = tuple(max(0, c - 80 + i * 30) for c in self.color)
            pygame.draw.rect(surface, alpha_color, (tx + shake_offset[0], ty + shake_offset[1], PIXEL_SCALE, PIXEL_SCALE))
        # Current position - bright pixel
        pygame.draw.rect(surface, (255, 255, 255), (int(self.x + shake_offset[0]), int(self.y + shake_offset[1]), PIXEL_SCALE, PIXEL_SCALE))

class ParticleSystem:
    def __init__(self):
        self.particles: list[ParticleBase] = []

    def emit(self, x, y, color, count=5, ptype="circle"):
        for _ in range(count):
            if ptype == "circle":
                self.particles.append(Particle(x, y, color))
            elif ptype == "spark":
                self.particles.append(Spark(x, y, color))

    def burst(self, x, y, color, count=15, ptype="spark"):
        for _ in range(count):
            if ptype == "spark":
                self.particles.append(Spark(x, y, color))
            else:
                self.particles.append(Particle(x, y, color, 
                    size=random.choice([PIXEL_SCALE, PIXEL_SCALE * 2]),
                    decay=random.uniform(10, 20)))

    def update(self):
        # In-place filtering is generally faster than list comprehension for large lists
        # especially if many particles are removed at once.
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface, shake_offset=(0, 0)):
        # Cache int conversion outside the loop if shake_offset is stable
        sx, sy = int(shake_offset[0]), int(shake_offset[1])
        for p in self.particles:
            p.draw(surface, (sx, sy))
