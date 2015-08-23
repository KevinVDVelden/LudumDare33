import ecs
import gamelogic
import pygame
import random
import game
import base

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

        self.transformTarget = config['transformTarget'] if 'transformTarget' in config else None
        self.transformCost = config['transformCost'] if 'transformCost' in config else None

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

    def render( self, entity, accumelatorTime ):
        if self.transformTarget is not None:
            pos = ( int( ( entity.position[0] ) * 32 ) - game.cameraPosX,
                    int( ( entity.position[1] ) * 32 ) - game.cameraPosY )
            base.drawing.drawSprite( pos, game.assets[ 'img/progress.png' ] )

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

        if self.transformTarget is not None:
            ent.getComponent( ecs.COMPONENT_RESOURCE ).resourceRenderMult = 20

        self.setTexture()

    def removeFromWorld( self, ent, world ):
        for i in range( len( self.neighbours ) ):
            neighbour = self.neighbours[ i ]
            if neighbour is None:
                continue

            neighbour.registerNewNeighbour( None, BUILDING_REVERSE[ i ] )
        game.corruption.addSource( ent.position, 0 )
        game.pathFinding.addSource( ent.position, 0 )

    def canReceive( self, resource, sourceStored ):
        storage = self.entity.getComponent( ecs.COMPONENT_RESOURCE )

        if storage is None:
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

        if self.transformTarget is not None:
            if not any( [ storage.stored[resource] < self.transformCost[resource] for resource in self.transformCost ] ):
                self.world.removeEntity( ent )
                makeBuilding( self.world, ent.position, self.transformTarget )
                return
            else:
                for resource in [ key for key in self.transformCost if storage.stored[key] > self.transformCost[key] ]:
                    storage.stored[resource] = self.transformCost[resource]
                    storage.caps[resource] = self.transformCost[resource]

            return

        for resource in ( 'energy', 'metals' ):
            if resource not in storage.rates:
                continue
            if storage.burst[resource] <= 0:
                continue

            def getStored():
                stored = storage.stored[resource]
                if storage.receiveCap[resource] == 0:
                    stored = -1
                else:
                    stored /= storage.caps[resource]
                return stored

            storage.increase( resource, -storage.rates[ resource ] )

            #Direct neighbours
            neighbourI = list( [ i for i in range( 4 ) if self.neighbours[ i ] is not None ] )
            random.shuffle( neighbourI )

            for i in neighbourI:
                stored = getStored()

                canReceive = self.neighbours[ i ].canReceive( resource, stored )
                if canReceive > 1:
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

                stored = getStored()

                for dist in range( 10 ):
                    checkPos = ( checkPos[0] + BUILDINGDIRECTION[i][0], checkPos[1] + BUILDINGDIRECTION[i][1] )

                    targets = storageComponents.atPosition( checkPos )
                    if len( targets ) > 0:
                        canReceive = targets[0].getComponent( ecs.COMPONENT_RESOURCE ).canReceive( resource, stored )

                        if canReceive > 1:
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


def makeBuilding( world, pos, config ):
    ent = world.addEntity( pos )
    ent.addComponent( ecs.RenderComponent( 'img/buildings/combined/building_energy_11.png' ) )
    ent.team = config['team']

    if 'resources' in config:
        ent.addComponent( gamelogic.resources.ResourceStoreComponent( config['resources'] ) )

    if 'health' in config:
        ent.addComponent( ecs.HealthComponent( config['health'] ) )

    if 'building' in config:
        ent.addComponent( BuildingComponent( config['building'], config ) )

    #TODO: Make this a component?
    if 'corrupts' in config:
        game.corruption.addSource( pos, config['corrupts'] )
    if 'pathImportance' in config:
        game.pathFinding.addSource( pos, config['pathImportance'] )

    if 'attack' in config:
        ent.addComponent( gamelogic.enemies.AttackComponent( config['attack'] ) )

#Resources tuple: ( use per tick, maximum stored, maximum send per burst, maximum received )

Buildings = {}

Buildings['EnergyZiggurat'] = { 'building': 'building_energy',
                        'resources': { 'energy': ( -10, 20, 20, 0 ) },
                        'corrupts': 1000,
                        'pathImportance': 1000,
                        'buildCost': { 'metals': 100, 'energy': 2000 },
                        'health': 100,
                        'team': 0 }
Buildings['EnergyPylon'] = { 'building': 'pylon_energy',
                        'resources': { 'energy': ( 1, 200, 25, 25 ) },
                        'corrupts': 100,
                        'pathImportance': 1000,
                        'buildCost': { 'metals': 50, 'energy': 200 },
                        'health': 100,
                        'team': 0 }

Buildings['MetalsZiggurat'] = { 'building': 'building_metals',
                        'resources': { 'metals': ( -10, 20, 10, 0 ) },
                        'corrupts': 2000,
                        'pathImportance': 1000,
                        'buildCost': { 'metals': 500, 'energy': 200 },
                        'health': 100,
                        'team': 0 }
Buildings['MetalsPylon'] = { 'building': 'pylon_metals',
                        'resources': { 'metals': ( 1, 200, 25, 25 ) },
                        'corrupts': 300,
                        'pathImportance': 1000,
                        'buildCost': { 'metals': 100, 'energy': 20 },
                        'health': 100,
                        'team': 0 }

Buildings['HeartZiggurat'] = { 'building': 'building_heart',
                        'resources': { 'energy': ( -25, 50, 50, 0 ), 'metals': ( -25, 50, 50, 0 ) },
                        'corrupts': 3000,
                        'pathImportance': 1000,
                        'health': 100,
                        'team': 0 }
Buildings['HeartPylon'] = { 'building': 'pylon_heart',
                        'resources': { 'energy': ( 1, 200, 25, 25 ), 'metals': ( 1, 200, 25, 25 ) },
                        'corrupts': 3000,
                        'pathImportance': 1000,
                        'buildCost': { 'metals': 200, 'energy': 300 },
                        'health': 100,
                        'team': 0 }

Buildings['TurretT1'] = { 'building': 'turret_t1',
                        'resources': { 'energy': ( 0, 200, 0, 25 ) },
                        'pathImportance': 1010,
                        'attack': { 'range': 3, 'damage': 5, 'attackCooldown': 0.3, 'costs': { 'energy': 15 } },
                        'buildCost': { 'metals': 200, 'energy': 100 },
                        'buildTime': 20,
                        'health': 100,
                        'team': 0 }
Buildings['TurretT2'] = { 'building': 'turret_t2',
                        'resources': { 'energy': ( 0, 500, 0, 10 ), 'metals': ( 0, 500, 0, 10 ) },
                        'pathImportance': 1010,
                        'attack': { 'range': 5, 'damage': 20, 'splash': 5, 'costs': { 'energy': 25, 'metals': 10 } },
                        'buildCost': { 'metals': 300, 'energy': 150 },
                        'buildTime': 50,
                        'health': 100,
                        'team': 0 }

def MakeBuildingTransform( source, cost, minTime = 10 ):
    ret = { 'transformTarget': source, 'transformCost': cost }
    ret['resources'] = { key: ( 0, cost[key] * 20, 0, cost[key] / minTime ) for key in cost }
    ret['building'] = source['building']

    ret['health'] = source['health']
    ret['team'] = source['team']

    return ret

for key in tuple( Buildings.keys() ):
    building = Buildings[key]

    if 'buildCost' in building:
        Buildings[key + '_Transform'] = MakeBuildingTransform( building, building['buildCost'], building['buildTime'] if 'buildTime' in building else 10 )
