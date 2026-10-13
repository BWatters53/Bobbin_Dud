import pygame, os
import random as r
import math as m
from .utils import loadImg,loadLevel
from .particle import Particle

#-+-+-+-+-+-+-+-#
#- LABEL CLASS -#
#-+-+-+-+-+-+-+-#
class Label:
    def __init__(self, x, y, text):
        self.font = pygame.font.SysFont("arial", 10)
        self.strtext = text
        self.text = self.font.render(text, False, (137,87,39))
        self.rect = pygame.Rect(x,y,self.text.get_width()+10,self.text.get_height()+5)

    def render(self,surface):
        surface.blit(self.text,(self.rect.x + (self.rect.width-self.text.get_width())//2,self.rect.y + (self.rect.height-self.text.get_height())//2))

#----------------#
#- BANNER CLASS -#
#----------------#
class Banner(Label):
    def __init__(self,x,y,statMax,type):
        self.statMax = statMax
        self.type = type
        self.statCurrent = statMax
        super().__init__(x,y,str(self.statMax))
        if self.type == "bar":
            self.rectG = pygame.Rect(x,y,self.statMax//4,3) # Heights Subject To Change
            self.rectR = pygame.Rect(x+self.statCurrent//4,y,self.statMax//4-self.statCurrent//4,3)
            self.width = self.rectG.width + self.rectR.width
        
    def update(self, newValue, x=0, y=0):
        self.statCurrent = newValue
        if self.type == "counter":
            self.text = self.font.render(str(newValue),False,(137,87,39))
        else:
            self.rectG = pygame.Rect(x,y,self.statMax//4,3) # Heights Subject To Change
            self.rectR = pygame.Rect(x+self.statCurrent//4,y,self.statMax//4-self.statCurrent//4,3)
    
    def render(self,surface):
        if self.type == "bar":
            pygame.draw.rect(surface,"green",self.rectG)
            pygame.draw.rect(surface,"red",self.rectR)
        else:
            super().render(surface)

#   [{()()}]   #
# BUTTON CLASS #
#   [{()()}]   #
class Button(Label):
    def __init__(self,x,y,text,type_,subtype=None,destination=None):
        self.type = type_
        if self.type == "transition":
            self.destination = destination
            self.text = text
        elif self.type == "upgrade":
            self.subtype = subtype
            self.costs = {
                "attack":20,
                "defence":15,
                "speed":25,
            }
            self.text = str(self.costs[self.subtype]) + " GOLD"
            match self.subtype:
                case "attack":
                    self.img = loadImg("shoppe_2")
                case "defence":
                    self.img = loadImg("shoppe_3")
                case "speed":
                    self.img = loadImg("shoppe_4")
        else:
            self.text = text
            self.subtype = subtype
            self.response = ""
            self.responseCounter = 0
        super().__init__(x,y,self.text)
    # What To Do When The Button Is Pressed
    def onClick(self,game):
        from scripts.entity import Player
        match self.type:
            case "transition":
                if self.destination == "custom" and game.state != "olde_shoppe":
                    # Is The Level Valid To Play?
                    game.levels["custom"] = game.loadLevel("temp")
                    flag = True
                    for enemy in game.levels["custom"]["enemies"]:
                        if enemy.name != "spikemole":
                            flag = False
                    if (game.levels["custom"]["playerStart"] == None or flag):
                        game.state = "play_menu"
                        game.menuMusic.play(game.sounds["error"][0])
                    else:
                        game.bgMusic.fadeout(2500)
                        game.loadGame(["Loading Your Level",""],"custom")
                        game.bgMusic.set_volume(0.3)
                        game.bgMusic.play(game.sounds["background"][1],-1)
                        game.state = self.destination
                        game.particles += [Particle(game.player.rect.centerx,game.player.rect.centery,"spawn",game,angle=10*i) for i in range(36)]
                else:
                    if self.destination == "game" and game.state != "olde_shoppe":
                        game.bgMusic.fadeout(2500)
                        game.loadGame(["Loading Campaign Levels",""],1)
                        game.bgMusic.set_volume(0.3)
                        game.bgMusic.play(game.sounds["background"][1],-1)
                    elif self.destination == "leaderboards":
                        for leaderboard in game.leaderboards:
                            leaderboard.update()
                        game.menuMusic.play(game.sounds["leaderboard"][0])
                    elif game.state == "game" or game.state == "custom":
                        game.bgMusic.stop() # So That The Music Does Not Keep Playing
                        game.user.updateStats() # Leaderboards Will Refresh Every Time The User Finishes Their Game
                        game.bgMusic.play(game.sounds["background"][2],-1)
                    elif self.destination == "editor":
                        try:
                            game.editor.tilemap,game.editor.bouncepads,game.editor.movingplatforms,game.editor.climbingwalls,game.editor.enemies,game.editor.playerStart,game.editor.decor,game.editor.serfs = loadLevel("temp",game.editor)
                        except FileNotFoundError:
                            game.editor.tilemap,game.editor.bouncepads,game.editor.movingplatforms,game.editor.climbingwalls,game.editor.enemies,game.editor.playerStart,game.editor.decor,game.editor.serfs = [],[],[],[],[],None,[],[]
                    game.state = self.destination
                    if self.destination == "game":
                        game.particles += [Particle(game.player.rect.centerx,game.player.rect.centery,"spawn",game,angle=10*i) for i in range(36)]
            case "submit":
                for textbox in game.accountMenuTextboxes:
                    if textbox.purpose == "Username":
                        username = textbox.storedText
                    elif textbox.purpose == "Password":
                        password = textbox.storedText
                    textbox.storedText = ""
                match self.subtype:
                    case "create_account": # Extract The Details To Create An Account
                        if f"{username}.txt" not in os.listdir("accounts"):
                            self.response = game.createAccount(username,password)
                            if self.response == "ACCOUNT SUCCESSFULLY CREATED":
                                game.user = game.loadAccount(username)
                        else:
                            self.response = "USER WITH THAT USERNAME ALREADY EXISTS."
                        self.responseCounter += 180
                    case "validate_account":
                        self.response = game.validateAccount(username,password)
                        if self.response == "WELCOME BACK!":
                            game.user = game.loadAccount(username)
                        self.responseCounter += 180
                    case _:
                        print("submission error")

            case "upgrade":
                if game.player.score >= self.costs[self.subtype]:
                    match self.subtype:
                        case "attack":
                            game.player.strengthMultiplier *= 1.2
                        case "defence":
                            game.player.maxHP = int(1.2*game.player.maxHP)
                        case "speed":
                            game.player.speed *= 1.1
                    game.player.score -= self.costs[self.subtype]
                    self.costs[self.subtype] = int(1.5 * self.costs[self.subtype])
                    pygame.mixer.Channel(7).play(game.sounds["validation"][0])
                    self.text = self.font.render(str(self.costs[self.subtype]) + " GOLD", False, (137,87,39))
                    game.player = Player(game,game.player.rect.x,game.player.rect.y,game.player.lives,game.player.maxHP,game.player.score,game.player.strengthMultiplier,game.player.speed)
                else:
                    pygame.mixer.Channel(7).play(game.sounds["error"][0])
    def render(self,surface):
        if (self.type == "transition" and self.strtext not in ("BACK","EXIT","CONTINUE")) or self.type == "submit":
            self.rect.x = surface.get_width()//2 - self.rect.width//2

        pygame.draw.rect(surface,(48,52,29),self.rect,border_radius=3)
        super().render(surface)
        if self.type == "upgrade":
            surface.blit(self.img,(self.rect.centerx-self.img.get_width()//2,self.rect.y-self.img.get_height()-5))

        elif self.type == "submit":
            self.responseText = self.font.render(self.response,False,"red")
            surface.blit(self.responseText, (surface.get_width()//2-self.responseText.get_width()//2,self.rect.bottom+2))
            if len(self.response) > 0: # Only Show The Message For A Short While
                self.responseCounter = max(0,self.responseCounter-1)
                if self.responseCounter == 0:
                    self.response = ""         

#\             /#
# TEXTBOX CLASS #
#/             \#
class Textbox(Label):
    def __init__(self,x,y,text,purpose):
        self.colour = "grey"
        self.focus = False
        self.storedText = ""
        super().__init__(x,y,text)
        self.font = pygame.font.SysFont("Arial", 15)
        self.rect = pygame.Rect(x,y,self.font.render("M",False,(137,87,39)).get_width()*21 + 5, self.font.render("f",False,(137,87,39)).get_height()+4)
        self.label = self.font.render(purpose+":",False,"black")
        self.purpose = purpose

    def update(self):
        if self.purpose == "Password":
            self.text = self.font.render("*"*len(self.storedText), False, (0,0,0))
        else:
            self.text = self.font.render(self.storedText, False, (0,0,0))

        if self.focus:
            self.colour = "white"
        else:
            self.colour = "grey"
    
    def render(self,surface):
        self.rect.x = surface.get_width()//2 - self.rect.width//2 + self.label.get_width()//2
        pygame.draw.rect(surface,self.colour,self.rect)
        surface.blit(self.label,(self.rect.x-self.label.get_width()-5,self.rect.y+2))
        surface.blit(self.text,(self.rect.x+5, self.rect.y+2))
        if len(self.storedText) == 20:
            surface.blit(Label(0,0,"").font.render("Max 20 Characters",False,"red"),(self.rect.x+2,self.rect.bottom+1))
# ####**#### #
# SERF CLASS #
# ####**#### #
class Serf(Label):
    def __init__(self,game,x,y,type_):
        # Update Attributes #
        self.game = game
        self.cost = r.randint(9,31) # Sets the price for the upgrade
        self.prizeRoll = r.choice(["Increase Attack","Heal HP","Give A Life","Increase HP","Increase Speed","Pay Back"]) # Chooses the prize that will be received
        self.fadeCounter = 255 # Max Alpha Value
        self.distanceFromPlayer = "" # To not accidentally trigger good effects
        self.valid = False
        self.alive = True
        super().__init__(x,y-11,str(self.cost) + "GOLD") # y-11 so that cost renders above the image
        # Render Attributes #
        self.textRect = self.rect # Use The rect Made By The Label's Init
        self.type = type_
        self.img = self.game.assets["serf"][self.type]
        self.rect = pygame.Rect(x,y,self.img.get_width(),self.img.get_height())

    def update(self):
        if self.alive:
            self.img.set_alpha(255)
            self.distanceFromPlayer = m.sqrt(((self.game.player.rect.centerx-self.rect.centerx)**2) + ((self.game.player.rect.centery-self.rect.centery)**2))
            if self.distanceFromPlayer <= 50:
                self.valid = True # The Player Can Roll For Prizes
            else:
                self.valid = False
        else:
            self.fadeout()
    
    def rollReward(self,):
        if self.game.player.score >= self.cost:
            self.game.player.score -= self.cost 
            self.game.menuMusic.play(self.game.sounds["coins"][0])
            match self.prizeRoll:
                case "Increase Attack":
                    self.game.player.strengthMultiplier *= r.randint(11,20) * 0.1
                case "Heal HP":
                    self.game.player.hp = min(self.game.player.maxHP, self.game.player.hp + r.randint(15,30))
                case "Give A Life":
                    self.game.player.lives += 1
                case "Increase HP":
                    self.game.player.maxHP += r.randint(15,30)
                case "Increase Speed":
                    self.game.player.speed += r.randint(5,15) * 0.1
                case "Pay Back":
                    self.game.player.score += r.randint(20,30)
            return True

        else:
            return False # Not Enough Money So Ignore
    
    def fadeout(self):
        #print(self.img.get_alpha())
        self.fadeCounter -= 1
        self.img.set_alpha(self.fadeCounter)
        self.text.set_alpha(self.fadeCounter)

    def render(self,scroll):
        # Apply Scroll To Both Rects #
        self.rect.x += scroll[0]
        self.rect.y += scroll[1]
        self.textRect.x += scroll[0]
        self.textRect.y += scroll[1]
        try:
            if self.game.tab:
                pass
        except AttributeError: # In The Editor, Do Not Show The Price
            self.game.display.blit(self.text,(self.textRect.x,self.textRect.y))
        self.game.display.blit(self.img,(self.rect.x,self.rect.y))


