"""
Pixel Art Sprite Generator for Magic Fighting Game.
All sprites are generated programmatically from small pixel grids,
then scaled up for a crisp retro look.
"""
import pygame

# ── Scale ──
PIXEL_SCALE = 3  # Each "pixel" in the grid becomes 3x3 on screen

# ── Palette ──
T = None  # Transparent

# Player (Wizard) palette — Blue theme
P_ROBE     = (25, 55, 120)
P_ROBE_LT  = (50, 90, 170)
P_ROBE_DK  = (15, 30, 70)
P_SKIN     = (240, 200, 160)
P_EYE      = (230, 160, 40)    # Orange-gold eyes
P_HAT      = (20, 40, 90)
P_HAT_STAR = (230, 160, 40)    # Orange-gold star
P_STAFF    = (160, 120, 60)
P_STAFF_GEM = (230, 160, 40)   # Orange-gold gem

# Bot (Dark Knight) palette — Red theme
B_ARMOR    = (150, 25, 20)
B_ARMOR_LT = (210, 40, 35)
B_ARMOR_DK = (90, 15, 10)
B_EYE      = (230, 160, 40)    # Orange-gold eyes
B_HORN     = (60, 60, 60)
B_VISOR    = (30, 20, 20)

# Spell palettes
FIRE_CORE   = (255, 255, 100)
FIRE_MID    = (255, 150, 0)
FIRE_EDGE   = (255, 50, 0)
ICE_CORE    = (255, 255, 255)
ICE_MID     = (150, 230, 255)
ICE_EDGE    = (0, 200, 255)
NORM_CORE   = (255, 255, 255)
NORM_MID    = (220, 220, 240)
NORM_EDGE   = (180, 180, 200)
BLOCK_CORE  = (200, 230, 255)
BLOCK_MID   = (80, 150, 255)
BLOCK_EDGE  = (40, 100, 220)


def _grid_to_surface(grid, scale=PIXEL_SCALE):
    """Convert a 2D list of (R,G,B)|None to a scaled pygame.Surface."""
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0
    surf = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            if color is not None:
                pygame.draw.rect(surf, color, (x * scale, y * scale, scale, scale))
    return surf


def _grid_to_surface_alpha(grid, scale=PIXEL_SCALE):
    """Convert a 2D list of (R,G,B,A)|None to a scaled pygame.Surface with alpha."""
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0
    surf = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            if color is not None:
                pygame.draw.rect(surf, color, (x * scale, y * scale, scale, scale))
    return surf


# ═══════════════════════════════════════════
#  PLAYER WIZARD SPRITE (16 wide x 22 tall)
# ═══════════════════════════════════════════
def create_player_sprite():
    _ = T
    S = P_SKIN
    R = P_ROBE
    L = P_ROBE_LT
    D = P_ROBE_DK
    H = P_HAT
    E = P_EYE
    W = P_HAT_STAR
    St = P_STAFF
    G = P_STAFF_GEM

    grid = [
        # Row 0-2: Hat tip
        [_,_,_,_,_,_,_, H,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_, H, H, H,_,_,_,_,_,_,_],
        [_,_,_,_,_, H, H, W, H, H,_,_,_,_,_,_],
        # Row 3-4: Hat brim
        [_,_,_,_, H, H, H, H, H, H, H,_,_,_,_,_],
        [_,_,_, H, H, H, H, H, H, H, H, H,_,_,_,_],
        # Row 5-6: Face
        [_,_,_,_, S, S, S, S, S, S, S,_,_,_,_,_],
        [_,_,_,_, S, E, S, S, S, E, S,_,_,_,_,_],
        # Row 7: Mouth
        [_,_,_,_,_, S, S, S, S, S,_,_,_,_,_,_],
        # Row 8-14: Robe body
        [_,_,_,_, R, R, L, R, L, R, R,_,_,_,_,_],
        [_,_,_, R, R, R, L, R, L, R, R, R,_,_,_,_],
        [_,_,_, R, R, R, R, R, R, R, R, R,_,_,_,_],
        [_,_, D, R, R, R, L, R, L, R, R, R, D,_,_,_],
        [_,_, D, R, R, R, R, R, R, R, R, R, D,_,_,_],
        [_,_, D, R, R, R, L, R, L, R, R, R, D,_,_,_],
        [_,_,_, D, R, R, R, R, R, R, R, D,_,_,_,_],
        # Row 15-17: Robe bottom (flared)
        [_,_, D, D, R, R, R, R, R, R, R, D, D,_,_,_],
        [_,_, D, R, R, R, R, R, R, R, R, R, D,_,_,_],
        [_,_, D, R, R, R, R, R, R, R, R, R, D,_,_,_],
        # Row 18-19: Feet
        [_,_,_, D, D, R, R,_,_, R, R, D, D,_,_,_],
        [_,_,_, D, D, D,_,_,_,_, D, D, D,_,_,_],
        # Row 20-21: Staff (beside body)
        [St,St,_,_,_,_,_,_,_,_,_,_,_,_,St,St],
        [ G, G,_,_,_,_,_,_,_,_,_,_,_,_, G, G],
    ]
    return _grid_to_surface(grid)


