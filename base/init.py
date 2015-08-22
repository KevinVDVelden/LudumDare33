import pygame
import game

def initAssets():
    import os

    def initPath( path ):
        for _file in os.listdir( path ):
            if os.path.isfile( path + _file ):
                try:
                    game.assets[ path + _file ] = pygame.image.load( path + _file ).convert()
                except Exception as e:
                    #Text files? Whatever
                    print( e )
            else:
                initPath( path + _file + '/' )

    initPath( 'img/' )
