import ecs
import pygame
import game
import base.drawing
import random

class Component:
    def __init__( self, typeId ):
        self.typeId = typeId

    def setEntity( self, ent, world ):
        self.entity = ent
        self.world = world

class HealthComponent( Component ):
    def __init__( self, maxHealth ):
        self.health = maxHealth
        self.maxHealth = maxHealth
        super().__init__( ecs.COMPONENT_HEALTH )

    def takeDamage( self, damage ):
        self.health -= damage

        if self.health < 0:
            pos = self.entity.position
            pos = ( pos[0] + random.random() - 0.5, pos[1] + random.random() - 0.5 )
            base.drawing.drawMap( pos, game.assets[ 'img/blood_%d.png' % random.randrange( 1, 4 ) ] )
            self.world.removeEntity( self.entity )
        elif self.health > self.maxHealth:
            self.health = self.maxHealth

    def render( self, ent, accumelator ):
        if self.health >= self.maxHealth:
            return

        light = ( 244, 7, 7 )
        dark = ( 140, 4, 4 )

        rect = pygame.Rect( ( ( ent.position[0] + ent.velocity[0] * accumelator ) * 32 ) - game.cameraPosX, ( ( ent.position[1] + 1 + ent.velocity[1] * accumelator ) * 32 ) - game.cameraPosY, 32, 6 )
        game.screen.fill( dark, rect = rect )

        rect = pygame.Rect( rect.left + 1, rect.top + 1, int( 30 * self.health / self.maxHealth ), 4 )
        game.screen.fill( light, rect = rect )
