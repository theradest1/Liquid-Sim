import pygame
import math

def textToScreen(text, color, position):
    screen.blit(font.render(text, True, color), position)

pygame.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Testing")
font = pygame.font.Font(None, 36)


class Edge():
    def __init__(self):
        self.velocity = 0
    
    def draw(self, x, y, radius, valueToPrint):
        screenPos = (x * scale + 100, y * scale + 100)

        pygame.draw.circle(screen, (0, 0, 0), screenPos, radius)
        textToScreen(str(valueToPrint), (255, 255, 255), screenPos)
    
scale = 300
horizontalEdges = [[Edge()], [Edge()]]
verticalEdges = [[Edge(), Edge()]]

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    #get weights
    weights = []

    mouseX, mouseY = pygame.mouse.get_pos()
    mouseX /= scale
    mouseY /= scale

    weights.append()


    screen.fill((100, 100, 100))

    count = 0

    for x in range(len(horizontalEdges[0])):
        for y in range(len(horizontalEdges)):
            horizontalEdges[y][x].draw(x + .5, y, 5, weights[count])
            count += 1
    
    for x in range(len(verticalEdges[0])):
        for y in range(len(verticalEdges)):
            verticalEdges[y][x].draw(x, y + .5, 5, weights[count])
            count += 1

    pygame.display.flip()
    clock.tick(30)