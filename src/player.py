import pygame
import random
from settings import WIDTH, HEIGHT, GRAVITY, PIXEL_SCALE
from spells import Spell
from pixel_sprites import (
    create_player_sprite, create_ice_overlay,
    create_shield_overlay, create_tinted_variant,
    create_white_flash
)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 66)  # 16*3 x 22*3
        self.vel_y = 0
        self.health = 100.0
        self.max_health = 100.0
        self.on_ground = False
        self.spells = []
        self.cooldown = 0
        
        # Status Effects
        self.burn_timer = 0
        self.burn_damage_timer = 0
        self.freeze_timer = 0
        self.block_timer = 0
        self.hurt_timer = 0

        # Pixel art sprites
        self.base_sprite = create_player_sprite()
        self._build_variants()

    def set_character_sprite(self, sprite_surface):
        """Replace the player sprite with a character-specific one and regenerate variants."""
        self.base_sprite = sprite_surface
        self._build_variants()

    def _build_variants(self):
        """Build hurt/freeze/burn variants from the current base_sprite."""
        self.hurt_sprite = create_white_flash(self.base_sprite)
        self.freeze_sprite = create_tinted_variant(self.base_sprite, (100, 200, 255), 100)
        self.burn_sprite = create_tinted_variant(self.base_sprite, (255, 100, 0), 80)
        self.ice_overlay = create_ice_overlay(self.rect.width + 12, self.rect.height + 12)
        self.shield_overlay = create_shield_overlay(self.rect.width + 10, self.rect.height + 10)

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
            draw_x += random.randint(-3, 3)
            draw_y += random.randint(-3, 3)
        elif self.freeze_timer > 0:
            draw_x += random.randint(-1, 1)
            draw_y += random.randint(-1, 1)

        # Choose sprite based on state
        if self.hurt_timer > 0:
            sprite = self.hurt_sprite
        elif self.freeze_timer > 0:
            sprite = self.freeze_sprite
        elif self.burn_timer > 0:
            sprite = self.burn_sprite
        else:
            sprite = self.base_sprite

        surface.blit(sprite, (draw_x, draw_y))

        # Ice Overlay
        if self.freeze_timer > 0:
            surface.blit(self.ice_overlay, (draw_x - 6, draw_y - 6))

        # Shield effect
        if self.block_timer > 0:
            surface.blit(self.shield_overlay, (draw_x - 5, draw_y - 5))

        for s in self.spells:
            s.draw(surface)

    def cast_spell(self, gesture, particle_system=None, sounds=None):
        if self.cooldown > 0 or self.freeze_timer > 0: return
        
        # Block is a special "spell" (Skill 4)
        if gesture == "|":
            self.block_timer = 120 # 2s
            self.cooldown = 60
            return

        new_spell = Spell(self.rect.right, self.rect.centery, 1, gesture)
        self.spells.append(new_spell)
        self.cooldown = 40
        
        # Play skill sound immediately on cast
        if sounds:
            if gesture == "/" and sounds.get("gun"):
                sounds["gun"].play(maxtime=800)
            elif gesture == "\\" and sounds.get("explosion"):
                sounds["explosion"].play(maxtime=800)
            elif gesture == "O" and sounds.get("freeze"):
                sounds["freeze"].play(maxtime=800)
        
        if particle_system:
            particle_system.burst(self.rect.right, self.rect.centery, new_spell.color, count=10, ptype="circle")
