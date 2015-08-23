import game
import numpy

class Flowmap:
    def __init__( self, size, diagonalWeight = -1 ):
        self.size = size
        size = size[0] * size[1]

        self.sources = {}
        self.weights = numpy.full( (size,), 1, dtype=numpy.float )
        self.surface = numpy.full( (size,), 0, dtype=numpy.float )
        self.backSurface = numpy.array( self.surface )
        self.resting = bytearray( [ 6 for n in range(size) ] )
        self.backResting = bytearray( [ 6 for n in range(size) ] )

        self.directions = ( ( -1,0 ), ( 1,0 ), ( 0,-1 ), (0,1) )
        self.offsets = ( -1, 1, -self.size[0], self.size[0] )

        #self.iterativeOffests = ( -1, 1, -self.size[0], self.size[0], -1-self.size[0], -1+self.size[0], 1-self.size[0], 1+self.size[0], 0 )
        self.iterativeOffests = ( -1, 1, -self.size[0], self.size[0], 0 )
        self.iterativeWeights = ( 0.1, 0.1, 0.1, 0.1, 0.5 )

        self.isDirty = True

    def I( self, pos ):
        return int( pos[0] ) + int( pos[1] ) * self.size[0]

    def addSource( self, pos, val ):
        try:
            index = self.I( pos )
        except TypeError:
            index = pos

        if val > 0:
            self.sources[ index ] = val
        elif index in self.sources:
            del self.sources[ index ]

        self.isDirty = True

    def cleanIterative( self, cleanPerStep = -1.0 ):
        #Set edges on backSurface
        for x in range( game.mapSize[ 0 ] ):
            self.backSurface[ x ] = 0
            self.backSurface[ x + ( game.mapSize[0] * ( game.mapSize[1]-1 ) ) ] = 0
        for y in range( game.mapSize[ 0 ] ):
            _y = y * game.mapSize[ 0 ]
            self.backSurface[ _y ] = 0
            self.backSurface[ _y + ( game.mapSize[0] - 1 ) ] = 0

        iterativeIs = tuple( range( len( self.iterativeOffests ) ) )

        for n in self.sources:
            self.surface[ n ] = self.sources[ n ]
            self.resting[ n ] = 0

        sleeping = 0
        for y in range( 1, game.mapSize[1] - 1 ):
            index = self.I( ( 1, y ) )
            for x in range( 1, game.mapSize[0] - 1 ):
                if self.resting[ index ] >= 5:
                    if self.resting[ index ] == 5:
                        self.backResting[ index ] = self.resting[ index ] + 1
                    sleeping += 1
                    index += 1
                    continue

                #self.backSurface[ index ] = sum( [
                #        self.iterativeWeights[ n ] * self.surface[ index + self.iterativeOffests[ n ] ]
                #        for n in iterativeIs
                #    ] )

                curVal = self.surface[ index ]
                newVal  = (
                        self.iterativeWeights[ 0 ] * self.surface[ index + self.iterativeOffests[ 0 ] ] +
                        self.iterativeWeights[ 1 ] * self.surface[ index + self.iterativeOffests[ 1 ] ] +
                        self.iterativeWeights[ 2 ] * self.surface[ index + self.iterativeOffests[ 2 ] ] +
                        self.iterativeWeights[ 3 ] * self.surface[ index + self.iterativeOffests[ 3 ] ] +
                        self.iterativeWeights[ 4 ] * curVal
                        )

                self.backSurface[ index ] = newVal

                if abs( curVal - newVal ) > 0.001:
                    self.backResting[ index + self.iterativeOffests[ 0 ] ] = 0
                    self.backResting[ index + self.iterativeOffests[ 1 ] ] = 0
                    self.backResting[ index + self.iterativeOffests[ 2 ] ] = 0
                    self.backResting[ index + self.iterativeOffests[ 3 ] ] = 0
                else:
                    self.backResting[ index ] = self.resting[ index ] + 1

                index += 1

    def swap( self ):
        temp = self.surface
        self.surface = self.backSurface
        self.backSurface = temp

        temp = self.resting
        self.resting = self.backResting
        self.backResting = temp
        
    def cleanRecursive( self ):
        if not self.isDirty:
            return tuple()

        self.isDirty = False
        size = self.size[0] * self.size[1]
        self.surface = numpy.full( (size,), 0, dtype=numpy.float )

        dirtyTiles = set()

        def addDirty( i, val ):
            x, y = i % self.size[0], i // self.size[0]

            for n in self.directions:
                _x, _y = x+n[0], y+n[1]
                if _x < 0 or _y < 0:
                    continue
                if _x >= self.size[0] or _y >= self.size[1]:
                    continue

                index =  _x + _y * self.size[0] 
                if self.surface[ index ] < val:
                    dirtyTiles.add( index )

        for key in self.sources:
            self.surface[ key ] = self.sources[ key ]
            addDirty( key, self.sources[ key ] )

        for key in self.sources:
            dirtyTiles.discard( key )

        changedSet = set()
        count = 0
        while len( dirtyTiles ) > 0:
            index = dirtyTiles.pop()
            count += 1
            changedSet.add( index )

            val = max( [ self.surface[ index + n ] for n in self.offsets ] )
            val = max( 0, val - self.weights[ index ] )
            self.surface[ index ] = val

            addDirty( index, val )
        return changedSet
