import game
import base.drawing
import bisect
from functools import lru_cache

COMPONENT_RENDER = 1
COMPONENT_THINK = 2
COMPONENT_ATTACK = 3
COMPONENT_BUILDING = 4
COMPONENT_RESOURCE = 5
COMPONENT_MAX = 6

def idToMask( _id ):
    return 1 << ( _id - 1 )


class RenderComponent:
    def __init__( self, tileName ):
        self.tile = game.assets[ tileName ]
        self.typeId = COMPONENT_RENDER

    def render( self, entity, accumelatorTime ):
        pos = ( int( ( entity.position[0] + entity.velocity[0]*accumelatorTime ) * 32 ) - game.cameraPosX,
                int( ( entity.position[1] + entity.velocity[1]*accumelatorTime ) * 32 ) - game.cameraPosY )
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
        self.velocity = ( 0, 0 )
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

    def __str__( self ):
        return '<Entity %d at %s>' % ( id(self), str( self.position ) )

    def __repr__( self ):
        return '<Entity %d at %s>' % ( id(self), str( self.position ) )

class EntityList( list ):
    def __init__( self, world, *args, **kargs ):
        super().__init__( *args, **kargs )
        self.world = world

    def atPosition( self, pos ):
        ret = EntityList( self.world, [ ent for ent in self if (
            ent.position[0] == pos[0] and ent.position[1] == pos[1] ) ] )

        return ret

    def withComponent( self, component ):
        mask = idToMask( component )
        return EntityList( self.world, [ ent for ent in self if (
            ent.componentMask & mask > 0 ) ] )


class World:
    def __init__( self ):
        self.entities = []
        self.isDirty = True

    def doTick( self ):
        thinkComponents = ( COMPONENT_BUILDING, COMPONENT_THINK )

        for componentType in thinkComponents:
            for ent in self.entitiesWithComponent( componentType ):
                ent.components[ componentType ].think( ent, self )


    def doFrame( self, frameTime, accumelatorTime ):
        renderComponents = ( COMPONENT_RENDER, COMPONENT_RESOURCE )

        for componentType in renderComponents:
            for ent in self.entitiesWithComponent( componentType ):
                ent.components[ componentType ].render( ent, accumelatorTime )

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

    def entsInX( self, minX, maxX ):
        minI = bisect.bisect_left( self.positionListX, minX )
        maxI = bisect.bisect_right( self.positionListX, maxX, lo = minI )

        return set( [ self.positionEntsX[i] for i in range( minI, maxI ) ] )
    def entsInY( self, minY, maxY ):
        minI = bisect.bisect_left( self.positionListY, minY )
        maxI = bisect.bisect_right( self.positionListY, maxY, lo = minI )

        return set( [ self.positionEntsY[i] for i in range( minI, maxI ) ] )

    def entsInRect( self, rect ):
        return self.entsInX( rect.left, rect.left + rect.width ) & self.entsInY( rect.top, rect.top + rect.height )

    def doClean( self ):
        if self.isDirty:
            self.isDirty = False
            self.entityMasks = list( [ None for n in range( COMPONENT_MAX ) ] )

    def sortEntities( self ):
        self.positionEntsX = tuple( sorted( self.entities, key=lambda n: n.position[0] ) )
        self.positionListX = tuple( [ ent.position[0] for ent in self.positionEntsX ] )

        self.positionEntsY = tuple( sorted( self.entities, key=lambda n: n.position[1] ) )
        self.positionListY = tuple( [ ent.position[1] for ent in self.positionEntsY ] )


class Component:
    def __init__( self, typeId ):
        self.typeId = typeId

    def setEntity( self, ent, world ):
        self.entity = ent
        self.world = world

