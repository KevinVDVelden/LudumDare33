import game
import base.drawing
from functools import lru_cache

COMPONENT_RENDER = 1
COMPONENT_THINK = 2
COMPONENT_ATTACK = 3
COMPONENT_BUILDING = 4
COMPONENT_RESOURCE_USER = 5
COMPONENT_RESOURCE_STORE = 6
COMPONENT_MAX = 7

def idToMask( _id ):
    return 1 << ( _id - 1 )


class RenderComponent:
    def __init__( self, tileName ):
        self.tile = game.assets[ tileName ]
        self.typeId = COMPONENT_RENDER

    def render( self, entity, accumelatorTime ):
        pos = ( int( entity.position[0] * 32 ) - game.cameraPosX, int( entity.position[1] * 32 ) - game.cameraPosY )
        base.drawing.drawSprite( pos, self.tile )

    def setSprite( self, newTile ):
        self.tile = game.assets[ newTile ]

    def setEntity( self, ent, world ):
        pass

class Entity:
    def __init__( self, position, world ):
        self.componentMask = 0
        self.components = list( [ None for n in range( COMPONENT_MAX ) ] )
        self.position = position
        self.world = world

    def hasComponent( self, compId ):
        return self.componentMask & idToMask( compId ) > 0

    def addComponent( self, comp ):
        self.world.isDirty = True

        self.components[ comp.typeId ] = comp
        self.componentMask |= idToMask( comp.typeId )

        comp.setEntity( self, self.world )

    def getComponent( self, typeId ):
        return self.components[ typeId ]

    def removeFromWorld( self ):
        for comp in self.components:
            if hasattr( comp, 'removeFromWorld' ):
                comp.removeFromWorld( self, self.world )

class EntityList( list ):
    def __init__( self, world, *args, **kargs ):
        super().__init__( *args, **kargs )
        self.world = world

    def atPosition( self, pos ):
        ret = EntityList( self.world, [ ent for ent in self if (
            ent.position[0] == pos[0] and ent.position[1] == pos[1] ) ] )

        return ret

class World:
    def __init__( self ):
        self.entities = []
        self.isDirty = True

    def doTick( self ):
        pass

    def doFrame( self, frameTime, accumelatorTime ):
        for ent in self.entitiesWithComponent( COMPONENT_RENDER ):
            ent.components[ COMPONENT_RENDER ].render( ent, accumelatorTime )

    def removeEntity( self, ent ):
        self.isDirty = True
        self.entities.remove( ent )

        ent.removeFromWorld()

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
            self.entityMasks[ compId ] = EntityList( self, [ ent for ent in self.entities if ent.componentMask & mask > 0 ] )

        return self.entityMasks[ compId ]

    def doClean( self ):
        if self.isDirty:
            self.isDirty = False
            self.entityMasks = list( [ None for n in range( COMPONENT_MAX ) ] )

class Component:
    def __init__( self, typeId ):
        self.typeId = typeId

    def setEntity( self, ent, world ):
        self.entity = ent
        self.world = world

