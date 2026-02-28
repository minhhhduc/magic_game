import pygame
import random
from config.settings import *
from core.spells import Spell
from ui.pixel_sprites import (
    create_bot_sprite, create_ice_overlay,
    create_shield_overlay, create_tinted_variant,
    create_white_flash
)

class Bot:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 66)  # 16*3 x 22*3
        self.health = 100.0
        self.max_health = 100.0
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

        # Pixel art sprites
        self.base_sprite = create_bot_sprite()
        self.hurt_sprite = None
        self.freeze_sprite = None
        self.burn_sprite = None
        self.ice_overlay = None
        self.shield_overlay = None
        self._build_variants()

    def set_bot_sprite(self, sprite_surface):
        """Replace the bot sprite with a character-specific one and regenerate variants."""
        self.base_sprite = sprite_surface
        self._build_variants()

    def _build_variants(self):
        """Build hurt/freeze/burn variants from the current base_sprite."""
        self.hurt_sprite = create_white_flash(self.base_sprite)
        self.freeze_sprite = create_tinted_variant(self.base_sprite, (100, 200, 255), 100)
        self.burn_sprite = create_tinted_variant(self.base_sprite, (255, 100, 0), 80)
        self.ice_overlay = create_ice_overlay(self.rect.width + 10, self.rect.height + 10)
        self.shield_overlay = create_shield_overlay(self.rect.width + 10, self.rect.height + 10)
        # Flip bot sprite to face left
        self.base_sprite = pygame.transform.flip(self.base_sprite, True, False)
        if self.hurt_sprite: self.hurt_sprite = pygame.transform.flip(self.hurt_sprite, True, False)
        if self.freeze_sprite: self.freeze_sprite = pygame.transform.flip(self.freeze_sprite, True, False)
        if self.burn_sprite: self.burn_sprite = pygame.transform.flip(self.burn_sprite, True, False)

    def update(self, player, particle_system=None, sounds=None):
        player_rect = player.rect
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
                self.health = max(0.0, self.health - 5.0)
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
 
        # Reactive Dodge Logic: If player spell is coming close
        incoming_threat = False
        for s in player.spells:
            if abs(s.rect.centerx - self.rect.centerx) < 200:
                incoming_threat = True
                break
        
        if incoming_threat and self.action_cooldown == 0:
            choice = random.random()
            if choice < 0.3: # Block
                self.block_timer = 120 # 2s
                self.action_cooldown = 60
                return
            elif choice < 0.6: # Jump
                self.v_move_dir = -1
                self.v_move_timer = 30
                self.action_cooldown = 40
            else: # Dodge Horizontal
                self.state = "DODGE"
                self.action_cooldown = 30
 
        # AI Decisions - Horizontal
        dist = player_rect.centerx - self.rect.centerx
        
        # Chance tostand still to attack
        if self.action_cooldown == 0:
            if abs(dist) < 350 and random.random() < 0.08:
                self.state = "STAND_ATTACK"
                # Smart spell selection
                if player.freeze_timer <= 0:
                    stype = "O" if random.random() < 0.6 else random.choice(["/", "\\"])
                else:
                    stype = random.choice(["/", "\\"])
                
                self._cast_random_spell(particle_system, stype, sounds)
                self.action_cooldown = 60 # Faster attacks
            else:
                self.state = "CHASE"
 
        # Horizontal Movement logic
        move_speed = 4
        if self.state == "CHASE" and abs(dist) > 180:
            self.rect.x += move_speed if dist > 0 else -move_speed
        elif self.state == "DODGE":
            self.rect.x += -move_speed * 1.5 if dist > 0 else move_speed * 1.5
            self.rect.x = max(50, min(WIDTH - 100, self.rect.x))
 
        # Vertical Movement logic
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

    def _cast_random_spell(self, particle_system=None, stype=None, sounds=None):
        if self.freeze_timer > 0: return # Extra safety
        # Choose from all types if not specified
        if stype is None:
            stype = random.choice(["/", "\\", "O"])

        direction = -1 if self.rect.centerx > WIDTH // 2 else 1
        new_spell = Spell(self.rect.left - 30 if direction < 0 else self.rect.right, self.rect.centery, direction, stype)
        self.spells.append(new_spell)
        
        # Play skill sound immediately on cast
        if sounds:
            if stype == "/" and sounds.get("gun"):
                sounds["gun"].play(maxtime=800)
            elif stype == "\\" and sounds.get("explosion"):
                sounds["explosion"].play(maxtime=800)
            elif stype == "O" and sounds.get("freeze"):
                sounds["freeze"].play(maxtime=800)
        
        if particle_system:
            particle_system.burst(new_spell.rect.centerx, new_spell.rect.centery, new_spell.color, count=8, ptype="circle")

    def draw(self, surface, shake_offset=(0, 0)):
        # Shake effect
        draw_x = self.rect.x + shake_offset[0]
        draw_y = self.rect.y + shake_offset[1]
        
        if self.hurt_timer > 0:
            draw_x += random.randint(-4, 4)
            draw_y += random.randint(-4, 4)
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

        if sprite:
            surface.blit(sprite, (draw_x, draw_y))

        # Ice Overlay
        if self.freeze_timer > 0 and self.ice_overlay:
            surface.blit(self.ice_overlay, (draw_x - 5, draw_y - 5))

        # Shield effect
        if self.block_timer > 0 and self.shield_overlay:
            surface.blit(self.shield_overlay, (draw_x - 5, draw_y - 5))

        for s in self.spells:
            s.draw(surface, shake_offset)
