import pygame
import random
from settings import WIDTH, HEIGHT, GRAVITY
from spells import Spell

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 80)
        self.vel_y = 0
        self.health = 100.0
        self.max_health = 100.0
        self.color = (0, 200, 255)
        self.on_ground = False
        self.spells = []
        self.cooldown = 0
        
        # Status Effects
        self.burn_timer = 0
        self.burn_damage_timer = 0
        self.freeze_timer = 0
        self.block_timer = 0
        self.hurt_timer = 0

    def move(self, dx):
        if self.freeze_timer > 0: return
        self.rect.x += dx
        # Boundary check
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH // 2: self.rect.right = WIDTH // 2

    def jump(self):
        if self.freeze_timer > 0: return
        if self.on_ground:
            self.vel_y = -15

    def update(self, particle_system=None):
        # Cooldowns and Timers
        if self.cooldown > 0: self.cooldown -= 1
        if self.freeze_timer > 0: self.freeze_timer -= 1
        if self.block_timer > 0: self.block_timer -= 1
        if self.hurt_timer > 0: self.hurt_timer -= 1
        
        # Handle Burn (Damage every 2s for 4s)
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if particle_system and random.random() < 0.2:
                particle_system.emit(self.rect.centerx + random.uniform(-15, 15), 
                                   self.rect.centery + random.uniform(-25, 25), 
                                   (255, 60, 0), count=2, ptype="spark")
            
            self.burn_damage_timer += 1
            if self.burn_damage_timer >= 120:
                self.health = max(0.0, self.health - 5.0)
                self.burn_damage_timer = 0
                print(f"Player took burn damage! Health: {self.health}")
        
        # Handle Ice particles
        if self.freeze_timer > 0:
            if particle_system and random.random() < 0.1:
                particle_system.emit(self.rect.centerx + random.uniform(-20, 20), 
                                   self.rect.centery + random.uniform(-30, 30), 
                                   (150, 255, 255), count=1)

        # Movement (Disabled if frozen)
        if self.freeze_timer <= 0:
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y
        else:
            self.vel_y = 0
        
        # Floor collision
        floor_y = HEIGHT // 2 + 80
        if self.rect.bottom > floor_y:
            self.rect.bottom = floor_y
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Update internal spells
        for s in self.spells[:]:
            s.update(particle_system)
            if not s.active:
                self.spells.remove(s)

    def draw(self, surface):
        # Shake effect
        draw_x, draw_y = self.rect.x, self.rect.y
        if self.hurt_timer > 0:
            draw_x += random.randint(-4, 4)
            draw_y += random.randint(-4, 4)

        draw_color = self.color
        if self.hurt_timer > 0: 
            draw_color = (255, 255, 255) # Flash White
        elif self.freeze_timer > 0: 
            draw_color = (150, 255, 255)
        elif self.burn_timer > 0: 
            draw_color = (255, 150, 50)
        
        pygame.draw.rect(surface, draw_color, (draw_x, draw_y, self.rect.width, self.rect.height), border_radius=5)
        
        # Caster Eyes (Cyan)
        eye_color = (0, 255, 255)
        pygame.draw.circle(surface, eye_color, (draw_x + 15, draw_y + 25), 4)
        pygame.draw.circle(surface, eye_color, (draw_x + 35, draw_y + 25), 4)

        # Ice Overlay
        if self.freeze_timer > 0:
            ice_surf = pygame.Surface((self.rect.width + 12, self.rect.height + 12), pygame.SRCALPHA)
            pygame.draw.rect(ice_surf, (200, 255, 255, 130), (0, 0, ice_surf.get_width(), ice_surf.get_height()), border_radius=10)
            pygame.draw.line(ice_surf, (255, 255, 255, 150), (10, 10), (self.rect.width, self.rect.height), 2)
            surface.blit(ice_surf, (draw_x - 6, draw_y - 6))

        # Shield effect
        if self.block_timer > 0:
            shield_rect = pygame.Rect(draw_x - 5, draw_y - 5, self.rect.width + 10, self.rect.height + 10)
            pygame.draw.rect(surface, (50, 150, 255), shield_rect, 3, border_radius=10)
        for s in self.spells:
            s.draw(surface)

    def cast_spell(self, gesture):
        if self.cooldown > 0 or self.freeze_timer > 0: return
        
        # Block is a special "spell"
        if gesture == "|":
            self.block_timer = 120 
            self.cooldown = 60
            print("Player is Blocking!")
            return

        new_spell = Spell(self.rect.right, self.rect.centery, 1, gesture)
        self.spells.append(new_spell)
        self.cooldown = 40
