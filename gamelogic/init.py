import flowmap
import base
import widgets
import game
import ecs
import gamelogic

def init( self ):
    if self.loadLevel == 0:
        base.drawing.initMap( ( 256, 256 ) )
    elif self.loadLevel == 1:
        for i in range( len( game.mapBuffer ) ):
            game.mapBuffer[ i ] = 10

        flow = flowmap.Flowmap( game.mapSize )
        self.corruption = flow
    elif self.loadLevel == 10:
        for x in range( 256 ):
            for y in range( 256 ):
                base.drawing.drawMap( ( x, y ), game.RenderTiles[ game.mapBuffer[ x + y * 256 ] ] )
    elif self.loadLevel == 19:
        self.world = ecs.World()

        for x in range( 127, 130 ):
            for y in range( 127, 130 ):
                pos = ( x, y )
                ent = self.world.addEntity( pos )
                ent.addComponent( ecs.RenderComponent( 'img/buildings/combined/building_mana_11.png' ) )
                ent.addComponent( gamelogic.BuildingComponent( 'heart' ) )
                self.changingCorruption[ self.corruption.I( pos ) ] = 2000
    elif self.loadLevel > 20:
        gamelogic.centerCameraOnTile( ( 128, 128 ) )
        initGui( self )
        return True

    self.loadLevel += 1
    return False

def initGui( self ):
    self.widgets = []
    self.widgets.append( widgets.Bar( 512, 'img/gui/bar' ) )
    self.widgets[0].addChild( widgets.IconButton, game.assets[ 'img/gui/bar_iconholder.png' ], game.assets[ 'img/gui/bar_iconholder_hover.png' ] )

    self.widgets.append( widgets.Bar( 512, 'img/gui/bar', onTop = True, margin=10 ) )

    self.widgets[1].addChild( widgets.Charger, game.assets[ 'img/gui/bar_chargeholder.png' ], game.assets[ 'img/gui/bar_chargeholder_hover.png' ] )
    rect = self.widgets[1].children[0].rect.copy()
    rect.height /= 2
    self.widgets[1].addChild( widgets.TextButton, 'Mana', rect = rect, drawBackground = False )
    self.manaWidget = self.widgets[1].children[0]

    self.widgets[1].addChild( widgets.Charger, game.assets[ 'img/gui/bar_chargeholder.png' ], game.assets[ 'img/gui/bar_chargeholder_hover.png' ] )
    rect = self.widgets[1].children[2].rect.copy()
    rect.height /= 2
    self.widgets[1].addChild( widgets.TextButton, 'Souls', rect = rect, drawBackground = False )
    self.soulsWidget = self.widgets[1].children[2]
