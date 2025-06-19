import pygame
def loadImg(path):
    img = pygame.image.load("assets/"+path+".png")
    img.set_colorkey((0,0,0))
    return img 