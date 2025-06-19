import pygame

class Entity:
    def __init__(self,size,colour,x,y,speed):
        self.size = size
        self.colour = colour
        self.rect = pygame.Rect(x,y,self.size,self.size)
        self.speed = speed

class Player(Entity):
    def __init__(self,size,colour,x,y,speed):
        super().__init__(size,colour,x,y,speed)
        self.movement = [False,False,0]#l,r,v
        self.airtime = 0
        self.jump = 2#Allow Double Jump

    def findCollisions(self,tilemap):#Find All Collisions In The Area
        hits = []
        for rect in tilemap.copy():
            if self.rect.colliderect(rect):
                hits.append(rect)
        return hits
    
    def update(self,movement,tilemap):
        self.collisions = {"up":False,"down":False,"left":False,"right":False}
        self.rect.y += movement[1]#All Y-Collisions
        hits = self.findCollisions(tilemap)
        for rect in hits:
            if movement[1] > 0:
                self.rect.bottom = rect.top
                self.collisions["down"] = True
            if movement[1] < 0:
                self.rect.top = rect.bottom
                self.collisions["up"] = True

        self.rect.x += movement[0]#All X-Collisions
        hits = self.findCollisions(tilemap)
        for rect in hits:
            if movement[0] > 0:
                self.rect.right = rect.left
                self.collisions["right"] = True
            if movement[0] < 0:
                self.rect.left = rect.right
                self.collisions["left"] = True

        if self.collisions["down"]:
            self.movement[2] = 0#Normal movement
            self.jump = 2#Regain jumps
        if self.collisions["up"]:
            self.movement[2] = 0

    def render(self,surface):#Will be changed when graphics overhaul occurs 
        pygame.draw.rect(surface,self.colour,self.rect)