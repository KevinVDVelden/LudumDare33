import ecs

class Component:
    def __init__( self, typeId ):
        self.typeId = typeId

    def setEntity( self, ent, world ):
        self.entity = ent
        self.world = world

class HealthComponent( Component ):
    def __init__( self, maxHealth ):
        self.health = maxHealth
        self.maxHealth = maxHealth
        super().__init__( ecs.COMPONENT_HEALTH )

    def takeDamage( self, damage ):
        self.health -= damage

        if self.health < 0:
            #TODO: Splat
            print( 'SPLAT', self.entity )
            self.world.removeEntity( self.entity )
