import game

class Scene:
    def __init__( self ):
        self.nextScene = None
        self.parent = None

    def doFrame( self, frameTime ):
        if self.nextScene is not None:
            if self.nextScene.init():
                self.nextScene.parent = self
                game.scene = self.nextScene
                self.nextScene = None
