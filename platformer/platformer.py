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

HEIGHT = 450
WIDTH = 400
ACC = 0.5 
FRIC = -0.12 

VOLUME_LEVEL = 5
PRE_MUTE_VOLUTE = 5
IS_MUTED = False 

# playing music
pygame.mixer.music.load("background.wav")
pygame.mixer.music.play(-1)  # -1 so it repeats
pygame.mixer.music.set_volume(VOLUME_LEVEL/10.0)

# setting display
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer")
background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


# making the player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((30, 30))
        self.surf.fill((128, 255, 40))
        self.rect = self.surf.get_rect(center=(10, 420))

        # movement
        self.pos = vec((10, 385))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def move(self): 
        self.acc = vec(0, 0)

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]: 
            self.acc.x = -ACC 
        if pressed_keys[K_RIGHT]: 
            self.acc.x = ACC 
        
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
         
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
             
        self.rect.midbottom = self.pos


# making the platform
class platform(pygame.sprite.Sprite):
    def __init__(self): 
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))
        self.surf.fill(GREEN)
        self.rect = self.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))


# game loop 
def game_loop():
    # creating player and platform
    PT1 = platform()
    P1 = Player() 
    
    all_sprites = pygame.sprite.Group()
    all_sprites.add(PT1)
    all_sprites.add(P1)

    playing = True 
    while playing: 
        for event in pygame.event.get(): 
            if event.type == QUIT: 
                pygame.quit() 
                sys.exit() 
        
        displaysurface.fill((0, 0, 0))

        for entity in all_sprites: 
            displaysurface.blit(entity.surf, entity.rect)
        
        pygame.display.update() 
        FramePerSec.tick(FPS)






















# screen information
SPEED = 25
SCORE = 0
HIGH_SCORE = 0 
MAX_ENEMIES = 3

# setting up fonts
font = pygame.font.SysFont("Verdana", 40)
font_small = pygame.font.SysFont("Verdana", 30)


"""
# making the player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        # initiating the pygame.sprite.Sprite
        super().__init__()

        # loading image
        self.image = pygame.image.load("player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 200))

        # creating rectangular hitbox
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-200)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        # moving up/down
        if self.rect.top > 0:
            if pressed_keys[K_UP]:
                self.rect.move_ip(0, -1 * SPEED - 5)
        if self.rect.bottom < SCREEN_HEIGHT:
            if pressed_keys[K_DOWN]:
                self.rect.move_ip(0, SPEED - 5)

        # moving left/right
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-1 * SPEED - 5, 0)
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(SPEED - 5, 0)
    

# making the enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_group):
        # initiating super
        super().__init__()

        self.image = pygame.image.load("enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 200))

        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), -200)
        self.mask = pygame.mask.from_surface(self.image)#pygame.transform.scale(self.image, (100, 200)))

        # making sure the enemies don't overlap 
        valid_position = False 
        while not valid_position:
            self.rect.center = (random.randint(50, SCREEN_WIDTH - 50), random.randint(-400, -200))
            if not pygame.sprite.spritecollideany(self, enemy_group):
                valid_position = True 

"""




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
        
        # background image
        displaysurface.blit(background, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((250, 250, 250, 80)) 
        displaysurface.blit(overlay, (0, 0))
        
        # displaying title and high score
        title = font.render("Platformer", True, WHITE)
        displaysurface.blit(title, (WIDTH/2 - title.get_width()/2, 150))
        high_score = font.render(f"High Score: {HIGH_SCORE}", True, WHITE)
        displaysurface.blit(high_score, (WIDTH/2 - high_score.get_width()/2, 230))

        # buttons
        start_btn = draw_button("Start Game", WIDTH/2 - 150, 320, 300, 60, GRAY, DARK_GRAY, mouse_pos)
        settings_btn = draw_button("Settings", WIDTH/2 - 150, 410, 300, 60, GRAY, DARK_GRAY, mouse_pos)
        quit_btn = draw_button("Quit", WIDTH/2 - 150, 500, 300, 60, GRAY, DARK_GRAY, mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT: 
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
    global MAX_ENEMIES, VOLUME_LEVEL, IS_MUTED, PRE_MUTE_VOLUME
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        # background
        displaysurface.blit(background, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((250, 250, 250, 80)) 
        displaysurface.blit(overlay, (0, 0))

        # displaying title
        title = font.render("Settings", True, BLUE)
        displaysurface.blit(title, (WIDTH/2 - title.get_width()/2, 80))

        # max number of enemies
        lbl_enemies = font.render("Max enemies: ", True, WHITE)
        num_enemies = font.render(f"{MAX_ENEMIES}", True, WHITE)
        
        row1_total_width = lbl_enemies.get_width() + 60 + 15 + num_enemies.get_width() + 15 + 60
        start_x1 = WIDTH / 2 - row1_total_width / 2
        y1 = 220
        
        displaysurface.blit(lbl_enemies, (start_x1, y1))
        btn_e_minus = draw_button("-", start_x1 + lbl_enemies.get_width(), y1 - 5, 60, 60, GRAY, DARK_GRAY, mouse_pos)
        displaysurface.blit(num_enemies, (btn_e_minus.right + 15, y1))
        btn_e_plus = draw_button("+", btn_e_minus.right + 15 + num_enemies.get_width() + 15, y1 - 5, 60, 60, GRAY, DARK_GRAY, mouse_pos)

        # audio volume
        lbl_volume = font.render("Audio volume: ", True, WHITE)
        volume_display_str = "Muted" if IS_MUTED else f"{VOLUME_LEVEL}"
        num_volume = font.render(volume_display_str, True, WHITE)
        
        row2_total_width = lbl_volume.get_width() + 110 + 15 + 60 + 15 + num_volume.get_width() + 15 + 60
        start_x2 = WIDTH / 2 - row2_total_width / 2
        y2 = 340
        
        displaysurface.blit(lbl_volume, (start_x2, y2))
        mute_label = "Unmute" if IS_MUTED else "Mute"
        btn_mute = draw_button(mute_label, start_x2 + lbl_volume.get_width(), y2 - 5, 110, 60, GRAY, DARK_GRAY, mouse_pos)
        btn_v_minus = draw_button("-", btn_mute.right + 15, y2 - 5, 60, 60, GRAY, DARK_GRAY, mouse_pos)
        displaysurface.blit(num_volume, (btn_v_minus.right + 15, y2))
        btn_v_plus = draw_button("+", btn_v_minus.right + 15 + num_volume.get_width() + 15, y2 - 5, 60, 60, GRAY, DARK_GRAY, mouse_pos)

        # back button
        btn_back = draw_button("Back to Menu", WIDTH/2 - 150, 480, 300, 60, GRAY, DARK_GRAY, mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # enemies
                if btn_e_minus.collidepoint(mouse_pos):
                    if MAX_ENEMIES > 1: MAX_ENEMIES -= 1
                elif btn_e_plus.collidepoint(mouse_pos):
                    if MAX_ENEMIES < 10: MAX_ENEMIES += 1
                
                # volume
                elif btn_v_minus.collidepoint(mouse_pos):
                    if VOLUME_LEVEL > 0:
                        VOLUME_LEVEL -= 1
                        IS_MUTED = True if VOLUME_LEVEL == 0 else False
                        pygame.mixer.music.set_volume(VOLUME_LEVEL / 10.0)
                elif btn_v_plus.collidepoint(mouse_pos):
                    if VOLUME_LEVEL < 10:
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
    
