""" 
Pygame tutorial: following https://coderslegacy.com/python/python-pygame-tutorial/ 

@author: B.A. Sturre

Created on 07-06-2026

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

# colours
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (100, 100, 100)

# screen information
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 25
SCORE = 0
HIGH_SCORE = 0 
MAX_ENEMIES = 3

VOLUME_LEVEL = 5
PRE_MUTE_VOLUTE = 5
IS_MUTED = False 

# setting up fonts
font = pygame.font.SysFont("Verdana", 40)
font_small = pygame.font.SysFont("Verdana", 30)

# initializing display window
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# making window fullscreen
DISPLAYSURF = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = DISPLAYSURF.get_size()

DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("star shooter")

# setting the background
background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# playing music
pygame.mixer.music.load("background.wav")
pygame.mixer.music.play(-1)  # -1 so it repeats
pygame.mixer.music.set_volume(VOLUME_LEVEL/10.0)

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
        self.mask = pygame.mask.from_surface(self.image)#pygame.transform.scale(self.image, (65, 160)))

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

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if (self.rect.bottom > SCREEN_HEIGHT):
            SCORE += 1
            #self.rect.top = 0
            #self.rect.center = (random.randint(40, SCREEN_WIDTH - 80), 0)
            self.kill()


# make a button
def draw_button(text, x, y, width, height, normal_color, hover_color, mouse_pos):
    rect = pygame.Rect(x, y, width, height)
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(DISPLAYSURF, hover_color, rect)
    else:
        pygame.draw.rect(DISPLAYSURF, normal_color, rect)

    text_surf = font_small.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    DISPLAYSURF.blit(text_surf, text_rect)
    return rect 


# home screen function 
def home_screen(): 
    while True: 
        mouse_pos = pygame.mouse.get_pos() 
        
        # background image
        DISPLAYSURF.blit(background, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((250, 250, 250, 80)) 
        DISPLAYSURF.blit(overlay, (0, 0))
        
        # displaying title and high score
        title = font.render("Star Shooter", True, WHITE)
        DISPLAYSURF.blit(title, (SCREEN_WIDTH/2 - title.get_width()/2, 150))
        high_score = font.render(f"High Score: {HIGH_SCORE}", True, WHITE)
        DISPLAYSURF.blit(high_score, (SCREEN_WIDTH/2 - high_score.get_width()/2, 230))

        # buttons
        start_btn = draw_button("Start Game", SCREEN_WIDTH/2 - 150, 320, 300, 60, GRAY, DARK_GRAY, mouse_pos)
        settings_btn = draw_button("Settings", SCREEN_WIDTH/2 - 150, 410, 300, 60, GRAY, DARK_GRAY, mouse_pos)
        quit_btn = draw_button("Quit", SCREEN_WIDTH/2 - 150, 500, 300, 60, GRAY, DARK_GRAY, mouse_pos)

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
        DISPLAYSURF.blit(background, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((250, 250, 250, 80)) 
        DISPLAYSURF.blit(overlay, (0, 0))

        # displaying title
        title = font.render("Settings", True, BLUE)
        DISPLAYSURF.blit(title, (SCREEN_WIDTH/2 - title.get_width()/2, 80))

        # max number of enemies
        lbl_enemies = font.render("Max enemies: ", True, WHITE)
        num_enemies = font.render(f"{MAX_ENEMIES}", True, WHITE)
        
        row1_total_width = lbl_enemies.get_width() + 60 + 15 + num_enemies.get_width() + 15 + 60
        start_x1 = SCREEN_WIDTH / 2 - row1_total_width / 2
        y1 = 220
        
        DISPLAYSURF.blit(lbl_enemies, (start_x1, y1))
        btn_e_minus = draw_button("-", start_x1 + lbl_enemies.get_width(), y1 - 5, 60, 60, GRAY, DARK_GRAY, mouse_pos)
        DISPLAYSURF.blit(num_enemies, (btn_e_minus.right + 15, y1))
        btn_e_plus = draw_button("+", btn_e_minus.right + 15 + num_enemies.get_width() + 15, y1 - 5, 60, 60, GRAY, DARK_GRAY, mouse_pos)

        # audio volume
        lbl_volume = font.render("Audio volume: ", True, WHITE)
        volume_display_str = "Muted" if IS_MUTED else f"{VOLUME_LEVEL}"
        num_volume = font.render(volume_display_str, True, WHITE)
        
        row2_total_width = lbl_volume.get_width() + 110 + 15 + 60 + 15 + num_volume.get_width() + 15 + 60
        start_x2 = SCREEN_WIDTH / 2 - row2_total_width / 2
        y2 = 340
        
        DISPLAYSURF.blit(lbl_volume, (start_x2, y2))
        mute_label = "Unmute" if IS_MUTED else "Mute"
        btn_mute = draw_button(mute_label, start_x2 + lbl_volume.get_width(), y2 - 5, 110, 60, GRAY, DARK_GRAY, mouse_pos)
        btn_v_minus = draw_button("-", btn_mute.right + 15, y2 - 5, 60, 60, GRAY, DARK_GRAY, mouse_pos)
        DISPLAYSURF.blit(num_volume, (btn_v_minus.right + 15, y2))
        btn_v_plus = draw_button("+", btn_v_minus.right + 15 + num_volume.get_width() + 15, y2 - 5, 60, 60, GRAY, DARK_GRAY, mouse_pos)

        # back button
        btn_back = draw_button("Back to Menu", SCREEN_WIDTH/2 - 150, 480, 300, 60, GRAY, DARK_GRAY, mouse_pos)

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


# game loop 
def game_loop(): 
    global SPEED, SCORE, HIGH_SCORE

    SPEED = 25
    SCORE = 0
    background_y = 0

    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    P1 = Player()
    all_sprites.add(P1)

    # creating event
    INC_SPEED = pygame.USEREVENT + 1 
    # call the INC_SPEED object every 1000 ms (=1s)
    pygame.time.set_timer(INC_SPEED, 2000)

    # spawning enemies
    SPAWN_ENEMY = pygame.USEREVENT + 2
    # trying to spawn a new enemy every 1-5 seconds
    pygame.time.set_timer(SPAWN_ENEMY, random.randint(0, 2000))

    playing = True

    # running the game
    while playing: 
        # cycling through the events occuring
        for event in pygame.event.get():
            # increasing the speed (every 1 s)
            if event.type == INC_SPEED:
                SPEED += 5
            
            # spawning enemies
            if event.type == SPAWN_ENEMY:
                if len(enemies) < MAX_ENEMIES:
                    E = Enemy(enemies)
                    enemies.add(E)
                    all_sprites.add(E)

                pygame.time.set_timer(SPAWN_ENEMY, random.randint(0, int(10000/SPEED)))

            # quitting
            if event.type == QUIT:
                pygame.quit()
                sys.exit() 

        # moving the background 
        background_y += 5
        if background_y >= SCREEN_HEIGHT:
            background_y = 0

        # drqwing the background and score
        DISPLAYSURF.fill(WHITE)
        DISPLAYSURF.blit(background, (0, background_y))
        DISPLAYSURF.blit(background, (0, background_y - SCREEN_HEIGHT))

        scores = font_small.render(f"Score: {str(SCORE)}", True, GREEN)
        DISPLAYSURF.blit(scores, (40, 40))
        high_score = font_small.render(f"High score: {str(HIGH_SCORE)}", True, GREEN)
        DISPLAYSURF.blit(high_score, (40, 80))

        # drawing the entities
        for entity in all_sprites:
            DISPLAYSURF.blit(entity.image, entity.rect)
            entity.move()
        
        if SCORE > HIGH_SCORE: 
                HIGH_SCORE = SCORE 
            
        # collision
        if pygame.sprite.spritecollide(P1, enemies, False, pygame.sprite.collide_mask) :
            # playing crashing sound
            pygame.mixer.Sound('crash.wav').play()
            #time.sleep(0.5)

            # making screen red
            DISPLAYSURF.fill(RED)
            game_over = font.render("Game Over", True, BLACK)
            DISPLAYSURF.blit(game_over, (SCREEN_WIDTH/2 - game_over.get_width()/2, SCREEN_HEIGHT/2))
            score_go = font.render(f"Score: {str(SCORE)}", True, BLACK)
            DISPLAYSURF.blit(score_go, (SCREEN_WIDTH/2 - score_go.get_width()/2, 3* SCREEN_HEIGHT/4))

            pygame.display.update()

            # killing all the sprites
            for entity in all_sprites:
                # removing sprite from group (-> will no longer be drawn)
                entity.kill()

            # quiting the game
            time.sleep(2)
            playing = False

        # updating the display
        pygame.display.update()
        
        # waiting a bit before 
        FramePerSec.tick(FPS)


# main
if __name__ == "__main__": 
    home_screen()
    
