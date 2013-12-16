#!/usr/bin/env python

import os.path, random, operator, math

# import basic pygame modules
import pygame
from pygame.locals import *

# game constants
SCREENRECT      = Rect(0, 0, 1920, 1080)
MAX_SHOTS       = 1
ENEMY_RELOAD    = 20
ENEMY_ODDS      = 25
SCORE           = 0
BOMB_ODDS       = 10

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
        self.padding = 32
        self.hitbox = pygame.Rect(map(operator.add, self.rect, (self.padding, self.padding, -self.padding*2, -self.padding*2)))

    def update(self):
        self.hitbox = pygame.Rect(map(operator.add, self.rect, (self.padding, self.padding, -self.padding*2, -self.padding*2)))

    def move(self, direction):
        self.rect.move_ip(direction[0]*self.speed, direction[1]*self.speed)
        self.rect = self.rect.clamp(SCREENRECT)

class Shot(pygame.sprite.Sprite):
    speed = -11
    images = []
    def __init__(self, pos, t=None):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)
        self.homing = False if (t == None) else True
        self.target = t

    def update(self):
        if self.homing and self.target != None:
            dx = self.target.rect.x + self.target.rect.width/2 - self.rect.x - self.rect.width/2
            if (dx > 0):
                dx = min(dx, math.fabs(self.speed))
            else:
                dx = max(dx, -math.fabs(self.speed))
            self.rect.move_ip(dx, self.speed)
        else:
            self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.speed = math.fabs(self.speed)
            self.homing = True
        if self.rect.bottom >= SCREENRECT.height:
            self.speed = -math.fabs(self.speed)
        self.rect = self.rect.clamp(SCREENRECT)

class Enemy(pygame.sprite.Sprite):
    speed = 10
    animcycle = 12
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1,1)) * Enemy.speed
        self.ydir = 1
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing;
            if self.ydir == 1:
                self.rect.top = self.rect.bottom + 1
            else:
                self.rect.bottom = self.rect.top - 1
            if self.rect.bottom > SCREENRECT.height:
                self.ydir = -math.fabs(self.ydir)
            if self.rect.top < 0:
                self.ydir = math.fabs(self.ydir)
            self.rect = self.rect.clamp(SCREENRECT)

class Explosion(pygame.sprite.Sprite):
    defaultlife = 12
    animcycle = 3
    images = []
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life//self.animcycle%2]
        if self.life <= 0: self.kill()

class Bomb(pygame.sprite.Sprite):
    speed = 9
    images = []
    def __init__(self, alien):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=
                    alien.rect.move(0,5).midbottom)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom >= SCREENRECT.height - 32:
            Explosion(self)
            self.kill()

class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = Color('white')
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(20, SCREENRECT.height - 20)

    def update(self):
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)

class Starfield():
    def __init__(self, screen):
        global stars
        stars = []
        for i in range(200):
            star = [random.randrange(0,SCREENRECT.width), random.randrange(0,SCREENRECT.height), random.choice([1,2,3])]
            stars.append(star)

    def update(self, screen):
        global stars
        for star in stars:
            star[1] += star[2]
            if star[1] >= SCREENRECT.height:
                star[1] = 0
                star[0] = random.randrange(0,SCREENRECT.width)
                star[2] = random.choice([1,2,3])

            if star[2] == 1:
                color = (100,100,100)
            elif star[2] == 2:
                color = (190,190,190)
            elif star[2] == 3:
                color = (255,255,255)

            pygame.draw.rect(screen, color, (star[0],star[1],star[2],star[2]))