# ═══════════════════════════════════════════
#  BOT (DARK KNIGHT) SPRITE (16 wide x 22 tall)
# ═══════════════════════════════════════════
def create_bot_sprite():
    _ = T
    A = B_ARMOR
    L = B_ARMOR_LT
    D = B_ARMOR_DK
    E = B_EYE
    H = B_HORN
    V = B_VISOR

    grid = [
        # Row 0-1: Horns
        [_,_, H,_,_,_,_,_,_,_,_,_,_, H,_,_],
        [_,_, H, H,_,_,_,_,_,_,_,_, H, H,_,_],
        # Row 2-4: Helmet
        [_,_,_, H, A, A, A, A, A, A, A, A, H,_,_,_],
        [_,_,_, A, A, A, A, A, A, A, A, A, A,_,_,_],
        [_,_,_, V, V, E, V, V, V, E, V, V, V,_,_,_],
        # Row 5: Jaw
        [_,_,_,_, V, V, A, A, A, V, V,_,_,_,_,_],
        # Row 6-7: Neck / pauldrons
        [_,_, L, L, A, A, A, A, A, A, A, L, L,_,_,_],
        [_, L, L, A, A, A, A, A, A, A, A, A, L, L,_,_],
        # Row 8-14: Body armor
        [_,_, D, A, A, L, A, A, A, L, A, A, D,_,_,_],
        [_,_, D, A, A, A, L, A, L, A, A, A, D,_,_,_],
        [_,_, D, A, A, A, A, L, A, A, A, A, D,_,_,_],
        [_,_, D, A, A, A, L, A, L, A, A, A, D,_,_,_],
        [_,_, D, A, A, L, A, A, A, L, A, A, D,_,_,_],
        [_,_,_, D, A, A, A, A, A, A, A, D,_,_,_,_],
        # Row 15-17: Legs
        [_,_,_, D, A, A, A, A, A, A, A, D,_,_,_,_],
        [_,_,_, D, A, A, D,_,_, D, A, A, D,_,_,_],
        [_,_,_, D, A, D,_,_,_,_, D, A, D,_,_,_],
        # Row 18-19: Boots
        [_,_, D, D, A, D,_,_,_,_, D, A, D, D,_,_],
        [_,_, D, D, D, D,_,_,_,_, D, D, D, D,_,_],
        # Row 20-21: padding
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    ]
    return _grid_to_surface(grid)


# ═══════════════════════════════════════════
#  SPELL PROJECTILE SPRITES (10 wide x 8 tall)
# ═══════════════════════════════════════════
def create_bullet_spell():
    """A sharp, high-velocity projectile (Neon Yellow/White)."""
    _ = T
    C = (255, 255, 200) # Glaring White Core
    M = (255, 255, 50)  # Glaring Yellow
    E = (200, 200, 0)   # Yellow Edge
    # 8x4 small bullet shape
    grid = [
        [_, _, E, E, E, E, _, _],
        [E, E, M, M, M, M, E, E],
        [E, E, C, C, C, C, E, E],
        [_, _, E, E, E, E, _, _],
    ]
    return _grid_to_surface(grid)


def create_bomb_spell():
    """A circular bomb with a lit fuse (Neon Red/Orange)."""
    _ = T
    C = (255, 200, 100) # Bright Glow
    M = (255, 50, 0)   # Neon Orange-Red
    E = (50, 50, 50)    # Dark Bomb casing
    F = (255, 255, 0)   # Yellow fuse spark
    grid = [
        [_, _, _, _, F, _, _, _, _, _],
        [_, _, _, _, E, _, _, _, _, _],
        [_, _, E, E, E, E, E, _, _, _],
        [_, E, M, M, C, M, M, E, _, _],
        [E, M, C, C, C, C, C, M, E, _],
        [E, M, C, C, C, C, C, M, E, _],
        [_, E, M, C, C, C, M, E, _, _],
        [_, _, E, E, E, E, E, _, _, _],
    ]
    return _grid_to_surface(grid)


def create_ice_spell():
    _ = T
    C = ICE_CORE
    M = ICE_MID
    E = ICE_EDGE
    grid = [
        [_,_,_, E,_, E,_,_,_,_],
        [_,_, E, C, E, M, E,_,_,_],
        [_, E, M, C, C, C, M, E,_,_],
        [ E, M, C, C, C, C, C, M, E,_],
        [_, E, M, C, C, C, M, E,_,_],
        [_,_, E, M, C, M, E,_,_,_],
        [_,_,_, E, M, E,_,_,_,_],
        [_,_,_,_, E,_,_,_,_,_],
    ]
    return _grid_to_surface(grid)


