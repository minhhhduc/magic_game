import pygame
import sys
import os
import random
import cv2
import math

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import (
    WIDTH, HEIGHT, FPS, PIXEL_SCALE, BG_COLOR, TEXT_COLOR, ACCENT_COLOR,
    BLUE_PRIMARY, BLUE_LIGHT, BLUE_DARK, RED_PRIMARY, RED_LIGHT, RED_DARK,
    ORANGE_PRIMARY, ORANGE_LIGHT, ORANGE_DARK, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT
)
from vision.manager import VisionSystem
from core.player import Player
from core.bot import Bot
from ui.manager import GameUI
from core.particles import ParticleSystem
from ui.pixel_sprites import (
    create_floor_tile, get_pixel_font, PIXEL_SCALE,
    CHARACTER_DATA as CD, create_victim_sprite, 
    create_victim_body_sprite, create_iron_cage_sprite
)
from config.iconfig import SOUND_DIR
# Spell data configuration for easy balancing
SPELL_CONFIG = {
    "/":  {"name": "GUN",    "damage": (15, 20), "status": None,    "duration": 0},
    "\\": {"name": "BOMB",   "damage": (12, 16), "status": "burn",  "duration": 240},
    "O":  {"name": "FREEZE", "damage": (1, 4),   "status": "freeze", "duration": 240},
    "|":  {"name": "SHIELD", "damage": (0, 0),   "status": None,    "duration": 0}
}

class MagicGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Magic Fighting Game - Pixel Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.frame_count = 0
        
        # Systems
        self.vision = VisionSystem()
        self.ui = GameUI()
        self.particles = ParticleSystem()
        
        # Game States
        self.STATE_START = "START"
        self.STATE_CHAR_SELECT = "CHAR_SELECT"
        self.STATE_PLAYING = "PLAYING"
        self.STATE_RESCUE = "RESCUE"
        self.STATE_LOST = "LOST"
        self.STATE_GAME_OVER = "GAME_OVER"
        
        self.current_state = self.STATE_START
        self.winner = None
        self.selected_char_idx = 0
        self.frame_count = 0
        
        # Entity placeholders
        self.player = None
        self.bot = None
        self.star_layers = []
        self.tile_w = 0
        self.victim_sprite = None
        self.victim_body_sprite = None
        self.victim_x = 0
        self.victim_y = 0
        self.iron_cage_sprite = None
        self.cage_y = 0
        self.cage_fall_speed = 0
        self.lose_frame = 0
        self.rescue_frame = 0
        self.rescue_arrival_time = 0
        self.floor_tile = None
        self.tile_w = 0
        
        # Polish: Shake, Health Interpolation, Fades, Spell Popup
        self.shake_amount = 0.0
        self.shake_offset = (0, 0)
        self.p_health_disp = 100.0
        self.b_health_disp = 100.0
        self.fade_alpha = 255
        self.fade_target = 0
        self.popup_text = ""
        self.popup_timer = 0
        self.popup_color = (255, 255, 255)
        self._vision_error_logged = False
        
        # Assets and Background
        self.setup_assets()
        self.setup_background()
        
        # UI state
        self.ui.reset_start_animation()
        self.frozen_font = get_pixel_font(22)

    def setup_assets(self):
        # Load sounds
        try:
            music_vol, skill_vol, ui_vol = 0.5, 0.8, 0.7
            
            self.match_end_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "match_end.mp3"))
            self.win_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "win.mp3"))
            self.lose_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "lose.mp3"))
            self.menu_music = pygame.mixer.Sound(os.path.join(SOUND_DIR, "menu_music.mp3"))
            self.gameplay_music = pygame.mixer.Sound(os.path.join(SOUND_DIR, "gameplay_music.mp3"))
            
            for s in [self.match_end_sound, self.win_sound, self.lose_sound]: s.set_volume(skill_vol)
            self.menu_music.set_volume(music_vol)
            self.gameplay_music.set_volume(0.2)

            self.sounds = {
                "gun": pygame.mixer.Sound(os.path.join(SOUND_DIR, "gunshot.mp3")),
                "explosion": pygame.mixer.Sound(os.path.join(SOUND_DIR, "explosion.mp3")),
                "freeze": pygame.mixer.Sound(os.path.join(SOUND_DIR, "freeze.mp3")),
                "shield": pygame.mixer.Sound(os.path.join(SOUND_DIR, "shield.mp3")),
                "ui": pygame.mixer.Sound(os.path.join(SOUND_DIR, "ui_click.mp3"))
            }
            for key, s in self.sounds.items():
                s.set_volume(skill_vol if key != "ui" else ui_vol)

            self.gameplay_music_channel = None
            self.menu_music_channel = None
        except Exception as e:
            print(f"Failed to load sounds: {e}")
            self.match_end_sound = self.win_sound = self.lose_sound = None
            self.menu_music = self.gameplay_music = None
            self.sounds = {}
            self.gameplay_music_channel = self.menu_music_channel = None

    def setup_background(self):
        self.floor_tile = create_floor_tile()
        if self.floor_tile is not None:
            self.tile_w = int(self.floor_tile.get_width())
        else:
            self.tile_w = WIDTH
        
        self.star_layers = []
        layer_config = [
            (80, 0.3, (50, 60, 80)),
            (50, 0.8, (100, 130, 160)),
            (30, 1.5, (200, 220, 255)),
        ]
        
        # Pre-render star layers onto surfaces that are 2x height for seamless scrolling
        for count, speed, base_color in layer_config:
            layer_surf = pygame.Surface((WIDTH, HEIGHT * 2), pygame.SRCALPHA)
            for _ in range(count):
                sx = random.uniform(0, WIDTH)
                sy = random.uniform(0, HEIGHT * 2)
                size = PIXEL_SCALE if speed < 1.0 else PIXEL_SCALE + 1
                # Add some slight variation to the base color
                var = random.randint(-20, 20)
                c = (max(0, min(255, base_color[0] + var)),
                     max(0, min(255, base_color[1] + var)),
                     max(0, min(255, base_color[2] + var)))
                pygame.draw.rect(layer_surf, c, (int(sx), int(sy), size, size))
            
            self.star_layers.append({
                "surf": layer_surf,
                "speed": speed,
                "y": 0.0
            })

    def reset_game(self):
        char_data = CD[self.selected_char_idx]
        
        self.player = Player(WIDTH // 4, HEIGHT // 2)
        self.player.set_character_sprite(char_data["create"]())
        self.player.ui_color = char_data["color"]
        
        self.bot = Bot(WIDTH * 3 // 4, HEIGHT // 2)
        self.bot.set_bot_sprite(char_data["opponent_create"](char_data["opponent_color"]))
        self.bot.ui_color = char_data["opponent_color"]
        
        # Rescue/Lost state entities
        self.victim_sprite = create_victim_sprite(char_data["victim_color"], char_data["victim_gender"])
        self.victim_body_sprite = create_victim_body_sprite(char_data["victim_color"], char_data["victim_gender"])
        self.victim_x, self.victim_y = WIDTH - 80, HEIGHT // 2 - 40
        self.rescue_frame = 0
        self.rescue_arrival_time = 0
        
        self.iron_cage_sprite = create_iron_cage_sprite()
        self.cage_y, self.cage_fall_speed, self.lose_frame = -200, 0, 0
        
        # Reset display health
        self.p_health_disp = self.player.health
        self.b_health_disp = self.bot.health
        
        if self.vision: self.vision.clear_gesture()
        self.current_state = self.STATE_PLAYING
        self.winner = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    if self.sounds.get("ui"): self.sounds["ui"].play(maxtime=500)
                    if self.current_state == self.STATE_START:
                        self.current_state = self.STATE_CHAR_SELECT
                    elif self.current_state in [self.STATE_GAME_OVER, self.STATE_RESCUE, self.STATE_LOST]:
                        self.current_state = self.STATE_START
                        pygame.mixer.stop()
                        self.ui.reset_start_animation()
                elif event.key == pygame.K_r:
                    if self.current_state in [self.STATE_GAME_OVER, self.STATE_RESCUE, self.STATE_LOST]:
                        if self.sounds.get("ui"): self.sounds["ui"].play(maxtime=500)
                        pygame.mixer.stop()
                        self.reset_game()
                
                if self.current_state == self.STATE_CHAR_SELECT:
                    if event.key == pygame.K_LEFT:
                        if self.sounds.get("ui"): self.sounds["ui"].play(maxtime=500)
                        self.selected_char_idx = (self.selected_char_idx - 1) % 5
                    elif event.key == pygame.K_RIGHT:
                        if self.sounds.get("ui"): self.sounds["ui"].play(maxtime=500)
                        self.selected_char_idx = (self.selected_char_idx + 1) % 5
                    elif event.key == pygame.K_RETURN:
                        if self.sounds.get("ui"): self.sounds["ui"].play(maxtime=500)
                        pygame.mixer.stop()
                        self.reset_game()

    def update(self):
        self.frame_count += 1
        
        # Don't exit if vision fails, just log it. Use keyboard as fallback.
        if not hasattr(self, '_vision_error_logged') and not self.vision.running:
            print("Vision system not running. Falling back to keyboard.")
            self._vision_error_logged = True

        # Music management
        self.manage_music()

        if self.current_state == self.STATE_PLAYING:
            gesture = self.vision.get_gesture()
            if gesture:
                self.player.cast_spell(gesture, self.particles, self.sounds)
                self.show_popup(gesture)

            self.player.update(self.particles)
            self.bot.update(self.player, self.particles, self.sounds)
            self.bot.rect.x = max(WIDTH // 2, min(WIDTH - 50, self.bot.rect.x))
            self.particles.update()
            self.check_collisions()
            self.check_win_conditions()
        
        elif self.current_state == self.STATE_LOST:
            self.update_lose_animation()
            
        # UI Polish Updates
        # 1. Smooth Health
        if self.player is not None:
            self.p_health_disp += (self.player.health - self.p_health_disp) * 0.1
        if self.bot is not None:
            self.b_health_disp += (self.bot.health - self.b_health_disp) * 0.1
            
        # 2. Screen Shake
        if self.shake_amount > 0:
            sh = int(self.shake_amount)
            self.shake_offset = (random.randint(-sh, sh), random.randint(-sh, sh))
            self.shake_amount *= 0.9
            if self.shake_amount < 0.5:
                self.shake_amount = 0.0
                self.shake_offset = (0, 0)
        
        # 3. Fade transitions
        if int(self.fade_alpha) != int(self.fade_target):
            diff = self.fade_target - self.fade_alpha
            sign = 1 if diff > 0 else -1
            step = sign * 10 if abs(diff) > 10 else diff
            self.fade_alpha += step
            
        # 4. Popup Timer
        if self.popup_timer > 0:
            self.popup_timer -= 1

    def show_popup(self, gesture):
        names = {"/": "GUN!", "\\": "BOMB!", "O": "FREEZE!", "|": "SHIELD!"}
        colors: dict[str, tuple[int, int, int]] = {
            "/": (255, 255, 100), 
            "\\": (255, 50, 0), 
            "O": (0, 255, 255), 
            "|": (50, 150, 255)
        }
        self.popup_text = names.get(gesture, "MAGIC!")
        self.popup_color = colors.get(gesture, (255, 255, 255))
        self.popup_timer = 90

    def manage_music(self):
        if self.current_state in [self.STATE_START, self.STATE_CHAR_SELECT]:
            if self.menu_music and (self.menu_music_channel is None or not self.menu_music_channel.get_busy()):
                self.menu_music_channel = self.menu_music.play(loops=-1)
        elif self.current_state == self.STATE_PLAYING:
            if self.menu_music_channel:
                self.menu_music_channel.stop()
                self.menu_music_channel = None
            if self.gameplay_music and (self.gameplay_music_channel is None or not self.gameplay_music_channel.get_busy()):
                self.gameplay_music_channel = self.gameplay_music.play(loops=-1)
        else:
            if self.menu_music_channel: self.menu_music_channel.stop(); self.menu_music_channel = None
            if self.gameplay_music_channel: self.gameplay_music_channel.stop(); self.gameplay_music_channel = None

    def check_collisions(self):
        self.check_spells_vs_entity(self.player.spells, self.bot)
        self.check_spells_vs_entity(self.bot.spells, self.player)

    def check_spells_vs_entity(self, spells, target):
        for s in spells:
            if s.active and s.rect.colliderect(target.rect):
                s.active = False
                self.particles.burst(s.rect.centerx, s.rect.centery, s.color, count=15, ptype="spark")
                
                # Shield block logic
                if target.block_timer > 0 and s.type in ["/", "\\", "O"]:
                    if self.sounds.get("shield"): self.sounds["shield"].play(maxtime=800)
                    continue
                
                # Apply data-driven effects
                config = SPELL_CONFIG.get(s.type)
                if config is not None:
                    dmg_range = config["damage"]
                    if isinstance(dmg_range, tuple):
                        d_min, d_max = dmg_range
                        damage = float(random.uniform(float(d_min), float(d_max)))
                    else:
                        damage = 0.0
                    
                    status = config["status"]
                    duration = config["duration"]
                    if status == "burn": target.burn_timer = int(duration)
                    elif status == "freeze": target.freeze_timer = int(duration)
                    
                    target.hurt_timer = 10
                    target.health = max(0.0, target.health - damage)
                    self.shake_amount = float(max(self.shake_amount, damage * 0.5))
                    
                    if s.type in ["/", "\\", "O"] and self.sounds.get("shield"): 
                        self.sounds["shield"].play(maxtime=800)

    def check_win_conditions(self):
        if self.player.health <= 0:
            self.current_state, self.winner, self.lose_frame = self.STATE_LOST, "Bot", 0
            self.cage_y, self.cage_fall_speed = -300, 0
            if self.match_end_sound: self.match_end_sound.play()
            self.clear_entity_effects(self.player)
        elif self.bot.health <= 0:
            self.current_state, self.rescue_frame = self.STATE_RESCUE, 0
            if self.match_end_sound: self.match_end_sound.play()
            self.clear_entity_effects(self.bot)

    def clear_entity_effects(self, entity):
        entity.burn_timer = entity.freeze_timer = entity.block_timer = entity.hurt_timer = 0
        entity.spells.clear()

    def update_rescue_animation(self):
        self.rescue_frame += 1
        target_x = self.victim_x - 40
        if self.player.rect.x < target_x: self.player.rect.x += 3
        else: self.player.rect.x = int(target_x)
        
        if self.rescue_frame > 180:
            self.current_state, self.winner = self.STATE_GAME_OVER, "Player"
            if self.win_sound: self.win_sound.play()

    def update_lose_animation(self):
        self.lose_frame += 1
        if self.iron_cage_sprite is not None and self.player is not None:
            target_cage_y = self.player.rect.bottom - self.iron_cage_sprite.get_height() + 10
            if self.cage_y < target_cage_y:
                self.cage_fall_speed += 1
                self.cage_y += self.cage_fall_speed
                if self.cage_y >= target_cage_y: self.cage_y = target_cage_y
        
        if self.lose_frame > 180:
            self.current_state, self.winner = self.STATE_GAME_OVER, "Bot"
            if self.lose_sound: self.lose_sound.play()

    def draw(self):
        self.draw_background()
        self.draw_vision_feedback()
        
        if self.current_state in [self.STATE_PLAYING, self.STATE_RESCUE, self.STATE_LOST]:
            self.draw_world()
            self.draw_entities()
            self.draw_ui()
        elif self.current_state == self.STATE_START:
            self.ui.draw_start_screen(self.screen)
        elif self.current_state == self.STATE_CHAR_SELECT:
            self.ui.draw_char_select_screen(self.screen, self.selected_char_idx)
        if self.current_state == self.STATE_GAME_OVER:
            self.draw_game_over()
            
        # Spell popup
        if self.popup_timer > 0:
            alpha = min(255, self.popup_timer * 5)
            txt = self.frozen_font.render(self.popup_text, True, self.popup_color)
            txt.set_alpha(alpha)
            self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 100))
            
        # Screen fade overlay
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((WIDTH, HEIGHT))
            fade_surf.set_alpha(self.fade_alpha)
            fade_surf.fill((0, 0, 0))
            self.screen.blit(fade_surf, (0, 0))
            
        pygame.display.flip()

    def draw_vision_feedback(self):
        """Show Vision and Neural feeds in separate OpenCV windows in the main thread."""
        # 1. Main Camera Feed
        if self.vision.current_frame is not None:
            cv2.imshow("Vision - Camera Feed", self.vision.current_frame)
        
        # 2. Neural/AI Preprocessed View
        if hasattr(self.vision, 'debug_roi') and self.vision.debug_roi is not None:
            # Upscale for better visibility in its own window
            neural_view = cv2.resize(self.vision.debug_roi, (280, 280), interpolation=cv2.INTER_NEAREST)
            cv2.imshow("Vision - Neural Hub", neural_view)
        
        # Required for OpenCV windows to update in the main thread
        cv2.waitKey(1)

    def draw_background(self):
        self.screen.fill(BG_COLOR)
        for layer in self.star_layers:
            # Update scroll position
            layer["y"] = (layer["y"] + layer["speed"]) % HEIGHT
            
            # Draw two copies for seamless vertical scrolling
            # Apply 20% shake offset to background layers for parallax depth
            off_x = self.shake_offset[0] * 0.2
            off_y = self.shake_offset[1] * 0.2
            
            # Blit the pre-rendered surface (which is 2x height)
            # We just need to blit the part that's currently visible
            self.screen.blit(layer["surf"], (int(off_x), int(off_y - layer["y"])))

    def draw_world(self):
        if self.floor_tile is None: return
        floor_y = HEIGHT // 2 + 80
        # Floor (scrolling)
        offset = (self.frame_count * 2) % self.tile_w
        for x in range(-self.tile_w, WIDTH + self.tile_w, self.tile_w):
            self.screen.blit(self.floor_tile, (x - offset + self.shake_offset[0], floor_y + self.shake_offset[1]))
        
        # Static floor line - Optimized with single rect instead of loop
        pygame.draw.rect(self.screen, ACCENT_COLOR, (self.shake_offset[0], floor_y + self.shake_offset[1], WIDTH, PIXEL_SCALE))
        
        if self.victim_sprite is not None:
            self.draw_castle(floor_y)

    def draw_castle(self, floor_y):
        castle_w, castle_h = 60, 130
        castle_x, castle_y = int(self.victim_x) - 6, floor_y - castle_h
        pygame.draw.rect(self.screen, (70, 60, 80), (castle_x + self.shake_offset[0], castle_y + self.shake_offset[1], castle_w, castle_h))
        # (Simplified stone texture/battlement drawing)
        win_w, win_h = 28, 30
        win_x, win_y = castle_x + (castle_w - win_w) // 2, castle_y + 14
        pygame.draw.rect(self.screen, (30, 25, 40), (win_x + self.shake_offset[0], win_y + self.shake_offset[1], win_w, win_h))
        vs_scaled = pygame.transform.scale(self.victim_sprite, (win_w - 4, win_h - 6))
        self.screen.blit(vs_scaled, (win_x + 2 + self.shake_offset[0], win_y + 2 + self.shake_offset[1]))

    def draw_entities(self):
        if self.current_state == self.STATE_RESCUE:
            self.draw_rescue_entities()
        elif self.current_state == self.STATE_LOST:
            self.draw_lost_entities()
        else:
            self.draw_gameplay_entities()
        self.particles.draw(self.screen, self.shake_offset)

    def draw_rescue_entities(self):
        if self.rescue_frame < 60 and self.bot is not None:
            dead_bot = pygame.transform.rotate(self.bot.base_sprite, -90)
            dead_bot.set_alpha(max(0, 255 - self.rescue_frame * 5))
            self.screen.blit(dead_bot, (self.bot.rect.x + self.shake_offset[0], HEIGHT // 2 + 80 - dead_bot.get_height() + self.shake_offset[1]))
        
        if self.player is not None:
            ani_offset = (self.rescue_frame // 5) % 2 * 2 if self.player.rect.x < self.victim_x - 45 else 0
            jump_p = int(abs(math.sin(max(0, self.rescue_frame - 40) * 0.2) * 20)) if self.player.rect.x >= self.victim_x - 45 else 0
            self.screen.blit(self.player.base_sprite, (self.player.rect.x + self.shake_offset[0], self.player.rect.y - jump_p - ani_offset + self.shake_offset[1]))

        # Victim
        if self.victim_sprite is not None:
            self.screen.blit(self.victim_sprite, (self.victim_x + self.shake_offset[0], self.victim_y + self.shake_offset[1]))

    def draw_lost_entities(self):
        if self.player is None or self.bot is None: return
        dead_player = pygame.transform.rotate(self.player.base_sprite, 90)
        self.screen.blit(dead_player, (self.player.rect.centerx - dead_player.get_width() // 2 + self.shake_offset[0], HEIGHT // 2 + 80 - dead_player.get_height() + self.shake_offset[1]))
        if self.iron_cage_sprite is not None:
            self.screen.blit(self.iron_cage_sprite, (self.player.rect.centerx - self.iron_cage_sprite.get_width() // 2 + self.shake_offset[0], int(self.cage_y) + self.shake_offset[1]))
        self.screen.blit(self.bot.base_sprite, (self.bot.rect.x + self.shake_offset[0], self.bot.rect.y - int(abs(math.sin(self.lose_frame * 0.2) * 25)) + self.shake_offset[1]))

    def draw_gameplay_entities(self):
        # Draw player and bot with shake
        self.player.draw(self.screen, self.shake_offset)
        self.bot.draw(self.screen, self.shake_offset)
        
        if self.bot.freeze_timer > 0:
            txt = self.frozen_font.render("FROZEN!", True, (230, 160, 40))
            self.screen.blit(txt, (self.bot.rect.centerx - 40 + self.shake_offset[0], self.bot.rect.top - 30 + self.shake_offset[1]))
        if self.player.freeze_timer > 0:
            txt = self.frozen_font.render("FROZEN!", True, (230, 160, 40))
            self.screen.blit(txt, (self.player.rect.centerx - 40 + self.shake_offset[0], self.player.rect.top - 30 + self.shake_offset[1]))

    def draw_ui(self):
        cd = CD[self.selected_char_idx]
        if self.current_state == self.STATE_PLAYING:
            self.ui.draw(self.screen, 
                         self.p_health_disp, self.player.max_health,
                         self.b_health_disp, self.bot.max_health,
                         cd["name"], cd["opponent_name"],
                         self.player.ui_color, self.bot.ui_color)
        elif self.current_state == self.STATE_START:
            self.ui.draw_start_screen(self.screen)
        elif self.current_state == self.STATE_CHAR_SELECT:
            self.ui.draw_char_select_screen(self.screen, self.selected_char_idx)

    def draw_game_over(self):
        char_data = CD[self.selected_char_idx]
        if self.winner == "Player":
            self.ui.draw_game_over_screen(self.screen, self.winner, char_data, self.player.base_sprite, self.victim_body_sprite)
        else:
            self.ui.draw_game_over_screen(self.screen, self.winner, char_data["opponent_name"], self.bot.base_sprite)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        self.vision.stop()
        pygame.quit()
        sys.exit()

def main():
    game = MagicGame()
    game.run()

if __name__ == "__main__":
    main()