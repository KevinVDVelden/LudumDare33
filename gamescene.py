from scene import Scene
import base
import game
import gamelogic
import util
import config
import random
import ecs

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

    def init( self ):
        if self.loadLevel == 0:
            base.drawing.initMap( ( 256, 256 ) )
        elif self.loadLevel == 1:
            for i in range( len( game.mapBuffer ) ):
                game.mapBuffer[ i ] = 10

            i = 0
            for x in range( 256 ):
                for y in range( 256 ):
                    spawnDist = ( ( x - 128 ) ** 2 + ( y - 128 ) ** 2 ) - ( 10 + random.random() * 5 ) ** 2
                    if spawnDist > 0:
                        game.mapBuffer[ i ] = 10
                    elif spawnDist < -(10**2):
                        game.mapBuffer[ i ] = 12
                    else:
                        game.mapBuffer[ i ] = 11
                    

                    i += 1

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
                    ent.addComponent( gamelogic.BuildingComponent( 'mana' ) )
        elif self.loadLevel > 20:
            centerCameraOnTile( ( 128, 128 ) )
            return True

        self.loadLevel += 1
        return False

    def doInput( self, frameTime ):
        #TODO: Get back input
        base.frame.receiveInput()

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
        base.drawing.renderMap( ( int( game.cameraPosX ), int( game.cameraPosY ) ) )

    def doFrame( self, frameTime ):
        self.doInput( frameTime )
        self.drawGame( frameTime )
        self.world.doFrame( frameTime, game.accumelator )

    def doTick( self ):
        self.world.doTick()
