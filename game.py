SCREEN_SIZE = ( 640, 480 )

gameIsRunning = True

import pygame
screen = pygame.display.set_mode( SCREEN_SIZE )

mapSurface = None
mapSize = None
mapBuffer = None
mapPixelSizeX = None
mapPixelSizeY = None

cameraPosX = 0
cameraPosY = 0

assets = {}
fonts = {}

scene = None
