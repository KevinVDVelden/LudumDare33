import game

class Flowmap:
    def __init__( self, size ):
        self.size = size
        size = size[0] * size[1]

        self.sources = {}
        self.weights = bytearray( [ 1 for n in range( size ) ] )
        self.surface = bytearray( [ 255 for n in range( size ) ] )

        self.directions = ( ( -1,0 ), ( 1,0 ), ( 0,-1 ), (0,1) )
        self.offsets = ( -1, 1, -self.size[0], self.size[0] )

        self.isDirty = True

    def addSource( self, pos, val ):
        try:
            index = pos[0] + pos[1] * self.size[0]
        except IndexError:
            index = pos

        self.sources[ index ] = val
        
    def clean( self ):
        size = self.size[0] * self.size[1]
        self.surface = bytearray( [ 0 for n in range( size ) ] )

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

        count = 0
        while len( dirtyTiles ) > 0:
            index = dirtyTiles.pop()
            count += 1

            val = max( [ self.surface[ index + n ] for n in self.offsets ] )
            val = max( 0, val - self.weights[ index ] )
            self.surface[ index ] = val

            addDirty( index, val )
        print( count )
