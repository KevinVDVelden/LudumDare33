import pygame
import base.drawing
import game

class Widget:
    def __init__( self, rect, **kargs ):
        if 'layoutFunc' in kargs:
            self.rect = kargs['layoutFunc']( self )
        else:
            self.rect = rect
        self.children = []

        self.isDirty = False

    def clean( self ):
        pass

    def draw( self, screen ):
        isDirty = self.isDirty or any( [ n.isDirty for n in self.children ] )

        if self.isDirty:
            self.clean()

        if len( self.children ) > 0:
            self.backBuffer = pygame.Surface( ( self.buffer.get_width(), self.buffer.get_height() ) )
            self.backBuffer.blit( self.buffer, ( 0, 0 ) )

            for n in self.children:
                n.draw( self.backBuffer )
            screen.blit( self.backBuffer, ( self.rect.left, self.rect.top ) )
        else:
            if hasattr( self, 'buffer' ):
                screen.blit( self.buffer, ( self.rect.left, self.rect.top ) )

    def createBuffer( self ):
        self.buffer = pygame.Surface( ( int( self.rect.width ), int( self.rect.height ) ) )
        return self.buffer


class Button( Widget ):
    def __init__( self, rect, **kargs ):
        self.bgColor = ( 200, 200, 180 ) 

        if 'callback' in kargs:
            self.callback = kargs['callback']
        else:
            self.callback = None

        super().__init__( rect, **kargs )
        self.buffer = self.createBuffer()
        self.isDirty = True

    def onHover( self ):
        self.setBgColor( ( 200, 50, 30 ) )

    def onHoverLeave( self ):
        self.setBgColor( ( 200, 200, 180 ) )

    def clean( self ):
        self.isDirty = False

    def setBgColor( self, color ):
        self.isDirty = True
        self.bgColor = color

    def checkIntersect( self, event ):
        #buttons', 'dict', 'pos', 'rel', 'type
        if self.rect.collidepoint( event.pos ):
            self.onHover()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if callable( self.callback ):
                    self.callback( self )
            return True
        else:
            self.onHoverLeave()
            return False


class TextButton( Button ):
    def __init__( self, rect, text, font = 'menu', **kargs ):
        self.text = text
        self.font = font
        self.color = ( 0, 0, 0 )

        super().__init__( rect, **kargs )

    def clean( self ):
        super().clean()

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

class IconButton( Button ):
    def __init__( self, rect, normalImage, hoverImage, **kargs ):
        self.normalImage = normalImage
        self.hoverImage = hoverImage

        self.setImage( self.normalImage )
        if rect.width < 0:
            rect.width = self.normalImage.get_width()
        if rect.height < 0:
            rect.height = self.normalImage.get_height()

        super().__init__( rect, **kargs )

    def onHover( self ):
        self.setImage( self.hoverImage )
    def onHoverLeave( self ):
        self.setImage( self.normalImage )

    def setImage( self, image ):
        self.image = image
        self.isDirty = True
        
    def clean( self ):
        super().clean()
        self.buffer = self.buffer.convert_alpha()
        self.buffer.fill( (0,0,0,0) )
        self.buffer.blit( self.image, ( 0, 0 ) )

class Bar( Widget ):
    def __init__( self, width, imgPrefix, font = 'menu', **kargs ):
        self.imgPrefix = imgPrefix

        self.left = game.assets[ imgPrefix + '_left.png' ]
        self.right = game.assets[ imgPrefix + '_right.png' ]
        self.center = game.assets[ imgPrefix + '_center.png' ]

        super().__init__( pygame.Rect( (
            ( game.SCREEN_SIZE[0] - width ) / 2,
            ( game.SCREEN_SIZE[1] - self.left.get_height() ),
            width, self.left.get_height() ) ), **kargs )

        self.buffer = self.createBuffer()
        self.isDirty = True

    def clean( self ):
        self.isDirty = False
        
        self.buffer.blit( self.left, ( 0, 0 ) )
        for n in range( self.left.get_width(), self.buffer.get_width(), self.center.get_width() ):
            self.buffer.blit( self.center, ( n, 0 ) )
        self.buffer.blit( self.right, ( self.buffer.get_width() - self.right.get_width(), 0 ) )

    def addChild( self, construct, *args ):
        if len( self.children ) == 0:
            left = self.left.get_width()
        else:
            left = max( [ n.rect.width + n.rect.left for n in self.children ] )
        rect = pygame.Rect( left, 0, -1, -1 )

        self.children.append( construct( *( tuple( [ rect ] ) + args ) ) )

    def checkIntersect( self, event ):
        pos = event.pos

        for child in self.children:
            event.pos = ( pos[0] - self.rect.left, pos[1] - self.rect.top )
            if child.checkIntersect( event ):
                event.pos = pos
                return True

        event.pos = pos
        if self.rect.collidepoint( event.pos ):
            return True
        else:
            return False
