from scene import Scene
import base
import game
import util
import config

keysPressed = base.frame.keysPressed

class GameScene( Scene ):
    def init( self ):
        base.drawing.initMap( ( 64, 64 ) )

        for x in range( 64 ):
            for y in range( 64 ):
                img = game.assets[ 'img/dungeon/floor_1.png' if x % 5 == 0 else 'img/dungeon/wall_1.png' ]
                base.drawing.drawMap( ( x, y ), img )
        return True

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

