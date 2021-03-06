import pygame
import game

def initAssets():
    import os

    def initPath( path ):
        for _file in os.listdir( path ):
            if os.path.isfile( path + _file ):
                try:
                    game.assets[ path + _file ] = pygame.image.load( path + _file ).convert_alpha()
                except Exception as e:
                    #Text files? Whatever
                    pass
            else:
                initPath( path + _file + '/' )

    initPath( 'img/' )

