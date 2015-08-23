import game
import numpy
import math
from collections import deque

sqrt2 = math.sqrt( 2 )


class Flowmap:
    def __init__( self, size, diagonalWeight = -1 ):
        self.size = size
        size = size[0] * size[1]

        self.sources = {}
        self.weights = numpy.full( (size,), 1, dtype=numpy.float )
        self.surface = numpy.full( (size,), 0, dtype=numpy.float )

        self.directions = ( ( -1,0 ), ( 1,0 ), ( 0,-1 ), ( 0,1 ), ( -1,-1 ), ( -1,1 ), ( 1,-1 ), ( 1,1 ) )
        self.offsets = (
                -1, 1,
                -self.size[0], self.size[0],
                -1-self.size[0], -1+self.size[0],
                1-self.size[0], 1+self.size[0] )
        self.weightMult = ( 1, 1, 1, 1, sqrt2, sqrt2, sqrt2, sqrt2 )
        self.offsetIs = tuple( range( len( self.offsets ) ) )

        self.isDirty = True
        self.isCleaning = False

    def InBounds( self, pos, add = (0,0) ):
        if ( pos[0]+add[0] < 0 or pos[1]+add[1] < 0 or
                pos[0]+add[0] >= self.size[0] or pos[1]+add[1] >= self.size[1] ):
            return False
        else:
            return True


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
        
    def cleanRecursive( self ):
        if self.isDirty:
            self.isDirty = False
            self.isCleaning = False
            size = self.size[0] * self.size[1]
            self.surface = numpy.full( (size,), 0, dtype=numpy.float )

            dirtyTiles = deque()
            dirtyTileSet = set()
            self.visited = 0
        elif self.isCleaning:
            dirtyTiles = self.dirtyTiles
            dirtyTileSet = self.dirtyTileSet
        else:
            return None


        def addDirty( i, val ):
            x, y = i % self.size[0], i // self.size[0]

            for n in self.directions:
                _x, _y = x+n[0], y+n[1]
                if _x < 1 or _y < 1:
                    continue
                if _x >= self.size[0] - 1 or _y >= self.size[1] - 1:
                    continue

                index =  _x + _y * self.size[0] 
                if index not in dirtyTileSet and self.surface[ index ] + 2 < val:
                    dirtyTiles.append( index )
                    dirtyTileSet.add( index )

        if not self.isCleaning:
            for key in self.sources:
                self.surface[ key ] = self.sources[ key ]
                addDirty( key, self.sources[ key ] )

            for key in self.sources:
                if key in dirtyTileSet:
                    dirtyTiles.remove( key )
                    dirtyTileSet.remove( key )


        count = 0
        run = 0
        while len( dirtyTiles ) > 0:
            run += 1
            if run == 5000:
                break

            index = dirtyTiles.popleft()
            dirtyTileSet.remove( index )
            count += 1

            val = max( [
                self.surface[ index + self.offsets[n] ] - ( self.weights[ index ] * self.weightMult[n] )
                for n in self.offsetIs ] )

            val = max( 0, val )
            if self.surface[ index ] > val:
                continue

            self.surface[ index ] = val
            addDirty( index, val )

        self.visited += run
        print( len( dirtyTiles ), self.visited / (game.mapSize[0]*game.mapSize[1]) )
        if len( dirtyTiles ) > 0:
            self.dirtyTiles = dirtyTiles
            self.dirtyTileSet = dirtyTileSet
            self.isCleaning = True
        else:
            self.isCleaning = False
