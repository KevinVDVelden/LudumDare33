import pygame
import sys
import cProfile
pygame.init()

import game

from base.init import *
from base.frame import *
from base.drawing import *

initAssets()

accumelator = 0
lastTime = pygame.time.get_ticks() - 1

from mainmenu import *
game.scene = MainMenu()

game.fonts['menu'] = pygame.font.Font( 'fonts/kenvector_future_thin.ttf', 48 )
game.fonts['resources'] = pygame.font.Font( 'fonts/kenvector_future_thin.ttf', 16 )
game.fonts['description'] = pygame.font.Font( 'fonts/kenvector_future_thin.ttf', 12 )
game.fonts['gameover1'] = pygame.font.Font( 'fonts/kenvector_future_thin.ttf', 32 )
game.fonts['gameover2'] = pygame.font.Font( 'fonts/kenvector_future_thin.ttf', 12 )
game.fonts['gameover3'] = pygame.font.Font( 'fonts/kenvector_future_thin.ttf', 8 )

while game.gameIsRunning:
    curTime = pygame.time.get_ticks()
    lastFrameTime = curTime - lastTime
    lastTime = curTime

    accumelator += lastFrameTime
    game.accumelator = accumelator / 200

    frameTime = lastFrameTime / 1000 #Given in miliseconds, converting it to a float of unit seconds

    game.scene.doFrame( frameTime )

    pygame.display.set_caption( 'Untitled game (%f/%d frametime. %d/%d camera)' % ( frameTime, accumelator, game.cameraPosX, game.cameraPosY ) )
    if accumelator > 200:
        #cProfile.run( 'game.scene.doTick()' )
        game.scene.doTick()

        skipped = -1
        while accumelator > 200:
            accumelator -= 200
            skipped += 1
        if skipped > 0:
            print( 'Skipping %d ticks.' % skipped )

    sys.stdout.flush()
    pygame.display.flip()
