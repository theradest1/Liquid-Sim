import pygame
import random
#import math

def textToScreen(text, color, position):
    screen.blit(font.render(text, True, color), position)

pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Testing")
font = pygame.font.Font(None, 36)


class Edge():
    def __init__(self, velocity = None):
        self.velocity = random.random() * 100 + (100 if random.random() < .5 else -100)
        
        if velocity is not None:
            self.velocity = velocity
    
    def draw(self, x, y, radius, xDir, yDir):
        screenPos = (x * scale + screenPadding, y * scale + screenPadding)
        endScreenPos = (x * scale + screenPadding + self.velocity * xDir, y * scale + screenPadding + self.velocity * yDir)

        pygame.draw.circle(screen, (0, 0, 0), screenPos, radius)
        pygame.draw.line(screen, (255, 255, 255), screenPos, endScreenPos)
    
def waitForPress():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
            elif event.type == pygame.KEYDOWN:
                return
            

scale = 300
screenPadding = 150


while True:
    left = Edge()
    right = Edge()
    top = Edge()
    bottom = Edge()

    screen.fill((100, 100, 100))
    rect = pygame.Rect(screenPadding, screenPadding, scale, scale)
    pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    left.draw(0, .5, 5, 1, 0,)
    right.draw(1, .5, 5, 1, 0)
    top.draw(.5, 0, 5, 0, -1)
    bottom.draw(.5, 1, 5, 0, -1)

    openEdges = 4
    divergence = (right.velocity - left.velocity + top.velocity - bottom.velocity)
    splitDivergence = divergence/openEdges

    textToScreen("Divergence:", (0, 0, 0), (1, 1))
    textToScreen(f"Before: {round(divergence, 2)}", (0, 0, 0), (1, 21))
    textToScreen("After: ---", (0, 0, 0), (1, 41))

    pygame.display.flip()


    waitForPress()

    right.velocity -= splitDivergence
    left.velocity += splitDivergence
    top.velocity -= splitDivergence
    bottom.velocity += splitDivergence

    #should be roughly 0
    new_divergence = right.velocity - left.velocity + top.velocity - bottom.velocity

    screen.fill((100, 100, 100))

    rect = pygame.Rect(screenPadding, screenPadding, scale, scale)
    pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    left.draw(0, .5, 5, 1, 0)
    right.draw(1, .5, 5, 1, 0)
    top.draw(.5, 0, 5, 0, -1)
    bottom.draw(.5, 1, 5, 0, -1)

    textToScreen("Divergence:", (0, 0, 0), (1, 1))
    textToScreen(f"Before: {round(divergence, 2)}", (0, 0, 0), (1, 21))
    textToScreen(f"After: {round(new_divergence, 2)}", (0, 0, 0), (1, 41))

    pygame.display.flip()

    waitForPress()