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

global RenderTiles
RenderTiles = []

def addTile( tileId, name ):
    while len( RenderTiles ) <= tileId:
        RenderTiles.append( None )

    img = game.assets[ name ]

    RenderTiles[ tileId ] = img

addTile( 10, 'img/land/grass.png' )
addTile( 11, 'img/land/grass_2.png' )
addTile( 12, 'img/land/grass_3.png' )

def centerCameraOnTile( pos ):
    game.cameraPosX = ( pos[0] * 32 + 16 ) - game.SCREEN_SIZE[0] / 2
    game.cameraPosY = ( pos[1] * 32 + 16 ) - game.SCREEN_SIZE[1] / 2

class GameScene( Scene ):
    def __init__( self ):
        super().__init__()

        self.loadLevel = 0
        self.changingCorruption = dict()
        self.flowThread = None

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
            base.drawing.drawMap( ( x, y ), RenderTiles[ game.mapBuffer[ i ] ] )
        

    def init( self ):
        if self.loadLevel == 0:
            base.drawing.initMap( ( 256, 256 ) )
        elif self.loadLevel == 1:
            for i in range( len( game.mapBuffer ) ):
                game.mapBuffer[ i ] = 10

            flow = flowmap.Flowmap( game.mapSize )
            self.corruption = flow
        elif self.loadLevel == 10:
            global RenderTiles
            for x in range( 256 ):
                for y in range( 256 ):
                    base.drawing.drawMap( ( x, y ), RenderTiles[ game.mapBuffer[ x + y * 256 ] ] )
        elif self.loadLevel == 19:
            self.world = ecs.World()

            for x in range( 127, 130 ):
                for y in range( 127, 130 ):
                    pos = ( x, y )
                    ent = self.world.addEntity( pos )
                    ent.addComponent( ecs.RenderComponent( 'img/buildings/combined/building_mana_11.png' ) )
                    ent.addComponent( gamelogic.BuildingComponent( 'heart' ) )
                    self.changingCorruption[ self.corruption.I( pos ) ] = 2000
        elif self.loadLevel > 20:
            centerCameraOnTile( ( 128, 128 ) )
            return True

        self.loadLevel += 1
        return False

    def clickTile( self, pos, event ):
        if event.button == 1:
            entities = self.world.entitiesWithComponent( ecs.COMPONENT_BUILDING ).atPosition( pos )
            if len( entities ) == 0:
                ent = self.world.addEntity( pos )
                ent.addComponent( ecs.RenderComponent( 'img/buildings/combined/building_mana_11.png' ) )
                ent.addComponent( gamelogic.BuildingComponent( 'mana' ) )

                self.changingCorruption[ self.corruption.I( pos ) ] = 1000
            else:
                for ent in entities:
                    self.world.removeEntity( ent )
        elif event.button == 3:
            i = self.corruption.I( pos )
            print( self.corruption.surface[ i ], self.corruption.backSurface[ i ] )
            print( self.corruption.resting[ i ], self.corruption.backResting[ i ] )

    def doInput( self, frameTime ):
        #TODO: Get back input
        for event in base.frame.receiveInput():
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
                    base.drawing.drawMap( ( x, y ), RenderTiles[ game.mapBuffer[ i ] ] )

        base.drawing.renderMap( ( int( game.cameraPosX ), int( game.cameraPosY ) ) )

    def doFrame( self, frameTime ):
        self.doInput( frameTime )
        self.drawGame( frameTime )
        self.world.doFrame( frameTime, game.accumelator )

    def doTick( self ):
        self.world.doTick()

        if self.flowThread is None or not self.flowThread.is_alive():
            self.corruption.swap()

            for n in self.changingCorruption:
                self.corruption.addSource( n, self.changingCorruption[ n ] )

            self.corruption.cleanIterative()
            #self.flowThread = threading.Thread( target = lambda: self.corruption.cleanIterative() )
            #self.flowThread.start()
        else:
            print( 'WARNING: Flow update thread not done on time!' )
            #self.corruption.cleanIterative()

        #changeDone = set()
        #for index in self.changingCorruption:
        #    neighbourVal = max( [ self.corruption.surface[ index + n ] for n in self.corruption.offsets ] )
        #    curVal = self.corruption.surface[ index ]

        #    target = self.changingCorruption[ index ]


        #    if target == 0:
        #        if neighbourVal >= curVal:
        #            curVal = 0

        #        if curVal == 0:
        #            changeDone.add( index )

        #        self.corruption.addSource( index, curVal - 1 )
        #    else:
        #        if curVal + 1 >= target:
        #            changeDone.add( index )
        #            curVal = target - 1

        #        self.corruption.addSource( index, curVal + 1 )

        #for n in self.corruption.clean():
        #    self.calculateTileCorruption( n )
        #for n in self.changingCorruption:
        #    self.calculateTileCorruption( n )

        #for done in changeDone:
        #    del self.changingCorruption[ done ]


