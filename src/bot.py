import pygame
import random
from settings import *
from spells import Spell

class Bot:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 80)
        self.health = 100.0
        self.max_health = 100.0
        self.color = (255, 50, 50)
        self.state = "IDLE"
        self.action_cooldown = 0
        self.spells = []
        
        # Status Effects
        self.burn_timer = 0
        self.burn_damage_timer = 0
        self.freeze_timer = 0
        self.block_timer = 0
        self.hurt_timer = 0
        
        # New: Vertical movement properties
        self.v_move_timer = 0
        self.v_move_dir = 0
        self.v_move_speed = 3

    def update(self, player_rect, particle_system=None):
        if self.action_cooldown > 0: self.action_cooldown -= 1
        if self.freeze_timer > 0: self.freeze_timer -= 1
        if self.block_timer > 0: self.block_timer -= 1
        if self.hurt_timer > 0: self.hurt_timer -= 1
        
        # Handle Burn
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if particle_system and random.random() < 0.3:
                particle_system.emit(self.rect.centerx + random.uniform(-20, 20), 
                                   self.rect.centery + random.uniform(-30, 30), 
                                   (255, 100, 0), count=2, ptype="spark")
            
            self.burn_damage_timer += 1
            if self.burn_damage_timer >= 120:
                damage = self.max_health * 0.05
                self.health = max(0.0, self.health - damage)
                self.burn_damage_timer = 0
                print(f"Bot took burn damage! Health: {self.health}")
        
        # Handle Ice particles when frozen
        if self.freeze_timer > 0:
            if particle_system and random.random() < 0.1:
                particle_system.emit(self.rect.centerx + random.uniform(-25, 25), 
                                   self.rect.centery + random.uniform(-40, 40), 
                                   (150, 255, 255), count=1)
        
        # Update internal spells
        for s in self.spells[:]:
            s.update(particle_system)
            if not s.active:
                self.spells.remove(s)

        # Skip AI logic if frozen
        if self.freeze_timer > 0:
            self.v_move_dir = 0
            return

        # AI Decisions - Horizontal
        dist = player_rect.centerx - self.rect.centerx
        
        # Chance to Dodge or stand still to attack
        if self.action_cooldown == 0:
            if abs(dist) < 150 and random.random() < 0.1:
                self.state = "DODGE"
                # Move away from player
                self.rect.x += -3 if dist > 0 else 3
            elif abs(dist) < 300 and random.random() < 0.05:
                self.state = "STAND_ATTACK"
                self._cast_random_spell(particle_system)
                self.action_cooldown = 80
            else:
                self.state = "CHASE"

        # Horizontal Movement logic based on state
        if self.state == "CHASE" and abs(dist) > 200:
            self.rect.x += 2 if dist > 0 else -2
        elif self.state == "DODGE":
            self.rect.x += -4 if dist > 0 else 4
            # Boundary check for dodge
            self.rect.x = max(50, min(WIDTH - 100, self.rect.x))

        # New: Vertical Movement logic
        if self.v_move_timer <= 0:
            # Pick a random direction (-1, 0, 1) and a random time (30 to 120 frames)
            self.v_move_dir = random.choice([-1, 0, 1])
            self.v_move_timer = random.randint(30, 90)
        else:
            self.v_move_timer -= 1
            self.rect.y += self.v_move_dir * self.v_move_speed
            
            # Boundary check for Y (keep it within the middle area)
            margin = 100
            if self.rect.top < margin:
                self.rect.top = margin
                self.v_move_dir = 0
            elif self.rect.bottom > HEIGHT - margin:
                self.rect.bottom = HEIGHT - margin
                self.v_move_dir = 0

    def _cast_random_spell(self, particle_system=None):
        if self.freeze_timer > 0: return # Extra safety
        # Choose from all new types
        stype = random.choice(["/", "\\", "O"])
        direction = -1 if self.rect.centerx > WIDTH // 2 else 1
        new_spell = Spell(self.rect.left - 30 if direction < 0 else self.rect.right, self.rect.centery, direction, stype)
        self.spells.append(new_spell)
        if particle_system:
            particle_system.burst(new_spell.rect.centerx, new_spell.rect.centery, new_spell.color, count=8, ptype="circle")

    def draw(self, surface):
        # Shake effect
        draw_x, draw_y = self.rect.x, self.rect.y
        if self.hurt_timer > 0:
            draw_x += random.randint(-4, 4)
            draw_y += random.randint(-4, 4)
        elif self.freeze_timer > 0:
            draw_x += random.randint(-1, 1)
            draw_y += random.randint(-1, 1)

        draw_color = self.color
        if self.hurt_timer > 0:
            draw_color = (255, 255, 255) # Flash White
        elif self.freeze_timer > 0:
            draw_color = (150, 255, 255) # Ice blue
        elif self.burn_timer > 0:
            draw_color = (255, 150, 50) # Burning orange
            
        pygame.draw.rect(surface, draw_color, (draw_x, draw_y, self.rect.width, self.rect.height), border_radius=5)
        
        # Dark eyes
        pygame.draw.rect(surface, (0, 0, 0), (draw_x + 10, draw_y + 20, 10, 10))
        pygame.draw.rect(surface, (0, 0, 0), (draw_x + 30, draw_y + 20, 10, 10))

        # Ice Overlay
        if self.freeze_timer > 0:
            ice_surf = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(ice_surf, (200, 255, 255, 120), (0, 0, ice_surf.get_width(), ice_surf.get_height()), border_radius=8)
            # Some "cracks"
            pygame.draw.line(ice_surf, (255, 255, 255, 180), (5, 5), (self.rect.width, self.rect.height), 2)
            pygame.draw.line(ice_surf, (255, 255, 255, 180), (self.rect.width, 5), (5, self.rect.height), 1)
            surface.blit(ice_surf, (draw_x - 5, draw_y - 5))

        for s in self.spells:
            s.draw(surface)
