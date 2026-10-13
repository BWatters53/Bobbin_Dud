import pygame
from .utils import findCollisions
from .particle import Particle
# =            = #
#- WEAPON CLASS -#
# =            = #
class Weapon:
    def __init__(self,user,x,y,width,height,type_):
        #- Movement Variables
        self.user = user
        self.movement = [0,0]
        self.rect = pygame.Rect(x,y,width,height)

        #- Attack Variables
        self.hits = []
        self.attackCounter = 0
        self.attackX = 0
        self.attackY = 0
        self.damage = 0
        self.cooldown = 0
        if type_ == "sword":
            self.displacement = 1
            self.img = self.user.game.assets["sword"]
        elif type_ == "boss_sword_1":
            self.displacement = 3
            self.img = self.user.game.assets["boss_sword_1"]
        elif type_ == "boss_sword_2":
            self.displacement = 2
            self.img = self.user.game.assets["boss_sword_2"]
        else:
            self.displacement = 0
            self.img = self.user.game.assets["spear"]
        self.type = type_

    def render(self,surface,id="norm"):
        if id == "norm":
            if self.user.dir == -1:
                surface.blit(self.img,(self.rect.x,self.rect.y-self.displacement)) # Account for some of the weapon's shaping
            else:
                surface.blit(pygame.transform.flip(self.img,True,False),(self.rect.x,self.rect.y-self.displacement))
        elif id == "rotate":
            if (self.user.attackDir == 1 and self.type != "boss_sword_2") or (self.user.attackDir == -1 and self.type == "boss_sword_2"):
                surface.blit(self.img_copy,(self.rect.centerx-self.img_copy.get_width()//2,self.rect.centery-self.img_copy.get_height()//2))
            else:
                surface.blit(pygame.transform.flip(self.img_copy,True,False),(self.rect.centerx-self.img_copy.get_width()//2,self.rect.centery-self.img_copy.get_height()//2))
    # Animation Will Be Applied Here In The Future
    def update(self):
        # Set Own Location To Be At The player's Side
        if self.user.dir == 1:
            self.rect.x = self.user.rect.centerx + self.attackX
        if self.user.dir == -1:
            self.rect.x = self.user.rect.centerx - self.rect.width + self.attackX
        self.rect.y = self.user.rect.centery + self.attackY
        # Cooldown Reset
        self.cooldown = max(0,self.cooldown-1)
        # Damage Dealing
        if self.cooldown == 0:
            if self.user.maxJumps == 2: # The Player
                self.hits = findCollisions(self.rect,self.user.game.enemies)
            else: # otherwise assume enemy
                self.hits = findCollisions(self.rect,[self.user.game.player])
            for hit in self.hits:
                if self.damage != 0:
                    if self.user.maxJumps == 2:
                        if self.user.lightAttacking:
                            self.user.game.screenshakeStrength = 1.3
                        elif self.user.heavyAttacking:
                            self.user.game.screenshakeStrength = 1.6
                    else:
                        self.user.game.screenshakeStrength = 0.4
                    self.user.game.particles += [Particle(hit.rect.centerx,hit.rect.centery,"attack",self.user.game) for i in range(4)]
                hit.hp = max(0, hit.hp-self.damage)
            if len(self.hits) > 0:
                self.cooldown += 9 # Won't damage every frame, so an enemy moving out of the way will avoid some damage