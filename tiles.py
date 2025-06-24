import pygame
class Tile:
    def __init__(self,_type,location):
        self.type = _type
        match _type:
            case "climb":
                self.colour = "orange"
                self.sizew = 16
                self.sizeh = 112
            case "bounce":
                self.colour = "green"
                self.sizew = 32
                self.sizeh = 16
            case "move":
                self.colour = "brown"
                self.sizew = 42
                self.sizeh = 8
            case _:
                self.colour = "blue"
                self.sizew = 16
                self.sizeh = 16
        self.loc = location
        self.rect = pygame.Rect(location[0],location[1],self.sizew,self.sizeh)
        self.top = self.rect.top#Convenience
        self.bottom = self.rect.bottom
        self.left = self.rect.left
        self.right = self.rect.right
        self.x = self.rect.x
        self.y = self.rect.y
                
    def render(self,surface):
        pygame.draw.rect(surface,self.colour,self.rect)