def create_normal_spell():
    """Red/Orange circular fireball."""
    _ = T
    C = FIRE_CORE # Changed to fire colors
    M = FIRE_MID
    E = FIRE_EDGE
    grid = [
        [_,_,_,_, E,_,_,_,_,_],
        [_,_,_, E, M, E,_,_,_,_],
        [_,_, E, M, C, M, E,_,_,_],
        [_, E, M, C, C, C, M, E,_,_],
        [_, E, M, C, C, C, M, E,_,_],
        [_,_, E, M, C, M, E,_,_,_],
        [_,_,_, E, M, E,_,_,_,_],
        [_,_,_,_, E,_,_,_,_,_],
    ]
    return _grid_to_surface(grid)


def create_block_spell():
    _ = T
    C = BLOCK_CORE
    M = BLOCK_MID
    E = BLOCK_EDGE
    grid = [
        [_,_, E, E, E, E, E, E,_,_],
        [_, E, M, M, M, M, M, M, E,_],
        [ E, M, M, C, C, C, C, M, M, E],
        [ E, M, C, C, C, C, C, C, M, E],
        [ E, M, C, C, C, C, C, C, M, E],
        [ E, M, M, C, C, C, C, M, M, E],
        [_, E, M, M, M, M, M, M, E,_],
        [_,_, E, E, E, E, E, E,_,_],
    ]
    return _grid_to_surface(grid)


# ═══════════════════════════════════════════
#  ICE OVERLAY (for frozen state)
# ═══════════════════════════════════════════
def create_ice_overlay(width, height):
    """Pixel art ice overlay with transparency."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    # Fill with semi-transparent ice
    for y in range(0, height, PIXEL_SCALE):
        for x in range(0, width, PIXEL_SCALE):
            # Checkerboard pattern for crystalline look
            if (x // PIXEL_SCALE + y // PIXEL_SCALE) % 3 == 0:
                pygame.draw.rect(surf, (200, 255, 255, 100), (x, y, PIXEL_SCALE, PIXEL_SCALE))
            elif (x // PIXEL_SCALE + y // PIXEL_SCALE) % 3 == 1:
                pygame.draw.rect(surf, (150, 230, 255, 80), (x, y, PIXEL_SCALE, PIXEL_SCALE))
            else:
                pygame.draw.rect(surf, (180, 240, 255, 60), (x, y, PIXEL_SCALE, PIXEL_SCALE))
    # Diagonal cracks
    for i in range(0, max(width, height), PIXEL_SCALE * 2):
        if i < width and i < height:
            pygame.draw.rect(surf, (255, 255, 255, 150), (i, i, PIXEL_SCALE, PIXEL_SCALE))
    return surf


# ═══════════════════════════════════════════
#  SHIELD OVERLAY (for block state)
# ═══════════════════════════════════════════
def create_shield_overlay(width, height):
    """Pixel art shield border."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    c = (80, 160, 255, 160)
    ps = PIXEL_SCALE
    # Top and bottom borders
    for x in range(0, width, ps):
        pygame.draw.rect(surf, c, (x, 0, ps, ps))
        pygame.draw.rect(surf, c, (x, height - ps, ps, ps))
    # Left and right borders
    for y in range(0, height, ps):
        pygame.draw.rect(surf, c, (0, y, ps, ps))
        pygame.draw.rect(surf, c, (width - ps, y, ps, ps))
    return surf


# ═══════════════════════════════════════════
#  TINT HELPERS
# ═══════════════════════════════════════════
def tint_surface(surface, color):
    """Return a copy of surface tinted with the given color."""
    tinted = surface.copy()
    tint_surf = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
    tint_surf.fill((*color, 0))
    # Use BLEND_RGB_ADD for brightening or BLEND_RGB_MULT for tinting
    tinted.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    return tinted


def create_tinted_variant(base_surface, color, intensity=80):
    """Create a tinted version by blending color over the original."""
    result = base_surface.copy()
    overlay = pygame.Surface(result.get_size(), pygame.SRCALPHA)
    overlay.fill((*color, intensity))
    result.blit(overlay, (0, 0))
    return result


def create_white_flash(surface):
    """Create a white-flash version of a sprite."""
    w, h = surface.get_size()
    flash = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            r, g, b, a = surface.get_at((x, y))
            if a > 0:
                flash.set_at((x, y), (255, 255, 255, a))
    return flash


