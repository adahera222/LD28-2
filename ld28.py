#!/usr/bin/env python

import os.path

# import basic pygame modules
import pygame
from pygame.locals import *

main_dir = os.path.split(os.path.abspath(__file__))[0]

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

def main():
    pygame.init()
    if pygame.mixer and not pygame.mixer.get_init():
        print ('Warning, no sound')
        pygame.mixer = None

    fps = 30
    fps_clock = pygame.time.Clock()
    screen_width, screen_height = 1920, 1080
    display_surface = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    game_over = False
    
    if pygame.mixer:
        music = os.path.join(main_dir, 'POL-rocket-station-short.wav')
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

    while not game_over: #main game loop
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_LEFTBRACKET or event.key == K_RIGHTBRACKET):
                game_over = True
                
        pygame.display.update()
        fps_clock.tick(fps)
    #end main game loop
    pygame.quit()

if __name__ == "__main__":
    main()