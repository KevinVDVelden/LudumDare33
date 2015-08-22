from scene import Scene
import pygame
import base
import game
import util
import config

keysPressed = base.frame.keysPressed

from widgets import *

from gamescene import GameScene

class MainMenu( Scene ):
    def __init__( self ):
        super().__init__()

        self.widgets = []
        def getButtonRect( _ ):
            width = 200
            height = 40

            return pygame.Rect( ( game.SCREEN_SIZE[0] - width ) / 2, 60 * len( self.widgets ) + 20, width, height )

        def startCallback( _ ):
            #TODO: Add a loadingscreen here
            self.nextScene = GameScene()

        self.widgets.append( TextButton( None, 'Start', layoutFunc = getButtonRect, callback=startCallback ) )

        def quitCallback( _ ):
            game.gameIsRunning = False
        self.widgets.append( TextButton( None, 'Quit', layoutFunc = getButtonRect, callback=quitCallback ) )

    def doInput( self, frameTime ):
        for event in base.frame.receiveInput():
            if event.type in ( pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN ):
                for n in self.widgets:
                    n.checkIntersect( event )
            else:
                print( event )

    def doFrame( self, frameTime ):
        game.screen.fill( ( 30, 90, 80 ) )
        super().doFrame( frameTime )
        self.doInput( frameTime )

        for n in self.widgets:
            n.draw( game.screen )

    def doTick( self ):
        pass
