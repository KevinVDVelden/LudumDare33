import ecs
import random
import pygame
import game
import gamelogic

class PathWalker( ecs.Component ):
    def __init__( self, pathMap, move ):
        self.pathMap = pathMap
        self.ticksTillTarget = 0
        super().__init__( ecs.COMPONENT_THINK )

        self.moveFast = move[0]
        self.moveSlow = move[1]

    def setEntity( self, ent, world ):
        self.target = ent.position
        super().setEntity( ent, world )

    def think( self, ent, world ):
        ent.position = ( ent.position[0] + ent.velocity[0], ent.position[1] + ent.velocity[1] )
        self.ticksTillTarget -= 1

        if self.ticksTillTarget <= 0:
            pos = self.target
            ent.position = pos

            index = self.pathMap.I( pos )
            curVal = self.pathMap.surface[ index ]

            bestDir = None
            bestVal = curVal
            ticks = 0

            for i in range( 8 ):
                if not self.pathMap.InBounds( pos, self.pathMap.directions[ i ] ):
                    continue

                testIndex = index + self.pathMap.offsets[i]
                testVal = self.pathMap.surface[ testIndex ]
                ticks = self.moveFast if i < 4 else self.moveSlow

                if testVal > bestVal:
                    bestDir = self.pathMap.directions[i]
                    bestVal = testVal

            if bestDir is not None:
                ent.velocity = ( bestDir[0] / ticks, bestDir[1] / ticks )
                self.target = ( pos[0] + bestDir[0], pos[1] + bestDir[1] )
                self.ticksTillTarget = ticks
            else:
                ent.velocity = ( 0, 0 )

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

    def doAttack( self, target, targetHealth, world ):
        targetHealth.takeDamage( self.damage )

    def think( self, curEnt, world ):
        self.attackCurCooldown = max( 0, self.attackCurCooldown - 1 )

        if curEnt.team != 0:
            if not game.isNight:
                curEnt.getComponent( ecs.COMPONENT_HEALTH ).takeDamage( random.random() )

        if self.costs is None:
            storage = None
        else:
            storage = curEnt.getComponent( ecs.COMPONENT_RESOURCE )
            if storage is None:
                return

        #Return true if we can't attack the target due it either being dead or out of range
        def attackTarget( target ):
            if ( target.position[0] - curEnt.position[0] ) ** 2 + ( target.position[1] - curEnt.position[1] ) ** 2 > self.range ** 2 or target.getComponent( ecs.COMPONENT_HEALTH ).health < 0:
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
                self.doAttack( target, health, world )

                if health.health < 0:
                    return True

        if self.target is not None:
            if attackTarget( self.target ):
                self.target = None

        entities = list( world.entsInRect( pygame.Rect( curEnt.position[0] - self.range, curEnt.position[1] - self.range, self.range * 2, self.range * 2 ) ) )
        entities.sort( key=lambda target: ( target.position[0] - curEnt.position[0] ) ** 2 + ( target.position[1] - curEnt.position[1] ) ** 2 )

        for ent in entities:
            if ent.hasComponent( ecs.COMPONENT_HEALTH ) == False:
                continue
            elif ent.team == curEnt.team:
                continue

            if attackTarget( ent ) == False:
                self.target = ent

def makeEnemy( world, pos, config ):
    ent = world.addEntity( pos )
    ent.addComponent( ecs.RenderComponent( config['render'] ) )
    ent.team = config['team']

    if 'pathfinder' in config:
        _map = game.pathFinding if 'path' in config['pathfinder'] else None
        move = config['pathfinder']['move'] if 'move' in config['pathfinder'] else ( 2,3 )
        ent.addComponent( PathWalker( _map, move ) )

    if 'health' in config:
        ent.addComponent( ecs.HealthComponent( config['health'] ) )

    if 'attack' in config:
        ent.addComponent( gamelogic.enemies.AttackComponent( config['attack'] ) )


Enemies = {}

Enemies['Imp'] = {
                    'pathfinder': { 'path': 'default', 'move': ( 2, 3 ) },
                    'attack': { 'range': 1, 'damage': 5, 'splash': 5 },
                    'render': 'img/iron_imp.png',
                    'health': 30,
                    'team': 1 }
Enemies['Imp2'] = {
                    'pathfinder': { 'path': 'default', 'move': ( 4, 5 ) },
                    'attack': { 'range': 1, 'damage': 8 },
                    'render': 'img/second_imp.png',
                    'health': 60,
                    'team': 1 }
