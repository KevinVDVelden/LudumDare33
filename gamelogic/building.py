import ecs
import gamelogic
import pygame

class AttackComponent( ecs.Component ):
    def __init__( self, config ):
        self.config = config
        self.range = config['range']
        self.damage = config['damage']
        self.target = None

        self.costs = config['costs'] if 'costs' in config else None
        self.attackCooldown = config['attackCooldown'] if 'attackCooldown' in config else 1

        self.attackCurCooldown = 0

        super().__init__( ecs.COMPONENT_ATTACK )

    def think( self, ent, world ):
        self.attackCurCooldown = max( 0, self.attackCurCooldown - 1 )

        if self.costs is None:
            storage = None
        else:
            storage = ent.getComponent( ecs.COMPONENT_RESOURCE )
            if storage is None:
                return

        #Return true if we can't attack the target due it either being dead or out of range
        def attackTarget( target ):
            if ( target.position[0] - ent.position[0] ) ** 2 + ( target.position[1] - ent.position[1] ) ** 2 > self.range ** 2:
                return True

            while True:
                if storage is not None:
                    if storage.hasResources( self.costs ) and self.attackCurCooldown < 1:
                        storage.takeResources( self.costs )
                        self.attackCurCooldown += self.attackCooldown
                    else:
                        return False
                else:
                    if self.attackCurCooldown >= 1:
                        return False
                    else:
                        self.attackCurCooldown += self.attackCooldown

                health = target.getComponent( ecs.COMPONENT_HEALTH )
                #TODO: Keep track of "teams"
                health.takeDamage( self.damage )

                if health.health < 0:
                    return True

        if self.target is not None:
            if attackTarget( self.target ):
                self.target = None

        entities = list( world.entsInRect( pygame.Rect( ent.position[0] - self.range, ent.position[1] - self.range, self.range * 2, self.range * 2 ) ) )
        entities.sort( key=lambda target: ( target.position[0] - ent.position[0] ) ** 2 + ( target.position[1] - ent.position[1] ) ** 2 )

        for ent in entities:
            if ent.hasComponent( ecs.COMPONENT_HEALTH ) == False:
                continue

            if attackTarget( ent ) == False:
                self.target = ent


def makeBuilding( self, pos, config ):
    ent = self.world.addEntity( pos )
    ent.addComponent( ecs.RenderComponent( 'img/buildings/combined/building_energy_11.png' ) )

    if 'building' in config:
        ent.addComponent( gamelogic.BuildingComponent( config['building'], config ) )

    if 'resources' in config:
        ent.addComponent( gamelogic.resources.ResourceStoreComponent( config['resources'] ) )

    #TODO: Make this a component?
    if 'corrupts' in config:
        self.corruption.addSource( pos, config['corrupts'] )
    if 'pathImportance' in config:
        self.pathFinding.addSource( pos, config['pathImportance'] )

    if 'attack' in config:
        ent.addComponent( AttackComponent( config['attack'] ) )

#Resources tuple: ( use per tick, maximum stored, maximum send per burst, maximum received )

energyZiggurat = { 'building': 'building_energy', 'resources': { 'energy': ( -10, 20, 20, 0 ) }, 'corrupts': 1000, 'pathImportance': 1000 }
energyPylon = { 'building': 'pylon_energy', 'resources': { 'energy': ( 1, 200, 25, 25 ) }, 'corrupts': 100, 'pathImportance': 1000 }

metalsZiggurat = { 'building': 'building_metals', 'resources': { 'metals': ( -10, 20, 10, 0 ) }, 'corrupts': 2000, 'pathImportance': 1000 }
metalsPylon = { 'building': 'pylon_metals', 'resources': { 'metals': ( 1, 200, 25, 25 ) }, 'corrupts': 300, 'pathImportance': 1000 }

hearthZiggurat = { 'building': 'building_heart', 'resources': { 'energy': ( -25, 50, 50, 0 ), 'metals': ( -25, 50, 50, 0 ) }, 'corrupts': 3000, 'pathImportance': 1000 }
hearthPylon = { 'building': 'pylon_heart', 'resources': { 'energy': ( 1, 200, 25, 25 ), 'metals': ( 1, 200, 25, 25 ) }, 'corrupts': 3000, 'pathImportance': 1000 }

turretT1 = { 'building': 'turret_t1', 'resources': { 'energy': ( 0, 200, 0, 25 ) }, 'pathImportance': 1010, 'attack': { 'range': 3, 'damage': 5, 'attackCooldown': 0.1, 'costs': { 'energy': 5 } } }
turretT2 = { 'building': 'turret_t2', 'resources': { 'energy': ( 0, 500, 0, 10 ), 'metals': ( 0, 500, 0, 10 ) }, 'pathImportance': 1010, 'attack': { 'range': 5, 'damage': 20, 'splash': 5, 'costs': { 'energy': 5, 'metals': 10 } } }
