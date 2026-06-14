"""
Pygame platformer tutorial: following https://coderslegacy.com/python/pygame-platformer-game-development/

@author: B.A. Sturre

Created on 13-06-2026

"""

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

# FIX: Initialize display context first so Info() reads the correct monitor dimensions
displaysurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Platformer")

# setting display
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

HEIGHT = SCREEN_HEIGHT
WIDTH = int(400/450 * HEIGHT)

X_OFFSET = (SCREEN_WIDTH - WIDTH) // 2

# Scale factor based on vertical expansion
SCALE = HEIGHT / HEIGHT_ORIGINAL

# Scaling the physics constants relative to size magnification
ACC = 0.5 * SCALE
FRIC = -0.12 

MAX_PLATFORMS = 6
HIGH_SCORE = 0 

VOLUME_LEVEL = 5
PRE_MUTE_VOLUME = 5
IS_MUTED = False 

# playing music
pygame.mixer.music.load("background.wav")
pygame.mixer.music.play(-1)  # -1 so it repeats
pygame.mixer.music.set_volume(VOLUME_LEVEL/10.0)

# Load background asset and prepare it for full screen scaling
try:
    background_img = pygame.image.load("background.png").convert()
except:
    background_img = pygame.Surface((WIDTH, HEIGHT))
    background_img.fill((20, 20, 30))

# setting up fonts 
font = pygame.font.SysFont("Verdana", int(30 * SCALE))
font_small = pygame.font.SysFont("Verdana", int(20 * SCALE))
f = pygame.font.SysFont("Verdana", int(15 * SCALE))

