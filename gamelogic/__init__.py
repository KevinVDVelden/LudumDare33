import ecs
import gamelogic.init
import gamelogic.draw
import gamelogic.resources
import gamelogic.building
import random
import game

global BUILDINGDIRECTION
BUILDINGDIRECTION = ( ( 0, -1 ), ( 1, 0 ), ( 0, 1 ), ( -1, 0 ) )
BUILDING_REVERSE = ( 2, 3, 0, 1 )

BUILDING_IMG_FORMAT = 'img/buildings/combined/%s_%d.png'

class BuildingComponent( ecs.Component ):
    def __init__( self, buildingType, config ):
        super().__init__( ecs.COMPONENT_BUILDING )
        self.buildingType = buildingType
        self.config = config
        self.neighbours = [ None, None, None, None ]
        self.lastDirection = 0

    def registerNewNeighbour( self, neighbour, direction ):
        self.neighbours[ direction ] = neighbour
        self.setTexture()

    def setTexture( self ):
        mask = 0
        for i in range( len( self.neighbours ) ):
            if self.neighbours[ i ]:
                mask += ( 1 << i ) 

        newSprite = BUILDING_IMG_FORMAT % ( self.buildingType, mask ) 
        self.entity.getComponent( ecs.COMPONENT_RENDER ).setSprite( newSprite )

    def setEntity( self, ent, world ):
        super().setEntity( ent, world )

        otherBuildings = self.world.entitiesWithComponent( ecs.COMPONENT_BUILDING )

        pos = self.entity.position
        for i in range( len( BUILDINGDIRECTION ) ):
            _dir = BUILDINGDIRECTION[ i ]
            neighbour = otherBuildings.atPosition( ( self.entity.position[0] - _dir[0], self.entity.position[1] - _dir[1] ) )

            neighbour = None if len( neighbour ) == 0 else neighbour[ 0 ]

            if neighbour is not None:
                self.neighbours[ i ] = neighbour.getComponent( ecs.COMPONENT_BUILDING )
                neighbour.getComponent( ecs.COMPONENT_BUILDING ).registerNewNeighbour( self, BUILDING_REVERSE[ i ] )

        self.setTexture()

    def removeFromWorld( self, ent, world ):
        for i in range( len( self.neighbours ) ):
            neighbour = self.neighbours[ i ]
            if neighbour is None:
                continue

            neighbour.registerNewNeighbour( None, BUILDING_REVERSE[ i ] )

    def canReceive( self, resource, sourceStored ):
        storage = self.entity.getComponent( ecs.COMPONENT_RESOURCE_STORE )

        if storage is None or resource not in storage.caps:
            return 0
        else:
            if sourceStored < 0 or sourceStored > storage.stored[resource]:
                return storage.caps[resource] - storage.stored[resource]
            else:
                #print( 'No taking from the poor!' )
                return 0

    def receive( self, source, resource, amount ):
        storage = self.entity.getComponent( ecs.COMPONENT_RESOURCE_STORE )

        storage.stored[resource] = min( storage.stored[resource] + amount, storage.caps[resource] )

        #print( '%s received from %s %f of %s, now at %d/%d' % ( self, source, amount, resource, storage.stored[resource], storage.caps[resource] ) )

    def think( self, ent, world ):
        assert self.entity == ent
        assert self.world == world

        storage = self.entity.getComponent( ecs.COMPONENT_RESOURCE_STORE )
        usage = self.entity.getComponent( ecs.COMPONENT_RESOURCE_USER )

        #print( self, storage, usage )
        if storage is None and usage is None:
            return

        for resource in ( 'mana', 'soul' ):
            current = 0
            stored = -1

            if usage is not None and resource in usage.rates:
                current = -usage.rates[resource] 
            if storage is not None and resource in storage.stored:
                stored = storage.stored[resource]
                burst = min( stored, storage.burst[resource] )
                storage.stored[resource] -= burst
                current += burst

            if current < 5:
                if usage is not None and storage is not None and resource in storage.stored and resource in usage.rates:
                    storage.stored[resource] += usage.rates[resource]
                    #print( '%s is storing %d of %s, now at %d/%d' % ( self, usage.rates[resource], resource, storage.stored[resource],storage.caps[resource] ) )
                continue

            #Direct neighbours
            neighbourI = list( [ i for i in range( 4 ) if self.neighbours[ i ] is not None ] )
            random.shuffle( neighbourI )

            for i in neighbourI:
                neighbourI.remove( i )

                canReceive = self.neighbours[ i ].canReceive( resource, stored )
                if canReceive > 0:
                    canReceive = min( canReceive, current )
                    self.neighbours[ i ].receive( self, resource, canReceive )
                    current -= canReceive

            if current > 0 and storage is not None and resource in storage.caps:
                storage.stored[ resource ] += current


    def __str__( self ):
        return '<Building.%s %d>' % ( self.buildingType, id( self ) )

def centerCameraOnTile( pos ):
    game.cameraPosX = ( pos[0] * 32 + 16 ) - game.SCREEN_SIZE[0] / 2
    game.cameraPosY = ( pos[1] * 32 + 16 ) - game.SCREEN_SIZE[1] / 2
