import ecs
from collections import defaultdict
import game
import pygame

def calculateResources( self ):
    resources = defaultdict( lambda: ( 0, 0, 0 ) )

    for ent in self.world.entitiesWithComponent( ecs.COMPONENT_RESOURCE ):
        comp = ent.getComponent( ecs.COMPONENT_RESOURCE )

        for key in comp.caps:
            cur = resources[ key ]

            resources[ key ] = ( cur[0] + comp.stored[key], cur[1] + comp.caps[key], cur[2] )

    for ent in self.world.entitiesWithComponent( ecs.COMPONENT_RESOURCE ):
        comp = ent.getComponent( ecs.COMPONENT_RESOURCE )

        for key in comp.rates:
            cur = resources[ key ]
            resources[ key ] = ( cur[0], cur[1], cur[2] + comp.rates[key] )

    self.prevResources = self.resources
    self.resources = resources

    self.energy = self.resources['energy']
    if self.energy[1] > 0:
        self.energyWidget.setCharge( self.energy[0] / self.energy[1] )
    else:
        self.energyWidget.setCharge( 0 )

    self.metals = self.resources['metals']
    if self.metals[1] > 0:
        self.metalsWidget.setCharge( self.metals[0] / self.metals[1] )

class ResourceStoreComponent( ecs.Component ):
    def __init__( self, caps ):
        self.stored = { key: 0 for key in caps }
        self.rates = { key: caps[key][0] for key in caps }
        self.caps = { key: caps[key][1] for key in caps }
        self.burst = { key: caps[key][2] for key in caps }
        self.receiveCap = { key: caps[key][3] for key in caps }
        self.resourceRenderMult = 1

        super().__init__( ecs.COMPONENT_RESOURCE )

    def render( self, ent, accumelator ):
        resourceColorsLight = { 'energy': ( 5, 202, 245, 100 ), 'metals': ( 90, 100, 90, 100 ) }
        resourceColorsDark = { 'energy': ( 4, 119, 142, 100 ), 'metals': ( 30, 40, 30, 100 ) }

        offset = 0
        for resource in self.caps:
            if self.receiveCap[resource] <= 0:
                continue

            rect = pygame.Rect( ( ent.position[0] * 32 ) - game.cameraPosX, ( ent.position[1] * 32 ) - game.cameraPosY + offset, 32, 6 )
            game.screen.fill( resourceColorsDark[ resource ], rect = rect )

            rect = pygame.Rect( rect.left + 1, rect.top + 1, min( 30, int( 30 * self.stored[resource] / self.caps[resource] * self.resourceRenderMult ) ), 4 )
            game.screen.fill( resourceColorsLight[ resource ], rect = rect )

            offset -= 8

    def canReceive( self, resource, sourceStored ):
        if resource not in self.caps:
            return 0

        #No taking from the poor, unless they can't store at all
        if sourceStored < 0 or ( self.stored[resource] + self.receiveCap[resource] ) / self.caps[resource] < sourceStored:
            return min( self.caps[resource] - self.stored[resource], self.receiveCap[resource] )
        else:
            return 0

    def receive( self, source, resource, amount ):
        self.increase( resource, amount )
        #print( '%s received %d of %s from %s' % ( self, amount, resource, source ) )
        assert amount > 0

    def increase( self, resource, amount ):
        try:
            self.stored[resource] = max( 0, min( self.stored[resource] + amount, self.caps[resource] ) )
        except KeyError:
            pass

    def hasResources( self, resources ):
        return not any( [ self.stored[resource] < resources[resource] for resource in resources ] )

    def takeResources( self, resources ):
        for resource in resources:
            self.stored[ resource ] -= resources[ resource ]

    def getBurst( self, resource, cap ):
        if cap > self.burst[ resource ]:
            cap = self.burst[ resource ]

        if cap > self.stored[ resource ]:
            cap = self.stored[ resource ]

        if cap < 0 or self.stored[ resource ] < 0:
            return 0

        self.stored[ resource ] -= cap
        return cap

class ResourceOrb( ecs.Component ):
    def __init__( self, direction, resource, stored, finishCallback ):
        self.direction = direction
        self.resource = resource
        self.stored = stored
        self.traveled = 0
        self.finishCallback = finishCallback
        super().__init__( ecs.COMPONENT_THINK )

    def setEntity( self, ent, world ):
        self.entity = ent
        self.entity.velocity = self.direction

    def think( self, ent, world ):
        self.traveled += 1

        if self.traveled > 5:
            #Decay resource orb
            self.stored -= 0.5
        if self.traveled > 15 or self.stored <= 0:
            world.removeEntity( ent )
            return


        ent.position = ( ent.position[0] + self.direction[0], ent.position[1] + self.direction[1] )

        targets = tuple( [ n for n in world.entitiesWithComponent( ecs.COMPONENT_RESOURCE ).atPosition( ent.position ) if n != ent ] )
        if len( targets ) > 0:
            target = targets[0]
            target = target.getComponent( ecs.COMPONENT_RESOURCE )
            target.receive( self, self.resource, self.stored )
            world.removeEntity( ent )

    def removeFromWorld( self, ent, world ):
        self.finishCallback( self )
