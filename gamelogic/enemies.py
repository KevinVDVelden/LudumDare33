import ecs
import random

class PathWalker( ecs.Component ):
    def __init__( self, pathMap ):
        self.pathMap = pathMap
        self.ticksTillTarget = 0
        super().__init__( ecs.COMPONENT_THINK )

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
                ticks = 2 if i < 4 else 3

                if testVal > bestVal:
                    bestDir = self.pathMap.directions[i]
                    bestVal = testVal

            if bestDir is not None:
                ent.velocity = ( bestDir[0] / ticks, bestDir[1] / ticks )
                self.target = ( pos[0] + bestDir[0], pos[1] + bestDir[1] )
                self.ticksTillTarget = ticks
            else:
                ent.velocity = ( 0, 0 )
