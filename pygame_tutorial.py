""" 
Pygame tutorial: following https://coderslegacy.com/python/python-pygame-tutorial/ 

@author: B.A. Sturre

Created on 07-06-2026

"""

import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore", UserWarning)

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

# screen information
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0

# setting up fonts
font = pygame.font.SysFont("Verdana", 40)
font_small = pygame.font.SysFont("Verdana", 30)
game_over = font.render("Game Over", True, BLACK)

# initializing display window
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# making window fullscreen
DISPLAYSURF = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = DISPLAYSURF.get_size()

DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("pygame tutorial")

# setting the background
background = pygame.image.load("AnimatedStreet.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# playing music
pygame.mixer.music.load("background.wav")
pygame.mixer.music.play(-1)  # -1 so it repeats
pygame.mixer.music.set_volume(0.2)

# making the player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        # initiating the pygame.sprite.Sprite
        super().__init__()

        # loading image
        self.image = pygame.image.load("Player.png")
        self.image = pygame.transform.scale(self.image, (100, 200))

        # creating rectangular hitbox
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-80)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        # moving up/down
        if self.rect.top > 0:
            if pressed_keys[K_UP]:
                self.rect.move_ip(0, -5)
        if self.rect.bottom < SCREEN_WIDTH:
            if pressed_keys[K_DOWN]:
                self.rect.move_ip(0, 5)

        # moving left/right
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)
    

# making the enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        # initiating super
        super().__init__()

        self.image = pygame.image.load("Enemy.png")
        self.image = pygame.transform.scale(self.image, (80, 120))

        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if (self.rect.bottom > SCREEN_HEIGHT):
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 80), 0)


# initiating enemy and player
E1 = Enemy()
P1 = Player()

# creating sprites group
enemies = pygame.sprite.Group()
enemies.add(E1)
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)

# creating event
INC_SPEED = pygame.USEREVENT + 1 
# call the INC_SPEED object every 1000 ms (=1s)
pygame.time.set_timer(INC_SPEED, 2000)

# running the game
while True: 
    # cycling through the events occuring
    for event in pygame.event.get():
        # increasing the speed (every 1 s)
        if event.type == INC_SPEED:
            SPEED += 2

        # quitting
        if event.type == QUIT:
            pygame.quit()
            sys.exit() 

    # drawing the enemy and player
    DISPLAYSURF.fill(WHITE)

    # drqwing the background and score
    DISPLAYSURF.blit(background, (0, 0))
    scores = font_small.render(str(SCORE), True, BLACK)
    DISPLAYSURF.blit(scores, (10, 10))

    # drawing the entities
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()
        
    # collision
    if pygame.sprite.spritecollideany(P1, enemies):
        # playing crashing sound
        pygame.mixer.Sound('crash.wav').play()
        time.sleep(0.5)

        # making screen red
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(scores, (10, 10))
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()

        # killing all the sprites
        for entity in all_sprites:
            # removing sprite from group (-> will no longer be drawn)
            entity.kill()
        
        # quiting the game
        time.sleep(2)
        pygame.quit()
        sys.exit()

    # updating the display
    pygame.display.update()
    
    # waiting a bit before 
    FramePerSec.tick(FPS)
