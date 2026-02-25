import pygame
from settings import *

class GameUI:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 18)
        
    def draw(self, surface, player, bot):
        # Draw Health Bars
        self._draw_health_bar(surface, 50, 50, player.health, player.max_health, "Player")
        self._draw_health_bar(surface, WIDTH - 350, 50, bot.health, bot.max_health, "Bot")
        
        # Draw Skill Panel (Moved to Bottom)
        panel_height = 60
        panel_rect = pygame.Rect(0, HEIGHT - panel_height, WIDTH, panel_height)
        
        # Bottom tray effect
        s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 180), s.get_rect())
        surface.blit(s, panel_rect.topleft)
        pygame.draw.line(surface, ACCENT_COLOR, (0, panel_rect.y), (WIDTH, panel_rect.y), 2)
        
        # Skill targets
        skills = [
            ("1: \\", "Normal"), 
            ("2: /", "Fire"), 
            ("3: |", "Block"), 
            ("4: O", "Freeze")
        ]
        for i, (gesture, name) in enumerate(skills):
            x_pos = 100 + (i * 200)
            txt = self.font.render(f"{gesture} : {name}", True, TEXT_COLOR)
            surface.blit(txt, (x_pos, panel_rect.y + 15))

    def draw_start_screen(self, surface):
        self._rect_overlay(surface)
        
        # Title
        title = self.font.render("MAGIC FIGHTING GAME", True, ACCENT_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        surface.blit(title, title_rect)
        
        # Instruction
        inst = self.font.render("Press 'S' to Start", True, TEXT_COLOR)
        inst_rect = inst.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        surface.blit(inst, inst_rect)
        
        # Controls info
        ctrls = self.small_font.render("Draw spells with Index Finger | Pinch Index+Middle to cast", True, (150, 150, 150))
        ctrls_rect = ctrls.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        surface.blit(ctrls, ctrls_rect)

    def draw_game_over_screen(self, surface, winner):
        self._rect_overlay(surface)
        
        # Result text
        result_text = "YOU WIN!" if winner == "Player" else "GAME OVER - BOT WINS"
        color = (0, 255, 120) if winner == "Player" else (255, 50, 50)
        
        res = self.font.render(result_text, True, color)
        res_rect = res.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        surface.blit(res, res_rect)
        
        retry = self.small_font.render("Press 'S' to Restart", True, TEXT_COLOR)
        retry_rect = retry.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        surface.blit(retry, retry_rect)

    def _rect_overlay(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), (0, 0, WIDTH, HEIGHT))
        surface.blit(overlay, (0, 0))

    def _draw_health_bar(self, surface, x, y, val, max_val, label):
        # Label
        lbl = self.small_font.render(label, True, TEXT_COLOR)
        surface.blit(lbl, (x, y - 25))
        
        # Bar background
        pygame.draw.rect(surface, (50, 50, 70), (x, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), border_radius=5)
        # Bar foreground (gradient-like)
        fill_w = int((val / max_val) * HEALTH_BAR_WIDTH)
        color = (0, 255, 100) if label == "Player" else (255, 50, 80)
        pygame.draw.rect(surface, color, (x, y, fill_w, HEALTH_BAR_HEIGHT), border_radius=5)
