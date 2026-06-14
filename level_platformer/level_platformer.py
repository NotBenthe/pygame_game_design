import sys, os

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore", UserWarning)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame 
from pygame.locals import * 
import random 
import time 

pygame.init() 

FPS = 60
FramePerSec = pygame.time.Clock()

vec = pygame.math.Vector2  # 2 for 2D

# colours
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (100, 100, 100)

HEIGHT_ORIGINAL = 450
WIDTH_ORIGINAL = 400

# Initialize display context
displaysurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Platformer")

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

HEIGHT = SCREEN_HEIGHT
WIDTH = int(400/450 * HEIGHT)

X_OFFSET = (SCREEN_WIDTH - WIDTH) // 2
SCALE = HEIGHT / HEIGHT_ORIGINAL

ACC = 0.5 * SCALE
FRIC = -0.12 

VOLUME_LEVEL = 5
PRE_MUTE_VOLUME = 5
IS_MUTED = False 

# playing music
pygame.mixer.music.load("background.wav")
pygame.mixer.music.play(-1)  # -1 so it repeats
pygame.mixer.music.set_volume(VOLUME_LEVEL/10.0)

# Level Progression Systems
CURRENT_LEVEL = 1
COMPLETED_LEVELS = [False] * 11  # Index 1 to 10 used for tracking states

# Long structural designs for 10 levels (15-25 platforms per level). 
# Format: (approximate_y_step, absolute_width_percent, speed)
LEVEL_DATA = {
    1:  [(80, 0.25, 0)] * 14 + [(80, 0.30, 0)],
    2:  [(80, 0.25, 0), (85, 0.22, 1)] * 7 + [(80, 0.25, 0), (85, 0.25, 0)],
    3:  [(85, 0.22, 1), (85, 0.22, -1)] * 8 + [(85, 0.22, 0), (85, 0.25, 0)],
    4:  [(90, 0.20, 1), (90, 0.20, -1), (90, 0.22, 0)] * 6 + [(90, 0.22, 0)],
    5:  [(90, 0.18, 1), (90, 0.18, -1), (95, 0.18, 2), (95, 0.18, -2)] * 4 + [(90, 0.22, 0)],
    6:  [(95, 0.18, 2), (95, 0.18, -2), (95, 0.15, 2), (95, 0.15, -2)] * 5 + [(90, 0.20, 0)],
    7:  [(95, 0.15, 2), (95, 0.15, -2), (100, 0.15, 3), (100, 0.15, -3)] * 5 + [(90, 0.18, 0)],
    8:  [(100, 0.15, 3), (100, 0.12, -3), (100, 0.12, 3), (100, 0.12, -3)] * 5 + [(90, 0.18, 0)],
    9:  [(100, 0.12, 3), (105, 0.12, -3), (105, 0.12, 4), (105, 0.12, -4)] * 5 + [(90, 0.15, 0)],
    10: [(105, 0.12, 4), (105, 0.12, -4), (110, 0.10, 4), (110, 0.10, -4), (110, 0.09, 5)] * 5 + [(90, 0.15, 0)]
}

try:
    background_img = pygame.image.load("background.png").convert()
except:
    background_img = pygame.Surface((WIDTH, HEIGHT))
    background_img.fill((20, 20, 30))

