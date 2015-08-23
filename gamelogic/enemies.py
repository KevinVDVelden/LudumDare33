import ecs
import random

class PathWalker( ecs.Component ):
    def __init__( self, pathMap ):
        self.pathMap = pathMap
        super().__init__( ecs.COMPONENT_THINK )

    def think( self, ent, world ):
        ent.position = ( ent.position[0] + ent.velocity[0], ent.position[1] + ent.velocity[1] )
        pos = ent.position

        index = self.pathMap.I( pos )
        curVal = self.pathMap.surface[ index ]

        bestDir = None
        bestVal = curVal

        for i in range( 8 ):
            if not self.pathMap.InBounds( pos, self.pathMap.directions[ i ] ):
                continue

            testIndex = index + self.pathMap.offsets[i]
            testVal = self.pathMap.surface[ testIndex ]

            if testVal > bestVal:
                bestDir = self.pathMap.directions[i]
                bestVal = testVal

        if bestDir is not None:
            ent.velocity = bestDir
        else:
            ent.velocity = ( 0, 0 )
            #randDir = random.randrange( 4 )

            #if self.pathMap.InBounds( pos, self.pathMap.directions[ i ] ):
            #    ent.velocity = self.pathMap.directions[ i ]
