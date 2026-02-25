import pygame
import random
from settings import *

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = 255
        self.decay = random.uniform(5, 10)
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, int(self.life))
        color = (*self.color, alpha)
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=5):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
