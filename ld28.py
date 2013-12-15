#!/usr/bin/env python

import os.path, random

# import basic pygame modules
import pygame
from pygame.locals import *

# game constants
SCREENRECT      = Rect(0, 0, 1920, 1080)
MAX_SHOTS       = 1
ENEMY_RELOAD    = 12
ENEMY_ODDS      = 25

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs

class dummysound:
    def play(self): pass

def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()

class Player(pygame.sprite.Sprite):
    speed = 10
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

    def move(self, direction):
        self.rect.move_ip(direction[0]*self.speed, direction[1]*self.speed)
        self.rect = self.rect.clamp(SCREENRECT)

class Shot(pygame.sprite.Sprite):
    speed = -11
    images = []
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    speed = 10
    animcycle = 12
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1,1)) * Enemy.speed
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing;
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)

def main():
    pygame.init()
    random.seed()
    if pygame.mixer and not pygame.mixer.get_init():
        print ('Warning, no sound')
        pygame.mixer = None

    fps = 45
    fps_clock = pygame.time.Clock()
    screen_width, screen_height = 1920, 1080
    winstyle = pygame.FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    game_over = False
    
    img = load_image('player_ship.gif')
    Player.images = [img, pygame.transform.flip(img, 1, 0)]
    Shot.images = [load_image('shot.gif')]
    Enemy.images = [load_image('enemy.gif')]

    pygame.display.set_caption('Pygame Aliens')
    pygame.mouse.set_visible(0)

    #create the background, tile the bgd image
    bgdtile = load_image('background.gif')
    background = pygame.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        for y in range(0, SCREENRECT.height, bgdtile.get_height()):
            background.blit(bgdtile, (x, y))
    screen.blit(background, (0,0))
    pygame.display.flip()

    enemies = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()

    Player.containers = all
    Enemy.containers = enemies, all
    Shot.containers = shots, all

    # load the sound effects/music
    explode_sound = load_sound('explode.wav')
    shoot_sound = load_sound('shoot1.wav')
    if pygame.mixer:
        music = os.path.join(main_dir, 'data', 'POL-rocket-station-short.wav')
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

    enemy_reload = ENEMY_RELOAD
    kills = 0

    player = Player()
    Enemy()

    while not game_over: #main game loop
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and \
              (event.key == K_ESCAPE or event.key == K_LEFTBRACKET or event.key == K_RIGHTBRACKET):
                game_over = True
        keystate = pygame.key.get_pressed()

        # clear/erase the last drawn sprites
        all.clear(screen, background)

        #update all the sprites
        all.update()

        #handle player input
        direction = (keystate[K_RIGHT] - keystate[K_LEFT], keystate[K_DOWN] - keystate[K_UP])
        firing = keystate[K_SPACE]
        if not player.reloading and firing and len(shots) < MAX_SHOTS:
            Shot((player.rect.centerx, player.rect.top))
            shoot_sound.play()
        player.reloading = firing
        player.move(direction)
        firing = keystate[K_SPACE]

        # create new enemy
        if enemy_reload:
            enemy_reload -= 1
        elif not int(random.random() * ENEMY_ODDS):
            Enemy()
            enemy_reload = ENEMY_RELOAD

        # detect collisions
        for enemy in pygame.sprite.spritecollide(player, enemies, 1):
            explode_sound.play()
            player.kill()
            game_over = True

        for enemy in pygame.sprite.groupcollide(shots, enemies, 1, 1).keys():
            explode_sound.play()
            #Explosion(alien)
            #SCORE = SCORE + 1

        #draw the scene
        dirty = all.draw(screen)
        pygame.display.update(dirty)
        fps_clock.tick(fps)

    #end main game loop

    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)
    pygame.time.wait(1000)
    pygame.quit()

if __name__ == "__main__":
    main()