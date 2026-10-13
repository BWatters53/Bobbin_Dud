#- COLLISION CHECKING SUBROUTINE -#
import pygame
import os

def findCollisions(rect, lst):
    hits = []
    for item in lst:
        if item.rect.colliderect(rect):
            hits.append(item)
    return hits 

#- IMAGE LOADING SUBROUTINES -#
def loadImg(path):
    img = pygame.image.load("assets/"+path+".png").convert()
    img.set_colorkey((0,0,0))
    return img
def loadImages(path):
    images = []
    for img in os.listdir("assets/"+path):
        images.append(loadImg(path+"/"+img[:-4]))
    return images
#- SOUND LOADING -#
def loadSounds(path):
    sounds = []
    for sound in os.listdir("sounds/"+path):
        sounds.append(pygame.mixer.Sound("sounds/"+path+"/"+sound))
    #print(sounds)
    return sounds

#- ANIMATION SUBROUTINE -#
def animate(user):
    if not user.game.pause:
        # SPIKEMOLE CONTROL
        if user.maxHP == 101 and user.transition:
            if user.state == "up":
                if user.frameCounter == 0:
                    user.frameCounter = user.game.assets[user.name]["down"]["frameCounter"]*4
                    user.currentFrame = 4
                    user.img = user.game.assets[user.name]["down"]["frames"][user.currentFrame-1]
                elif user.frameCounter > 0:
                    if user.frameCounter % user.game.assets[user.name]["down"]["frameCounter"] == 0:
                        user.currentFrame -= 1
                        user.img = user.game.assets[user.name]["down"]["frames"][user.currentFrame-1]
                user.frameCounter -= 1
                if user.frameCounter == 0:
                    user.transition = False
                    user.img = user.game.assets[user.name]["up"]["frames"][0]
            else:
                if user.frameCounter == 0:
                    user.frameCounter = user.game.assets[user.name]["down"]["frameCounter"]*4
                    user.currentFrame = 1
                    user.img = user.game.assets[user.name]["down"]["frames"][user.currentFrame-1]
                elif user.frameCounter > 0:
                    if user.frameCounter % user.game.assets[user.name]["down"]["frameCounter"] == 0:
                        user.currentFrame += 1
                        user.img = user.game.assets[user.name]["down"]["frames"][user.currentFrame-1]
                user.frameCounter -= 1
                if user.frameCounter == 0:
                    user.frameCounter += 1
                    user.currentFrame = 5
                    user.img = user.game.assets[user.name]["down"]["frames"][user.currentFrame-1]
        # OTHER ENTITIES
        else:
            user.frameCounter += 1
            if user.state != "light_attack" and user.state != "heavy_attack" and user.state != "bow_attack":
                if user.frameCounter == user.game.assets[user.name][user.state]["frameCounter"]:
                    user.currentFrame = user.currentFrame%len(user.game.assets[user.name][user.state]["frames"]) + 1
                    user.img = user.game.assets[user.name][user.state]["frames"][user.currentFrame-1]
                    user.frameCounter = 0

#- LEVEL LOADING SUBROUTINE -#
def loadLevel(filename,game):
    from .tile import Tile,MovingPlatform,Horizontal,Vertical,BouncePad,ClimbingWall,Decor
    from .entity import Spikemole,Guard,Soldier,Archer,Knight,FinalBoss
    from .label import Serf
    tilemap = []
    bouncepads = []
    movingplatforms = []
    climbingwalls = []
    enemies = []
    playerStart = None
    decor = []
    serfs = []
    game.enemyCounter = 0
    file = open("scripts/levels/"+filename+".txt", "r")
    for line in file.readlines():
        if line[:8] == "tilemap:": # Create The Tilemap Data
            for tile in line[9:].split(";")[:-1]: # Split The List Into Tile Entities (Ignore The Empty End Entity)
                data = [int(k) for k in tile[1:-1].split(",")] # Split Each Entity Into Its Data Elements
                tilemap.append(Tile(data[0],data[2],data[3],game,data[1])) # Turn The Data Into A Tile
        elif line[:11] == "bouncepads:": # Create The Bounce Pads
            for tile in line[12:].split(";")[:-1]:
                data = [int(k) for k in tile[1:-1].split(",")]
                bouncepads.append(BouncePad(data[0],data[1],game))
        elif line[:11] == "horizontal:": # Create The Horizontal Moving Platforms
            for tile in line[12:].split(";")[:-1]:
                data = [int(k) for k in tile[1:-1].split(",")]
                movingplatforms.append(Horizontal(data[0],data[1],data[2],data[3],game,data[4]))
        elif line[:9] == "vertical:": # Create The Vertical Moving Platforms
            for tile in line[10:].split(";")[:-1]:
                data = [int(k) for k in tile[1:-1].split(",")]
                movingplatforms.append(Vertical(data[0],data[1],data[2],data[3],game,data[4]))
        elif line[:14] == "climbingwalls:": # Create The Climbing Walls
            for tile in line[15:].split(";")[:-1]:
                data = [int(k) for k in tile[1:-1].split(",")]
                climbingwalls.append(ClimbingWall(data[0],data[1],game,data[2]))
        elif line[:6] == "decor:":
            for decoration in line[7:].split(";")[:-1]:
                data = [int(k) for k in decoration[1:-1].split(",")]
                decor.append(Decor(data[0],data[1],game,data[2]))
        elif line[:11] == "spikemoles:":
            for tile in line[12:].split(";")[:-1]:
                data = [int(k) for k in tile[1:-1].split(",")]
                enemies.append(Spikemole(game,data[0],data[1]))
        elif line[:7] == "guards:":
            for tile in line[8:].split(";")[:-1]:
                data = [int(k) for k in tile[1:-1].split(",")]
                enemies.append(Guard(game,data[0],data[1]))
        elif line[:9] == "soldiers:":
            for tile in line[10:].split(";")[:-1]:
                data = [int(k) for k in tile[1:-1].split(",")]
                enemies.append(Soldier(game,data[0],data[1]))
        elif line[:8] == "archers:":
            for tile in line[9:].split(";")[:-1]:
                data = [int(k) for k in tile[1:-1].split(",")]
                enemies.append(Archer(game,data[0],data[1]))
        elif line[:8] == "knights:":
            for tile in line[9:].split(";")[:-1]:
                data = [int(k) for k in tile[1:-1].split(",")]
                enemies.append(Knight(game,data[0],data[1]))
        elif line[:13] == "final_bosses:":
            for tile in line[14:].split(";")[:-1]:
                data = [int(k) for k in tile[1:-1].split(",")]
                enemies.append(FinalBoss(game,data[0],data[1]))
        elif line[:13] == "player start:": # Add The Player Start Position
            try:
                data = line[14:].split(",")
                playerStart = (int(data[0][1:]),int(data[1][:-2]))
            except ValueError: # (If It Exists)
                playerStart = None
        elif line[:6] == "serfs:":
            for serf in line[7:].split(";")[:-1]:
                data = [int(k) for k in serf[1:-1].split(",")]
                serfs.append(Serf(game,data[0],data[1],data[2]))
    file.close()
    return tilemap,bouncepads,movingplatforms,climbingwalls,enemies,playerStart,decor,serfs
