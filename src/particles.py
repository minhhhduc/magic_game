import pygame
import random
from settings import *

class ParticleBase:
    def update(self) -> bool: return False
    def draw(self, surface: pygame.Surface): pass

class Particle(ParticleBase):
    def __init__(self, x, y, color, size=None, vx=None, vy=None, decay=None):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.vx = float(vx if vx is not None else random.uniform(-2, 2))
        self.vy = float(vy if vy is not None else random.uniform(-2, 2))
        self.life = 255.0
        self.decay = float(decay if decay is not None else random.uniform(5, 12))
        self.size = float(size if size is not None else random.randint(3, 6))

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size *= 0.96
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0: return
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))
        if self.size > 2:
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), int(self.size//2))

class Spark(ParticleBase):
    def __init__(self, x, y, color, vx=None, vy=None):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        speed = random.uniform(4, 8)
        self.vx = float(vx if vx is not None else random.uniform(-1, 1) * speed)
        self.vy = float(vy if vy is not None else random.uniform(-1, 1) * speed)
        self.life = 255.0
        self.decay = float(random.uniform(10, 20))

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1 # Gravity
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0: return
        end_x = self.x - self.vx * 1.5
        end_y = self.y - self.vy * 1.5
        pygame.draw.line(surface, self.color, (int(self.x), int(self.y)), (int(end_x), int(end_y)), 2)
        pygame.draw.line(surface, (255, 255, 255), (int(self.x), int(self.y)), (int(self.x - self.vx*0.5), int(self.y - self.vy*0.5)), 1)

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
                self.particles.append(Particle(x, y, color, size=random.randint(4, 8), decay=random.uniform(10, 20)))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
