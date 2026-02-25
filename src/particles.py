import pygame
import random
from settings import *

class Particle:
    def __init__(self, x, y, color, size=None, vx=None, vy=None):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx if vx is not None else random.uniform(-2, 2)
        self.vy = vy if vy is not None else random.uniform(-2, 2)
        self.life = 255
        self.decay = random.uniform(5, 12)
        self.size = size if size is not None else random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size *= 0.95 # Particles shrink over time
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, int(self.life))
        color = (*self.color, alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))

class Spark:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 3.14 * 2)
        speed = random.uniform(2, 5)
        self.vx = speed * random.uniform(-1, 1)
        self.vy = speed * random.uniform(-1, 1)
        self.life = 255
        self.decay = random.uniform(10, 20)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface):
        points = [
            (self.x + self.vx * 2, self.y + self.vy * 2),
            (self.x - self.vy, self.y + self.vx),
            (self.x + self.vy, self.y - self.vx)
        ]
        alpha = max(0, int(self.life))
        color = (*self.color, alpha)
        pygame.draw.polygon(surface, color, points)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=5, ptype="circle"):
        for _ in range(count):
            if ptype == "circle":
                self.particles.append(Particle(x, y, color))
            elif ptype == "spark":
                self.particles.append(Spark(x, y, color))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