font = pygame.font.SysFont("Verdana", int(30 * SCALE))
font_small = pygame.font.SysFont("Verdana", int(20 * SCALE))
f = pygame.font.SysFont("Verdana", int(15 * SCALE))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        p_size = int(30 * SCALE)
        self.surf = pygame.Surface((p_size, p_size))
        self.surf.fill((128, 255, 40))
        self.rect = self.surf.get_rect(center=(WIDTH // 2, HEIGHT - int(50 * SCALE)))

        self.pos = vec((WIDTH // 2, HEIGHT - int(65 * SCALE)))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.jumping = False 

    def move(self): 
        self.acc = vec(0, 0.5 * SCALE)
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]: 
            self.acc.x = -ACC 
        if pressed_keys[K_RIGHT]: 
            self.acc.x = ACC 
        
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
         
        self.rect.midbottom = self.pos

        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx
            self.vel.x = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.pos.x = self.rect.centerx
            self.vel.x = 0

    def jump(self, platforms): 
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
           self.jumping = True
           self.vel.y = -15 * SCALE 

    def cancel_jump(self):
        if self.jumping:
            if self.vel.y < -3 * SCALE:
                self.vel.y = -3 * SCALE

    def update(self, platforms):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if self.vel.y > 0:        
            if hits:
                if self.pos.y < hits[0].rect.bottom:
                    self.pos.y = hits[0].rect.top + 1
                    self.vel.y = 0
                    self.jumping = False


class platform(pygame.sprite.Sprite):
    def __init__(self, width_ratio, target_y, speed, is_goal=False): 
        super().__init__()
        p_width = int((WIDTH_ORIGINAL * width_ratio) * SCALE)
        p_height = int(12 * SCALE)
        self.surf = pygame.Surface((p_width, p_height))
        
        # Color coding target goal versus normal structural components
        if is_goal:
            self.surf.fill(BLACK) # Distinct Black Finish Platform
        else:
            self.surf.fill(GREEN)
            
        self.rect = self.surf.get_rect()
        self.rect.left = random.randint(0, max(0, WIDTH - p_width))
        self.rect.centery = target_y
        
        self.speed = speed
        self.moving = True if speed != 0 else False
        self.is_goal = is_goal

    def move(self): 
        if self.moving:  
            self.rect.move_ip(self.speed, 0)
            if self.speed > 0 and self.rect.right > WIDTH:
                self.speed = -self.speed
            if self.speed < 0 and self.rect.left < 0:
                self.speed = -self.speed


def load_level(level_num, platforms, all_sprites):
    """Generates explicit static layout blocks matching strict design maps."""
    # Base configuration floor setup
    floor = platform(1.0, HEIGHT - int(10 * SCALE), 0)
    floor.surf.fill(RED)
    floor.moving = False
    platforms.add(floor)
    all_sprites.add(floor)
    
    current_y = HEIGHT - int(10 * SCALE)
    data = LEVEL_DATA[level_num]
    
    for i, step in enumerate(data):
        y_gap, w_ratio, speed = step
        current_y -= int(y_gap * SCALE)
        
        # Flag the absolute last platform in index as the Level Complete Goal
        is_goal = (i == len(data) - 1)
        
        p = platform(w_ratio, current_y, speed, is_goal)
        platforms.add(p)
        all_sprites.add(p)


def draw_button(text, x, y, width, height, normal_color, hover_color, mouse_pos):
    rect = pygame.Rect(x, y, width, height)
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(displaysurface, hover_color, rect)
    else:
        pygame.draw.rect(displaysurface, normal_color, rect)

    text_surf = font_small.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    displaysurface.blit(text_surf, text_rect)
    return rect 


def game_loop():
    global COMPLETED_LEVELS
    P1 = Player()
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    
    all_sprites.add(P1)
    load_level(CURRENT_LEVEL, platforms, all_sprites)

    playing = True
    game_over_state = False

    while playing:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get(): 
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): 
                pygame.quit() 
                sys.exit() 
        
            if not game_over_state:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    P1.jump(platforms)
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    P1.cancel_jump()
            else:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if btn_retry.collidepoint(mouse_pos):
                        return "retry"
                    if btn_menu.collidepoint(mouse_pos):
                        return "menu"

        # Background Drawing Setup
        displaysurface.fill(DARK_GRAY) 
        bg_centered = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
        displaysurface.blit(bg_centered, (X_OFFSET, 0))
        
        # Render Title Card overlay
        lbl_text = f"Level {CURRENT_LEVEL}" if not game_over_state else "Game Over"
        g = f.render(lbl_text, True, (255, 255, 255) if not game_over_state else BLACK)
        text_rect = g.get_rect(center=(X_OFFSET + WIDTH // 2, int(25 * SCALE)))
        displaysurface.blit(g, text_rect)
    
        if not game_over_state:
            P1.update(platforms)

            # Camera scrolling tracking
            if P1.rect.top <= HEIGHT/3 and P1.vel.y < 0: 
                scroll_offset = abs(P1.vel.y)
                P1.pos.y += scroll_offset
                for plat in platforms: 
                    plat.rect.y += scroll_offset

            # Check if player landed on the distinct final level platform
            hits = pygame.sprite.spritecollide(P1, platforms, False)
            if hits and P1.vel.y == 0:
                if getattr(hits[0], 'is_goal', False):
                    COMPLETED_LEVELS[CURRENT_LEVEL] = True
                    time.sleep(0.5)
                    return "win"

            # Check fall tracking dead zone
            if P1.rect.top > HEIGHT:
                game_over_state = True

            # Draw & animate game sprites
            for entity in all_sprites: 
                displaysurface.blit(entity.surf, (entity.rect.x + X_OFFSET, entity.rect.y))
                entity.move()
        else:
            # Game Over Context Menu Box Controls
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((200, 0, 0, 80))
            displaysurface.blit(overlay, (X_OFFSET, 0))

            btn_w, btn_h = int(220 * SCALE), int(50 * SCALE)
            btn_retry = draw_button("Retry", SCREEN_WIDTH/2 - btn_w/2, HEIGHT * 0.45, btn_w, btn_h, GRAY, DARK_GRAY, mouse_pos)
            btn_menu = draw_button("Level Menu", SCREEN_WIDTH/2 - btn_w/2, HEIGHT * 0.58, btn_w, btn_h, GRAY, DARK_GRAY, mouse_pos)

        pygame.display.update() 
        FramePerSec.tick(FPS)


def level_select_screen():
    global CURRENT_LEVEL
    while True:
        mouse_pos = pygame.mouse.get_pos()
        displaysurface.fill(DARK_GRAY)
        
        bg_full = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        displaysurface.blit(bg_full, (0, 0))
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140)) 
        displaysurface.blit(overlay, (X_OFFSET, 0))
        
        title = font.render("Select Level", True, WHITE)
        displaysurface.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, HEIGHT * 0.1))

        # Generate custom layout tracking grids for 10 distinct level select buttons
        buttons = {}
        b_size = int(60 * SCALE)
        start_x = X_OFFSET + int(40 * SCALE)
        start_y = int(140 * SCALE)
        gap_x = int(70 * SCALE)
        gap_y = int(75 * SCALE)

        for lvl in range(1, 11):
            row = (lvl - 1) // 4
            col = (lvl - 1) % 4
            
            x = start_x + (col * gap_x)
            y = start_y + (row * gap_y)
            
            # If a level is beaten, color the button bright green
            color = GREEN if COMPLETED_LEVELS[lvl] else GRAY
            hover_color = (0, 200, 0) if COMPLETED_LEVELS[lvl] else DARK_GRAY
            
            btn = draw_button(str(lvl), x, y, b_size, b_size, color, hover_color, mouse_pos)
            buttons[lvl] = btn

        btn_back_w, btn_back_h = int(220 * SCALE), int(45 * SCALE)
        btn_back = draw_button("Main Menu", SCREEN_WIDTH / 2 - btn_back_w / 2, HEIGHT * 0.82, btn_back_w, btn_back_h, GRAY, DARK_GRAY, mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): 
                pygame.quit() 
                sys.exit() 
            
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(mouse_pos):
                    return
                for lvl, btn in buttons.items():
                    if btn.collidepoint(mouse_pos):
                        CURRENT_LEVEL = lvl
                        status = "retry"
                        while status == "retry":
                            status = game_loop()
                        if status == "win" or status == "menu":
                            break

        pygame.display.update() 
        FramePerSec.tick(FPS)


