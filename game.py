SCREEN_SIZE = ( 1024, 640 )

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
dayTicksReductionEvery = 100

baseEnemyAmount = 75
enemyPerNight = 50
enemyPerNightPower = 1.5
