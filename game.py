#File Imports
from utils import loadImg
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

running = True
while running:
    #Display Scaling
    screen.blit(pygame.transform.scale(display, (800,800)), (0,0))
    display.blit(assets["sky"],(0,0))

    #Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Extra Stuff
    pygame.display.update()
    clock.tick(60)

pygame.quit()