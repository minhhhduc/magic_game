import pygame
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from settings import *
from vision import VisionSystem
from player import Player
from bot import Bot
from ui import GameUI
from particles import ParticleSystem

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Magic Fighting Game - Vision Edition")
    clock = pygame.time.Clock()

    # Initialize systems
    vision = None
    try:
        vision = VisionSystem()
    except Exception as e:
        print(f"Vision System failed to initialize: {e}")
        print("Falling back to Keyboard Controls: [1: /, 2: \\, 3: ^]")

    player = Player(WIDTH // 4, HEIGHT // 2)
    bot = Bot(WIDTH * 3 // 4, HEIGHT // 2)
    ui = GameUI()
    particles = ParticleSystem()

    running = True
    while running:
        screen.fill(BG_COLOR)
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Keyboard Controls Fallback
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.cast_spell("/")
                elif event.key == pygame.K_2:
                    player.cast_spell("\\")
                elif event.key == pygame.K_3:
                    player.cast_spell("^")

        # Get inputs from Vision (if available)
        if vision:
            gesture = vision.get_gesture()
            if gesture:
                player.cast_spell(gesture)

        # Update
        player.update()
        bot.update(player.rect)
        particles.update()

        # Collision Detection: Player Spells hitting Bot
        for s in player.spells:
            if s.active and s.rect.colliderect(bot.rect):
                s.active = False
                bot.health = max(0, bot.health - 10)
                particles.emit(s.rect.centerx, s.rect.centery, s.color, 20)
                print(f"Bot hit! Health: {bot.health}")

        # Collision Detection: Bot Spells hitting Player
        for s in bot.spells:
            if s.active and s.rect.colliderect(player.rect):
                s.active = False
                player.health = max(0, player.health - 5)
                particles.emit(s.rect.centerx, s.rect.centery, s.color, 20)
                print(f"Player hit! Health: {player.health}")

        # Draw
        # Draw floor (Centered vertically)
        floor_y = HEIGHT // 2 + 80
        pygame.draw.rect(screen, (30, 30, 50), (0, floor_y, WIDTH, 10))
        # Add a subtle platform glow
        pygame.draw.line(screen, ACCENT_COLOR, (0, floor_y), (WIDTH, floor_y), 1)
        
        player.draw(screen)
        bot.draw(screen)
        particles.draw(screen)
        ui.draw(screen, player, bot)

        pygame.display.flip()
        clock.tick(FPS)

        if player.health <= 0 or bot.health <= 0:
            print("Game Over!")
            # Add small delay before closing or resetting
            pygame.time.delay(2000)
            running = False

    if vision:
        vision.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()