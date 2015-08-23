from collections import defaultdict
from scene import Scene
import pygame
import base
import game
import gamelogic
import util
import config
import random
import ecs
import threading
import math
import widgets

keysPressed = base.frame.keysPressed

game.RenderTiles = []

def addTile( tileId, name ):
    while len( game.RenderTiles ) <= tileId:
        game.RenderTiles.append( None )

    img = game.assets[ name ]

    game.RenderTiles[ tileId ] = img

addTile( 10, 'img/land/grass.png' )
addTile( 11, 'img/land/grass_2.png' )
addTile( 12, 'img/land/grass_3.png' )

addTile( 20, 'img/land/grass_night.png' )
addTile( 21, 'img/land/grass_2_night.png' )
addTile( 22, 'img/land/grass_3_night.png' )

addTile( 32, 'img/tree_3.png' )
addTile( 64, 'img/tree_2.png' )
addTile( 96, 'img/tree_1.png' )

class GameScene( Scene ):
    def __init__( self ):
        super().__init__()

        self.loadLevel = 0
        self.flowThread = None
        self.pathThread = None

        self.resources = defaultdict( lambda: ( 0, 0, 0 ) )
        self.buildingConfig = None
        game.clock = 0
        game.wasNight = False
        game.isNight = False
        game.isOver = False
        game.spawnedTotal = 0
        self.spawned = 0
        
        self.checkedTrees = 0
        game.isPaused = False

    def isNight( self ):
        game.nightTicks = game.dayTicks - max( game.minDayTicks, game.baseDayTicks - ( game.clock / game.dayTicksReductionEvery ) )
        return ( game.clock % game.dayTicks ) > game.dayTicks - game.nightTicks

    def init( self ):
        return gamelogic.init.init( self )

    def clickTile( self, pos, event ):
        if event.button == 1:
            entities = self.world.entitiesWithComponent( ecs.COMPONENT_BUILDING ).atPosition( pos )
            if len( entities ) == 0:
                if not self.buildingConfig is None:
                    gamelogic.building.makeBuilding( self.world, pos, self.buildingConfig )
            else:
                for ent in entities:
                    self.world.removeEntity( ent )
        elif event.button == 3:
            i = self.corruption.I( pos )
            #print( self.corruption.surface[ i ], self.corruption.backSurface[ i ] )
            #print( self.corruption.resting[ i ], self.corruption.backResting[ i ] )

    def doInput( self, frameTime ):
        for event in base.frame.receiveInput():
            if event.type in ( pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION ):
                handled = False
                for widget in self.widgets:
                    if widget.checkIntersect( event ):
                        handled = True
                        break

                if handled:
                    continue
            elif event.type == pygame.KEYDOWN:
                if event.key >= ord('1') and event.key < ord('9'):
                    try:
                        button = self.widgets[0].children[ ( event.key-ord('1') ) * 3 ]
                        button.callback( button )
                    except IndexError:
                        pass
                elif event.key == pygame.K_ESCAPE:
                    self.showGamePause()


            if event.type == pygame.MOUSEBUTTONUP:
                mapPosition = ( game.cameraPosX + event.pos[0], game.cameraPosY  + event.pos[1] )
                tilePosition = ( mapPosition[0] // 32, mapPosition[1] // 32 )
                self.clickTile( tilePosition, event )

        if keysPressed[ 'cameraDown' ]:
            game.cameraPosY += config.cameraSpeedY * frameTime
        if keysPressed[ 'cameraUp' ]:                         
            game.cameraPosY -= config.cameraSpeedY * frameTime
        if keysPressed[ 'cameraLeft' ]:                       
            game.cameraPosX -= config.cameraSpeedX * frameTime
        if keysPressed[ 'cameraRight' ]:                      
            game.cameraPosX += config.cameraSpeedX * frameTime

        game.cameraPosX = util.clamp( game.cameraPosX, 0, game.mapPixelSizeX - game.SCREEN_SIZE[0] )
        game.cameraPosY = util.clamp( game.cameraPosY, 0, game.mapPixelSizeY - game.SCREEN_SIZE[1] )

    def drawGame( self, frameTime ):
        for x in range( int( game.cameraPosX // 32 - 1 ), int( ( game.cameraPosX + game.SCREEN_SIZE[0] ) // 32 + 1 ) ):
            for y in range( int( game.cameraPosY // 32 - 1 ), int( ( game.cameraPosY + game.SCREEN_SIZE[1] ) // 32 + 1 ) ):
                i = x + ( y * game.mapSize[0] )
                corruption = self.corruption.surface[ i ]

                cur = game.mapBuffer[ i ]

                if corruption > 7:
                    game.mapBuffer[ i ] = 12
                elif corruption > 1:
                    game.mapBuffer[ i ] = 11
                else:
                    game.mapBuffer[ i ] = 10

                if self.isNight():
                    game.mapBuffer[ i ] += 10

                if cur & 96 > 0:
                    game.mapBuffer[ i ] |= cur & 96

                if cur != game.mapBuffer[ i ]:
                    base.drawing.drawMap( 0, ( x, y ), game.RenderTiles[ game.mapBuffer[ i ] & 31 ] )

        base.drawing.renderMap( ( int( game.cameraPosX ), int( game.cameraPosY ) ) )

    def doFrame( self, frameTime ):
        super().doFrame( frameTime )

        self.doInput( frameTime )
        self.drawGame( frameTime )
        self.world.doFrame( frameTime, game.accumelator )
        gamelogic.draw.drawGui( self, frameTime, game.accumelator )

        while self.checkedTrees < game.accumelator * 300:
            self.checkedTrees += 1
            pos = ( random.randrange( game.mapSize[0] ), random.randrange( game.mapSize[1] ) )
            i = self.corruption.I( pos )

            if game.mapBuffer[ i ] & 96 > 0 and self.corruption.surface[i] > 1:
                game.mapBuffer[ i ] -= 32

                game.mapSurface[2].fill( (255,0,255), pygame.Rect( pos[0]*32, pos[1]*32, 32, 32 ) )
                cur = game.mapBuffer[ i ] & 96
                if cur > 0:
                    base.drawing.drawMap( 2, pos, game.RenderTiles[ cur ] )

    def showGamePause( self ):
        if game.isPaused:
            #Hiding menu
            game.isPaused = False

            for n in self.pausedWidgets:
                self.widgets.remove( n )

            self.pausedWidgets = None
        else:
            self.pausedWidgets = []
            pos = ( (game.SCREEN_SIZE[0]-320)/2, (game.SCREEN_SIZE[1]-600)/2 )
            self.pausedWidgets.append( widgets.Icon( pygame.Rect( pos[0], pos[1], 320, 600 ), game.assets['img/gameover.png'] ) )

            pos = ( pos[0]+10, pos[1]+10 )
            rect = pygame.Rect( pos[0], pos[1],300, 40 )
            self.pausedWidgets.append( widgets.Text( rect, 'Paused.', font='gameover1' ) )

            pollution = len([i for i in range(game.corruption.size[0]*game.corruption.size[1]) if game.corruption.surface[i] > 1])

            def quitCb( *_ ):
                game.gameIsRunning = False
            def resumeCb( *_ ):
                self.showGamePause()
            def mainCb( *_ ):
                self.nextScene = self.parent

            rect.top += 300
            self.pausedWidgets.append( widgets.TextButton( rect, 'Resume.', font='gameover3', callback=resumeCb ) )
            rect.top += 50
            self.pausedWidgets.append( widgets.TextButton( rect, 'Exit to menu.', font='gameover3', callback=mainCb ) )
            rect.top += 50
            self.pausedWidgets.append( widgets.TextButton( rect, 'Exit game.', font='gameover3', callback=quitCb ) )

            for n in self.pausedWidgets:
                self.widgets.append( n )

            game.isPaused = True

    def showGameover( self ):
        pos = ( (game.SCREEN_SIZE[0]-320)/2, (game.SCREEN_SIZE[1]-600)/2 )
        self.widgets.append( widgets.Icon( pygame.Rect( pos[0], pos[1], 320, 600 ), game.assets['img/gameover.png'] ) )

        pos = ( pos[0]+10, pos[1]+10 )
        rect = pygame.Rect( pos[0], pos[1],300, 40 )
        self.widgets.append( widgets.Text( rect, 'Game over!', font='gameover1' ) )

        pollution = len([i for i in range(game.corruption.size[0]*game.corruption.size[1]) if game.corruption.surface[i] > 1])

        rect.top += 50
        self.widgets.append( widgets.Text( rect, 'You survived %d nights.' % int( game.clock / game.dayTicks ), font='gameover2' ) )
        rect.top += 50
        self.widgets.append( widgets.Text( rect, 'You killed %d defenseless people.' % game.spawnedTotal, font='gameover2' ) )
        rect.top += 50
        self.widgets.append( widgets.Text( rect, 'You destroyed %d acres of land.' % pollution, font='gameover2' ) )
        rect.top += 50
        self.widgets.append( widgets.Text( rect, 'And why?', font='gameover3' ) )
        rect.top += 50
        self.widgets.append( widgets.Text( rect, 'They were only defending themselves.', font='gameover2' ) )
        rect.top += 100
        def quitCb( *_ ):
            game.gameIsRunning = False
        self.widgets.append( widgets.TextButton( rect, 'Exit.', font='gameover3', callback=quitCb ) )
        rect.top += 50
        def mainCb( *_ ):
            self.nextScene = self.parent
        self.widgets.append( widgets.TextButton( rect, 'Main menu.', font='gameover3', callback=mainCb ) )

    def doTick( self ):
        if game.isPaused:
            return

        self.checkedTrees = 0
        game.clock += 1
        game.wasNight = game.isNight
        game.isNight = self.isNight()

        buildings = tuple( self.world.entitiesWithComponent( ecs.COMPONENT_BUILDING ) )
        if len( buildings ) == 0:
            if not game.isOver:
                self.showGameover()
                game.isOver = True
        else:
            building = random.choice( buildings )
            i = game.corruption.I( building.position )
            if i in game.corruption.sources:
                game.corruption.addSource( i, game.corruption.sources[i] * 1.1 )

        self.world.sortEntities()
        self.world.doTick()
        gamelogic.resources.calculateResources( self )



        #pos = (game.cameraPosX/32,game.cameraPosY/32)
        if self.isNight():
            if not game.wasNight:
                self.spawnPoints = [ i for i in range( self.pathFinding.size[0]*self.pathFinding.size[1] ) if self.pathFinding.surface[i] > 940 and self.pathFinding.surface[i] < 980 ]
                self.toSpawn = int( math.floor( ( game.baseEnemyAmount + game.enemyPerNight * math.pow( math.floor( game.clock / game.dayTicks ), game.enemyPerNightPower ) ) ) )
                self.perTick = int( math.ceil( self.toSpawn / game.nightTicks ) ) + 1

                self.spawned = 0


            if len( self.spawnPoints ) > 0:
                i = 0
                while i < self.perTick and self.spawned < self.toSpawn:
                    pos = random.choice( self.spawnPoints )
                    pos = ( pos % self.pathFinding.size[0], int( pos // self.pathFinding.size[0] ) )

                    base = gamelogic.enemies.Enemies[ random.choice( tuple( gamelogic.enemies.Enemies.keys() ) ) ]
                    gamelogic.enemies.makeEnemy( self.world, pos, base )

                    i += base['value']
                    self.spawned += base['value']
                    game.spawnedTotal += 1

        if self.flowThread is None or not self.flowThread.is_alive():
            self.corruption.swap()

            self.flowThread = threading.Thread( target = lambda: self.corruption.cleanIterative() )
            self.flowThread.start()
        else:
            print( 'WARNING: Flow update thread not done on time!' )

        if self.pathThread is None or not self.pathThread.is_alive():
            self.pathThread = threading.Thread( target = lambda: self.pathFinding.cleanRecursive() )
            self.pathThread.start()
        else:
            print( 'WARNING: Pathfinding update thread not done on time!' )
