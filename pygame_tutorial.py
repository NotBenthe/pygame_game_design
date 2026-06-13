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
SPEED = 25
SCORE = 0
MAX_ENEMIES = 3

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
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
background_y = 0  # tracking vertical position

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
                self.rect.move_ip(0, -1 * SPEED)
        if self.rect.bottom < SCREEN_HEIGHT:
            if pressed_keys[K_DOWN]:
                self.rect.move_ip(0, SPEED)

        # moving left/right
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-1 * SPEED, 0)
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(SPEED, 0)
    

# making the enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
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
            if not pygame.sprite.spritecollideany(self, enemies):
                valid_position = True 

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if (self.rect.bottom > SCREEN_HEIGHT):
            SCORE += 1
            #self.rect.top = 0
            #self.rect.center = (random.randint(40, SCREEN_WIDTH - 80), 0)
            self.kill()


# initiating enemy and player
P1 = Player()

# creating sprites group
enemies = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)


# creating event
INC_SPEED = pygame.USEREVENT + 1 
# call the INC_SPEED object every 1000 ms (=1s)
pygame.time.set_timer(INC_SPEED, 2000)

# spawning enemies
SPAWN_ENEMY = pygame.USEREVENT + 2
# trying to spawn a new enemy every 1-5 seconds
pygame.time.set_timer(SPAWN_ENEMY, random.randint(1000, 3000))

# running the game
while True: 
    # cycling through the events occuring
    for event in pygame.event.get():
        # increasing the speed (every 1 s)
        if event.type == INC_SPEED:
            SPEED += 2
        
        # spawning enemies
        if event.type == SPAWN_ENEMY:
            if len(enemies) < MAX_ENEMIES:
                E = Enemy()
                enemies.add(E)
                all_sprites.add(E)

            pygame.time.set_timer(SPAWN_ENEMY, random.randint(int(10000/SPEED), int(30000/SPEED)))

        # quitting
        if event.type == QUIT:
            pygame.quit()
            sys.exit() 

    # drawing the enemy and player
    DISPLAYSURF.fill(WHITE)

    # moving the background 
    background_y += 5
    if background_y >= SCREEN_HEIGHT:
        background_y = 0

    # drqwing the background and score
    DISPLAYSURF.blit(background, (0, background_y))
    DISPLAYSURF.blit(background, (0, background_y - SCREEN_HEIGHT))

    scores = font_small.render(str(SCORE), True, GREEN)
    DISPLAYSURF.blit(scores, (40, 40))

    # drawing the entities
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()
        
    # collision
    if pygame.sprite.spritecollide(P1, enemies, False, pygame.sprite.collide_mask) :
        # playing crashing sound
        pygame.mixer.Sound('crash.wav').play()
        #time.sleep(0.5)

        # making screen red
        DISPLAYSURF.fill(RED)
        #DISPLAYSURF.blit(scores, (40, 40))
        DISPLAYSURF.blit(game_over, (SCREEN_WIDTH/2-200, SCREEN_HEIGHT/2))
        score_go = font.render(f"Score: {str(SCORE)}", True, BLACK)
        DISPLAYSURF.blit(score_go, (SCREEN_WIDTH/2-200, 3* SCREEN_HEIGHT/4))

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
