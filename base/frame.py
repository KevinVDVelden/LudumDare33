import pygame
import game
import config

from base.drawing import *
import util

global keysPressed
keysPressed = {}

def receiveInput():
    keys = pygame.key.get_pressed()
    global keysPressed
    for i in range( len( keys ) ):
        if i in config.keyMapping:
             keysPressed[ config.keyMapping[ i ] ] = keys[ i ] > 0

    retVal = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.gameIsRunning = False
        else:
            retVal.append( event )

    return retVal
