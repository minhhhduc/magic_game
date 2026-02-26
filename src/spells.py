import pygame
from settings import *
from pixel_sprites import (
    create_bullet_spell, create_bomb_spell, create_ice_spell,
    create_normal_spell, create_block_spell,
    PIXEL_SCALE
)

class Spell:
    def __init__(self, x, y, direction, type):
        self.direction = direction
        self.type = type # "/", "\", "|", "O"
        self.speed = 12 * direction
        self.active = True
        
        # Color based on type (for particles)
        if type == "/": # Gun
            self.color = (255, 255, 100)  # Glaring Neon Yellow
            self.sprite = create_bullet_spell()
        elif type == "\\": # Bomb
            self.color = (255, 50, 0)     # Glaring Neon Red
            self.sprite = create_bomb_spell()
        elif type == "|":
            self.color = (50, 120, 255)   # Block Blue
            self.sprite = create_block_spell()
            self.speed = 5 * direction
        elif type == "O":
            self.color = (0, 255, 255)    # Ice Cyan
            self.sprite = create_ice_spell()
            self.speed = 15 * direction   # Fast freeze
        else:
            self.color = (200, 200, 200)
            self.sprite = create_normal_spell()

        # Set rect based on sprite size
        self.rect = pygame.Rect(x, y - self.sprite.get_height() // 2,
                                self.sprite.get_width(), self.sprite.get_height())

        # Flip sprite if going left
        if direction < 0:
            self.sprite = pygame.transform.flip(self.sprite, True, False)

    def update(self, particle_system=None):
        self.rect.x += self.speed
        if particle_system:
            # Emit pixel trail
            ptype = "circle"
            count = 2
            if self.type == "/": 
                ptype = "spark" # Gunshot sparks
                count = 4
            elif self.type == "\\":
                ptype = "circle" # Bomb trail
                count = 4
            elif self.type == "O":
                ptype = "circle" # Ice trail
                count = 2
            particle_system.emit(self.rect.centerx, self.rect.centery, self.color, count=count, ptype=ptype)

        if self.rect.x < -100 or self.rect.x > WIDTH + 100:
            self.active = False

    def draw(self, surface):
        surface.blit(self.sprite, self.rect.topleft)
