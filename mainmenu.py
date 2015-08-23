from scene import Scene
import pygame
import base
import game
import util
import config

keysPressed = base.frame.keysPressed

from widgets import *

from gamescene import GameScene

class GuiScene( Scene ):
    def __init__( self ):
        super().__init__()

        self.widgets = []

    def init( self ):
        return True

    def getButtonRect( self, _ ):
        width = 300
        height = 40

        return pygame.Rect( ( game.SCREEN_SIZE[0] - width ) / 2, 60 * len( self.widgets ) + 20, width, height )

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

    def backCb( self, _ ):
        self.nextScene = self.parent


class IconMenu( GuiScene ):
    def __init__( self, icon ):
        super().__init__()

        self.widgets.append( Icon( pygame.Rect( 0,0,game.SCREEN_SIZE[0], game.SCREEN_SIZE[1] ), game.assets[icon] ) )
        self.widgets.append( TextButton( pygame.Rect( game.SCREEN_SIZE[0]-40, 0,40,40 ), 'Back', callback=self.backCb, font='gameover2' ) )


class MainMenu( GuiScene ):
    def __init__( self ):
        super().__init__()

        def startCallback( _ ):
            #TODO: Add a loadingscreen here
            self.nextScene = GameScene()

        self.widgets.append( TextButton( None, 'Start', layoutFunc = self.getButtonRect, callback=startCallback ) )

        def help1( _ ):
            self.nextScene = IconMenu( 'img/readme.png' )
        self.widgets.append( TextButton( None, 'Read me', layoutFunc = self.getButtonRect, callback=help1 ) )

        def help2( _ ):
            print( 'help2!' )
            self.nextScene = IconMenu( 'img/tutorial.png' )
        self.widgets.append( TextButton( None, 'Tutorial', layoutFunc = self.getButtonRect, callback=help2 ) )

        def quitCallback( _ ):
            game.gameIsRunning = False
        self.widgets.append( TextButton( None, 'Quit', layoutFunc = self.getButtonRect, callback=quitCallback ) )

