import random as r
import math as m
import pygame
from .utils import findCollisions,loadSounds
# [][][][][][][] #
# PARTICLE CLASS #
# [][][][][][][] #
class Particle:
    def __init__(self,x,y,type_,game,angle=None):
        #- Randomness
        if type_ not in ("spawn","attack"):
            self.colour = (255,r.randint(179,215),10)
            self.speed = r.randint(3,5)
            self.startAngle = r.randint(int((1000 * m.pi)/8),int((7000 * m.pi)//8))/1000
        elif type_ == "attack":
            self.colour = (r.randint(125,145),8,8)
            self.speed = 1
            self.startAngle = r.randint(int((1000 * m.pi)/8),int((7000 * m.pi)//8))/1000
        else:
            self.colour = r.choice([(61,110,112),(150,66,83),(60,163,112)])
            self.speed = 3
            self.startAngle = m.pi * angle/180
            self.particleCounter = 0
            self.totalMovement = [0,0]
        self.rect = pygame.Rect(x,y,r.randint(1,3),r.randint(1,3))
        #- Misc
        self.type = type_
        self.game = game
        self.music = self.game.projectileMusic
        #- Movement
        self.hits = []
        self.gravity = 0.1
        self.movement = [self.speed*m.cos(self.startAngle),self.speed*-m.sin(self.startAngle)]
    
    def update(self):
        if not self.game.pause:
            if self.type == "spawn":
                self.particleCounter += 1
                if self.particleCounter == 30:
                    self.movement = [self.movement[0]*-6, self.movement[1]*-6]
                elif self.particleCounter == 1000:
                    self.game.particles.remove(self)
                self.totalMovement[0] += self.movement[0]
                self.totalMovement[1] += self.movement[1]
                self.rect.x,self.rect.y = self.game.player.rect.centerx+self.totalMovement[0],self.game.player.rect.centery+self.totalMovement[1]
            else:
                self.rect.x += self.movement[0]
                self.rect.y += self.movement[1]
                self.movement[1] += self.gravity # Update Location
                self.hits = findCollisions(self.rect,self.game.tilemap+self.game.bouncepads+self.game.climbingwalls+self.game.movingplatforms)
                if len(self.hits) > 0 or self.rect.y > 1000:
                    self.game.particles.remove(self)
                    if self.type == "player": # i.e. created by the player's death
                        self.music.play(r.choice(self.game.sounds["coins"]))
                    elif self.type == "enemy":
                        self.music.play(r.choice(self.game.sounds["coins"]))

    def render(self):
        pygame.draw.rect(self.game.display,self.colour,self.rect)