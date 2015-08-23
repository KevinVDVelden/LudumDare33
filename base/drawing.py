import pygame
import game

def drawSprite( pos, sprite ):
    game.screen.blit( sprite, pos )

def initMap( mapSize ):
    game.mapSurface = None
    game.mapSize = None
    game.mapBuffer = None


    game.mapSurface = (
            pygame.Surface( ( mapSize[0] * 32, mapSize[1] * 32 ) ),
            pygame.Surface( ( mapSize[0] * 32, mapSize[1] * 32 ) ),
            pygame.Surface( ( mapSize[0] * 32, mapSize[1] * 32 ) ) )
    game.mapSurface[2].set_colorkey( ( 255,0,255 ) )
    game.mapSurface[2].fill( (255,0,255) )

    game.mapSize = mapSize
    game.mapBuffer = bytearray( mapSize[0] * mapSize[1] )

    game.mapPixelSizeX = game.mapSurface[0].get_width()
    game.mapPixelSizeY = game.mapSurface[0].get_height()

def drawMap( mapI, mapPos, sprite ):
    game.mapSurface[mapI].blit( sprite, ( mapPos[0] * 32, mapPos[1] * 32 ) )

def renderMap( cameraPos ):
    game.screen.blit( game.mapSurface[0], ( -cameraPos[0], -cameraPos[1] ) )
    game.screen.blit( game.mapSurface[2], ( -cameraPos[0], -cameraPos[1] ) )

from functools import lru_cache
@lru_cache( 32 )
def renderFont( fontName, text, color = ( 0,0,0 ) ):
    return game.fonts[ fontName ].render( text, False, color )
