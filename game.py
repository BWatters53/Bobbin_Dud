#File Imports
from utils import loadImg
from entities import Entity,Player
#Library Imports
import pygame

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((800,800))
pygame.display.set_caption("Bobbin Dud")
display = pygame.Surface((400,400)) # 2x Scaling

#Assets
assets = {
    "sky":loadImg("sky_bg"),
}

#Map
tilemap = [pygame.Rect(310,320,100,15),pygame.Rect(195,365,115,15),pygame.Rect(0,380,400,20),pygame.Rect(0,200,75,15),pygame.Rect(350,45,60,15),pygame.Rect(100,100,100,15),pygame.Rect(20,20,150,15)]


#Player
player = Player(16,"red",200,200,2)
gravity = 0.2

running = True
while running:
    #Display Scaling
    screen.blit(pygame.transform.scale(display, (800,800)), (0,0))
    display.blit(assets["sky"],(0,0))

    ##Player
    player.movement[2] = min(7, player.movement[2]+gravity)
    p_movement = [player.speed*(player.movement[1]-player.movement[0]),player.movement[2]]
    player.update(p_movement,tilemap)
    player.render(display)

    #Map
    for rect in tilemap:
        pygame.draw.rect(display,"green",rect)

    #Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                player.movement[1] = True
            if event.key == pygame.K_LEFT:
                player.movement[0] = True
            if event.key == pygame.K_UP and player.jump > 0:
                player.movement[2] = -5
                player.jump -= 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                player.movement[1] = False
            if event.key == pygame.K_LEFT:
                player.movement[0] = False

    #Extra Stuff
    pygame.display.update()
    clock.tick(60)

pygame.quit() 