def home_screen(): 
    while True: 
        mouse_pos = pygame.mouse.get_pos() 
        displaysurface.fill(DARK_GRAY)
        
        bg_full = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        displaysurface.blit(bg_full, (0, 0))
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100)) 
        displaysurface.blit(overlay, (X_OFFSET, 0))
        
        title = font.render("Platformer", True, WHITE)
        displaysurface.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, HEIGHT * 0.2))

        btn_w, btn_h = int(250 * SCALE), int(50 * SCALE)
        start_btn = draw_button("Start Game", SCREEN_WIDTH / 2 - btn_w / 2, HEIGHT * 0.45, btn_w, btn_h, GRAY, DARK_GRAY, mouse_pos)
        settings_btn = draw_button("Settings", SCREEN_WIDTH / 2 - btn_w / 2, HEIGHT * 0.55, btn_w, btn_h, GRAY, DARK_GRAY, mouse_pos)
        quit_btn = draw_button("Quit Game", SCREEN_WIDTH / 2 - btn_w / 2, HEIGHT * 0.65, btn_w, btn_h, GRAY, DARK_GRAY, mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): 
                pygame.quit() 
                sys.exit() 
            
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if start_btn.collidepoint(mouse_pos): 
                    level_select_screen() 
                elif settings_btn.collidepoint(mouse_pos):
                    settings_screen()
                elif quit_btn.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update() 
        FramePerSec.tick(FPS)