def main():
    pygame.init()
    random.seed()

    #Detect and initialize joysticks for input
    pygame.joystick.init()
    joysticks = []
    for i in range(0, pygame.joystick.get_count()):
        joysticks.append(pygame.joystick.Joystick(i))
        joysticks[-1].init()

    if pygame.mixer and not pygame.mixer.get_init():
        print ('Warning, no sound')
        pygame.mixer = None

    fps = 60
    fps_clock = pygame.time.Clock()
    screen_width, screen_height = 1920, 1080
    winstyle = pygame.FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    game_over = False

    Player.images = [load_image('player_ship.gif')]
    img = load_image('explosion.gif')
    Explosion.images = [img, pygame.transform.flip(img, 1, 1)]
    Shot.images = [load_image('shot.gif')]
    Enemy.images = [load_image('enemy.gif')]
    Bomb.images = [load_image('bomb.gif')]

    icon = pygame.transform.scale(Enemy.images[0], (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Pygame Aliens')
    pygame.mouse.set_visible(0)

    # initialize game groups
    enemies = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
    lastenemy = pygame.sprite.GroupSingle()

    # assign default groups to each sprite class
    Player.containers = all
    Enemy.containers = enemies, all, lastenemy
    Shot.containers = shots, all
    Bomb.containers = bombs, all
    Explosion.containers = all
    Score.containers = all

    # load the sound effects/music
    explode_sound = load_sound('explode.wav')
    shoot_sound = load_sound('shoot1.wav')
    if pygame.mixer:
        music = os.path.join(main_dir, 'data', 'bgmusic.mid')
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

    global score
    enemy_reload = ENEMY_RELOAD
    kills = 0

    global SCORE
    player = Player()
    Enemy()
    if pygame.font:
        all.add(Score())

    starfield = Starfield(screen)

    while not game_over: #main game loop
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and \
              (event.key == K_ESCAPE or event.key == K_LEFTBRACKET or event.key == K_RIGHTBRACKET):
                game_over = True
        keystate = pygame.key.get_pressed()

        screen.fill((0,0,0))
        starfield.update(screen)

        #update all the sprites
        all.update()

        #handle player input
        (dx, dy) = (keystate[K_RIGHT] - keystate[K_LEFT], keystate[K_DOWN] - keystate[K_UP])
        if pygame.joystick.get_count() > 0:
            (dx, dy) = pygame.joystick.Joystick(0).get_hat(0)
            dy = -dy
        firing = keystate[K_SPACE]
        if pygame.joystick.get_count() > 0:
            firing = pygame.joystick.Joystick(0).get_button(0)
        if not player.reloading and firing and len(shots) < MAX_SHOTS:
            Shot((player.rect.centerx, player.rect.top), player)
            shoot_sound.play()
        player.reloading = firing
        player.move((dx, dy))
        firing = keystate[K_SPACE]
        if pygame.joystick.get_count() > 0:
            firing = pygame.joystick.Joystick(0).get_button(0)

        # create new enemy
        if enemy_reload:
            enemy_reload -= 1
        elif not int(random.random() * ENEMY_ODDS):
            Enemy()
            enemy_reload = ENEMY_RELOAD

        # drop bombs
        if lastenemy and not int(random.random() * BOMB_ODDS):
            Bomb(lastenemy.sprite)

        # detect collisions
        for enemy in enemies.sprites():
            if (player.hitbox.colliderect(enemy.rect)):
                explode_sound.play()
                Explosion(enemy)
                Explosion(player)
                SCORE = SCORE + 1
                player.kill()
                game_over = True

        for shot in pygame.sprite.groupcollide(shots, enemies, 0, 1).keys():
            explode_sound.play()
            Explosion(shot)
            shot.speed = -shot.speed
            shot.homing = True
            SCORE = SCORE + 1

        for shot in shots.sprites():
            if player.hitbox.colliderect(shot.rect):
                shot.kill()

        for bomb in bombs.sprites():
            if (player.hitbox.colliderect(bomb.rect)):
                explode_sound.play()
                Explosion(bomb)
                bomb.kill()
                player.kill()
                game_over = True

        all.draw(screen)
        pygame.display.update()
        fps_clock.tick(fps)

    #end main game loop

    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)
    pygame.time.wait(1000)
    pygame.quit()

if __name__ == "__main__":
    main()