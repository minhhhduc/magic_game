import pygame
import sys
import os
import random

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from settings import *
from vision import VisionSystem
from player import Player
from bot import Bot
from ui import GameUI
from particles import ParticleSystem
from pixel_sprites import create_floor_tile, get_pixel_font, PIXEL_SCALE

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Magic Fighting Game - Pixel Edition")
    clock = pygame.time.Clock()

    # Load sounds
    try:
        # Volume balance
        music_vol = 0.5
        skill_vol = 0.8
        ui_vol = 0.7
        
        match_end_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "match_end.mp3"))
        win_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "win.mp3"))
        lose_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "lose.mp3"))
        menu_music = pygame.mixer.Sound(os.path.join("assets", "sound", "menu_music.mp3"))
        gameplay_music = pygame.mixer.Sound(os.path.join("assets", "sound", "gameplay_music.mp3"))
        
        match_end_sound.set_volume(skill_vol)
        win_sound.set_volume(skill_vol)
        lose_sound.set_volume(skill_vol)
        menu_music.set_volume(music_vol)
        gameplay_music.set_volume(0.2) # Keeping music slightly lower than skills

        # Skill sounds - Restored to original files
        gunshot_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "gunshot.mp3"))
        explosion_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "explosion.mp3"))
        freeze_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "freeze.mp3"))
        shield_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "shield.mp3"))
        ui_click_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "ui_click.mp3"))

        gunshot_sound.set_volume(skill_vol)
        explosion_sound.set_volume(skill_vol)
        freeze_sound.set_volume(skill_vol)
        shield_sound.set_volume(skill_vol)
        ui_click_sound.set_volume(ui_vol)

        gameplay_music_channel = None
        menu_music_channel = None
    except Exception as e:
        print(f"Failed to load sounds: {e}")
        match_end_sound = win_sound = lose_sound = None
        menu_music = gameplay_music = None
        gunshot_sound = explosion_sound = freeze_sound = shield_sound = ui_click_sound = None
        gameplay_music_channel = menu_music_channel = None

    # ── Pre-generate pixel background ──
    floor_tile = create_floor_tile()
    tile_w = floor_tile.get_width()
    tile_h = floor_tile.get_height()

    # Generate multi-layer parallax starfield (moving universe)
    import math
    star_layers = []  # 3 layers: far (slow, dim), mid, near (fast, bright)
    layer_config = [
        (80,  0.3, [50, 60, 80]),      # far: 80 stars, speed 0.3, dim
        (50,  0.8, [100, 130, 160]),    # mid: 50 stars, speed 0.8
        (30,  1.5, [200, 220, 255]),    # near: 30 stars, speed 1.5, bright
    ]
    for count, speed, brights in layer_config:
        layer = []
        for _ in range(count):
            sx = random.uniform(0, WIDTH)
            sy = random.uniform(0, HEIGHT)
            bright = random.choice(brights)
            size = PIXEL_SCALE if speed < 1.0 else PIXEL_SCALE + 1
            layer.append([sx, sy, bright, speed, size])
        star_layers.append(layer)

    # Initialize systems
    vision = None
    try:
        vision = VisionSystem()
    except Exception as e:
        print(f"Vision System failed to initialize: {e}")
        print("Falling back to Keyboard Controls: [1: /, 2: \\, 3: ^]")

    # Game States
    STATE_START = "START"
    STATE_CHAR_SELECT = "CHAR_SELECT"
    STATE_PLAYING = "PLAYING"
    STATE_RESCUE = "RESCUE"
    STATE_LOST = "LOST"
    STATE_GAME_OVER = "GAME_OVER"
    
    current_state = STATE_START
    winner = None
    selected_char_idx = 0
    
    # Victim NPC (far right, on a castle)
    victim_sprite = None
    victim_body_sprite = None
    victim_x = WIDTH - 80
    victim_y = HEIGHT // 2 - 40
    
    # Rescue animation
    rescue_frame = 0
    bot_dissolve_alpha = 255
    rescue_arrival_time = 0
    rescue_player_target_x = 0
    
    # Losing animation (Cage)
    iron_cage_sprite = None
    cage_y = -200
    cage_fall_speed = 0
    lose_frame = 0

    def reset_game():
        nonlocal player, bot, current_state, winner
        nonlocal victim_sprite, victim_body_sprite, victim_x, victim_y
        nonlocal rescue_frame, bot_dissolve_alpha
        player = Player(WIDTH // 4, HEIGHT // 2)
        # Create victim NPC on the far right (on castle)
        from pixel_sprites import CHARACTER_DATA as CD, create_victim_sprite, create_victim_body_sprite
        char_data = CD[selected_char_idx]
        player.set_character_sprite(char_data["create"]())
        player.ui_color = char_data["color"]
        
        bot = Bot(WIDTH * 3 // 4, HEIGHT // 2)
        bot.set_bot_sprite(char_data["opponent_create"](char_data["opponent_color"]))
        bot.ui_color = char_data["opponent_color"]
        
        # Create victim NPCs
        victim_sprite = create_victim_sprite(char_data["victim_color"], char_data["victim_gender"])
        victim_body_sprite = create_victim_body_sprite(char_data["victim_color"], char_data["victim_gender"])
        victim_x = WIDTH - 80
        victim_y = HEIGHT // 2 - 40
        rescue_frame = 0
        bot_dissolve_alpha = 255
        nonlocal rescue_arrival_time
        rescue_arrival_time = 0
        nonlocal iron_cage_sprite, cage_y, cage_fall_speed, lose_frame
        from pixel_sprites import create_iron_cage_sprite
        iron_cage_sprite = create_iron_cage_sprite()
        cage_y = -200
        cage_fall_speed = 0
        lose_frame = 0
        if vision:
            vision.clear_gesture()
        current_state = STATE_PLAYING
        winner = None

    player = Player(WIDTH // 4, HEIGHT // 2)
    bot = Bot(WIDTH * 3 // 4, HEIGHT // 2)
    ui = GameUI()
    ui.reset_start_animation()
    particles = ParticleSystem()

    frozen_font = get_pixel_font(22)
    frame_count = 0

    running = True
    while running:
        frame_count += 1

        # ── Draw scrolling starfield background ──
        screen.fill(BG_COLOR)

        for layer in star_layers:
            for star in layer:
                # Move star downward
                star[1] += star[3]
                # Wrap around when off screen
                if star[1] > HEIGHT:
                    star[1] = -PIXEL_SCALE
                    star[0] = random.uniform(0, WIDTH)
                # Twinkle
                twinkle = int(20 * math.sin(frame_count * 0.05 + star[0]))
                b = max(30, min(255, int(star[2]) + twinkle))
                b_blue = min(255, b + 15)
                pygame.draw.rect(screen, (b, b, b_blue),
                               (int(star[0]), int(star[1]), int(star[4]), int(star[4])))
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # Start screen → go to character select
                if event.key == pygame.K_s:
                    if ui_click_sound: ui_click_sound.play(maxtime=500)
                    if current_state == STATE_START:
                        current_state = STATE_CHAR_SELECT
                    elif current_state == STATE_GAME_OVER:
                        current_state = STATE_START
                        pygame.mixer.stop()
                        ui.reset_start_animation() # Reset menu animation if applicable
                
                # Character select controls
                if current_state == STATE_CHAR_SELECT:
                    if event.key == pygame.K_LEFT:
                        if ui_click_sound: ui_click_sound.play(maxtime=500)
                        selected_char_idx = (selected_char_idx - 1) % 5
                    elif event.key == pygame.K_RIGHT:
                        if ui_click_sound: ui_click_sound.play(maxtime=500)
                        selected_char_idx = (selected_char_idx + 1) % 5
                    elif event.key == pygame.K_RETURN:
                        if ui_click_sound: ui_click_sound.play(maxtime=500)
                        pygame.mixer.stop()
                        reset_game()
                
                # Keyboard Controls Fallback (Only in PLAYING)
                if current_state == STATE_PLAYING:
                    skill_sounds = {"gun": gunshot_sound, "explosion": explosion_sound, "freeze": freeze_sound}
                    if event.key == pygame.K_1:
                        player.cast_spell("/", particles, skill_sounds)
                        print("Keyboard Cast: GUN")
                    elif event.key == pygame.K_2:
                        player.cast_spell("\\", particles, skill_sounds)
                        print("Keyboard Cast: BOMB")
                    elif event.key == pygame.K_3:
                        player.cast_spell("|", particles)
                        print("Keyboard Cast: SHIELD")
                    elif event.key == pygame.K_4:
                        player.cast_spell("O", particles, skill_sounds)
                        print("Keyboard Cast: FREEZE")
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP:
                        player.jump()

        # Get inputs from Vision (if available and in PLAYING state)
        if vision:
            if not vision.running:
                running = False
            elif current_state == STATE_PLAYING:
                gesture = vision.get_gesture()
                if gesture:
                    skill_sounds = {"gun": gunshot_sound, "explosion": explosion_sound, "freeze": freeze_sound}
                    player.cast_spell(gesture, particles, skill_sounds)

        if current_state == STATE_PLAYING:
            # Continuous Keyboard Movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player.move(-5)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player.move(5)

            # Update
            player.update(particles)
            skill_sounds = {"gun": gunshot_sound, "explosion": explosion_sound, "freeze": freeze_sound}
            bot.update(player, particles, skill_sounds)
            bot.rect.x = max(WIDTH // 2, min(WIDTH - 50, bot.rect.x)) # Keep bot on right side
            particles.update()

            # Collision Detection: Player Spells hitting Bot
            for s in player.spells:
                if s.active and s.rect.colliderect(bot.rect):
                    s.active = False
                    particles.burst(s.rect.centerx, s.rect.centery, s.color, count=20, ptype="spark")
                    
                    # Block (Skill 4) makes target fully immune to Skills 1/2/3
                    if bot.block_timer > 0 and s.type in ["/", "\\", "O"]:
                        if shield_sound:
                            shield_sound.play(maxtime=800)
                        continue
                    
                    bot.hurt_timer = 10
                    if s.type == "/": # Skill 1: Lightning
                        damage = random.uniform(15, 20)
                    elif s.type == "\\": # Skill 2: Fire (slightly stronger total)
                        bot.burn_timer = 240
                        damage = random.uniform(12, 16)
                    elif s.type == "O": # Skill 3: Freeze
                        bot.freeze_timer = 240 # 4 seconds
                        damage = random.uniform(1, 4)
                    elif s.type == "|":
                        damage = 0
                    else:
                        damage = 0
                    
                    if s.type in ["/", "\\", "O"] and shield_sound:
                        shield_sound.play(maxtime=800)
                    
                    bot.health = max(0.0, bot.health - damage)

            # Collision Detection: Bot Spells hitting Player
            for s in bot.spells:
                if s.active and s.rect.colliderect(player.rect):
                    s.active = False
                    particles.burst(s.rect.centerx, s.rect.centery, s.color, count=15, ptype="spark")
                    
                    # Block (Skill 4) makes target fully immune to Skills 1/2/3
                    if player.block_timer > 0 and s.type in ["/", "\\", "O"]:
                        if shield_sound:
                            shield_sound.play(maxtime=800)
                        continue
                    
                    player.hurt_timer = 10
                    if s.type == "/": # Skill 1: Lightning
                        damage = random.uniform(15, 20)
                    elif s.type == "\\": # Skill 2: Fire (slightly stronger total)
                        player.burn_timer = 240
                        damage = random.uniform(12, 16)
                    elif s.type == "O": # Skill 3: Freeze
                        player.freeze_timer = 240 # 4 seconds
                        damage = random.uniform(1, 4)
                    else:
                        damage = 0
                    
                    if s.type in ["/", "\\", "O"] and shield_sound:
                        shield_sound.play(maxtime=800)
                    
                    player.health = max(0.0, player.health - damage)

        # Draw
        if current_state in [STATE_PLAYING, STATE_RESCUE, STATE_LOST]:
            # Draw pixel floor tiles
            floor_y = HEIGHT // 2 + 80
            for fx in range(0, WIDTH, tile_w):
                screen.blit(floor_tile, (fx, floor_y))
            # Floor accent line
            for fx in range(0, WIDTH, PIXEL_SCALE):
                pygame.draw.rect(screen, ACCENT_COLOR, (fx, floor_y, PIXEL_SCALE, PIXEL_SCALE))
            
            
            # Draw tall castle tower + victim face in top window
            if victim_sprite:
                castle_w, castle_h = 60, 130
                castle_x = int(victim_x) - 6
                castle_y = floor_y - castle_h
                
                # Tower body (dark stone)
                pygame.draw.rect(screen, (70, 60, 80), (castle_x, castle_y, castle_w, castle_h))
                # Stone texture lines
                for sy in range(castle_y + 12, castle_y + castle_h, 16):
                    pygame.draw.line(screen, (60, 50, 70), (castle_x, sy), (castle_x + castle_w, sy), 1)
                    for sx in range(castle_x + (8 if (sy // 16) % 2 == 0 else 0), castle_x + castle_w, 16):
                        pygame.draw.line(screen, (60, 50, 70), (sx, sy), (sx, sy + 16), 1)
                # Battlements on top
                for bx in range(castle_x - 4, castle_x + castle_w + 4, 10):
                    pygame.draw.rect(screen, (80, 70, 95), (bx, castle_y - 10, 7, 10))
                # Top ledge
                pygame.draw.rect(screen, (90, 80, 100), (castle_x - 4, castle_y - 2, castle_w + 8, 4))
                
                # Top window (where victim peeks out)
                win_w, win_h = 28, 30
                win_x = castle_x + (castle_w - win_w) // 2
                win_y = castle_y + 14
                pygame.draw.rect(screen, (30, 25, 40), (win_x, win_y, win_w, win_h))  # dark opening
                pygame.draw.rect(screen, (100, 90, 110), (win_x - 2, win_y - 2, win_w + 4, win_h + 4), 2)  # frame
                # Window sill
                pygame.draw.rect(screen, (100, 90, 110), (win_x - 3, win_y + win_h - 2, win_w + 6, 4))
                
                # Victim face inside the window (scaled to fit) - always visible
                vs_scaled = pygame.transform.scale(victim_sprite,
                    (win_w - 4, win_h - 6))
                screen.blit(vs_scaled, (win_x + 2, win_y + 2))
                
                # Bottom window (decorative, empty)
                bwin_y = castle_y + 70
                pygame.draw.rect(screen, (30, 25, 40), (win_x, bwin_y, win_w, 22))
                pygame.draw.rect(screen, (100, 90, 110), (win_x - 2, bwin_y - 2, win_w + 4, 26), 2)
                # Door at bottom
                door_w, door_h = 20, 28
                door_x = castle_x + (castle_w - door_w) // 2
                door_y = castle_y + castle_h - door_h
                pygame.draw.rect(screen, (50, 35, 25), (door_x, door_y, door_w, door_h))
                pygame.draw.rect(screen, (80, 70, 60), (door_x, door_y, door_w, door_h), 2)
                # Door handle
                pygame.draw.circle(screen, (180, 160, 60), (door_x + door_w - 5, door_y + door_h // 2), 2)
            
            # During RESCUE: bot lies down dead, player walks to castle, victim emerges, celebration
            if current_state == STATE_RESCUE:
                rescue_frame += 1
                
                # Draw bot lying down (rotated 90°) on the ground
                if rescue_frame < 60:
                    bot_dead_sprite = pygame.transform.rotate(bot.base_sprite, -90)
                    bot_dead_x = bot.rect.x
                    bot_dead_y = floor_y - bot_dead_sprite.get_height()
                    bot_dead_sprite.set_alpha(max(0, 255 - rescue_frame * 5))
                    screen.blit(bot_dead_sprite, (bot_dead_x, bot_dead_y))
                
                # Phase 1: Player walks RIGHT to castle (target is in front of door)
                # Door location is roughly at victim_x
                target_x = victim_x - 40
                if player.rect.x < target_x:
                    player.rect.x += 3
                    ani_offset_p = (rescue_frame // 5) % 2 * 2 # Slight bobbing while walking
                else:
                    player.rect.x = int(target_x)
                    ani_offset_p = 0
                
                # Phase 2: Victim emerges from castle and both celebrate
                # Appear when player is very close to door
                if player.rect.x >= target_x - 5:
                    # Draw victim body sprite standing next to player (to the right)
                    # player width is ~48px, so place victim at +50 for a nice gap
                    vx = player.rect.x + 50
                    vy = floor_y - 66 
                    
                    if rescue_frame > rescue_arrival_time + 10:
                        # Player jump animation
                        jump_p = int(abs(math.sin((rescue_frame - rescue_arrival_time) * 0.2) * 20))
                    
                    # Draw player with jump and walk bob (ani_offset_p is 0 when standing)
                    player_copy = player.base_sprite.copy()
                    screen.blit(player_copy, (player.rect.x, player.rect.y - jump_p - ani_offset_p))
                else:
                    # Draw player with walk bob
                    player_copy = player.base_sprite.copy()
                    screen.blit(player_copy, (player.rect.x, player.rect.y - ani_offset_p))
                
                particles.draw(screen)
                
                # Finish after long enough celebration
                if rescue_frame > 180:
                    current_state = STATE_GAME_OVER
                    winner = "Player"
                    if win_sound:
                        win_sound.play()
            
            elif current_state == STATE_LOST:
                lose_frame += 1
                
                # Phase 1: Cage falls from the sky
                if iron_cage_sprite is None:
                    from pixel_sprites import create_iron_cage_sprite
                    iron_cage_sprite = create_iron_cage_sprite()
                
                target_cage_y = player.rect.bottom - iron_cage_sprite.get_height() + 10
                if cage_y < target_cage_y:
                    cage_fall_speed += 1
                    cage_y += cage_fall_speed
                    if cage_y >= target_cage_y:
                        cage_y = target_cage_y
                        # Slight screen shake or particles could go here
                
                # Phase 2: Bot jumps for joy after cage lands
                jump_bot = 0
                if cage_y >= target_cage_y:
                    jump_bot = int(abs(math.sin(lose_frame * 0.2) * 25))
                
                # Draw player lying down (rotated 90°) behind cage
                player_dead_sprite = pygame.transform.rotate(player.base_sprite, 90)
                player_dead_x = player.rect.centerx - player_dead_sprite.get_width() // 2
                player_dead_y = floor_y - player_dead_sprite.get_height()
                screen.blit(player_dead_sprite, (player_dead_x, player_dead_y))
                
                # Draw cage
                if iron_cage_sprite:
                    screen.blit(iron_cage_sprite, (player.rect.centerx - iron_cage_sprite.get_width() // 2, cage_y))
                
                # Draw bot with jump
                bot_copy = bot.base_sprite.copy()
                screen.blit(bot_copy, (bot.rect.x, bot.rect.y - jump_bot))
                
                particles.draw(screen)
                
                # Finish after celebration
                if lose_frame > 180:
                    current_state = STATE_GAME_OVER
                    winner = "Bot"
                    if lose_sound:
                        lose_sound.play()
            
            else:
                player.draw(screen)
                bot.draw(screen)
                particles.draw(screen)
                
                # Show "FROZEN!" text over characters (pixel font)
                if bot.freeze_timer > 0:
                    txt = frozen_font.render("FROZEN!", True, (230, 160, 40))
                    screen.blit(txt, (bot.rect.centerx - 40, bot.rect.top - 30))
                if player.freeze_timer > 0:
                    txt = frozen_font.render("FROZEN!", True, (230, 160, 40))
                    screen.blit(txt, (player.rect.centerx - 40, player.rect.top - 30))

            from pixel_sprites import CHARACTER_DATA as CD_UI
            cd = CD_UI[selected_char_idx]
            ui.draw(screen, player, bot, cd["name"], cd["opponent_name"])

        # Handle Background Music (Start/CharSelect)
        if current_state in [STATE_START, STATE_CHAR_SELECT]:
            if menu_music and (menu_music_channel is None or not menu_music_channel.get_busy()):
                try:
                    menu_music_channel = menu_music.play(loops=-1)
                except:
                    menu_music_channel = None
        elif current_state == STATE_PLAYING:
            if menu_music_channel:
                try:
                    menu_music_channel.stop()
                except:
                    pass
                menu_music_channel = None
            
            # Handle gameplay music loop seamlessly
            if gameplay_music and (gameplay_music_channel is None or not gameplay_music_channel.get_busy()):
                try:
                    gameplay_music_channel = gameplay_music.play(loops=-1)
                except:
                    gameplay_music_channel = None
        else:
            if menu_music_channel:
                try:
                    if menu_music_channel.get_busy():
                        menu_music_channel.stop()
                except:
                    pass
                menu_music_channel = None
            if gameplay_music_channel:
                try:
                    if gameplay_music_channel.get_busy():
                        gameplay_music_channel.stop()
                except:
                    pass
                gameplay_music_channel = None

        if current_state == STATE_START:
            ui.draw_start_screen(screen)
        elif current_state == STATE_CHAR_SELECT:
            ui.draw_char_select_screen(screen, selected_char_idx)
        elif current_state == STATE_GAME_OVER:
            from pixel_sprites import CHARACTER_DATA as CD
            char_data = CD[selected_char_idx]
            if winner == "Player":
                ui.draw_game_over_screen(screen, winner, char_data, player.base_sprite, victim_body_sprite)
            else:
                ui.draw_game_over_screen(screen, winner, char_data["opponent_name"], bot.base_sprite)

        pygame.display.flip()
        clock.tick(FPS)

        # Check for Game Over / Rescue
        if current_state == STATE_PLAYING:
            if player.health <= 0:
                current_state = STATE_LOST
                winner = "Bot"
                lose_frame = 0
                cage_y = -300
                cage_fall_speed = 0
                if match_end_sound:
                    match_end_sound.play()
                # Clear all player effects
                player.burn_timer = 0
                player.freeze_timer = 0
                player.block_timer = 0
                player.hurt_timer = 0
                player.spells.clear()
            elif bot.health <= 0:
                current_state = STATE_RESCUE
                rescue_frame = 0
                if match_end_sound:
                    match_end_sound.play()
                # Clear all bot effects
                bot.burn_timer = 0
                bot.freeze_timer = 0
                bot.block_timer = 0
                bot.hurt_timer = 0
                bot.spells.clear()

    if vision:
        vision.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()