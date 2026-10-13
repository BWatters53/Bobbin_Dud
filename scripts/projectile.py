import pygame 
import math as m
import random as r
from .utils import loadImg, findCollisions, loadSounds
from .particle import Particle
# 8888888888888888 #
# PROJECTILE CLASS # 
# 8888888888888888 #
class Projectile:
    def __init__(self,x,y,damage,angle,game,user,drawback=1,type_="arrow"):
        # Movement
        self.movement = [drawback*m.cos(angle),drawback*m.sin(angle)] # Using Projectile Motion Here
        self.angle = angle
        self.gravity = 0.1
        # Attack
        self.damage = damage
        self.hits = []
        self.user = user
        # General
        self.type = type_
        self.game = game
        self.alive = True
        self.music = self.game.projectileMusic
        if self.type == "arrow":
            self.img = self.game.assets["arrow"]
        else:
            self.img = self.game.assets["coin"]
        self.rect = pygame.Rect(x,y,self.img.get_width(),self.img.get_height())
    def render(self):
        self.rect.x += self.game.scroll[0]
        self.rect.y += self.game.scroll[1]
        try:
            angle = -180*m.atan(self.movement[1]/self.movement[0])/m.pi
        except ZeroDivisionError:
            if self.movement[1] > 0:
                angle = 90
            else:
                angle = -90
        if self.movement[0] > 0:
            self.img_copy = pygame.transform.rotate(self.img,angle)
        else:
            self.img_copy = pygame.transform.rotate(pygame.transform.flip(self.img,True,False),angle)
        self.game.display.blit(self.img_copy,(self.rect.centerx-self.img_copy.get_width()//2,self.rect.centery-self.img_copy.get_height()//2))
    def update(self):
        if not self.game.pause:
            self.rect.x += self.movement[0]
            self.rect.y += self.movement[1]
            self.movement[1] += self.gravity
            # Collisions with tilemaps
            self.hits = findCollisions(self.rect, self.game.tilemap+self.game.bouncepads+self.game.movingplatforms+self.game.climbingwalls)
            if len(self.hits) > 0:
                self.alive = False # We can delete this projectile
            # Collisions with entities
            self.hits = findCollisions(self.rect, self.game.enemies + [self.game.player])
            for hit in self.hits:
                self.game.screenshakeStrength = 0.8
                if hit != self.user:
                    hit.hp = max(hit.hp-self.damage,0) # Damage The Entity
                    self.game.particles += [Particle(hit.rect.centerx,hit.rect.centery,"attack",self.user.game) for i in range(4)]
                    self.alive = False
                    if self.type == "arrow":
                        self.music.play(r.choice(self.game.sounds["arrow"]))
                    else:
                        self.music.play(r.choice(self.game.sounds["coins"]))
        return self.alive

