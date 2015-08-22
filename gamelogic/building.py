import ecs
import gamelogic

def makeBuilding( self, pos, config ):
    ent = self.world.addEntity( pos )
    ent.addComponent( ecs.RenderComponent( 'img/buildings/combined/building_mana_11.png' ) )

    if 'building' in config:
        ent.addComponent( gamelogic.BuildingComponent( config['building'], config ) )

    if 'resource_storage' in config:
        ent.addComponent( gamelogic.resources.ResourceStoreComponent( config['resource_storage'] ) )
    if 'resource_use' in config:
        ent.addComponent( gamelogic.resources.ResourceUseComponent( config['resource_use'] ) )

    #TODO: Make this a component?
    if 'corrupts' in config:
        self.changingCorruption[ self.corruption.I( pos ) ] = config['corrupts']

manaZiggurat = { 'building': 'building_mana', 'resource_use': { 'mana': -10 }, 'corrupts': 1000 }
soulZiggurat = { 'building': 'building_power', 'resource_use': { 'soul': -10 }, 'corrupts': 2000 }

manaPylon = { 'building': 'pylon_mana', 'resource_storage': { 'mana': ( 200, 25 ) }, 'resource_use': { 'mana': 1 }, 'corrupts': 100 }
soulPylon = { 'building': 'pylon_power', 'resource_storage': { 'soul': ( 200, 25 ) }, 'resource_use': { 'soul': 1 }, 'corrupts': 300 }

hearthZiggurat = { 'building': 'building_heart', 'resource_use': { 'mana': -25, 'soul': -25 }, 'corrupts': 3000 }
hearthPylon = { 'building': 'pylon_heart', 'resource_storage': { 'mana': ( 200, 25 ), 'soul': ( 200, 25 ) }, 'resource_use': { 'mana': 1, 'soul': 1 }, 'corrupts': 3000 }
