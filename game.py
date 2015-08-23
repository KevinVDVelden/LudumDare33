SCREEN_SIZE = ( 1280, 768 )

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

dayTicks = 300
minDayTicks = 100
baseDayTicks = 200
dayTicksReductionEvery = 150

baseEnemyAmount = 125
enemyPerNight = 35
