import pygame

# Window settings
WIDTH = 800
HEIGHT = 600
FPS = 60

# Pixel Art Scale
PIXEL_SCALE = 3

# ── Primary Color Theme (Blue / Red / Orange-Gold) ──
BLUE_PRIMARY    = (25, 55, 120)
BLUE_LIGHT      = (50, 90, 170)
BLUE_DARK       = (15, 30, 70)
RED_PRIMARY     = (210, 40, 35)
RED_LIGHT       = (240, 80, 60)
RED_DARK        = (150, 25, 20)
ORANGE_PRIMARY  = (230, 160, 40)
ORANGE_LIGHT    = (255, 200, 80)
ORANGE_DARK     = (180, 120, 20)

# UI Colors
BG_COLOR = (10, 12, 25)         # Deep dark navy
TEXT_COLOR = (220, 220, 240)
ACCENT_COLOR = ORANGE_PRIMARY    # Orange-gold accent

# Background stars
BG_STAR_COLORS = [
    (40, 50, 100),
    (80, 100, 160),
    (160, 180, 230),
]

# HUD Settings
SKILL_PANEL_WIDTH = 200
SKILL_PANEL_MARGIN = 20
HEALTH_BAR_WIDTH = 300
HEALTH_BAR_HEIGHT = 16

# Player & Bot settings
PLAYER_SPEED = 5
JUMP_FORCE = -15
GRAVITY = 0.8

# Gestures
GESTURE_COOLDOWN = 60
SHAPE_TOLERANCE = 50

# Console Debugging
TURN_PREDICT_CONSOLE = False
