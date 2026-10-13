#############
# LIBRARIES #
#############
from .utils import findCollisions
from .projectile import Projectile
from .label import Banner
from .weapon import Weapon
from .particle import Particle
from .tile import Tile
import pygame
import random as r
import math as m
#[[[[[[[]]]]]]]#
# ENTITY CLASS #
#[[[[[[[]]]]]]]#
class Entity:
    #-INITIALISATION-#
    def __init__(self,name,game,x,y,state,pointsValue,speed,maxJumps,jumpStrength,hp):
        #- General
        self.game = game
        self.img = self.game.assets[name][state]["frames"][0]
        if len(self.game.assets[name]) > 0:
            if hp != 101:
                self.rect = pygame.Rect(x,y,10,self.img.get_height())
                self.dir = 1 # Facing Right
            else: # For Spikemoles
                #print(self.img.get_width())
                self.rect = pygame.Rect(x,y,5,5)
                self.dir = -1
        else:
            self.img = ""
        self.currentFrame = 1
        self.frameCounter = 0
        self.state = state
        self.pointsValue = pointsValue
        self.name = name
        #- Movement
        self.movement = [0,0]
        self.gravity = 0.3
        self.speed = speed
        self.maxJumps = maxJumps
        self.jumps = maxJumps
        self.jumpStrength = jumpStrength
        self.moveV = False
        self.prevMoveV = False
        self.climbing = False
        self.climbShock = 0
        self.fallCounter = 0
        #- Attacks
        self.lightAttacking = False
        self.lightAttackCooldown = 0
        self.lightAttackCounter = 0
        self.lightAttackDir = 0
        #- Health
        self.alive = True
        self.hp = hp
        self.maxHP = hp
        self.damageTaken = False
        self.hpBar = Banner(0,0,self.maxHP,"bar")

    #- Collision Control
    def update(self):
        #- Initialisation
        self.hpBar.update(self.hp, self.rect.x + (self.rect.width-self.hpBar.width)//2, self.rect.y - 6)
        self.hpBar.render(self.game.display)
        if not self.game.pause:
            self.hits = []
            self.collisions = {"up":False, "down":False, "left":False, "right":False, "movingPlatform":False}
            if self.maxJumps == 2:
                if self.climbShock >= 0:
                    self.movement = [max(self.climbShock-0.5,0)+(self.speed *(self.game.movement[1] - self.game.movement[0])), min(self.movement[1]+self.gravity, 7)] # Terminal Velocity Also Set
                    self.climbShock -= 1
                else:
                    self.movement = [min(self.climbShock+0.5,0)+(self.speed *(self.game.movement[1] - self.game.movement[0])), min(self.movement[1]+self.gravity, 7)]
                    self.climbShock += 1
            else:
                self.movement = [self.movement[0],min(self.movement[1]+self.gravity,7)]
            # If fall counter exceeds a certain value, the player "dies"
            if self.movement[1] == 7:
                self.fallCounter += 1
            else:
                self.fallCounter = 0
            # Set Direction Faced For Attacks And Animation
            if self.maxJumps == 2:
                if self.game.movement[1]-self.game.movement[0] < 0: # Facing Left
                    self.dir = -1
                if self.game.movement[1]-self.game.movement[0] > 0: # Facing Right
                    self.dir = 1
            # If not moving at all, it continues to face in the same direction

            if self.moveV:
                self.prevMoveV = True
            #- Check Horizontal Collisions
            self.rect.x += self.movement[0]
            # Specifically check for collisions with climbing walls
            if self.maxJumps == 2: # Only the player
                self.hits = findCollisions(self.rect,self.game.climbingwalls)
                if len(self.hits) > 0:
                    self.climbing = True
                    if not self.music.get_busy():
                        match self.hits[0].tile:
                            case 2|4:
                                self.music.play(self.game.sounds["climb"][0])
                            case 3|5:
                                self.music.play(self.game.sounds["climb"][1])
                else:
                    self.climbing = False
            #- All Other Horizontal Collisions
            self.hits = findCollisions(self.rect, self.game.tilemap+self.game.bouncepads+self.game.movingplatforms+self.game.climbingwalls)
            for tile in self.hits:
                if tile.type == 4 and tile.tile in (1,2):
                    print("ok")
                else:
                    if self.movement[0] < 0:
                        self.rect.left = tile.rect.right
                        self.collisions["left"] = True
                    if self.movement[0] > 0:
                        self.rect.right = tile.rect.left
                        self.collisions["right"] = True
            #- Check Vertical Collisions
            self.rect.y += self.movement[1]
            # Specifically check for trampoline collisions
            self.hits = findCollisions(self.rect, self.game.bouncepads)
            if len(self.hits) > 0 and self.movement[1] > 0:
                for bouncepad in self.hits:
                    self.rect.bottom = bouncepad.rect.top
                    self.movement[1] = -1*bouncepad.power
                    self.jumps = self.maxJumps
                    self.music.play(r.choice(self.game.sounds["jump"]))
            else:
                # Specifically check for moving platform collisions
                self.hits = findCollisions(self.rect, self.game.movingplatforms)
                if len(self.hits) > 0 and self.movement[1] > 0:
                    self.collisions["movingPlatform"] = True
                    self.fallCounter = 0
                    for movingplatform in self.hits:
                        self.rect.bottom = movingplatform.rect.top
                        self.jumps = self.maxJumps
                        if movingplatform.moveType == "h":
                            self.rect.x += (movingplatform.speed*movingplatform.dir)
                            self.movement[1] = self.gravity
                        else:
                            self.rect.y += (movingplatform.speed*movingplatform.dir)
                            self.moveV = True
                        if not self.music.get_busy() and self.movement[0] > 0 and self.maxJumps == 2:
                            match movingplatform.tile:
                                case 0:
                                    self.music.play(r.choice(self.game.sounds["grass"]))
                                case 1:
                                    self.music.play(r.choice(self.game.sounds["stone"]))

                else:
                    self.moveV = False
                    self.hits = findCollisions(self.rect, self.game.tilemap+self.game.bouncepads+self.game.climbingwalls)
                    for tile in self.hits:
                        if self.movement[1] < 0:
                            self.rect.top = tile.rect.bottom
                            self.collisions["up"] = True
                        if self.movement[1] > 0:
                            self.rect.bottom = tile.rect.top
                            self.collisions["down"] = True
                            if not self.music.get_busy() and self.movement[0] > 0 and self.maxJumps == 2:
                                match tile.type:
                                    case 0|1:
                                        self.music.play(r.choice(self.game.sounds["grass"]))
                                    case 2:
                                        self.music.play(r.choice(self.game.sounds["stone"]))
                    # Colliding With The Bottom Of Moving Platforms
                    self.hits = findCollisions(self.rect, self.game.movingplatforms)
                    for tile in self.hits:
                        if tile.moveType == "v" and tile.dir == 1:
                            self.rect.top = tile.rect.bottom+(2*tile.speed)
                        else:
                            self.rect.top = tile.rect.bottom
                        self.collisions["up"] = True
            #- Set Vertical Velocity To Zero For Touching Floor Or Ceiling
            if self.collisions["down"] or self.collisions["up"]:
                self.movement[1] = 0
                if self.collisions["down"]:
                    self.jumps = self.maxJumps
            #- State Management
            if self.maxJumps == 2: # only relevant to the player
                if self.collisions["down"] or self.collisions["movingPlatform"]:
                    if abs(self.movement[0]) <= 0.5:
                        self.changeState("idle")
                    elif abs(self.movement[0]) > 0.5:
                        self.changeState("run")
                    else:
                        self.changeState("idle")
                if not(self.collisions["down"] or self.collisions["movingPlatform"]) and self.movement[1] > 0.3:
                    self.changeState("fall")

            #- Check If The Previous Frame Was A Moving Platform Versus This Frame
            if not self.moveV and self.prevMoveV and self.movement[1] > 0:
                self.rect.y -= self.movement[1]
                self.movement[1] = 0
                self.prevMoveV = False
            if self.rect.y == 2000: # Enemies Will Fall To -2000 before dying
                self.hp = 0

    #- Jump Management
    def jump(self):
        if self.jumps > 0 and not self.game.pause:
            self.music.play(r.choice(self.game.sounds["jump"]))
            self.movement[1] = -1*self.jumpStrength # Negative value because of coordinate geometry in Pygame
            self.jumps -= 1
            if self.maxJumps == 2:
                self.changeState("jump")
                self.game.user.stats["no. jumps"] += 1

    #- Attack Management
    def attack(self):
        pass

    def lightAttack(self,weapon): # Used By Player And Guard/Soldier
        self.lightAttackCounter += 1
        weapon.render(self.game.display)
        if self.lightAttackCounter <= 7:
            weapon.attackX += (2 * self.lightAttackDir)
        else:
            weapon.attackX -= (2 * self.lightAttackDir)
        if self.lightAttackCounter == 14:
            self.lightAttackCooldown += 30
            self.lightAttackCounter = -1
            self.lightAttacking = False
            weapon.attackX = 0
            weapon.damage = 0
        if self.lightAttackCounter in (0,12):
            self.img = self.game.assets[self.name][self.state]["frames"][0]
        elif self.lightAttackCounter in (3,9):
            self.img = self.game.assets[self.name][self.state]["frames"][1]
        elif self.lightAttackCounter == 6:
            self.img = self.game.assets[self.name][self.state]["frames"][2]
        if self.lightAttackCounter == 1:
            self.music.play(self.game.sounds["light_attack"][0])

    #- Changing State
    def changeState(self,state):
        if self.state != state:
            self.state = state
            self.frameCounter = 0
            self.currentFrame = 0

    #- Draw The Entity
    def render(self):
        # pygame.draw.rect(self.game.display,"red",self.rect) #- USED FOR TESTING
        if self.dir > 0:
            self.game.display.blit(pygame.transform.flip(self.img,True,False),(self.rect.x-6,self.rect.y))
        else:
            self.game.display.blit(self.img,(self.rect.x,self.rect.y))
        
#-=-=-=--=-=-=-#
#-PLAYER CLASS-#
#-=-=-=--=-=-=-#
class Player(Entity):
    #-INITIAILISATION-#
    def __init__(self,game,x,y,lives=3,hp=100,score=0,strengthMultiplier=1,speed=2,gameType="game"):
        #- Movement
        self.maxJumps = 2
        self.jumpStrength = 5
        self.speed = speed
        self.climbCounter = 0
        self.stamina = 100
        #- Health
        self.lives = lives
        #- Gameplay
        self.state = "idle"
        self.score = score
        self.pointsValue=0
        super().__init__("player",game,x,y,self.state,self.pointsValue,self.speed,self.maxJumps,self.jumpStrength,hp)
        #- Scrolling
        self.initX = self.rect.x
        self.initY = self.rect.y
        #- Attacks
        # Bow
        self.bowChargeTimer = 0
        self.loading = False
        self.bowAttackCooldown = 0
        self.bowAttackCounter = 0
        # Sword
        self.sword = Weapon(self,self.rect.centerx,self.rect.centery,21,4,"sword")
        self.heavyAttacking = False
        self.heavyAttackCooldown = 0
        self.heavyAttackCounter = 0
        self.heavyAttackDir = 0

        self.strengthMultiplier = strengthMultiplier
        self.pointsValue = int(min(self.hp//8, self.score))

        # Music
        if gameType == "game":
            self.music = pygame.mixer.Channel(2)
            self.music.set_volume(0.5)

    def update(self):
        super().update()
        if self.collisions["down"] or (len(findCollisions(self.rect,self.game.bouncepads+self.game.movingplatforms)) and self.movement[1]>0): # If you hit a floor, the stamina resets
            self.climbCounter = 0

        # SCROLLING #
        self.dx = self.rect.x - self.initX # Work out how much the x and y values have changed
        self.dy = self.rect.y - self.initY

        # Apply X Scroll
        if self.rect.right < self.game.scrollThreshold["x"] or self.rect.left > self.game.display.get_width() - self.game.scrollThreshold["x"]:
            self.rect.x -= self.dx
            self.game.scroll[0] = -1*self.dx
            self.game.scrollTotal[0] += self.dx
            print("yo")
        # Apply Y Scroll
        if self.rect.top > self.game.display.get_height() - self.game.scrollThreshold["y"] or self.rect.bottom < self.game.scrollThreshold["y"]:
            self.rect.y -= self.dy
            self.game.scroll[1] = -1*self.dy
            self.game.scrollTotal[1] += self.dy
        # Climbing Distance Is Also Incorporated
        self.initX = self.rect.x
        self.initY = self.rect.y
        # Apply Attack Cooldowns Here
        self.bowAttackCooldown = max(self.bowAttackCooldown-1, 0)
        self.lightAttackCooldown = max(self.lightAttackCooldown-1, 0)
        self.heavyAttackCooldown = max(self.heavyAttackCooldown-1, 0)
        if self.lightAttacking:
            self.dir = self.lightAttackDir
        if self.heavyAttacking:
            self.dir = self.heavyAttackDir
        # Update Sword Location
        self.sword.update()
        # Update Value
        self.pointsValue = int(min(self.maxHP//8, self.score))

    #- Climbing Management
    def climb(self):
        self.changeState("climb")
        self.movement[1] = 0
        self.climbCounter += 1
        self.rect.y -= self.speed * 0.75 # Therefore this also gets upgraded in the Olde Shoppe

        if self.climbCounter == self.stamina:
            if self.movement[0] > 0:
                self.climbShock = -8
                self.game.movement[1] = 0
            else:
                self.climbShock = 8
                self.game.movement[0] = 0
            self.changeState("idle")

    #-Attack Management Polymorphism (Kind Of)
    def heavyAttack(self):
        self.heavyAttackCounter += 1
        self.sword.damage = 8 * self.strengthMultiplier
        self.sword.render(self.game.display)
        self.sword.attackX = self.heavyAttackDir*(30)*m.cos((self.heavyAttackCounter * m.pi/30)-m.pi)
        self.sword.attackY = -30*m.sin(self.heavyAttackCounter * m.pi/30)
        if self.heavyAttackCounter == 30:
            self.heavyAttackCooldown = 120
            self.heavyAttacking = False
            self.sword.attackX = 0
            self.sword.attackY = 0
            self.heavyAttackCounter = 0
        match self.heavyAttackCounter:
            case 0|27:
                self.img = self.game.assets[self.name][self.state]["frames"][0]
            case 3|24:
                self.img = self.game.assets[self.name][self.state]["frames"][1]
            case 6|21:
                self.img = self.game.assets[self.name][self.state]["frames"][2]
            case 9|18:
                self.img = self.game.assets[self.name][self.state]["frames"][3]
            case 12|15:
                self.img = self.game.assets[self.name][self.state]["frames"][4]
            case 1: # To Play The Sound
                self.music.play(self.game.sounds["heavy_attack"][0])
    def bowAttack(self):
        if not self.game.pause:
            if self.bowAttackCooldown == 0:
                if self.rect.centerx-self.game.mpos[0] >= 0: 
                    self.dir = 1
                    try:
                        self.bowAngle = m.atan((self.rect.centery-self.game.mpos[1])/(self.rect.centerx-self.game.mpos[0]))
                    except ZeroDivisionError:
                        if self.rect.centery-self.game.mpos[1] > 0:
                            self.bowAngle = m.pi/2
                        else:
                            self.bowAngle = -m.pi/2
                else:
                    self.dir = -1
                    try:
                        self.bowAngle = m.pi + m.atan((self.rect.centery-self.game.mpos[1])/(self.rect.centerx-self.game.mpos[0]))
                    except ZeroDivisionError:
                        self.bowAngle = 3*m.pi/2
                #if self.dir == 1:
                #   pygame.draw.rect(self.game.display,"blue",pygame.Rect(self.rect.centerx+8*m.cos(self.bowAngle),self.rect.centery+8*m.sin(self.bowAngle),12,3))
                #else:
                #   pygame.draw.rect(self.game.display,"blue",pygame.Rect(self.rect.centerx+8*m.cos(self.bowAngle)-12,self.rect.centery+8*m.sin(self.bowAngle),12,3))
                self.img_copy = pygame.transform.rotate(self.game.assets["bow"],-180*self.bowAngle//m.pi)
                self.bowAttackCounter += 1
                if self.bowAttackCounter == 0:
                    self.img = self.game.assets[self.name]["bow_attack"]["frames"][0]
                elif self.bowAttackCounter == self.game.assets[self.name]["bow_attack"]["frameCounter"]:
                    self.img = self.game.assets[self.name]["bow_attack"]["frames"][1]
                elif self.bowAttackCounter == 2*self.game.assets[self.name]["bow_attack"]["frameCounter"]:
                    self.bowAttackCounter = -1
                #pygame.draw.rect(self.game.display,"red",pygame.Rect(self.rect.x+100*m.cos(self.bowAngle),self.rect.y+100*m.sin(self.bowAngle),2,2))
                self.bowChargeTimer += 1
                if not self.loading:
                    if not(len(findCollisions(pygame.Rect(self.rect.centerx+10*m.cos(self.bowAngle),self.rect.centery+10*m.sin(self.bowAngle),1,1),self.game.tilemap + self.game.bouncepads + self.game.movingplatforms + self.game.climbingwalls)) > 0):
                        if self.dir == 1:
                            self.game.projectiles.append(Projectile(self.rect.centerx+10*m.cos(self.bowAngle),-5+self.rect.centery+10*m.sin(self.bowAngle),min(20,self.bowChargeTimer//15)*self.strengthMultiplier,self.bowAngle,self.game,self,min(6,(1/15)*m.sqrt((self.rect.centery-self.game.mpos[1])**2 + (self.rect.centerx-self.game.mpos[0])**2))))
                        else:
                            self.game.projectiles.append(Projectile(self.rect.centerx+10*m.cos(self.bowAngle)-13,-5+self.rect.centery+10*m.sin(self.bowAngle),min(20,self.bowChargeTimer//15)*self.strengthMultiplier,self.bowAngle,self.game,self,min(6,(1/15)*m.sqrt((self.rect.centery-self.game.mpos[1])**2 + (self.rect.centerx-self.game.mpos[0])**2))))
                        self.music.play(self.game.sounds["bow"][0])
                        self.bowAttackCooldown += 200
    def render(self):
        super().render()
        if self.loading and self.bowAttackCooldown == 0: # So That The Bow Renders In Front Of The Player
            self.game.display.blit(self.img_copy,(self.rect.centerx-self.img_copy.get_width()//2,self.rect.centery-self.img_copy.get_height()//2))
#|||||||||||||#
# ENEMY CLASS #
#|||||||||||||#
class Enemy(Entity):
    def __init__(self,name,attackCooldown,strength,game,x,y,state,pointsValue,speed,jumpStrength,hp):
        #- Attacking
        self.attackCooldown = attackCooldown
        self.strength = strength
        self.dir = 1
        #- Pathfinding
        self.idleTimer = 0
        #- Health
        super().__init__(name,game,x,y,state,pointsValue,speed,1,jumpStrength,hp)
        self.prevHP = self.hp
        #- Sound
        try:
            self.music = self.game.enemyMusic
            self.music.set_volume(0.3)
        except AttributeError: # When Using The Editor
            pass

    def update(self):
        super().update()
        if self.hp == 0:
            for i in range(self.pointsValue):
                self.game.particles.append(Particle(self.rect.centerx,self.rect.centery,"enemy",self.game))
            self.game.enemies.remove(self)
            self.game.player.score += self.pointsValue
            self.game.user.stats["total score"] += self.pointsValue
            self.music.play(self.game.sounds["death"][0])

    def render(self,scroll):
        self.rect.x += scroll[0]
        self.rect.y += scroll[1]
        super().render()

    # TILE CHECKING METHODS #
    def convert(self, value): #- Convert an integer value into a x-y location
        if value >= 0:
            return (self.rect.centerx+(self.dir*self.speed)+(self.dir*self.rect.width//2), 1+ self.rect.y + self.rect.height +(-16*value))
        else:
            return (self.rect.centerx+(self.dir*self.speed)+(self.dir*self.rect.width//2), self.rect.y + 1 + (16*(1+abs(value))))

    def tilesAround(self,desired,show=False):
        hits = [False]*len(desired)
        for indx, location in enumerate(desired):
            loc = self.convert(location)
            if show: # Great For Testing
                pygame.draw.rect(self.game.display,"red",pygame.Rect(loc[0],loc[1],2,2)) # Used in testing
            for rect in self.game.tilemap + self.game.movingplatforms + self.game.climbingwalls + self.game.bouncepads:
                if rect.rect.collidepoint(loc):
                    hits[indx] = True
        return hits

    # LINE OF SIGHT CHECKER #
    def checkLOS(self,viewRange,show=False):
        playerPos = (self.game.player.rect.centerx,self.game.player.rect.centery)
        selfPos = (self.rect.centerx,self.rect.centery)
        distance = m.sqrt((playerPos[0]-selfPos[0])**2+(playerPos[1]-selfPos[1])**2)
        if distance < viewRange and (playerPos[0] - selfPos[0])*self.dir >= 0: # Give a certain range for sight
            points = [(selfPos[0]+k*(playerPos[0]-selfPos[0])/int(distance/2), selfPos[1]+k*(playerPos[1]-selfPos[1])/int(distance/2)) for k in range(0,int(distance/2),2)]
            for point in points:
                if show:
                    pygame.draw.rect(self.game.display,"purple",pygame.Rect(point[0],point[1],2,2))
                for rect in self.game.tilemap + self.game.climbingwalls + self.game.bouncepads + self.game.movingplatforms:
                    if rect.rect.collidepoint(point):
                        return False # The Enemy Cannot See The Player
            return True # The Enemy Can See The Player
        return False # The Enemy Is Not In Range To See The Player
# ^             ^#
# | GUARD CLASS |#
# |             |#
class Guard(Enemy):
    def __init__(self,game,x,y,name="guard"):
        super().__init__(name,40,4,game,x,y,"idle",10,1,5,32)
        self.weapon = Weapon(self,self.rect.centerx,self.rect.centery,21,4,"sword")

    def update(self):
        super().update()
        self.weapon.update()
        if not self.game.pause:
            # Check Region Ahead
            self.movement[0] = self.speed * self.dir
            self.tilesAhead = self.tilesAround([k for k in range(-3,4)]) # Returns the value of the tiles ahead- to check for various movement possibilities
            # IDLE ACTION #
            if self.state == "idle":
                if self.tilesAhead[3] and not self.tilesAhead[4]: 
                    if r.randint(1,540) == 17 and not self.game.pause:
                        self.dir *= -1
                else:
                    self.dir *= -1
                if self.checkLOS(175):
                    self.changeState("attack")
                    if not self.music.get_busy():
                        self.music.play(r.choice(self.game.sounds["grunt"]))
                elif self.prevHP > self.hp:
                    self.dir *= -1
                    self.prevHP = self.hp

            # ATTACKING ACTION #
            elif self.state in ("attack","light_attack"):
                try:
                    self.dir = abs(self.game.player.rect.x-self.rect.x)/(self.game.player.rect.x-self.rect.x)
                except ZeroDivisionError:
                    self.dir = 1
                if abs(self.rect.centerx - self.game.player.rect.centerx) < 16 and self.game.player.rect.y == self.rect.y:
                    self.movement[0] = 0
                    if self.lightAttackCooldown == 0:
                        self.lightAttacking = True
                        self.lightAttackDir = self.dir
                        self.changeState("light_attack")
                else:
                    if not self.lightAttacking:
                        self.changeState("attack")
                if self.tilesAhead[3]:
                    if (self.tilesAhead[4] and self.tilesAhead[5] and not self.tilesAhead[6]) or (self.tilesAhead[4] and not self.tilesAhead[5]): # Ledge To Jump Up
                        self.jump()
                elif not (self.tilesAhead[0] or self.tilesAhead[1] or self.tilesAhead[2]): # Safe Drop
                    # No Feasible Action
                    self.movement[0] = 0
                if not self.checkLOS(175):
                    # Allows the enemy to potentially catch up to the player
                    self.idleTimer += 1
                    if self.idleTimer == 90:
                        self.changeState("idle")
                        self.idleTimer = 0
                if self.lightAttacking:
                    self.weapon.damage = self.strength
                    self.lightAttack(self.weapon)
                else:
                    self.weapon.damage = 0
            else: # If an unknown state is entered
                pass
                #print("jumping")
            self.lightAttackCooldown = max(0,self.lightAttackCooldown-1) # Prevents Attacking Constantly
#+|+|+|+|+|+|+|+#
# SOLDIER CLASS #
#+|+|+|+|+|+|+|+#
class Soldier(Guard):
    def __init__(self,game,x,y):
        super().__init__(game,x,y,name="soldier")
        self.img = self.game.assets[self.name][self.state]["frames"][0]
        self.strength = 3
        self.weapon = Weapon(self,self.rect.centerx,self.rect.centery,32,2,"spear")
#   >>>---->   #
# ARCHER CLASS #
#   >>>---->   #
class Archer(Enemy):
    def __init__(self,game,x,y):
        super().__init__("archer",90,8,game,x,y,"idle",15,0,0,16)
        self.attackCooldown = 90

    def update(self):
        super().update()
        if not self.game.pause:
            if self.state == "idle":
                if self.checkLOS(175): 
                    self.changeState("attack")
                    self.attackCooldown = 90
                elif self.prevHP > self.hp:
                    self.dir *= -1
                    self.prevHP = self.hp
                else:
                    if r.randint(1,180) == 17:
                        self.dir *= -1
            elif self.state == "attack":
                try:
                    self.dir = abs(self.game.player.rect.x-self.rect.x)/(self.game.player.rect.x-self.rect.x)
                except ZeroDivisionError:
                    self.dir = 1
                if self.attackCooldown <= 90:
                    x1,y1 = self.rect.centerx,self.rect.centery
                    x2,y2 = self.game.player.rect.centerx,self.game.player.rect.centery
                    try:
                        if x2 > x1:
                            angle = m.atan((-50 + m.sqrt(2500+20*(y2-y1)-((x2-x1)**2/25))) * (5/(x2-x1)))
                        else:
                            angle = m.atan((-50 + m.sqrt(2500+20*(y2-y1)-((x2-x1)**2/25))) * (5/(x2-x1))) + m.pi
                    except ZeroDivisionError:
                        if y2 > y1: # Player Below
                            angle = m.pi * 1.5
                        else:
                            angle = m.pi * 0.5
                    except ValueError:
                        #print((x2-x1), (y2-y1))
                        angle = 1.25 * m.pi + m.atan((-50 + m.sqrt(2500-20*(y2-y1)-((x2-x1)**2/25))) * (5/abs(x2-x1)))
                    self.img_copy = pygame.transform.rotate(self.game.assets["enemy_bow"],-180*angle//m.pi)
                    if self.attackCooldown == 0:
                        if self.dir == 1:
                            self.game.projectiles.append(Projectile(self.rect.centerx+10*m.cos(angle),-6+self.rect.centery+10*m.sin(angle),self.strength,angle,self.game,self,5))
                        else:
                            self.game.projectiles.append(Projectile(self.rect.centerx+10*m.cos(angle)-13,-6+self.rect.centery+10*m.sin(angle),self.strength,angle,self.game,self,5))
                        self.music.play(self.game.sounds["bow"][0])
                        self.attackCooldown += 90
                    self.attackCooldown = max(0,self.attackCooldown - 1)
                if not self.checkLOS(175):
                    self.changeState("idle")
                    self.attackCooldown = 90
            else:
                pass
                #print(self.state,self.collisions)
    def render(self,scroll):
        super().render(scroll)
        if self.attackCooldown < 90:
            self.game.display.blit(self.img_copy,(self.rect.centerx-self.img_copy.get_width()//2,self.rect.centery-self.img_copy.get_height()//2))
# * * * ** * * * #
#- KNIGHT CLASS -#
# * * * ** * * * #
class Knight(Enemy):
    def __init__(self,game,x,y,):
        super().__init__("knight",0,40,game,x,y,"idle",25,2,0,50)
        self.rect = pygame.Rect(x,y,27,26)
        self.dir = -1
    def checkPath(self):
        #for i in range((1+self.rect.x-self.game.player.rect.x)//16): # Used In Testing
        #    pygame.draw.rect(self.game.display,"red",pygame.Rect(self.rect.x-i*16, self.rect.y+30,2,2))
        for i in range((1+self.rect.x-self.game.player.rect.x)//16):
            flag = False
            for tile in self.game.tilemap:
                if tile.rect.collidepoint((self.rect.x-i*16, self.rect.y+30)):
                    flag = True
            if not flag:
                return False
        return True
                    
    def update(self):
        super().update()
        if not self.game.pause:
            if self.state == "idle":
                self.playerY = self.game.player.rect.y+self.game.player.rect.height
                if abs(self.playerY - (self.rect.y+self.rect.height))<6 and self.checkPath() and self.game.player.rect.x < self.rect.x: # Meet the conditions to charge the knight
                    self.changeState("charge")
            elif self.state == "charge": # Once charging, the knight cannot stop
                self.tilesAhead = self.tilesAround([k for k in range(-3,1)])
                #print(self.tilesAhead)
                self.movement[0] = self.speed * self.dir
                # Check For Collisions With The Player
                self.hits = findCollisions(self.rect,[self.game.player])
                if len(self.hits) > 0 or (self.collisions["left"] or self.collisions["right"] or sum(self.tilesAhead) == 0):
                    if len(self.hits) > 0:
                        self.game.player.hp -= self.strength
                        self.game.particles += [Particle(self.game.player.rect.centerx,self.game.player.rect.centery,"attack",self.game) for i in range(4)]
                    # Upon Crashing, Becomes A Soldier
                    self.game.enemies.append(Soldier(self.game,self.rect.x,self.rect.y))
                    self.game.enemies.remove(self)
                    self.music.play(self.game.sounds["heavy_attack"][0])
                    self.game.screenshakeStrength = 1.2
#<^><^><^><^><^><^>#
# SPIKEMOLE  CLASS #
#<^><^><^><^><^><^>#
class Spikemole(Enemy):
    def __init__(self,game,x,y):
        super().__init__("spikemole",50,2,game,x,y,"down",0,0,0,101)
        #- Attacking
        self.waitTimer = r.randint(3*60,10*60)
        self.transition = True

    #- Update Method -#
    def update(self):
        # Change State When The Timer Reaches Zero
        if not self.game.pause:
            if r.randint(1,10000) == 17 and not self.music.get_busy():
                self.music.play(self.game.sounds["spikemole"][0])
            if self.waitTimer == 0:
                if self.state == "down":
                    self.changeState("up")
                    #print("up")
                    self.transition = True
                    self.waitTimer = r.randint(3*60,7*60)
                else:
                    self.changeState("down")
                    #print("down")
                    self.transition = True
                    self.waitTimer = r.randint(3*60,10*60)
            # Change Timer
            self.waitTimer -= 1
            if self.attackCooldown > 0:
                self.attackCooldown -= 1
            # Check For Collisions
            if self.state == "up" and self.rect.colliderect(self.game.player.rect) and self.attackCooldown == 0:
                # Damage The Player Once Cooldown Is Met
                self.game.player.hp = max(0, self.game.player.hp - self.strength) # HP cannot be negative
                self.attackCooldown = 50
# |+|+|+|()|+|+|+| #
# FINAL BOSS CLASS #
# |+|+|+|()|+|+|+| #
class FinalBoss(Enemy):
    def __init__(self,game,x,y):
        super().__init__("final_boss",45,14,game,x,y,"idle",100,2,8,350)
        # Retreat Attributes
        # partial
        self.hpLog = [self.maxHP]
        self.partialRetreatCounter = 0
        # full
        self.fullRetreatCounter = 0
        self.numFullRetreats = 0
        self.fullRetreatStrength = 25
        self.numColumns = 0
        self.columnsChosen = [False]*15
        self.times = 0
        # attack
        self.swords = [Weapon(self,0,0,32,5,"boss_sword_1"), Weapon(self,0,0,16,3,"boss_sword_2"), Weapon(self,0,0,16,3,"boss_sword_2"),]
        self.lightAttackCounter = 0
        self.lightAttackCooldown = 54
        self.lightAttacking = False
    # This Means That Pathfinding Always Happens
    def pathFind(self):
        self.tilesAhead = self.tilesAround([k for k in range(-5,7)])
        if self.tilesAhead[6] and self.collisions["down"]:
            flag = False
            for value in self.tilesAhead[7:]:
                if not value:
                    flag = True
                # If there is something to jump up to
                    self.jump()
                    break
            if not flag:
                self.dir *= -1
        if sum(self.tilesAhead[:6]) == 0 and self.collisions["down"]: # If No Tiles Ahead
            match self.state:
                case "idle":
                    self.dir *= -1 # Turn around
                case "chase"|"partial_retreat":
                    self.movement[0] = 0
        
    def update(self):
        super().update()
        if not self.game.pause:
            self.pathFind()
            # HP Checks For Full Retreat
            if (self.hp <= 0.5 * self.maxHP and self.numFullRetreats == 0) or (self.hp <= 0.25 * self.maxHP and self.numFullRetreats == 1) and self.state != "full_retreat":
                self.numFullRetreats += 1
                self.changeState("full_retreat")
                for i in range(7):
                    tile = -(i%2)
                    self.game.tilemap.append(Tile(2,self.rect.x+16*(i-3),36,self.game,tile))
                for i in range(10):
                    self.game.particles.append(Particle(self.rect.centerx,self.rect.centery,"enemy",self.game))
                self.rect.y -= 200 # Get the final boss off of the screen
                if self.numFullRetreats == 1:
                    self.times = 4
                else:
                    self.times = 8
            # HP Logging For Partial Retreat #
            self.hpLog.append(self.hp)
            if len(self.hpLog) == 300 and self.state != "full_retreat":
                if self.hpLog[0] - self.hpLog[-1] >= 0.12 * self.maxHP:
                    self.changeState("partial_retreat")
                self.hpLog = self.hpLog[1:] # Always only have 300 elements to check the last five seconds
            # State Management #
            match self.state:
                case "partial_retreat":
                    self.partialRetreat()
                case "full_retreat":
                    self.fullRetreat()
                case "idle":
                    if self.checkLOS(200):
                        self.changeState("chase")
                    else:
                        self.movement[0] = self.speed//2 * self.dir # Move Slower When Idle
                        if r.randint(1,600) == 17:
                            self.dir *= -1
                        if self.hp != self.prevHP:
                            self.dir *= -1
                            self.prevHP = self.hp
                case "chase":
                    self.movement[0] = self.speed * self.dir # Set direction to chase the player
                    try:
                        self.dir = abs(self.game.player.rect.x-self.rect.x)/(self.game.player.rect.x-self.rect.x)
                    except ZeroDivisionError:
                        self.dir = 1
                    if not self.checkLOS(200):
                        self.idleTimer += 1
                        if self.idleTimer == 110: # The Final Boss Can Chase The Player For Longer After Losing LOS
                            self.changeState("idle")
                            self.idleTimer = 0
                    elif self.checkLOS(35):
                        self.changeState("attack")
                case "attack":
                    self.movement[0] = 0
                    if not self.checkLOS(35) and not self.lightAttacking:
                        self.changeState("chase")
                    self.attack()
                case _:
                    print("error with final boss state")

    # Attack Algorithm
    def attack(self):
        if self.lightAttackCooldown == 0:
            for indx, sword in enumerate(self.swords):
                match indx:
                    case 0:
                        angle = -self.lightAttackCounter*6
                        sword.img_copy = pygame.transform.rotate(sword.img,angle)
                        sword.attackX = self.attackDir*0.5*(-self.rect.width-sword.rect.width+8)+m.cos(m.pi*angle/180)*-self.attackDir*(self.rect.width+sword.rect.width)*0.5
                        sword.attackY = m.sin(m.pi*angle/180)*15
                        sword.damage = self.strength
                        sword.update()
                        sword.render(self.game.display,"rotate")
                    case 1:
                        angle = -self.lightAttackCounter*6
                        sword.img_copy = pygame.transform.rotate(sword.img,angle)
                        sword.attackX = -self.attackDir*0.5*8+m.cos(m.pi*angle/180)*self.attackDir*(self.rect.width+(0.5*sword.rect.width))
                        sword.attackY = m.sin(m.pi*angle/180)*15
                        sword.damage = 2
                        sword.update()
                        sword.render(self.game.display,"rotate")
                    case 2:
                        if self.lightAttackCounter < 15:
                            sword.attackX += self.attackDir*2
                        elif self.lightAttackCounter < 30:
                            sword.attackX -= self.attackDir*2
                        else:
                            sword.attackX = 0
                        sword.damage = 2
                        sword.update()
                        sword.render(self.game.display)
            if self.lightAttackCounter == 1:
                self.game.screenshakeStrength = 5
                self.music.play(r.choice(self.game.sounds["boss_attack"]))  
            elif self.lightAttackCounter == 30:
                self.lightAttackCounter = 0
                self.lightAttackCooldown += 45
                self.lightAttacking = False
            self.lightAttackCounter += 1
        self.lightAttackCooldown = max(self.lightAttackCooldown-1, 0)
        if self.lightAttackCooldown == 0:
            self.attackDir = self.dir
            self.lightAttacking = True

    # Retreat Algorithms
    def fullRetreat(self):
        self.movement[0] = 0
        self.fullRetreatCounter += 1
        # Dropping Coins
        if self.fullRetreatCounter == 70:
            self.numColumns = r.randint(7,15)
            # Selecting the columns to drop coins down
            for i in range(self.numColumns):
                options = []
                for index, element in enumerate(self.columnsChosen):
                    if element == False:
                        options.append(index)
                self.columnsChosen[r.choice(options)] = True
            # Creating The Coins
            for i in range(15):
                if self.columnsChosen[i]:
                    self.game.projectiles.append(Projectile(self.rect.centerx-((7-i)*16),self.rect.y+self.rect.height+17,self.fullRetreatStrength,m.pi/2,self.game,self,r.randint(2,4),"coin"))
            self.fullRetreatCounter = -25
            self.columnsChosen = 15*[False]
            self.times -= 1
            if self.times == 0:
                self.changeState("chase")
                self.game.tilemap = self.game.tilemap[:-7]
        elif self.fullRetreatCounter == 1:
            self.music.play(self.game.sounds["full_retreat"][0])

    def partialRetreat(self):
        self.partialRetreatCounter += 1
        try: # Move away from the player
            self.dir = -abs(self.game.player.rect.x-self.rect.x)/(self.game.player.rect.x-self.rect.x)
        except ZeroDivisionError: # If Pressed Against A Wall And The Player Is Close By, Change Direction
            self.dir = r.choice([-1,1])
        self.movement[0] = self.dir * self.speed
        # Stop The Partial Retreat
        if self.partialRetreatCounter == 1:
            self.music.play(self.game.sounds["partial_retreat"][0])
        if self.partialRetreatCounter == 180: # Lasts Three Seconds
            self.changeState("idle") # So That If Out Of Range, It Won't Start To Track The Player
            self.partialRetreatCounter = 0
        if self.partialRetreatCounter % 5 == 0:
            self.hp = min(self.hp+1,self.maxHP) # So That It Won't Heal 180 Health, just 36