import ecs
import gamelogic

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

#Resources tuple: ( use per tick, maximum stored, maximum send per burst, maximum received )

energyZiggurat = { 'building': 'building_energy', 'resources': { 'energy': ( -10, 20, 20, 0 ) }, 'corrupts': 1000, 'pathImportance': 1000 }
energyPylon = { 'building': 'pylon_energy', 'resources': { 'energy': ( 1, 200, 25, 25 ) }, 'corrupts': 100, 'pathImportance': 1000 }

metalsZiggurat = { 'building': 'building_metals', 'resources': { 'metals': ( -10, 20, 10, 0 ) }, 'corrupts': 2000, 'pathImportance': 1000 }
metalsPylon = { 'building': 'pylon_metals', 'resources': { 'metals': ( 1, 200, 25, 25 ) }, 'corrupts': 300, 'pathImportance': 1000 }

hearthZiggurat = { 'building': 'building_heart', 'resources': { 'energy': ( -25, 50, 50, 0 ), 'metals': ( -25, 50, 50, 0 ) }, 'corrupts': 3000, 'pathImportance': 1000 }
hearthPylon = { 'building': 'pylon_heart', 'resources': { 'energy': ( 1, 200, 25, 25 ), 'metals': ( 1, 200, 25, 25 ) }, 'corrupts': 3000, 'pathImportance': 1000 }
