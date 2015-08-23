import smoothflowmap
import flowmap
import base
import widgets
import game
import ecs
import gamelogic
import pygame

def init( self ):
    if self.loadLevel == 0:
        base.drawing.initMap( ( 256, 256 ) )
    elif self.loadLevel == 1:
        for i in range( len( game.mapBuffer ) ):
            game.mapBuffer[ i ] = 10

        self.corruption = smoothflowmap.Flowmap( game.mapSize )
        self.pathFinding = flowmap.Flowmap( game.mapSize )

        game.corruption = self.corruption
        game.pathFinding = self.pathFinding
    elif self.loadLevel == 10:
        for x in range( 256 ):
            for y in range( 256 ):
                base.drawing.drawMap( ( x, y ), game.RenderTiles[ game.mapBuffer[ x + y * 256 ] ] )
    elif self.loadLevel == 19:
        self.world = ecs.World()

        gamelogic.building.makeBuilding( self.world, ( 128, 128 ), gamelogic.building.Buildings['HearthZiggurat'] )

        gamelogic.building.makeBuilding( self.world, ( 127, 128 ), gamelogic.building.Buildings['HearthPylon'] )
        gamelogic.building.makeBuilding( self.world, ( 128, 127 ), gamelogic.building.Buildings['HearthPylon'] )
        gamelogic.building.makeBuilding( self.world, ( 129, 128 ), gamelogic.building.Buildings['HearthPylon'] )
        gamelogic.building.makeBuilding( self.world, ( 128, 129 ), gamelogic.building.Buildings['HearthPylon'] )
    elif self.loadLevel > 20:
        gamelogic.centerCameraOnTile( ( 128, 128 ) )
        initGui( self )
        return True

    self.loadLevel += 1
    return False

def initGui( self ):
    self.widgets = []

    #Buildings
    self.widgets.append( widgets.Bar( 512, 'img/gui/bar', margin=6 ) )

    buildingBar = self.widgets[0]
    def addBuilding( image, name, callback ):
        button = buildingBar.addChild( widgets.IconButton, game.assets[ 'img/gui/bar_iconholder.png' ], game.assets[ 'img/gui/bar_iconholder_hover.png' ], callback = callback )
        buildingBar.addChild( widgets.Icon, game.assets[ image ], rect = pygame.Rect( button.rect.left+2, button.rect.top+15, 32, 32 ) )
        buildingBar.addChild( widgets.Text, name, font = 'description', rect = pygame.Rect( button.rect.left, button.rect.top + 50, 34, 14 ) )

    def setBuildingCb( building ):
        def cb( _ ):
            self.buildingConfig = building
        return cb

    addBuilding( 'img/buildings/combined/building_energy_0.png', 'Energy ziggurat', setBuildingCb( gamelogic.building.Buildings['EnergyZiggurat_Transform'] ) )
    addBuilding( 'img/buildings/combined/building_metals_0.png', 'Metals ziggurat', setBuildingCb( gamelogic.building.Buildings['MetalsZiggurat_Transform'] ) )
    addBuilding( 'img/buildings/combined/pylon_energy_0.png', 'Energy pylon', setBuildingCb( gamelogic.building.Buildings['EnergyPylon_Transform'] ) )
    addBuilding( 'img/buildings/combined/pylon_metals_0.png', 'Metals pylon', setBuildingCb( gamelogic.building.Buildings['MetalsPylon_Transform'] ) )

    addBuilding( 'img/buildings/combined/turret_t1_0.png', 'T1 Turret', setBuildingCb( gamelogic.building.Buildings['TurretT1_Transform'] ) )
    addBuilding( 'img/buildings/combined/turret_t2_0.png', 'T2 Turret', setBuildingCb( gamelogic.building.Buildings['TurretT2_Transform'] ) )

    #Resources
    self.widgets.append( widgets.Bar( 512, 'img/gui/bar', onTop = True, margin=10 ) )

    def addResource( name ):
        self.widgets[1].addChild( widgets.Charger, game.assets[ 'img/gui/bar_chargeholder.png' ], game.assets[ 'img/gui/bar_chargeholder_hover.png' ] )
        rect = self.widgets[1].children[-1].rect.copy()
        rect.top += 4
        rect.height /= 2

        self.widgets[1].addChild( widgets.TextButton, name, rect = rect, drawBackground = False, font = 'resources' )
        return self.widgets[1].children[-2]

    self.energyWidget = addResource( 'Energy' )
    self.metalsWidget = addResource( 'Metals' )
