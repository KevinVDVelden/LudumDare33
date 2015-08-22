import pygame
import base.drawing
import game

class Widget:
    def __init__( self, rect ):
        self.rect = rect
        self.children = []

    def draw( self ):
        for n in self.children:
            n.draw()

    def createBuffer( self ):
        self.buffer = pygame.Surface( ( int( self.rect.width ), int( self.rect.height ) ) )
        return self.buffer


class Button( Widget ):
    def __init__( self, rect, text, font = 'menu', layoutFunc = None, callback = None ):
        self.text = text
        self.font = font
        self.bgColor = ( 200, 200, 180 ) 
        self.color = ( 0, 0, 0 )

        self.callback = callback

        if layoutFunc is not None:
            rect = layoutFunc( self )

        super().__init__( rect )
        self.buffer = self.createBuffer()
        self.isDirty = True

    def clean( self ):
        self.isDirty = False
        self.buffer.fill( self.bgColor )

        renderedText = base.drawing.renderFont( self.font, self.text, self.color )
        self.buffer.blit( renderedText, (
            ( self.buffer.get_width() - renderedText.get_width() ) // 2 ,
            ( self.buffer.get_height() - renderedText.get_height() ) // 2  ) )

    def setText( self, newText ):
        self.isDirty = True
        self.text = newText

    def setColor( self, color ):
        self.isDirty = True
        self.color = color

    def setBgColor( self, color ):
        self.isDirty = True
        self.bgColor = color

    def draw( self ):
        if self.isDirty:
            self.clean()

        game.screen.blit( self.buffer, ( self.rect.left, self.rect.top ) )

    def checkIntersect( self, event ):
        #buttons', 'dict', 'pos', 'rel', 'type
        if self.rect.collidepoint( event.pos ):
            self.setBgColor( ( 200, 50, 30 ) )

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if callable( self.callback ):
                    self.callback( self )
        else:
            self.setBgColor( ( 200, 200, 180 ) )