# ═══════════════════════════════════════════
#  FLOOR TILE (16x16 pixel grid)
# ═══════════════════════════════════════════
def create_floor_tile():
    _ = T
    D = (25, 25, 40)
    L = (35, 35, 55)
    A = (20, 20, 35)
    grid = [
        [ L, L, L, L, L, L, L, L, D, D, D, D, D, D, D, D],
        [ L, L, L, L, L, L, L, L, D, D, D, D, D, D, D, D],
        [ L, L, L, L, L, L, L, L, D, D, D, D, D, D, D, D],
        [ L, L, L, L, L, L, L, L, D, D, D, D, D, D, D, D],
        [ L, L, L, L, L, L, L, L, D, D, D, D, D, D, D, D],
        [ L, L, L, L, L, L, L, L, D, D, D, D, D, D, D, D],
        [ L, L, L, L, L, L, L, L, D, D, D, D, D, D, D, D],
        [ A, A, A, A, A, A, A, A, A, A, A, A, A, A, A, A],
        [ D, D, D, D, D, D, D, D, L, L, L, L, L, L, L, L],
        [ D, D, D, D, D, D, D, D, L, L, L, L, L, L, L, L],
        [ D, D, D, D, D, D, D, D, L, L, L, L, L, L, L, L],
        [ D, D, D, D, D, D, D, D, L, L, L, L, L, L, L, L],
        [ D, D, D, D, D, D, D, D, L, L, L, L, L, L, L, L],
        [ D, D, D, D, D, D, D, D, L, L, L, L, L, L, L, L],
        [ D, D, D, D, D, D, D, D, L, L, L, L, L, L, L, L],
        [ A, A, A, A, A, A, A, A, A, A, A, A, A, A, A, A],
    ]
    return _grid_to_surface(grid)


# ═══════════════════════════════════════════
#  STAR BACKGROUND PIXEL
# ═══════════════════════════════════════════
def create_pixel_star(brightness=255):
    s = pygame.Surface((PIXEL_SCALE, PIXEL_SCALE), pygame.SRCALPHA)
    s.fill((brightness, brightness, brightness))
    return s


# ═══════════════════════════════════════════
#  PIXEL FONT HELPER
# ═══════════════════════════════════════════
_pixel_font_cache = {}

def get_pixel_font(size=16):
    """Get a small pixel-like font. Falls back to system font if no pixel font available."""
    if size not in _pixel_font_cache:
        # Use a small system font rendered crisply
        try:
            _pixel_font_cache[size] = pygame.font.SysFont("Courier New", size, bold=True)
        except Exception:
            _pixel_font_cache[size] = pygame.font.SysFont(None, size, bold=True)
    return _pixel_font_cache[size]


