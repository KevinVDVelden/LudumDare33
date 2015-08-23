import ecs
import gamelogic.init
import gamelogic.draw
import gamelogic.resources
import gamelogic.building
import gamelogic.enemies
import random
import game

global BUILDINGDIRECTION
BUILDINGDIRECTION = ( ( 0, -1 ), ( 1, 0 ), ( 0, 1 ), ( -1, 0 ) )
BUILDING_REVERSE = ( 2, 3, 0, 1 )

BUILDING_IMG_FORMAT = 'img/buildings/combined/%s_%d.png'
ORB_IMG_FORMAT = 'img/buildings/parts/hue_%s.png'

class BuildingComponent( ecs.Component ):
    def __init__( self, buildingType, config ):
        super().__init__( ecs.COMPONENT_BUILDING )
        self.buildingType = buildingType
        self.config = config
        self.neighbours = [ None, None, None, None ]
        self.lastDirection = 0
        self.orbOut = [ False, False, False, False ]

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
        storage = self.entity.getComponent( ecs.COMPONENT_RESOURCE )

        if storage is None or resource not in storage.caps:
            return 0
        else:
            return storage.canReceive( resource, sourceStored )

    def receive( self, source, resource, amount ):
        storage = self.entity.getComponent( ecs.COMPONENT_RESOURCE )

        storage.receive( source, resource, amount )

    def think( self, ent, world ):
        assert self.entity == ent
        assert self.world == world

        storage = self.entity.getComponent( ecs.COMPONENT_RESOURCE )

        storageComponents = world.entitiesWithComponent( ecs.COMPONENT_RESOURCE )

        if storage is None:
            return

        for resource in ( 'energy', 'metals' ):
            if resource not in storage.rates:
                continue

            storage.increase( resource, -storage.rates[ resource ] )

            #Direct neighbours
            neighbourI = list( [ i for i in range( 4 ) if self.neighbours[ i ] is not None ] )
            random.shuffle( neighbourI )

            for i in neighbourI:
                stored = storage.stored[resource]
                if storage.receiveCap[resource] == 0:
                    stored = -1

                canReceive = self.neighbours[ i ].canReceive( resource, stored )
                if canReceive > 5:
                    send = storage.getBurst( resource, canReceive )
                    if send > 0:
                        self.neighbours[ i ].receive( self, resource, send )

            #Not connected neighbours
            #TODO: This should really not be working, but it is, I suspect a bug in the neighbour code
            neighbourI = list( [ BUILDING_REVERSE[i] for i in range( 4 ) if self.neighbours[ i ] is None ] )
            random.shuffle( neighbourI )

            for i in neighbourI:
                checkPos = ent.position

                if self.orbOut[ i ]:
                    continue

                stored = storage.stored[resource]
                if storage.receiveCap[resource] == 0:
                    stored = 0

                for dist in range( 10 ):
                    checkPos = ( checkPos[0] + BUILDINGDIRECTION[i][0], checkPos[1] + BUILDINGDIRECTION[i][1] )

                    targets = storageComponents.atPosition( checkPos )
                    if len( targets ) > 0:
                        canReceive = targets[0].getComponent( ecs.COMPONENT_RESOURCE ).canReceive( resource, stored )

                        if canReceive > 5:
                            send = storage.getBurst( resource, canReceive )

                            def callbackFactory( self, orbDir ):
                                def cb( orb ):
                                    self.orbOut[ orbDir ] = False
                                return cb


                            orb = world.addEntity( ent.position )
                            orb.addComponent( ecs.RenderComponent( ORB_IMG_FORMAT % resource ) )
                            orb.addComponent( gamelogic.resources.ResourceOrb( BUILDINGDIRECTION[i], resource, send, callbackFactory( self, i ) ) )
                            self.orbOut[ i ] = True
                            #print( '%s is sending %d of %s in the direction of %s' % ( self, canReceive, resource, targets[0] ) )

                        break

    def __str__( self ):
        return '<Building.%s %d>' % ( self.buildingType, id( self ) )

def centerCameraOnTile( pos ):
    game.cameraPosX = ( pos[0] * 32 + 16 ) - game.SCREEN_SIZE[0] / 2
    game.cameraPosY = ( pos[1] * 32 + 16 ) - game.SCREEN_SIZE[1] / 2
