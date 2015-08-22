from collections import defaultdict
from scene import Scene
import pygame
import base
import game
import gamelogic
import util
import config
import random
import ecs
import flowmap
import threading

keysPressed = base.frame.keysPressed

game.RenderTiles = []

def addTile( tileId, name ):
    while len( game.RenderTiles ) <= tileId:
        game.RenderTiles.append( None )

    img = game.assets[ name ]

    game.RenderTiles[ tileId ] = img

addTile( 10, 'img/land/grass.png' )
addTile( 11, 'img/land/grass_2.png' )
addTile( 12, 'img/land/grass_3.png' )

class GameScene( Scene ):
    def __init__( self ):
        super().__init__()

        self.loadLevel = 0
        self.changingCorruption = dict()
        self.flowThread = None

        self.resources = defaultdict( lambda: ( 0, 0, 0 ) )

    def calculateTileCorruption( self, i ):
        x, y = int( i % game.mapSize[0] ), int( i // game.mapSize[0] )
        corruption = self.corruption.surface[ i ]

        cur = game.mapBuffer[ i ]

        if corruption > 7:
            game.mapBuffer[ i ] = 12
        elif corruption > 0:
            game.mapBuffer[ i ] = 11
        else:
            game.mapBuffer[ i ] = 10

        if cur != game.mapBuffer[ i ]:
            print( 'Redrawing %d' % cur )
            base.drawing.drawMap( ( x, y ), game.RenderTiles[ game.mapBuffer[ i ] ] )
        

    def init( self ):
        return gamelogic.init.init( self )

    def clickTile( self, pos, event ):
        if event.button == 1:
            entities = self.world.entitiesWithComponent( ecs.COMPONENT_BUILDING ).atPosition( pos )
            if len( entities ) == 0:
                ent = self.world.addEntity( pos )
                ent.addComponent( ecs.RenderComponent( 'img/buildings/combined/building_mana_11.png' ) )
                ent.addComponent( gamelogic.BuildingComponent( 'mana' ) )
                ent.addComponent( gamelogic.resources.ResourceStoreComponent( { 'mana': 20 } ) )
                ent.addComponent( gamelogic.resources.ResourceUseComponent( { 'mana': 10 } ) )

                self.changingCorruption[ self.corruption.I( pos ) ] = 1000
            else:
                for ent in entities:
                    self.world.removeEntity( ent )
                self.changingCorruption[ self.corruption.I( pos ) ] = 0
        elif event.button == 3:
            i = self.corruption.I( pos )
            print( self.corruption.surface[ i ], self.corruption.backSurface[ i ] )
            print( self.corruption.resting[ i ], self.corruption.backResting[ i ] )

    def doInput( self, frameTime ):
        for event in base.frame.receiveInput():
            if event.type in ( pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION ):
                handled = False
                for widget in self.widgets:
                    if widget.checkIntersect( event ):
                        handled = True
                        break

                if handled:
                    continue

            if event.type == pygame.MOUSEBUTTONUP:
                mapPosition = ( game.cameraPosX + event.pos[0], game.cameraPosY  + event.pos[1] )
                tilePosition = ( mapPosition[0] // 32, mapPosition[1] // 32 )
                self.clickTile( tilePosition, event )

        if keysPressed[ 'cameraDown' ]:
            game.cameraPosY += config.cameraSpeedY * frameTime
        if keysPressed[ 'cameraUp' ]:                         
            game.cameraPosY -= config.cameraSpeedY * frameTime
        if keysPressed[ 'cameraLeft' ]:                       
            game.cameraPosX -= config.cameraSpeedX * frameTime
        if keysPressed[ 'cameraRight' ]:                      
            game.cameraPosX += config.cameraSpeedX * frameTime

        game.cameraPosX = util.clamp( game.cameraPosX, 0, game.mapPixelSizeX - game.SCREEN_SIZE[0] )
        game.cameraPosY = util.clamp( game.cameraPosY, 0, game.mapPixelSizeY - game.SCREEN_SIZE[1] )

    def drawGame( self, frameTime ):
        for x in range( int( game.cameraPosX // 32 - 1 ), int( ( game.cameraPosX + game.SCREEN_SIZE[0] ) // 32 + 1 ) ):
            for y in range( int( game.cameraPosY // 32 - 1 ), int( ( game.cameraPosY + game.SCREEN_SIZE[1] ) // 32 + 1 ) ):
                i = x + ( y * game.mapSize[0] )
                corruption = self.corruption.surface[ i ]

                cur = game.mapBuffer[ i ]

                if corruption > 7:
                    game.mapBuffer[ i ] = 12
                elif corruption > 1:
                    game.mapBuffer[ i ] = 11
                else:
                    game.mapBuffer[ i ] = 10

                if cur != game.mapBuffer[ i ]:
                    base.drawing.drawMap( ( x, y ), game.RenderTiles[ game.mapBuffer[ i ] ] )

        base.drawing.renderMap( ( int( game.cameraPosX ), int( game.cameraPosY ) ) )

    def doFrame( self, frameTime ):
        self.doInput( frameTime )
        self.drawGame( frameTime )
        self.world.doFrame( frameTime, game.accumelator )
        gamelogic.draw.drawGui( self, frameTime, game.accumelator )

    def doTick( self ):
        self.world.doTick()
        gamelogic.resources.calculateResources( self )

        if self.flowThread is None or not self.flowThread.is_alive():
            self.corruption.swap()

            for n in self.changingCorruption:
                self.corruption.addSource( n, self.changingCorruption[ n ] )

            self.flowThread = threading.Thread( target = lambda: self.corruption.cleanIterative() )
            self.flowThread.start()

            self.changingCorruption = dict()
        else:
            print( 'WARNING: Flow update thread not done on time!' )
            self.corruption.cleanIterative()
