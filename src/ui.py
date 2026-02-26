import pygame
from settings import *
from pixel_sprites import get_pixel_font, PIXEL_SCALE, CHARACTER_DATA
import os
import math
import random

class GameUI:
    def __init__(self):
        self.font = get_pixel_font(24)
        self.small_font = get_pixel_font(18)
        self.tiny_font = get_pixel_font(12)
        self.title_font = get_pixel_font(36)
        self.welcome_font = get_pixel_font(32)
        # Load original logo with circular frame
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'images',
                                 'Gemini_Generated_Image_yyuvskyyuvskyyuv.png')
        try:
            raw_logo = pygame.image.load(logo_path).convert_alpha()
            logo_size = 150
            raw_logo = pygame.transform.smoothscale(raw_logo, (logo_size, logo_size))
            # Create circular mask
            self.logo = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
            mask = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (logo_size // 2, logo_size // 2), logo_size // 2)
            raw_logo.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            self.logo.blit(raw_logo, (0, 0))
        except Exception:
            self.logo = None
        
        # Animation state
        self._start_frame = 0
        self._start_active = False

    def reset_start_animation(self):
        """Call when entering start screen to restart animations."""
        self._start_frame = 0
        self._start_active = True

    def draw(self, surface, player, bot, player_name="PLAYER", bot_name="BOT"):
        # Draw Health Bars (pixel segmented style)
        player_color = getattr(player, 'ui_color', BLUE_PRIMARY)
        bot_color = getattr(bot, 'ui_color', RED_PRIMARY)
        
        self._draw_health_bar(surface, 50, 50, player.health, player.max_health, player_name, player_color)
        self._draw_health_bar(surface, WIDTH - 350, 50, bot.health, bot.max_health, bot_name, bot_color)
        
        # Draw Skill Panel (Pixel art bottom bar)
        panel_height = 60
        panel_rect = pygame.Rect(0, HEIGHT - panel_height, WIDTH, panel_height)
        
        # Pixel border bottom tray
        pygame.draw.rect(surface, (10, 10, 20), panel_rect)
        # Top border line (pixel style)
        for x in range(0, WIDTH, PIXEL_SCALE):
            pygame.draw.rect(surface, ACCENT_COLOR, (x, panel_rect.y, PIXEL_SCALE, PIXEL_SCALE))
        
        # Skill labels
        skills = [
            ("1: /", "Gun", (255, 255, 100)), # Neon Yellow
            ("2: \\", "Bomb", (255, 50, 0)), # Neon Red
            ("3: O", "Freeze", (0, 255, 255)), 
            ("4: |", "Shield", BLUE_LIGHT)
        ]
        num_skills = len(skills)
        margin = 8
        total_margin = margin * (num_skills + 1)
        slot_width = (WIDTH - total_margin) // num_skills
        slot_height = 40
        slot_y = panel_rect.y + (panel_height - slot_height) // 2
        for i, (gesture, name, color) in enumerate(skills):
            # Background slot - evenly spaced
            slot_x = margin + i * (slot_width + margin)
            slot = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
            pygame.draw.rect(surface, (30, 30, 45), slot)
            pygame.draw.rect(surface, (60, 60, 80), slot, 1)

            # Render text and center it within the slot
            txt = self.small_font.render(f"{gesture} {name}", True, color)
            tx = slot_x + (slot_width - txt.get_width()) // 2
            ty = slot_y + (slot_height - txt.get_height()) // 2
            surface.blit(txt, (tx, ty))

    def _decode_text(self, surface, text, font, color, cx, cy, progress, f):
        """Render text with decode effect. progress: 0.0 to 1.0 = how many chars are decoded."""
        glyphs = "01@#$%&!?*<>{}[]~^"
        decoded_count = int(progress * len(text))
        
        # Build the displayed string char by char
        result_chars = []
        for i, ch in enumerate(text):
            if ch == ' ':
                result_chars.append(' ')
            elif i < decoded_count:
                result_chars.append(ch)  # Decoded
            else:
                # Scrambled — cycle through random glyphs
                idx = (f * 3 + i * 7) % len(glyphs)
                result_chars.append(glyphs[idx])
        
        displayed = ''.join(result_chars)
        
        # Render char by char with different colors
        total_w = font.size(text)[0]
        start_x = cx - total_w // 2
        x = start_x
        for i, ch in enumerate(displayed):
            if text[i] == ' ':
                x += font.size(' ')[0]
                continue
            if i < decoded_count:
                char_color = color
            else:
                # Glitch color — dimmer, greenish tint
                char_color = (60, 180, 80)
            char_surf = font.render(ch, True, char_color)
            surface.blit(char_surf, (x, cy - char_surf.get_height() // 2))
            x += font.size(text[i])[0]

    def draw_start_screen(self, surface):
        self._rect_overlay(surface)
        
        # ── Logo ──
        if self.logo:
            logo_rect = self.logo.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
            surface.blit(self.logo, logo_rect)
        
        # ── "WELCOME TO" ──
        txt_1 = self.welcome_font.render("WELCOME TO", True, RED_PRIMARY)
        rect_1 = txt_1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 5))
        surface.blit(txt_1, rect_1)
        
        # ── "MAGIC FIGHTING GAME" ──
        txt_2 = self.title_font.render("MAGIC FIGHTING GAME", True, ACCENT_COLOR)
        rect_2 = txt_2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        surface.blit(txt_2, rect_2)
        
        # ── "Press 'S' to Start" ──
        inst = self.font.render("Press 'S' to Start", True, TEXT_COLOR)
        inst_rect = inst.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        surface.blit(inst, inst_rect)
        
        # ── Controls ──
        ctrls = self.small_font.render("Draw spells with hand | Pinch to cast", True, (120, 120, 150))
        ctrls_rect = ctrls.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        surface.blit(ctrls, ctrls_rect)

    def draw_char_select_screen(self, surface, selected_idx):
        """Draw character selection screen."""
        self._rect_overlay(surface)
        
        # Title
        title = self.title_font.render("CHOOSE YOUR HERO", True, ACCENT_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, 60))
        surface.blit(title, title_rect)
        
        num_chars = len(CHARACTER_DATA)
        slot_w = WIDTH // num_chars  # 160px per slot at 800px
        
        for i, char in enumerate(CHARACTER_DATA):
            cx = slot_w * i + slot_w // 2
            cy = HEIGHT // 2 - 20
            
            # Selection highlight
            is_selected = (i == selected_idx)
            if is_selected:
                # Glowing border box
                box_w, box_h = slot_w - 16, 200
                box_rect = pygame.Rect(cx - box_w // 2, cy - 70, box_w, box_h)
                # Pulsing border
                pulse = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.005))
                border_color = (*char["color"][:2], pulse)
                pygame.draw.rect(surface, char["color"], box_rect, 3)
                # Inner glow
                glow = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                glow.fill((*char["color"], 30))
                surface.blit(glow, box_rect)
            
            # Character sprite (scaled up 2x for visibility)
            sprite = char["create"]()
            big_sprite = pygame.transform.scale(sprite, 
                (sprite.get_width() * 2, sprite.get_height() * 2))
            sprite_rect = big_sprite.get_rect(center=(cx, cy))
            surface.blit(big_sprite, sprite_rect)
            
            # Character name
            name_color = char["color"] if is_selected else (150, 150, 170)
            name_txt = self.font.render(char["name"], True, name_color)
            name_rect = name_txt.get_rect(center=(cx, cy + 80))
            surface.blit(name_txt, name_rect)
            
            # Description (only for selected, smaller font)
            if is_selected:
                desc_txt = self.tiny_font.render(char["desc"], True, TEXT_COLOR)
                desc_rect = desc_txt.get_rect(center=(cx, cy + 100))
                surface.blit(desc_txt, desc_rect)
        
        # Instructions
        inst = self.small_font.render("< >  to select  |  ENTER to confirm", True, (120, 120, 150))
        inst_rect = inst.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        surface.blit(inst, inst_rect)

    def draw_game_over_screen(self, surface, winner, char_data=None, char_sprite=None, victim_sprite=None):
        self._rect_overlay(surface)
        
        import math
        t = pygame.time.get_ticks()
        cx = WIDTH // 2   # Center X of screen
        cy = HEIGHT // 2  # Center Y of screen
        
        # ── Layout: evenly spaced vertically from center ──
        # Characters at top, then title, feat line, sub text, restart button
        title_y = cy - 30          # Main title (YOU WIN! / Monster Wins!)
        feat_y = cy + 20           # FEAT: name
        sub_y = cy + 55            # Sub text (SAVED/DARKNESS)
        restart_y = cy + 100       # Press S to Restart
        char_y_base = title_y - 30 # Character bottom = above title
        
        # ── 1) Jumping winner (centered above title) ──
        if char_sprite:
            s_w, s_h = char_sprite.get_size()
            scaled_winner = pygame.transform.scale(char_sprite, (s_w * 2, s_h * 2))
            
            jump = int(abs(math.sin(t * 0.01) * 20))
            winner_x = cx - (s_w * 2) // 2  # Centered horizontal
            winner_y = char_y_base - (s_h * 2) - jump
            surface.blit(scaled_winner, (winner_x, winner_y))
        
        # ── 2) Title text (centered) ──
        if winner == "Player":
            result_text = "YOU WIN!"
            color = (0, 255, 120)
        else:
            result_text = "Monster Wins!"
            color = (255, 50, 50)
        
        res = self.title_font.render(result_text, True, color)
        res_rect = res.get_rect(center=(cx, title_y))
        surface.blit(res, res_rect)
        
        # ── 3) Feat name (centered) ──
        if char_data:
            display_name = char_data['name'] if isinstance(char_data, dict) else str(char_data)
            name_txt = self.welcome_font.render(f"FEAT: {display_name}", True, TEXT_COLOR)
            name_rect = name_txt.get_rect(center=(cx, feat_y))
            surface.blit(name_txt, name_rect)
            
            sub_text = "THE WORLD IS SAVED!" if winner == "Player" else "THE WORLD IS IN DARKNESS!"
            sub_color = (150, 200, 255) if winner == "Player" else (200, 100, 100)
            desc_txt = self.small_font.render(sub_text, True, sub_color)
            desc_rect = desc_txt.get_rect(center=(cx, sub_y))
            surface.blit(desc_txt, desc_rect)
        
        # ── 4) Restart button (centered) ──
        retry = self.font.render("Press 'S' to Restart", True, TEXT_COLOR)
        retry_rect = retry.get_rect(center=(cx, restart_y))
        surface.blit(retry, retry_rect)

    def _rect_overlay(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

    def _draw_health_bar(self, surface, x, y, val, max_val, label, primary_color):
        # Label
        lbl = self.small_font.render(label, True, TEXT_COLOR)
        surface.blit(lbl, (x, y - 22))
        
        # Bar border (pixel style)
        bar_border = pygame.Rect(x - 2, y - 2, HEALTH_BAR_WIDTH + 4, HEALTH_BAR_HEIGHT + 4)
        pygame.draw.rect(surface, (80, 80, 100), bar_border)
        
        # Bar background
        pygame.draw.rect(surface, (30, 30, 45), (x, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
        
        # Bar foreground - segmented pixel blocks
        pct = max(0, min(1.0, val / max_val))
        fill_w = int(pct * HEALTH_BAR_WIDTH)
        
        # Derive dark color
        r, g, b = primary_color
        dark_color = (max(0, r-40), max(0, g-40), max(0, b-40))
        
        segment_w = PIXEL_SCALE * 2
        for sx in range(x, x + fill_w, segment_w):
            w = min(segment_w - 1, x + fill_w - sx)
            if w > 0:
                # Top half lighter
                pygame.draw.rect(surface, primary_color, (sx, y, w, HEALTH_BAR_HEIGHT // 2))
                # Bottom half darker
                pygame.draw.rect(surface, dark_color, (sx, y + HEALTH_BAR_HEIGHT // 2, w, HEALTH_BAR_HEIGHT // 2))

        # Percentage Text
        pct_text = f"{int(pct * 100)}%"
        # Use tiny font or small font? Let's use small_font but centered
        txt_surf = self.tiny_font.render(pct_text, True, (255, 255, 255))
        # Add shadow for visibility on any bar color
        shadow = self.tiny_font.render(pct_text, True, (0, 0, 0))
        
        tx = x + HEALTH_BAR_WIDTH // 2 - txt_surf.get_width() // 2
        ty = y + HEALTH_BAR_HEIGHT // 2 - txt_surf.get_height() // 2
        
        surface.blit(shadow, (tx + 1, ty + 1))
        surface.blit(txt_surf, (tx, ty))
