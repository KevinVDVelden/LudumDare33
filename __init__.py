import pygame
import sys
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

game.fonts['menu'] = pygame.font.Font( 'fonts/OpenScrawl_v1.ttf', 48 )

while game.gameIsRunning:
    curTime = pygame.time.get_ticks()
    lastFrameTime = curTime - lastTime
    lastTime = curTime

    frameTime = lastFrameTime / 1000 #Given in miliseconds, converting it to a float of unit seconds

    game.scene.doFrame( frameTime )

    sys.stdout.flush()
    pygame.display.set_caption( 'Untitled game (%d frametime)' % frameTime )
    pygame.display.flip()
