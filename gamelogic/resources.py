import ecs
from collections import defaultdict
import game
import pygame

def calculateResources( self ):
    resources = defaultdict( lambda: ( 0, 0, 0 ) )

    for ent in self.world.entitiesWithComponent( ecs.COMPONENT_RESOURCE_STORE ):
        comp = ent.getComponent( ecs.COMPONENT_RESOURCE_STORE )

        for key in comp.caps:
            cur = resources[ key ]

            resources[ key ] = ( cur[0] + comp.stored[key], cur[1] + comp.caps[key], cur[2] )

    for ent in self.world.entitiesWithComponent( ecs.COMPONENT_RESOURCE_USER ):
        comp = ent.getComponent( ecs.COMPONENT_RESOURCE_USER )

        for key in comp.rates:
            cur = resources[ key ]
            resources[ key ] = ( cur[0], cur[1], cur[2] + comp.rates[key] )

    self.prevResources = self.resources
    self.resources = resources

    self.mana = self.resources['mana']
    if self.mana[1] > 0:
        self.manaWidget.setCharge( self.mana[0] / self.mana[1] )
    else:
        self.manaWidget.setCharge( 0 )

    self.souls = self.resources['soul']
    if self.souls[1] > 0:
        self.soulsWidget.setCharge( self.souls[0] / self.souls[1] )

class ResourceUseComponent( ecs.Component ):
    def __init__( self, rates ):
        self.rates = rates
        super().__init__( ecs.COMPONENT_RESOURCE_USER )

class ResourceStoreComponent( ecs.Component ):
    def __init__( self, caps ):
        self.caps = caps
        self.stored = { key: 0 for key in self.caps }

        self.burst = { key: self.caps[key][1] for key in self.caps }
        self.caps = { key: self.caps[key][0] for key in self.caps }

        super().__init__( ecs.COMPONENT_RESOURCE_STORE )

    def render( self, ent, accumelator ):
        resourceColorsLight = { 'mana': ( 5, 202, 245, 100 ), 'soul': ( 249, 48, 0, 100 ) }
        resourceColorsDark = { 'mana': ( 4, 119, 142, 100 ), 'soul': ( 145, 26, 0, 100 ) }

        offset = 0
        for resource in self.caps:
            rect = pygame.Rect( ( ent.position[0] * 32 ) - game.cameraPosX, ( ent.position[1] * 32 ) - game.cameraPosY + offset, 32, 6 )
            game.screen.fill( resourceColorsDark[ resource ], rect = rect )

            rect = pygame.Rect( rect.left + 1, rect.top + 1, int( 30 * self.stored[resource] / self.caps[resource] ), 4 )
            game.screen.fill( resourceColorsLight[ resource ], rect = rect )

            offset -= 8
