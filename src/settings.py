import pygame

# Window settings
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors (RGB)
BG_COLOR = (15, 15, 25)  # Dark blue-black
TEXT_COLOR = (200, 200, 255)
ACCENT_COLOR = (0, 255, 150)  # Neon green

# HUD Settings
SKILL_PANEL_WIDTH = 200
SKILL_PANEL_MARGIN = 20
HEALTH_BAR_WIDTH = 300
HEALTH_BAR_HEIGHT = 20

# Player & Bot settings
PLAYER_SPEED = 5
JUMP_FORCE = -15
GRAVITY = 0.8

# Gestures
GESTURE_COOLDOWN = 60  # Frames
SHAPE_TOLERANCE = 50   # Sensitivity for gesture matching
