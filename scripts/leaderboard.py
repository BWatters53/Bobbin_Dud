import pygame,os
pygame.init()
# |||*\()/*||| #
# LEADERBOARDS #
# |||*/()\*||| #
class Leaderboard:
    def __init__(self,title,x,y,game,fileRef):
        # Title Stuff
        self.titleFont = pygame.font.SysFont("oldenglishtext",18)
        self.title = title # So that It Can Be Referenced By Title If Required
        self.titleText = self.titleFont.render(self.title,False,(137,87,39))
        
        # Stat Stuff
        self.mainFont = pygame.font.SysFont("Castellar",10)
        self.statistics = {"1":[None,-1], # These Will Be Filled With The Relevant Data By The Update Function
                           "2":[None,-1],
                           "3":[None,-1],
                           "4":[None,-1],
                           "5":[None,-1],
                           "6":[None,-1],
                           "7":[None,-1],
                           "8":[None,-1],
                           "9":[None,-1],
                           "10":[None,-1],
                           }
        self.fileRef = fileRef # Used to find the correct stas in the files
        # Rendering Stuff
        self.game = game
        self.rect = pygame.Rect(x,y,160,self.game.display.get_height()-70)
        self.titleLoc = (self.rect.centerx-self.titleText.get_width()//2,y+2)

    # Update Leaderboard
    def update(self):
        entries = []
        for file in os.listdir("accounts"):
            username = file[:-4]
            f = open(f"accounts/{file}","r")
            for line in f.readlines():
                if line[:len(self.fileRef)+6] == f"    [{self.fileRef}]":
                    #print(line[len(self.fileRef)+6:])
                    value = int(line[len(self.fileRef)+8:][:-1]) # To Igonore The ": " and "\n"
            entries.append([value,username])
        while len(entries) < 10:
            entries.append([-1,None]) # Fill The Leaderboard To Have Ten Values
        topTen = sorted(entries)[-10:]
        for i, item in enumerate(topTen):
            self.statistics[str(10-i)] = [item[1],item[0]] # Create The Correct Dictionary
            
        # Get All Stats Within The Leaderboard's Rect
        self.statisticsText = [f"{key}: {value[0]} : {value[1]}" for key,value in self.statistics.items()]
        counter = 0
        for i,item in enumerate(self.statisticsText.copy()):
            if len(item) >= 20:
                self.statisticsText = self.statisticsText[:i+counter] +[self.statisticsText[i+counter][:17]]+[self.statisticsText[i+counter][17:]]+self.statisticsText[i+counter+1:]
                counter += 1

    # Rendering Method
    def render(self):
        pygame.draw.rect(self.game.display,(48,52,29),self.rect,border_radius=6)
        self.game.display.blit(self.titleText,self.titleLoc)
        for i,stat in enumerate(self.statisticsText):
            self.game.display.blit(self.mainFont.render(stat,False,(137,87,39)),(self.rect.x+5,self.rect.y+10+(i+1)*15))
