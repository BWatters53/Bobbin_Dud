import pygame
class Tile:
    def __init__(self,type,location):
        self.type = type
        self.size = 16
        self.loc = location
        self.rect = pygame.Rect(location[0],location[1],self.size,self.size)
        self.top = self.rect.top
        self.bottom = self.rect.bottom
        self.left = self.rect.left
        self.right = self.rect.right
        match type:
            case "climb":
                self.colour = "orange"
            case _:
                self.colour = "blue"
    def render(self,surface):
        pygame.draw.rect(surface,self.colour,self.rect)