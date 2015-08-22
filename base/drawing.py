import pygame
import game

def drawSprite( pos, sprite ):
    game.screen.blit( sprite, pos )

def initMap( mapSize ):
    game.mapSurface = pygame.Surface( ( mapSize[0] * 32, mapSize[1] * 32 ) )
    game.mapSize = mapSize
    game.mapBuffer = bytearray( mapSize[0] * mapSize[1] )

    game.mapPixelSizeX = game.mapSurface.get_width()
    game.mapPixelSizeY = game.mapSurface.get_height()

def drawMap( mapPos, sprite ):
    game.mapSurface.blit( sprite, ( mapPos[0] * 32, mapPos[1] * 32 ) )

def renderMap( cameraPos ):
    game.screen.blit( game.mapSurface, ( -cameraPos[0], -cameraPos[1] ) )

from functools import lru_cache
@lru_cache( 32 )
def renderFont( fontName, text, color = ( 0,0,0 ) ):
    return game.fonts[ fontName ].render( text, False, color )
