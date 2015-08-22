import ecs

global BUILDINGDIRECTION
BUILDINGDIRECTION = ( ( 0, -1 ), ( 1, 0 ), ( 0, 1 ), ( -1, 0 ) )
BUILDING_REVERSE = ( 2, 3, 0, 1 )

BUILDING_IMG_FORMAT = 'img/buildings/combined/building_%s_%d.png'

class BuildingComponent:
    def __init__( self, buildingType ):
        self.typeId = ecs.COMPONENT_BUILDING
        self.buildingType = buildingType
        self.neighbours = [ None, None, None, None ]

    def registerNewNeighbour( self, neighbour, direction ):
        print( self, neighbour, direction )

        self.neighbours[ direction ] = neighbour
        self.setTexture()

    def setTexture( self ):
        mask = 0
        for i in range( len( self.neighbours ) ):
            if self.neighbours[ i ]:
                print( i )
                mask += ( 1 << i ) 

        newSprite = BUILDING_IMG_FORMAT % ( self.buildingType, mask ) 
        self.entity.getComponent( ecs.COMPONENT_RENDER ).setSprite( newSprite )
        print( newSprite )

    def setEntity( self, ent, world ):
        self.entity = ent
        self.world = world

        otherBuildings = self.world.entitiesWithComponent( ecs.COMPONENT_BUILDING )
        print( otherBuildings )

        pos = self.entity.position
        for i in range( len( BUILDINGDIRECTION ) ):
            _dir = BUILDINGDIRECTION[ i ]
            neighbour = otherBuildings.atPosition( ( self.entity.position[0] - _dir[0], self.entity.position[1] - _dir[1] ) )

            neighbour = None if len( neighbour ) == 0 else neighbour[ 0 ]

            if neighbour is not None:
                self.neighbours[ i ] = neighbour
                neighbour.getComponent( ecs.COMPONENT_BUILDING ).registerNewNeighbour( self, BUILDING_REVERSE[ i ] )

        self.setTexture()


    def think( self, ent, world ):
        assert self.entity == ent
        assert self.world == world
