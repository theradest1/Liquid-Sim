import pygame
import random
#import math

def textToScreen(text, color, position):
    screen.blit(font.render(text, True, color), position)

pygame.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Testing")
font = pygame.font.Font(None, 36)


class Edge():
    def __init__(self, velocity = None):
        self.velocity = random.random() * 100 if velocity is None else velocity
    
    def draw(self, x, y, radius, xDir, yDir):
        screenPos = (x * scale + 100, y * scale + 100)
        endScreenPos = (x * scale + 100 + self.velocity * xDir, y * scale + 100 + self.velocity * yDir)

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

left = Edge()
right = Edge()
top = Edge()
bottom = Edge()

screen.fill((100, 100, 100))

left.draw(0, .5, 5, 1, 0,)
right.draw(1, .5, 5, 1, 0)
top.draw(.5, 0, 5, 0, -1)
bottom.draw(.5, 1, 5, 0, -1)

pygame.display.flip()

openEdges = 4
divergence = (right.velocity - left.velocity + top.velocity - bottom.velocity)
splitDivergence = divergence/openEdges
print(divergence)

waitForPress()

right.velocity -= splitDivergence
left.velocity += splitDivergence
top.velocity -= splitDivergence
bottom.velocity += splitDivergence

#should be roughly 0
print(right.velocity - left.velocity + top.velocity - bottom.velocity)

screen.fill((100, 100, 100))

left.draw(0, .5, 5, 1, 0)
right.draw(1, .5, 5, 1, 0)
top.draw(.5, 0, 5, 0, -1)
bottom.draw(.5, 1, 5, 0, -1)

pygame.display.flip()

waitForPress()
exit()