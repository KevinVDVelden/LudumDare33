import game
import base.drawing

COMPONENT_RENDER = 1
COMPONENT_THINK = 2
COMPONENT_ATTACK = 3
COMPONENT_MAX = 4

def idToMask( _id ):
    return 1 << ( _id - 1 )


class RenderComponent:
    def __init__( self, tileName ):
        self.tile = game.assets[ tileName ]
        self.typeId = COMPONENT_RENDER

    def render( self, entity, accumelatorTime ):
        pos = ( int( entity.position[0] * 32 ) - game.cameraPosX, int( entity.position[1] * 32 ) - game.cameraPosY )
        base.drawing.drawSprite( pos, self.tile )

class Entity:
    def __init__( self, position, world ):
        self.componentMask = 0
        self.components = list( [ None for n in range( COMPONENT_MAX ) ] )
        self.position = position
        self.world = world

    def hasComponent( self, compId ):
        return self.componentMask & idToMask( compId ) > 0

    def addComponent( self, comp ):
        self.components[ comp.typeId ] = comp
        self.componentMask |= idToMask( comp.typeId )
        self.world.isDirty = True


class World:
    def __init__( self ):
        self.entities = []
        self.isDirty = True

    def doTick( self ):
        pass

    def doFrame( self, frameTime, accumelatorTime ):
        for ent in self.entitiesWithComponent( COMPONENT_RENDER ):
            ent.components[ COMPONENT_RENDER ].render( ent, accumelatorTime )


    def addEntity( self, position ):
        ent = Entity( position, self )
        self.entities.append( ent )
        self.isDirty = True
        return ent

    def entitiesWithComponent( self, compId ):
        if self.isDirty:
            self.doClean()

        if self.entityMasks[ compId ] is None:
            mask = idToMask( compId )
            self.entityMasks[ compId ] = list( [ ent for ent in self.entities if ent.componentMask & mask > 0 ] )

        return self.entityMasks[ compId ]

    def doClean( self ):
        if self.isDirty:
            self.isDirty = False
            self.entityMasks = list( [ None for n in range( COMPONENT_MAX ) ] )
