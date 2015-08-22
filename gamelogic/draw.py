import game

def drawGui( self, frameTime, accumelator ):
    for n in self.widgets:
        n.draw( game.screen )
