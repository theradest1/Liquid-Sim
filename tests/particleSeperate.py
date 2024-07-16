import pygame
import random
import math
import time
import numpy as np

def textToScreen(text, color, position):
    screen.blit(font.render(text, True, color), position)

def clamp(value, minValue, maxValue):
    return max(min(value, maxValue), minValue)

class Particle():
    def __init__(self, xVel = None, yVel = None, xPos = None, yPos = None):
        self.xVel = (xVel if xVel is not None else random.random() - .5) * .5
        self.yVel = (yVel if yVel is not None else random.random() - .5) * .5
        self.xPos = xPos if xPos is not None else random.random()
        self.yPos = yPos if yPos is not None else random.random()

    def move(self, dt):
        self.xPos += self.xVel * dt
        if self.xPos >= 1 or self.xPos <= 0:
            self.xVel *= -1
            self.xPos = clamp(self.xPos + self.xVel * dt, 0.001, .999)
        
        self.yPos += self.yVel * dt
        if self.yPos >= 1 or self.yPos <= 0:
            self.yVel *= -1
            self.yPos = clamp(self.yPos + self.yVel * dt, 0.001, .999)

    def draw(self, radius):
        screenPos = (self.xPos * scale + padding, self.yPos * scale + padding)
        #endScreenPos = (self.xPos * scale + padding + self.xVel, self.yPos * scale + padding + self.yVel)

        pygame.draw.circle(screen, (0, 0, 255), screenPos, radius * scale / 2)
        #pygame.draw.line(screen, (0, 0, 255), screenPos, endScreenPos)


class Cell():
    def __init__(self):
        self.particles = np.array([], dtype=Particle)
        self.nearCells = np.array([], dtype=Cell)

    def draw(self, x, y):
        size = cellSize * scale
        rect = pygame.Rect(x * size + padding, y * size + padding, size, size)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)
    
    def getParticles(self):
        nearParticles = np.array([], dtype=Particle)
        for nearCell in self.nearCells:
            nearParticles = np.concatenate((nearParticles, nearCell.particles))
        return nearParticles



class Grid():
    def __init__(self, xNumCells, yNumCells):
        self.width = xNumCells
        self.height = yNumCells

        self.cells = np.empty((yNumCells, xNumCells), dtype=Cell)
        for y in range(yNumCells):
            for x in range(xNumCells):
                self.cells[y, x] = Cell()

        for y in range(yNumCells):
            for x in range(xNumCells):
                nearCells = np.array([])
                for xOffset in range(-1, 2):
                    for yOffset in range(-1, 2):
                        nearY = y + yOffset
                        nearX = x + xOffset
                        if nearY >= 0 and nearY < self.height and nearX >= 0 and nearX < self.width:
                            nearCells = np.append(nearCells, self.cells[y + yOffset, x + xOffset])
                self.cells[y, x].nearCells = nearCells
            
    def draw(self):
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                self.cells[y, x].draw(x, y)
    
    def clear(self):
        for y in range(len(self.cells)):
            for x in range(len(self.cells[0])):
                self.cells[y, x].particles = np.array([])
    
    def addParticle(self, particle):
        xCell = math.floor(particle.xPos/cellSize)
        yCell = math.floor(particle.yPos/cellSize)

        cell = self.cells[yCell, xCell]

        cell.particles = np.append(cell.particles, particle)

        
def seperateTwoParticles(particle_1, particle_2):
    #global calcs
    #calcs += 1

    dx = particle_2.xPos - particle_1.xPos
    dy = particle_2.yPos - particle_1.yPos

    distance = math.sqrt(dx**2 + dy**2)
    if distance < particleRadius: #is overlaping
        overlap = particleRadius - distance
        
        # Calculate the direction in which to move the circles
        angle = math.atan2(dy, dx)
        
        # Move the circles away from each other
        move_x = overlap * math.cos(angle) / 2
        move_y = overlap * math.sin(angle) / 2
        
        particle_1.xPos = clamp(particle_1.xPos - move_x, 0.001, .999)
        particle_1.yPos = clamp(particle_1.yPos - move_y, 0.001, .999)
        particle_2.xPos = clamp(particle_2.xPos + move_x, 0.001, .999)
        particle_2.yPos = clamp(particle_2.yPos + move_y, 0.001, .999)

def seperateParticles():
    global comparisons

    if not badVersion:
        #setup
        grid.clear()
        for particle in particles:
            grid.addParticle(particle)

        for y in range(0, len(grid.cells), 2):
            for x in range(0, len(grid.cells[y]), 2):
                cell = grid.cells[y, x]
                cellParticles = cell.getParticles()
                for particle_1 in cellParticles:
                    for particle_2 in cellParticles:
                        if particle_1 != particle_2:
                            comparisons += 1
                            seperateTwoParticles(particle_1, particle_2)

    else:
        for particle_1 in particles:
            for particle_2 in particles:
                if particle_1 != particle_2:
                    comparisons += 1
                    seperateTwoParticles(particle_1, particle_2)


def waitForPress():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
            elif event.type == pygame.KEYDOWN:
                return


def drawAll():
    screen.fill((100, 100, 100))

    if not badVersion:
        grid.draw()
    else:
        rect = pygame.Rect(padding, padding, scale, scale)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)

    for particle in particles:
        particle.draw(particleRadius)

    textToScreen(f"Type: {"Particle by particle" if badVersion else "Cell based"}", (0, 0, 0), (1, 1))
    textToScreen(f"Comparisons: {comparisons}", (0, 0, 0), (1, 21))

    pygame.display.flip()


#initialize
particleRadius = .03
cellsInRow = int(1/(particleRadius*2))
grid = Grid(cellsInRow, cellsInRow)
cellSize = 1/cellsInRow
maxIterations = 5
particles = 200
scale = 800 #only visual
padding = 50 #only visual
badVersion = True

pygame.init()
screen = pygame.display.set_mode((scale + padding * 2, scale + padding * 2))
pygame.display.set_caption("Testing")
font = pygame.font.Font(None, 36)

particles = np.array([Particle() for _ in range(particles)])

#show
comparisons = 0
drawAll()
waitForPress()

#game loop
startFrame = time.time()
while True:
    comparisons = 0
    dt = time.time() - startFrame
    startFrame = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            badVersion = not badVersion

    for particle in particles:
        particle.move(dt)

    #calcs = 0

    for i in range(maxIterations):
        seperateParticles()

    #print(f"Iterations: {i}, Time: {time.time() - startFrame}")

    drawAll()

exit()