def settings_screen(): 
    global VOLUME_LEVEL, IS_MUTED, PRE_MUTE_VOLUME
    while True:
        mouse_pos = pygame.mouse.get_pos()
        displaysurface.fill(DARK_GRAY)
        
        bg_full = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        displaysurface.blit(bg_full, (0, 0))
            
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120)) 
        displaysurface.blit(overlay, (X_OFFSET, 0))

        title = font.render("Settings", True, WHITE)
        displaysurface.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, HEIGHT * 0.15))

        pad = int(15 * SCALE)
        b_w, b_h = int(50 * SCALE), int(45 * SCALE)
        mute_w = int(90 * SCALE)

        lbl_volume = font_small.render("Volume: ", True, WHITE)
        volume_display_str = "Muted" if IS_MUTED else f"{VOLUME_LEVEL}"
        num_volume = font_small.render(volume_display_str, True, WHITE)
        
        row2_total_width = lbl_volume.get_width() + mute_w + pad + b_w + pad + num_volume.get_width() + pad + b_w
        start_x2 = SCREEN_WIDTH / 2 - row2_total_width / 2
        y2 = HEIGHT * 0.45
        
        displaysurface.blit(lbl_volume, (start_x2, y2 + int(5 * SCALE)))
        mute_label = "Unmute" if IS_MUTED else "Mute"
        btn_mute = draw_button(mute_label, start_x2 + lbl_volume.get_width(), y2, mute_w, b_h, GRAY, DARK_GRAY, mouse_pos)
        btn_v_minus = draw_button("-", btn_mute.right + pad, y2, b_w, b_h, GRAY, DARK_GRAY, mouse_pos)
        displaysurface.blit(num_volume, (btn_v_minus.right + pad, y2 + int(5 * SCALE)))
        btn_v_plus = draw_button("+", btn_v_minus.right + pad + num_volume.get_width() + pad, y2, b_w, b_h, GRAY, DARK_GRAY, mouse_pos)

        btn_back_w, btn_back_h = int(250 * SCALE), int(50 * SCALE)
        btn_back = draw_button("Back to Menu", SCREEN_WIDTH / 2 - btn_back_w / 2, HEIGHT * 0.68, btn_back_w, btn_back_h, GRAY, DARK_GRAY, mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if btn_v_minus.collidepoint(mouse_pos):
                    if VOLUME_LEVEL > 0:
                        VOLUME_LEVEL -= 1
                        IS_MUTED = True if VOLUME_LEVEL == 0 else False
                        pygame.mixer.music.set_volume(VOLUME_LEVEL / 10.0)
                elif btn_v_plus.collidepoint(mouse_pos):
                    if VOLUME_LEVEL < 9:
                        VOLUME_LEVEL += 1
                        IS_MUTED = False
                        pygame.mixer.music.set_volume(VOLUME_LEVEL / 10.0)
                elif btn_mute.collidepoint(mouse_pos):
                    if IS_MUTED:
                        IS_MUTED = False
                        VOLUME_LEVEL = PRE_MUTE_VOLUME if PRE_MUTE_VOLUME > 0 else 2
                    else:
                        IS_MUTED = True
                        PRE_MUTE_VOLUME = VOLUME_LEVEL
                        VOLUME_LEVEL = 0
                    pygame.mixer.music.set_volume(VOLUME_LEVEL / 10.0)
                elif btn_back.collidepoint(mouse_pos):
                    return

        pygame.display.update()
        FramePerSec.tick(FPS)


if __name__ == "__main__": 
    home_screen()