import pygame
from .utils import loadImages, loadImg
#<^><^><^><^>#
# TILE CLASS #
#<^><^><^><^>#
class Tile:
    def __init__(self,type,x,y,game,tile=0):
        self.game = game
        self.img = self.game.assets[str(type)][tile]
        #- Rect
        self.type = type
        self.tile = tile
        self.tilesize = 16
        self.rect = pygame.Rect(x,y,self.tilesize,self.tilesize)
    #- Draw The Image Of The Tile
    def render(self,game,scroll):
        self.rect.x += scroll[0]
        self.rect.y += scroll[1]
        if self.game.name == "editor":# filter out the editor so that all tiles will show up
            game.display.blit(self.img,(self.rect.x,self.rect.y))
        elif (abs(self.rect.x-self.game.player.rect.x) < 500 and abs(self.rect.y-self.game.player.rect.y) < 260) or self.type == 4: # Only render if the tile is nearby
            game.display.blit(self.img,(self.rect.x,self.rect.y))
        #pygame.draw.rect(game.display,self.tiles[self.type][self.tile],self.rect)

class Decor(Tile):
    def __init__(self,x,y,game,tile):
        self.type = 3
        super().__init__(self.type,x,y,game,tile)
        self.rect = pygame.Rect(x,y,self.img.get_width(),self.img.get_height())
    #def render(self,game,scroll):
     #   pygame.draw.rect(self.game.display,"red",self.rect)
      #  super().render(game,scroll)


# ################ #
# TRAMPOLINE CLASS #
# ################ #
class BouncePad(Tile):
    def __init__(self,x,y,game,power=10):
        self.power = power
        self.type = 4
        self.tile = 6
        super().__init__(self.type,x,y,game,self.tile)
        self.rect = pygame.Rect(x,y,24,self.tilesize)

# <>-------------------<> #
# MOVING PLATFORM CLASSES #
# <>-------------------<> #
class MovingPlatform(Tile):
    def __init__(self,speed,x,y,game,tile):
        self.tile = tile
        self.type = 4
        super().__init__(self.type,x,y,game,self.tile)
        self.dir = 1
        self.speed = speed
        self.moveType = "n/a"
        self.rect = pygame.Rect(x,y,self.tilesize*2,self.tilesize)
        self.flag = False
    def update(self,scroll,mode="game"):
        pass # Used For The Editor

# -VERTICAL MOVERS
class Vertical(MovingPlatform):
    def __init__(self,speed,x,startY,endY,game,tile):
        self.tile = tile
        super().__init__(speed,x,startY,game,self.tile)
        self.startY = startY
        self.endY = endY
        self.moveType = "v"
    #- Update Location
    def update(self,scroll,mode="game"):
        if mode == "editor" or not self.game.pause:
            self.startY+=scroll[1]
            self.endY+=scroll[1]
            if mode != "editor":
                self.rect.y += (self.speed*self.dir)
                if (self.rect.y > self.endY or self.rect.y < self.startY):
                    if not self.flag:
                        if self.rect.y > self.endY:
                            self.dir = -1
                        else:
                            self.dir = 1
                        self.flag = True
                else:
                    self.flag = False

# -HORIZONTAL MOVERS
class Horizontal(MovingPlatform):
    def __init__(self,speed,startX,endX,y,game,tile):
        self.tile = tile
        super().__init__(speed,startX,y,game,self.tile)
        self.startX = startX
        self.endX = endX
        self.moveType = "h"
    #- Update Location
    def update(self,scroll,mode="game"):
        if mode == "editor" or not self.game.pause:
            self.startX += scroll[0]
            self.endX += scroll[0]
            if mode != "editor":
                self.rect.x += (self.speed*self.dir)
                if (self.rect.x > self.endX or self.rect.x < self.startX):
                    if not self.flag:
                        if self.rect.x > self.endX:
                            self.dir = -1
                        else:
                            self.dir = 1
                        self.flag = True
                else:
                    self.flag = False

# + + + + + + + + + + #
# CLIMBING WALL CLASS #
# + + + + + + + + + + #
class ClimbingWall(Tile):
    def __init__(self,x,y,game,tile):
        self.type = 4
        self.tile = tile
        super().__init__(self.type,x,y,game,self.tile)
        # Temporary Attributes:
        # These are temporary because the images will have defined heights later down the line
        self.rect = pygame.Rect(x,y,self.tilesize,8*self.tilesize)