# ═══════════════════════════════════════════
#  CLB LOGO SPRITE (circular pixel art)
# ═══════════════════════════════════════════
def create_logo_sprite(diameter=120):
    """
    Create a pixel-art version of the CLB logo:
    - Outer ring with binary digits (orange)
    - Inner dark blue circle border
    - Power button icon (dark blue)
    - 'A+' text (red) and '$' text (gold)
    All drawn with pixelated squares for consistent pixel art look.
    """
    import math

    ps = PIXEL_SCALE
    size = diameter
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    # Colors
    NAVY       = (25, 50, 100)
    NAVY_LIGHT = (40, 80, 150)
    ORANGE     = (220, 120, 30)
    RED        = (220, 40, 30)
    GOLD       = (230, 180, 30)
    WHITE_BG   = (240, 240, 245)
    
    # ── 1) Draw outer binary ring ──
    outer_r = size // 2 - 2
    inner_ring_r = size // 2 - 16
    
    # Fill ring area with pixelated binary text effect
    for py_ in range(0, size, ps):
        for px_ in range(0, size, ps):
            dx = px_ + ps // 2 - cx
            dy = py_ + ps // 2 - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if inner_ring_r < dist < outer_r:
                # Alternating 0/1 pattern
                idx = int((math.atan2(dy, dx) + math.pi) * 20 / math.pi + py_ * 3)
                if idx % 3 != 0:
                    pygame.draw.rect(surf, ORANGE, (px_, py_, ps, ps))
                    
    # ── 2) Draw inner circle (white fill) ──
    for py_ in range(0, size, ps):
        for px_ in range(0, size, ps):
            dx = px_ + ps // 2 - cx
            dy = py_ + ps // 2 - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= inner_ring_r:
                pygame.draw.rect(surf, WHITE_BG, (px_, py_, ps, ps))
    
    # ── 3) Draw navy circle border (inside) ──
    border_outer = inner_ring_r
    border_inner = inner_ring_r - ps * 2
    for py_ in range(0, size, ps):
        for px_ in range(0, size, ps):
            dx = px_ + ps // 2 - cx
            dy = py_ + ps // 2 - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if border_inner < dist <= border_outer:
                pygame.draw.rect(surf, NAVY, (px_, py_, ps, ps))

    # ── 4) Power button icon (center-top area) ──
    # Vertical line at center
    bar_x = cx - ps
    bar_top = cy - 22
    bar_bottom = cy - 2
    for y in range(bar_top, bar_bottom, ps):
        pygame.draw.rect(surf, NAVY, (bar_x, y, ps * 2, ps))

    # Top cap (rounded)
    pygame.draw.rect(surf, NAVY_LIGHT, (bar_x, bar_top, ps * 2, ps))

    # Arc (partial circle around the bar)
    arc_r = 18
    for angle_deg in range(50, 310):
        if 80 < angle_deg < 100:
            continue  # Gap at top for the bar
        angle = math.radians(angle_deg)
        ax = cx + int(arc_r * math.sin(angle))
        ay = cy - 5 + int(-arc_r * math.cos(angle))
        # Snap to pixel grid
        ax = (ax // ps) * ps
        ay = (ay // ps) * ps
        pygame.draw.rect(surf, NAVY, (ax, ay, ps, ps))

    # ── 5) "A+" text (bottom-left) ──
    a_font = get_pixel_font(18)
    a_surf = a_font.render("A", True, RED)
    surf.blit(a_surf, (cx - 28, cy + 8))
    # Small "+" 
    plus_font = get_pixel_font(12)
    plus_surf = plus_font.render("+", True, RED)
    surf.blit(plus_surf, (cx - 16, cy + 5))

    # ── 6) "$" text (bottom-right) ──
    d_font = get_pixel_font(20)
    d_surf = d_font.render("$", True, GOLD)
    surf.blit(d_surf, (cx + 10, cy + 6))

    return surf


# ═══════════════════════════════════════════
#  PLAYABLE CHARACTER SPRITES (16 wide x 22 tall)
# ═══════════════════════════════════════════

def _make_male_knight(armor, armor_lt, armor_dk, helm, visor, eye, plume=None):
    """Template for male knight sprite (16x22). Helmet + full armor."""
    _ = T
    S = (220, 180, 140)  # Skin
    A = armor; L = armor_lt; D = armor_dk
    H = helm; V = visor; E = eye
    P = plume if plume else H  # Plume on helmet
    grid = [
        [_,_,_,_,_,_, P,_,_, P,_,_,_,_,_,_],
        [_,_,_,_,_, H, H, H, H, H, H,_,_,_,_,_],
        [_,_,_,_, H, H, H, H, H, H, H, H,_,_,_,_],
        [_,_,_,_, H, H, H, H, H, H, H, H,_,_,_,_],
        [_,_,_,_, V, V, V, V, V, V, V, V,_,_,_,_],
        [_,_,_,_, V, E, V, V, V, E, V,_,_,_,_,_],
        [_,_,_,_, V, V, V, V, V, V, V,_,_,_,_,_],
        [_,_,_,_,_, S, S, S, S, S,_,_,_,_,_,_],
        [_,_,_,_, A, A, L, A, L, A, A,_,_,_,_,_],
        [_,_, L, A, A, A, L, A, L, A, A, A, L,_,_,_],
        [_,_, D, A, A, A, A, A, A, A, A, A, D,_,_,_],
        [_,_, D, A, A, A, L, A, L, A, A, A, D,_,_,_],
        [_,_, D, A, A, A, A, A, A, A, A, A, D,_,_,_],
        [_,_, D, A, A, A, L, A, L, A, A, A, D,_,_,_],
        [_,_,_, D, A, A, A, A, A, A, A, D,_,_,_,_],
        [_,_, D, D, A, A, A, A, A, A, A, D, D,_,_,_],
        [_,_, D, A, A, A, A, A, A, A, A, A, D,_,_,_],
        [_,_, D, A, A, A, A, A, A, A, A, A, D,_,_,_],
        [_,_,_, D, D, A, A,_,_, A, A, D, D,_,_,_],
        [_,_,_, D, D, D,_,_,_,_, D, D, D,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    ]
    return _grid_to_surface(grid)


def _make_female_knight(armor, armor_lt, armor_dk, hair, eye):
    """Template for female knight sprite (16x22). Hair + armor."""
    _ = T
    S = (245, 210, 175)  # Skin
    A = armor; L = armor_lt; D = armor_dk
    Hr = hair; E = eye
    grid = [
        [_,_,_,_,_,_,Hr,Hr,Hr,_,_,_,_,_,_,_],
        [_,_,_,_,_,Hr,Hr,Hr,Hr,Hr,_,_,_,_,_,_],
        [_,_,_,_,Hr,Hr,Hr,Hr,Hr,Hr,Hr,_,_,_,_,_],
        [_,_,_,Hr,Hr,Hr,Hr,Hr,Hr,Hr,Hr,Hr,_,_,_,_],
        [_,_,_,Hr, S, S, S, S, S, S, S,Hr,_,_,_,_],
        [_,_,_,Hr, S, E, S, S, S, E, S,Hr,_,_,_,_],
        [_,_,_,Hr, S, S, S, S, S, S, S,Hr,_,_,_,_],
        [_,_,_,_,_, S, S, S, S, S,_,_,_,_,_,_],
        [_,_,_,_, A, A, L, A, L, A, A,_,_,_,_,_],
        [_,_, L, A, A, A, L, A, L, A, A, A, L,_,_,_],
        [_,_, D, A, A, A, A, A, A, A, A, A, D,_,_,_],
        [_,_, D, A, A, A, L, A, L, A, A, A, D,_,_,_],
        [_,_, D, A, A, A, A, A, A, A, A, A, D,_,_,_],
        [_,_, D, A, A, A, L, A, L, A, A, A, D,_,_,_],
        [_,_,_, D, A, A, A, A, A, A, A, D,_,_,_,_],
        [_,_, D, D, A, A, A, A, A, A, A, D, D,_,_,_],
        [_,_, D, A, A, A, A, A, A, A, A, A, D,_,_,_],
        [_,_, D, A, A, A, A, A, A, A, A, A, D,_,_,_],
        [_,_,_, D, D, A, A,_,_, A, A, D, D,_,_,_],
        [_,_,_, D, D, D,_,_,_,_, D, D, D,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    ]
    return _grid_to_surface(grid)


def create_char_hector():
    """Male Knight 1 - HECTOR the Blue Knight"""
    return _make_male_knight(
        armor=(0, 110, 200), armor_lt=(0, 150, 255), armor_dk=(0, 70, 140),
        helm=(0, 90, 180), visor=(30, 50, 100), eye=(255, 215, 0),
        plume=(255, 255, 255),
    )

def create_char_ares():
    """Male Knight 2 - ARES the Fire Knight"""
    return _make_male_knight(
        armor=(200, 30, 30), armor_lt=(255, 49, 49), armor_dk=(140, 20, 20),
        helm=(60, 60, 60), visor=(40, 30, 30), eye=(255, 215, 0),
        plume=(255, 100, 50),
    )

def create_char_claw():
    """Male Knight 3 - CLAW the Gold Knight"""
    return _make_male_knight(
        armor=(200, 170, 40), armor_lt=(230, 210, 130), armor_dk=(150, 130, 20),
        helm=(180, 150, 60), visor=(80, 60, 30), eye=(255, 50, 30),
        plume=(255, 215, 0),
    )

def create_char_mira():
    """Female Knight 1 - MIRA the Pink Knight"""
    return _make_female_knight(
        armor=(220, 150, 170), armor_lt=(255, 192, 203), armor_dk=(180, 110, 130),
        hair=(255, 200, 220), eye=(200, 100, 150),
    )

def create_char_ivy():
    """Female Knight 2 - IVY the Nature Knight"""
    return _make_female_knight(
        armor=(30, 160, 30), armor_lt=(50, 205, 50), armor_dk=(20, 100, 20),
        hair=(180, 90, 40), eye=(50, 205, 50),
    )


# ═══════════════════════════════════════════
#  VICTIM FACE SPRITE (8 wide x 8 tall - just head peeking from window)
# ═══════════════════════════════════════════
def create_victim_sprite(color, gender="female"):
    """Create a small face sprite for a victim peeking from a castle window."""
    _ = T
    S = (250, 225, 200)  # skin
    E = (50, 50, 80)     # eyes
    M = (200, 80, 80)    # mouth/lips
    r, g, b = color
    R = (r, g, b)        # outfit/collar color

    if gender == "female":
        Hr = (180, 100, 50)  # brown-red long hair
        grid = [
            [_,_, Hr, Hr, Hr, Hr,_,_],
            [_, Hr, Hr, Hr, Hr, Hr, Hr,_],
            [Hr, Hr, S, S, S, S, Hr, Hr],
            [Hr, S, E, S, S, E, S, Hr],
            [Hr, S, S, S, S, S, S, Hr],
            [_, S, S, M, M, S, S,_],
            [_,_, R, R, R, R,_,_],
            [_,_, R, R, R, R,_,_],
        ]
    else:  # male
        Hr = (60, 40, 30)  # dark short hair
        grid = [
            [_,_, Hr, Hr, Hr, Hr,_,_],
            [_, Hr, Hr, Hr, Hr, Hr, Hr,_],
            [_, Hr, S, S, S, S, Hr,_],
            [_, S, E, S, S, E, S,_],
            [_, S, S, S, S, S, S,_],
            [_,_, S, M, M, S,_,_],
            [_,_, R, R, R, R,_,_],
            [_,_, R, R, R, R,_,_],
        ]
    return _grid_to_surface(grid)


# ═══════════════════════════════════════════
#  VICTIM BODY SPRITE (16 wide x 22 tall - full body for celebration)
# ═══════════════════════════════════════════
def create_victim_body_sprite(color, gender="female"):
    """Create a full-body victim sprite for the celebration scene."""
    _ = T
    S = (250, 225, 200)  # skin
    E = (50, 50, 80)     # eyes
    r, g, b = color
    R = (r, g, b)
    L = (min(255, r+40), min(255, g+40), min(255, b+40))
    D = (max(0, r-40), max(0, g-40), max(0, b-40))

    if gender == "female":
        Hr = (180, 100, 50)
        grid = [
            [_,_,_,_,_,_,Hr,Hr,Hr,_,_,_,_,_,_,_],
            [_,_,_,_,_,Hr,Hr,Hr,Hr,Hr,_,_,_,_,_,_],
            [_,_,_,_,Hr,Hr,Hr,Hr,Hr,Hr,Hr,_,_,_,_,_],
            [_,_,_,Hr,Hr, S, S, S, S,Hr,Hr,_,_,_,_,_],
            [_,_,_,Hr, S, E, S, S, E, S,Hr,_,_,_,_,_],
            [_,_,_,Hr, S, S, S, S, S, S,Hr,_,_,_,_,_],
            [_,_,_,_,_, S, S, S, S,_,_,_,_,_,_,_],
            [_,_,_,_, R, R, L, R, L, R,_,_,_,_,_,_],
            [_,_,_, R, R, R, L, R, L, R, R,_,_,_,_,_],
            [_,_,_, R, R, R, R, R, R, R, R,_,_,_,_,_],
            [_,_,D, R, R, R, L, R, L, R, R, D,_,_,_,_],
            [_,_,D, R, R, R, R, R, R, R, R, D,_,_,_,_],
            [_,_,_, D, R, R, R, R, R, R, D,_,_,_,_,_],
            [_,_,D, D, R, R, R, R, R, R, D, D,_,_,_,_],
            [_,_,D, R, R, R, R, R, R, R, R, D,_,_,_,_],
            [_,_,D, R, R, R, R, R, R, R, R, D,_,_,_,_],
            [_,_,_, D, D, R, R, R, R, D, D,_,_,_,_,_],
            [_,_,_, D, D, R,_,_, R, D, D,_,_,_,_,_],
            [_,_,_,_, D, D,_,_,_, D, D,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        ]
    else:  # male
        Hr = (60, 40, 30)
        grid = [
            [_,_,_,_,_,Hr,Hr,Hr,Hr,_,_,_,_,_,_,_],
            [_,_,_,_,Hr,Hr,Hr,Hr,Hr,Hr,_,_,_,_,_,_],
            [_,_,_,_,Hr,Hr,Hr,Hr,Hr,Hr,_,_,_,_,_,_],
            [_,_,_,_, S, S, S, S, S, S,_,_,_,_,_,_],
            [_,_,_,_, S, E, S, S, E, S,_,_,_,_,_,_],
            [_,_,_,_,_, S, S, S, S,_,_,_,_,_,_,_],
            [_,_,_,_,_, S, S, S, S,_,_,_,_,_,_,_],
            [_,_,_,_, R, R, L, R, L, R,_,_,_,_,_,_],
            [_,_,_, R, R, R, L, R, L, R, R,_,_,_,_,_],
            [_,_,_, R, R, R, R, R, R, R, R,_,_,_,_,_],
            [_,_,D, R, R, R, L, R, L, R, R, D,_,_,_,_],
            [_,_,D, R, R, R, R, R, R, R, R, D,_,_,_,_],
            [_,_,_, D, R, R, R, R, R, R, D,_,_,_,_,_],
            [_,_,D, D, R, R, R, R, R, R, D, D,_,_,_,_],
            [_,_,D, R, R, R, R, R, R, R, R, D,_,_,_,_],
            [_,_,_, D, D, R, R, R, R, D, D,_,_,_,_,_],
            [_,_,_, D, D, R,_,_, R, D, D,_,_,_,_,_],
            [_,_,_,_, D, D,_,_,_, D, D,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        ]
    return _grid_to_surface(grid)


# ═══════════════════════════════════════════
#  MONSTER SPRITE (16 wide x 22 tall)
# ═══════════════════════════════════════════
def create_monster_sprite(base_color=None):
    """A scary monster. Optionally tinted with a base_color."""
    _ = T
    if base_color is None:
        G1 = (30, 80, 20)   # Dark green
        G2 = (50, 150, 40)  # Mid green
        G3 = (100, 220, 60) # Light green
    else:
        r, g, b = base_color
        G2 = (r, g, b)
        G1 = (max(0, r-40), max(0, g-40), max(0, b-40))
        G3 = (min(255, r+50), min(255, g+50), min(255, b+70))

    S = (200, 180, 140) # Horn/Bone color
    E = (255, 50, 0)    # Red eyes
    B = (0, 0, 0)       # Pupil
    
    grid = [
        # Horns
        [_,_, S,_,_,_,_,_,_,_,_,_,_, S,_,_],
        [_,_, S, S,_,_,_,_,_,_,_,_, S, S,_,_],
        [_,_,_, S, S,_,_,_,_,_,_, S, S,_,_,_],
        # Head
        [_,_,_, G1, G1, G1, G1, G1, G1, G1, G1, G1,_,_,_,_],
        [_,_, G1, G2, G2, G2, G2, G2, G2, G2, G2, G1,_,_,_,_],
        [_,_, G1, G2, E, G2, G2, G2, E, G2, G2, G1,_,_,_,_],
        [_,_, G1, G2, B, G2, G2, G2, B, G2, G2, G1,_,_,_,_],
        [_,_, G1, G2, G2, G2, G2, G2, G2, G2, G2, G1,_,_,_,_],
        # Jaw/Teeth
        [_,_,_, G1, G2, S, S, S, S, G2, G1,_,_,_,_,_],
        # Body
        [_,_, G1, G2, G2, G2, G3, G2, G2, G2, G1,_,_,_,_],
        [_, G1, G2, G3, G2, G3, G3, G3, G2, G3, G2, G1,_,_],
        [_, G1, G2, G3, G3, G3, G3, G3, G3, G3, G2, G1,_,_],
        [_, G1, G2, G3, G2, G3, G3, G3, G2, G3, G2, G1,_,_],
        [_,_, G1, G2, G2, G3, G3, G3, G2, G2, G1,_,_,_,_],
        # Legs
        [_,_,_, G1, G1, G3, G3, G3, G1, G1,_,_,_,_,_],
        [_,_,_, G1, G2, G2,_, G2, G2, G1,_,_,_,_,_],
        [_,_,_, G1, G2, G2,_, G2, G2, G1,_,_,_,_,_],
        [_,_,_, G1, G2, G1,_, G1, G2, G1,_,_,_,_,_],
        # Feet
        [_,_, G1, G1, G1,_,_,_, G1, G1, G1,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    ]
    return _grid_to_surface(grid)


# ═══════════════════════════════════════════
#  IRON CAGE SPRITE (48 wide x 64 tall)
# ═══════════════════════════════════════════
def create_iron_cage_sprite():
    """An iron cage to imprison the player."""
    _ = T
    I1 = (60, 60, 65)   # Dark iron
    I2 = (100, 100, 110) # Mid iron
    I3 = (160, 160, 175) # Light iron (shine)
    
    w, h = 18, 24 # 18x24 pixels grid
    grid = [[None for _i in range(w)] for _j in range(h)]
    
    # Top and Bottom bars
    for x in range(w):
        grid[0][x] = I1
        grid[1][x] = I2
        grid[h-1][x] = I1
        grid[h-2][x] = I2
    
    # Vertical bars
    for x in range(0, w, 4):
        for y in range(h):
            grid[y][x] = I1
            if x+1 < w: grid[y][x+1] = I2
            if x+2 < w: grid[y][x+2] = I3 if y % 5 == 0 else None
    
    # Roof/Hook
    for x in range(w//2 - 2, w//2 + 2):
        grid[0][x] = I1
    grid[0][w//2] = I3
    
    return _grid_to_surface(grid, scale=4) # Scale a bit more for the cage


# ═══════════════════════════════════════════
#  CHARACTER DATA REGISTRY
# ═══════════════════════════════════════════
# 3 Male Knights → Princess victims, 2 Female Knights → Prince victims
CHARACTER_DATA = [
    {
        "name": "HECTOR", "desc": "Blue Knight", "color": (0, 110, 200),
        "create": create_char_hector,
        "opponent_name": "Forest Troll", "opponent_color": (30, 150, 40), "opponent_create": create_monster_sprite,
        "victim_color": (0, 110, 200), "victim_gender": "female",
    },
    {
        "name": "ARES", "desc": "Fire Knight", "color": (200, 30, 30),
        "create": create_char_ares,
        "opponent_name": "Slime Beast", "opponent_color": (150, 150, 40), "opponent_create": create_monster_sprite,
        "victim_color": (200, 30, 30), "victim_gender": "female",
    },
    {
        "name": "MIRA", "desc": "Pink Knight", "color": (220, 150, 170),
        "create": create_char_mira,
        "opponent_name": "Gorgon Spore", "opponent_color": (150, 30, 150), "opponent_create": create_monster_sprite,
        "victim_color": (220, 150, 170), "victim_gender": "male",
    },
    {
        "name": "IVY", "desc": "Nature Knight", "color": (30, 160, 30),
        "create": create_char_ivy,
        "opponent_name": "Deepfiend", "opponent_color": (30, 30, 150), "opponent_create": create_monster_sprite,
        "victim_color": (30, 160, 30), "victim_gender": "male",
    },
    {
        "name": "CLAW", "desc": "Gold Knight", "color": (200, 180, 100),
        "create": create_char_claw,
        "opponent_name": "Dread Weaver", "opponent_color": (80, 80, 80), "opponent_create": create_monster_sprite,
        "victim_color": (200, 180, 100), "victim_gender": "female",
    },
]