# making the player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Scale player dimension dynamically (Original base size 30x30)
        p_size = int(30 * SCALE)
        self.surf = pygame.Surface((p_size, p_size))
        self.surf.fill((128, 255, 40))
        self.rect = self.surf.get_rect(center=(WIDTH // 2, HEIGHT - int(50 * SCALE)))

        # movement
        self.pos = vec((WIDTH // 2, HEIGHT - int(65 * SCALE)))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        
        self.jumping = False 
        self.score = 0 

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

        # FIX: Keep entire player bounding box clipped inside the rectangle track bounds
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
           self.vel.y = -15 * SCALE # Magnify jump velocity

    def cancel_jump(self):
        # removing jumping velocity when space is released
        if self.jumping:
            if self.vel.y < -3 * SCALE:
                self.vel.y = -3 * SCALE

    def update(self, platforms):
        global HIGH_SCORE
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if self.vel.y > 0:        
            if hits:
                if self.pos.y < hits[0].rect.bottom:
                    if hits[0].point == True:  # making sure landing can only be done on top
                        hits[0].point = False   
                        self.score += 1  
                        if self.score > HIGH_SCORE:
                            HIGH_SCORE = self.score         
                    self.pos.y = hits[0].rect.top + 1
                    self.vel.y = 0
                    self.jumping = False


# making the platform
class platform(pygame.sprite.Sprite):
    def __init__(self, target_y=None): 
        super().__init__()
        # Scaling platform dimensions dynamically
        p_width = int(random.randint(50, 100) * SCALE)
        p_height = int(12 * SCALE)
        self.surf = pygame.Surface((p_width, p_height))
        self.surf.fill((0,255,0))
        
        if target_y is None:
            target_y = random.randint(int(100 * SCALE), HEIGHT - int(100 * SCALE))
            
        # FIX: Explicitly assign rect.left to prevent center placement from throwing it outside bounds
        self.rect = self.surf.get_rect()
        self.rect.left = random.randint(0, max(0, WIDTH - p_width))
        self.rect.centery = target_y
        
        self.speed = random.randint(-1, 1)
        self.point = True 
        self.moving = True 

    def move(self): 
        if self.moving == True:  
            self.rect.move_ip(self.speed, 0)
            # FIX: Keep moving platforms cleanly within the vertical channel boundaries
            if self.speed > 0 and self.rect.right > WIDTH:
                self.speed = -self.speed
            if self.speed < 0 and self.rect.left < 0:
                self.speed = -self.speed


# platform generation
def plat_gen(platforms, all_sprites): 
    while len(platforms) < MAX_PLATFORMS + 1:
        # Find the current highest platform in the sky (the lowest y coordinate)
        highest_y = 0
        for plat in platforms:
            if plat.rect.top < highest_y:
                highest_y = plat.rect.top
                
        p = platform()      
        C = True
         
        while C:
             # FIX: Absolute range sorting to completely prevent random.randint crashes
             min_step = max(1, int(60 * SCALE))
             max_step = max(min_step + 1, int(110 * SCALE))
             target_y = highest_y - random.randint(min_step, max_step)
             
             p = platform(target_y=target_y)
             C = check(p, platforms)
 
        platforms.add(p)
        all_sprites.add(p)


# checking if platforms don't collide and aren't too close
def check(platform, groupies):
    if pygame.sprite.spritecollideany(platform, groupies):
        return True
    else:
        for entity in groupies:
            if entity == platform:
                continue
            # Check horizontal and vertical spacing bounds simultaneously to eliminate overlapping completely
            x_overlap = platform.rect.right > entity.rect.left - int(20 * SCALE) and platform.rect.left < entity.rect.right + int(20 * SCALE)
            y_overlap = abs(platform.rect.top - entity.rect.top) < int(50 * SCALE)
            if x_overlap and y_overlap:
                return True
        return False 
    
# game loop 
def game_loop():
    # creating player and platform
    PT1 = platform()
    P1 = Player()

    # make a full first platform 
    PT1.surf = pygame.Surface((WIDTH, int(20 * SCALE)))
    PT1.surf.fill(RED)
    PT1.rect = PT1.surf.get_rect(center = (WIDTH/2, HEIGHT - int(10 * SCALE)))  
    PT1.moving = False 
    PT1.point = False 

    # making sprite groups  
    all_sprites = pygame.sprite.Group()
    all_sprites.add(PT1)
    all_sprites.add(P1)

    platforms = pygame.sprite.Group() 
    platforms.add(PT1)

    # initial platform generation stacking cleanly upwards from base plate
    last_y = HEIGHT - int(10 * SCALE)
    for x in range(MAX_PLATFORMS): 
        pl = platform() 
        C = True
        while C:
            min_step = max(1, int(65 * SCALE))
            max_step = max(min_step + 1, int(115 * SCALE))
            target_y = last_y - random.randint(min_step, max_step)
            pl = platform(target_y=target_y)
            C = check(pl, platforms)
        last_y = pl.rect.top
        platforms.add(pl) 
        all_sprites.add(pl) 

    playing = True 
    while playing: 
        for event in pygame.event.get(): 
            # quitting
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): 
                pygame.quit() 
                sys.exit() 
        
            # jumping
            if event.type == pygame.KEYDOWN:    
                if event.key == pygame.K_SPACE:
                    P1.jump(platforms)
            if event.type == pygame.KEYUP:    
                if event.key == pygame.K_SPACE:
                    P1.cancel_jump()
        
        # Draw background side bars on extra screen width, fill centered zone with background image
        displaysurface.fill(DARK_GRAY) 
        bg_centered = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
        displaysurface.blit(bg_centered, (X_OFFSET, 0))
        
        # Correctly center the score text object inside your column bounds
        g = f.render(str(P1.score), True, (123,255,0))
        text_rect = g.get_rect(center=(X_OFFSET + WIDTH // 2, int(25 * SCALE)))
        displaysurface.blit(g, text_rect)
    
        P1.update(platforms)
        plat_gen(platforms, all_sprites)

        # infinite window
        if P1.rect.top <= HEIGHT/3: 
            P1.pos.y += abs(P1.vel.y)
            for plat in platforms: 
                plat.rect.y += abs(P1.vel.y)
                if plat.rect.top >= HEIGHT: 
                    plat.kill() 

        # make entities
        for entity in all_sprites: 
            displaysurface.blit(entity.surf, (entity.rect.x + X_OFFSET, entity.rect.y))
            entity.move()

        # game over
        if P1.rect.top > HEIGHT:
            displaysurface.fill(RED)
            game_over = font.render("Game Over", True, BLACK)
            displaysurface.blit(game_over, (SCREEN_WIDTH / 2 - game_over.get_width() / 2, HEIGHT / 2 - int(40 * SCALE)))
            score_go = font.render(f"Score: {str(P1.score)}", True, BLACK)
            displaysurface.blit(score_go, (SCREEN_WIDTH / 2 - score_go.get_width() / 2, HEIGHT / 2 + int(40 * SCALE)))

            for entity in all_sprites:
                entity.kill()

            pygame.display.update()
            time.sleep(1.8)
            playing = False 
            break 
        
        pygame.display.update() 
        FramePerSec.tick(FPS)


# make a button
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


# home screen function 
def home_screen(): 
    while True: 
        mouse_pos = pygame.mouse.get_pos() 
        
        # Clear screen and stretch your background image across the ENTIRE physical monitor
        displaysurface.fill(DARK_GRAY)
        bg_full = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        displaysurface.blit(bg_full, (0, 0))
        
        # Draw the narrow gameplay column overlay, centered perfectly via X_OFFSET
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100)) 
        displaysurface.blit(overlay, (X_OFFSET, 0))
        
        # displaying title and high score
        title = font.render("Platformer", True, WHITE)
        displaysurface.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, HEIGHT * 0.2))
        high_score = font.render(f"High Score: {HIGH_SCORE}", True, WHITE)
        displaysurface.blit(high_score, (SCREEN_WIDTH / 2 - high_score.get_width() / 2, HEIGHT * 0.32))

        # buttons centered perfectly relative to fullscreen screen width
        btn_w, btn_h = int(250 * SCALE), int(50 * SCALE)
        start_btn = draw_button("Start Game", SCREEN_WIDTH / 2 - btn_w / 2, HEIGHT * 0.48, btn_w, btn_h, GRAY, DARK_GRAY, mouse_pos)
        settings_btn = draw_button("Settings", SCREEN_WIDTH / 2 - btn_w / 2, HEIGHT * 0.58, btn_w, btn_h, GRAY, DARK_GRAY, mouse_pos)
        quit_btn = draw_button("Quit Game", SCREEN_WIDTH / 2 - btn_w / 2, HEIGHT * 0.68, btn_w, btn_h, GRAY, DARK_GRAY, mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): 
                pygame.quit() 
                sys.exit() 
            
            # if pressing button
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if start_btn.collidepoint(mouse_pos): 
                    game_loop() 
                elif settings_btn.collidepoint(mouse_pos):
                    settings_screen()
                elif quit_btn.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update() 
        FramePerSec.tick(FPS)


# settings menu
def settings_screen(): 
    global MAX_PLATFORMS, VOLUME_LEVEL, IS_MUTED, PRE_MUTE_VOLUME
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        # background stretched to full screen size
        displaysurface.fill(DARK_GRAY)
        bg_full = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        displaysurface.blit(bg_full, (0, 0))
            
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120)) 
        displaysurface.blit(overlay, (X_OFFSET, 0))

        # displaying title
        title = font.render("Settings", True, BLACK)
        displaysurface.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, HEIGHT * 0.15))

        # Config row button metrics
        pad = int(15 * SCALE)
        b_w, b_h = int(50 * SCALE), int(45 * SCALE)
        mute_w = int(90 * SCALE)

        # max number of enemies
        lbl_enemies = font_small.render("Platforms: ", True, WHITE)
        num_enemies = font_small.render(f"{MAX_PLATFORMS}", True, WHITE)
        
        row1_total_width = lbl_enemies.get_width() + b_w + pad + num_enemies.get_width() + pad + b_w
        start_x1 = SCREEN_WIDTH / 2 - row1_total_width / 2
        y1 = HEIGHT * 0.4
        
        displaysurface.blit(lbl_enemies, (start_x1, y1 + int(5 * SCALE)))
        btn_e_minus = draw_button("-", start_x1 + lbl_enemies.get_width(), y1, b_w, b_h, GRAY, DARK_GRAY, mouse_pos)
        displaysurface.blit(num_enemies, (btn_e_minus.right + pad, y1 + int(5 * SCALE)))
        btn_e_plus = draw_button("+", btn_e_minus.right + pad + num_enemies.get_width() + pad, y1, b_w, b_h, GRAY, DARK_GRAY, mouse_pos)

        # audio volume
        lbl_volume = font_small.render("Volume: ", True, WHITE)
        volume_display_str = "Muted" if IS_MUTED else f"{VOLUME_LEVEL}"
        num_volume = font_small.render(volume_display_str, True, WHITE)
        
        row2_total_width = lbl_volume.get_width() + mute_w + pad + b_w + pad + num_volume.get_width() + pad + b_w
        start_x2 = SCREEN_WIDTH / 2 - row2_total_width / 2
        y2 = HEIGHT * 0.52
        
        displaysurface.blit(lbl_volume, (start_x2, y2 + int(5 * SCALE)))
        mute_label = "Unmute" if IS_MUTED else "Mute"
        btn_mute = draw_button(mute_label, start_x2 + lbl_volume.get_width(), y2, mute_w, b_h, GRAY, DARK_GRAY, mouse_pos)
        btn_v_minus = draw_button("-", btn_mute.right + pad, y2, b_w, b_h, GRAY, DARK_GRAY, mouse_pos)
        displaysurface.blit(num_volume, (btn_v_minus.right + pad, y2 + int(5 * SCALE)))
        btn_v_plus = draw_button("+", btn_v_minus.right + pad + num_volume.get_width() + pad, y2, b_w, b_h, GRAY, DARK_GRAY, mouse_pos)

        # back button
        btn_back_w, btn_back_h = int(250 * SCALE), int(50 * SCALE)
        btn_back = draw_button("Back to Menu", SCREEN_WIDTH / 2 - btn_back_w / 2, HEIGHT * 0.72, btn_back_w, btn_back_h, GRAY, DARK_GRAY, mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # enemies
                if btn_e_minus.collidepoint(mouse_pos):
                    if MAX_PLATFORMS > 4: MAX_PLATFORMS -= 1
                elif btn_e_plus.collidepoint(mouse_pos):
                    if MAX_PLATFORMS < 12: MAX_PLATFORMS += 1
                
                # volume
                elif btn_v_minus.collidepoint(mouse_pos):
                    if VOLUME_LEVEL > 0:
                        VOLUME_LEVEL -= 1
                        IS_MUTED = True if VOLUME_LEVEL == 0 else False
                        pygame.mixer.music.set_volume(VOLUME_LEVEL / 10.0)
                elif btn_v_plus.collidepoint(mouse_pos):
                    if VOLUME_LEVEL < 9:
                        VOLUME_LEVEL += 1
                        IS_MUTED = False
                        pygame.mixer.music.set_volume(VOLUME_LEVEL / 10.0)
                
                # mute
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


# main
if __name__ == "__main__": 
    home_screen()

