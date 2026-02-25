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

    # Game States
    STATE_START = "START"
    STATE_PLAYING = "PLAYING"
    STATE_GAME_OVER = "GAME_OVER"
    
    current_state = STATE_START
    winner = None

    def reset_game():
        nonlocal player, bot, current_state, winner
        player = Player(WIDTH // 4, HEIGHT // 2)
        bot = Bot(WIDTH * 3 // 4, HEIGHT // 2)
        current_state = STATE_PLAYING
        winner = None

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
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    if current_state in [STATE_START, STATE_GAME_OVER]:
                        reset_game()
                
                # Keyboard Controls Fallback (Only in PLAYING)
                if current_state == STATE_PLAYING:
                    if event.key == pygame.K_1:
                        player.cast_spell("/", particles)
                        print("⌨️  Keyboard Cast: FIRE")
                    elif event.key == pygame.K_2:
                        player.cast_spell("\\", particles)
                        print("⌨️  Keyboard Cast: NORMAL")
                    elif event.key == pygame.K_3:
                        player.cast_spell("|", particles)
                        print("⌨️  Keyboard Cast: BLOCK")
                    elif event.key == pygame.K_4:
                        player.cast_spell("O", particles)
                        print("⌨️  Keyboard Cast: FREEZE")
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP:
                        player.jump()

        # Get inputs from Vision (if available and in PLAYING state)
        if vision:
            if not vision.running:
                running = False
            elif current_state == STATE_PLAYING:
                gesture = vision.get_gesture()
                if gesture:
                    player.cast_spell(gesture, particles)
                    # The print is handled inside vision.py for now, but we can add more logic here

        if current_state == STATE_PLAYING:
            # Continuos Keyboard Movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player.move(-5)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player.move(5)

            # Update
            player.update(particles)
            bot.update(player.rect, particles)
            particles.update()

            # Collision Detection: Player Spells hitting Bot
            for s in player.spells:
                if s.active and s.rect.colliderect(bot.rect):
                    s.active = False
                    damage_multiplier = 0.2 if bot.block_timer > 0 else 1.0
                    bot.hurt_timer = 10 
                    particles.burst(s.rect.centerx, s.rect.centery, s.color, count=20, ptype="spark")
                    
                    if s.type == "/":
                        bot.burn_timer = 240
                        damage = 5 * damage_multiplier
                    elif s.type == "O":
                        bot.freeze_timer = 600 # 10 seconds at 60fps
                        damage = 2 * damage_multiplier
                        print("❄️  BOT FROZEN! (10 seconds)")
                    elif s.type == "|":
                        damage = 0
                    else:
                        damage = 10 * damage_multiplier
                    
                    bot.health = max(0.0, bot.health - damage)

            # Collision Detection: Bot Spells hitting Player
            for s in bot.spells:
                if s.active and s.rect.colliderect(player.rect):
                    s.active = False
                    damage_multiplier = 0.2 if player.block_timer > 0 else 1.0
                    player.hurt_timer = 10 
                    particles.burst(s.rect.centerx, s.rect.centery, s.color, count=15, ptype="spark")
                    
                    if s.type == "/":
                        player.burn_timer = 240
                        damage = 3 * damage_multiplier
                    elif s.type == "O":
                        player.freeze_timer = 60
                        damage = 1 * damage_multiplier
                        print("❄️  PLAYER FROZEN! (1 second)")
                    else:
                        damage = 5 * damage_multiplier
                    
                    player.health = max(0.0, player.health - damage)

        # Draw
        if current_state in [STATE_PLAYING, STATE_GAME_OVER]:
            # Draw floor
            floor_y = HEIGHT // 2 + 80
            pygame.draw.rect(screen, (30, 30, 50), (0, floor_y, WIDTH, 10))
            pygame.draw.line(screen, ACCENT_COLOR, (0, floor_y), (WIDTH, floor_y), 1)
            
            player.draw(screen)
            bot.draw(screen)
            particles.draw(screen)
            
            # Show "FROZEN!" text over characters
            if bot.freeze_timer > 0:
                font = pygame.font.SysFont("Arial", 24, bold=True)
                txt = font.render("FROZEN!", True, (0, 255, 255))
                screen.blit(txt, (bot.rect.centerx - 40, bot.rect.top - 40))
            if player.freeze_timer > 0:
                font = pygame.font.SysFont("Arial", 24, bold=True)
                txt = font.render("FROZEN!", True, (0, 255, 255))
                screen.blit(txt, (player.rect.centerx - 40, player.rect.top - 40))

            ui.draw(screen, player, bot)

        if current_state == STATE_START:
            ui.draw_start_screen(screen)
        elif current_state == STATE_GAME_OVER:
            ui.draw_game_over_screen(screen, winner)

        pygame.display.flip()
        clock.tick(FPS)

        # Check for Game Over
        if current_state == STATE_PLAYING:
            if player.health <= 0:
                current_state = STATE_GAME_OVER
                winner = "Bot"
            elif bot.health <= 0:
                current_state = STATE_GAME_OVER
                winner = "Player"

    if vision:
        vision.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()