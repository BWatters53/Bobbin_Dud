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
        self.climbcount = 0
        self.climbreload = 0
                
    def findCollisions(self,tilemap):#Find All Collisions In The Area
        hits = []
        for rect in tilemap.copy():
            if self.rect.colliderect(rect):
                hits.append(rect)
        return hits
    
    def update(self,movement,tilemap):
        self.collisions = {"up":False,"down":False,"left":False,"right":False}
        self.rect.x += movement[0]#All X-Collisions
        hits = self.findCollisions(tilemap)
        for rect in hits:
            if rect.type == "climb":
                self.climbcount += 1
                if abs(movement[0]) > 0:
                    self.jumps = 0
                    if self.climbcount <= 180:#You fall if you climb for too long
                        movement[1] = -1#Climb up climbing walls
                    elif self.climbcount == 301:
                        movement[1] = 0
            if movement[0] > 0:
                self.rect.right = rect.left
                self.collisions["right"] = True
            if movement[0] < 0:
                self.rect.left = rect.right
                self.collisions["left"] = True

        self.rect.y += movement[1]#All Y-Collisions
        hits = self.findCollisions(tilemap)
        for rect in hits:
            if movement[1] > 0:
                self.rect.bottom = rect.top
                self.collisions["down"] = True
                self.movement[2] = 0#Normal movement
                self.jump = 2#Regain jumps
                if rect.type == "bounce":
                    self.movement[2] = -7#Bounce on bounce blocks
            if movement[1] < 0:
                self.rect.top = rect.bottom
                self.collisions["up"] = True
                self.movement[2] = 0

        if not self.collisions["down"]:
            self.airtime += 1
            if self.airtime > 5:
                if self.collisions["right"]:
                    self.colour = "red"
                elif self.collisions["left"]:
                    self.colour = "black"
        if self.collisions["down"]:
            self.climbreload += 1
            if self.climbreload >= 10:#Have a short cooldown
                self.climbreload = 0
                self.climbcount = 0#Reset climb count
        else:
            self.airtime = 0
            self.colour = "yellow"


    def render(self,surface):#Will be changed when graphics overhaul occurs 
        pygame.draw.rect(surface,self.colour,self.rect)
