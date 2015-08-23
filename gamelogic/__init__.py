import ecs
import gamelogic.init
import gamelogic.draw
import gamelogic.resources
import gamelogic.building
import gamelogic.enemies
import game

def centerCameraOnTile( pos ):
    game.cameraPosX = ( pos[0] * 32 + 16 ) - game.SCREEN_SIZE[0] / 2
    game.cameraPosY = ( pos[1] * 32 + 16 ) - game.SCREEN_SIZE[1] / 2
