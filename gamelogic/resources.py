import ecs
from collections import defaultdict

def calculateResources( self ):
    resources = defaultdict( lambda: ( 0, 0, 0 ) )

    for ent in self.world.entitiesWithComponent( ecs.COMPONENT_RESOURCE_STORE ):
        comp = ent.getComponent( ecs.COMPONENT_RESOURCE_STORE )

        for key in comp.caps:
            cur = resources[ key ]

            resources[ key ] = ( cur[0] + comp.stored[key], cur[1] + comp.caps[key], cur[2] )

    for ent in self.world.entitiesWithComponent( ecs.COMPONENT_RESOURCE_USER ):
        comp = ent.getComponent( ecs.COMPONENT_RESOURCE_USER )

        for key in comp.rates:
            cur = resources[ key ]
            resources[ key ] = ( cur[0], cur[1], cur[2] + comp.rates[key] )

    self.prevResources = self.resources
    self.resources = resources

    self.mana = self.resources['mana']
    if self.mana[1] > 0:
        self.manaWidget.setCharge( self.mana[0] / self.mana[1] )
    else:
        self.manaWidget.setCharge( 0 )

    self.souls = self.resources['souls']
    if self.souls[1] > 0:
        self.soulsWidget.setCharge( self.souls[0] / self.souls[1] )

class ResourceUseComponent( ecs.Component ):
    def __init__( self, rates ):
        self.rates = rates
        super().__init__( ecs.COMPONENT_RESOURCE_USER )

class ResourceStoreComponent( ecs.Component ):
    def __init__( self, caps ):
        self.caps = caps
        self.stored = { key: 0 for key in self.caps }
        super().__init__( ecs.COMPONENT_RESOURCE_STORE )
