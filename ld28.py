import pygame
from pygame.locals import *

def main():
    pygame.init()
    fps = 30
    fps_clock = pygame.time.Clock()
    screen_width, screen_height = 1920, 1080
    display_surface = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    game_over = False
    
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