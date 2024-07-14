import pygame
import time
import math
import random

def textToScreen(text, color, position):
    screen.blit(font.render(text, True, color), position)

def normalize_tuple(t):
    # Calculate the Euclidean norm of the tuple
    norm = math.sqrt(sum(x**2 for x in t))
    
    # Avoid division by zero
    if norm == 0:
        raise ValueError("Cannot normalize a tuple with zero magnitude")
    
    # Return the normalized tuple
    return tuple(x / norm for x in t)


def clamp(value, minValue, maxValue):
    return max(min(value, maxValue), minValue)


class Particle:
    def __init__(self, xBound, yBound):
        self.xPos = random.random() * xBound
        self.yPos = random.random() * yBound
        self.xVel = 0
        self.yVel = 0
    
    def addVel(self, xVel, yVel):
        self.xVel += xVel
        self.yVel += yVel
    
    def move(self, dt):
        self.xPos += self.xVel * dt
        if self.xPos >= maxX or self.xPos <= 0:
            self.xPos = clamp(self.xPos, 0, maxX)
            self.xVel = 0

        self.yPos += self.yVel * dt
        if self.yPos >= maxY or self.yPos <= 0:
            self.yPos = clamp(self.yPos, 0, maxY)
            self.yVel = 0
    
    def draw(self, scale, color):
        pygame.draw.circle(screen, color, (self.xPos * scale, self.yPos * scale), scale * particleRadius)
        

#references to other data (like corners  or edges)
class Cell:
    def __init__(self, x, y, grid):
        self.xPos = x
        self.yPos = y

        self.edge_top = grid.horizontalEdges[x][y]
        self.edge_bottom = grid.horizontalEdges[x][y + 1]
        self.edge_left = grid.verticalEdges[x][y]
        self.edge_right = grid.verticalEdges[x + 1][y]

        self.reset()

    def reset(self):
        self.isAir = True
        self.particles = []
    
    def addParticle(self, particle):
        self.isAir = False

        trueX = self.xPos * cellSize
        trueY = self.yPos * cellSize

        remainderX = particle.xPos - trueX
        remainderY = particle.yPos - trueY

        pygame.draw.circle(screen, (0, 255, 0), (trueX * scale, trueY * scale), 10)

        particle.weight_left = 1 - remainderX/cellSize
        particle.weight_right = remainderX/cellSize
        particle.weight_top = 1 - remainderY/cellSize
        particle.weight_bottom = remainderY/cellSize

        self.edge_left.velocity += particle.xVel * particle.weight_left
        self.edge_right.velocity += particle.xVel * particle.weight_right
        self.edge_top.velocity += particle.yVel * particle.weight_top
        self.edge_bottom.velocity += particle.yVel * particle.weight_bottom

        self.edge_left.weight += particle.weight_left
        self.edge_right.weight += particle.weight_right
        self.edge_top.weight += particle.weight_top
        self.edge_bottom.weight += particle.weight_bottom

        self.particles.append(particle)

    def updateDensity(self):
        if self.isAir:
            return
        
        self.density = self.edge_right.weight + self.edge_left.weight + self.edge_top.weight + self.edge_bottom.weight
        #print(self.density)
    
    def updateParticles(self):
        for particle in self.particles:
            particle.xVel = (self.edge_left.velocity * particle.weight_left + self.edge_right.velocity * particle.weight_right) / (particle.weight_right + particle.weight_left)
            particle.yVel = (self.edge_top.velocity * particle.weight_top + self.edge_bottom.velocity * particle.weight_bottom) / (particle.weight_top + particle.weight_bottom)

    #for incompressibility
    def solve(self, overrelaxation):
        if self.isAir:
            return 0

        openEdges = self.edge_bottom.openEdge + self.edge_top.openEdge + self.edge_left.openEdge + self.edge_right.openEdge
        divergence = overrelaxation * (self.edge_right.velocity - self.edge_left.velocity + self.edge_top.velocity - self.edge_bottom.velocity)# - stiffness * (self.density - averageDensity)
        splitDivergence = divergence/openEdges

        self.edge_right.velocity -= splitDivergence * self.edge_right.openEdge
        self.edge_left.velocity += splitDivergence * self.edge_left.openEdge
        self.edge_top.velocity -= splitDivergence * self.edge_top.openEdge
        self.edge_bottom.velocity += splitDivergence * self.edge_bottom.openEdge
        
        return self.edge_right.velocity - self.edge_left.velocity + self.edge_top.velocity - self.edge_bottom.velocity

class Edge:
    def __init__(self):
        self.reset()
        self.openEdge = 1

    def reset(self):
        self.velocity = 0
        self.weight = 0
    
    def draw(self, x, y, scale, cellSize, xDir, yDir, color, size):
        pygame.draw.line(screen, color, (x * cellSize * scale, y * cellSize * scale), (x * cellSize * scale + xDir * self.velocity * scale, y * cellSize * scale + yDir * self.velocity * scale), size)


class Grid:
    def __init__(self, cellSize, height, width):
        self.cellSize = cellSize

        #create edges, horizontal/vertical is based on the actual edge (not the velocity)
        self.verticalEdges = [[Edge() for _ in range(width + 1)] for _ in range(height + 1)] #h
        self.horizontalEdges = [[Edge() for _ in range(width + 1)] for _ in range(height + 1)]

        for y in range(len(self.horizontalEdges)):
            for x in range(len(self.horizontalEdges[0])):
                self.horizontalEdges[y][x].openEdge = 0 if x == 0 or x == width else 1

        for y in range(len(self.verticalEdges)):
            for x in range(len(self.verticalEdges[0])):
                self.verticalEdges[y][x].openEdge = 0 if y == 0 or y == height else 1
        
        #create cells
        self.cells = []
        for x in range(height):
            self.cells.append([])
            for y in range(width):
                self.cells[x].append(Cell(x, y, self))
    
    def draw(self, scale, drawEdges):
        mouseX, mouseY = pygame.mouse.get_pos()
        cellX = math.floor(mouseX/scale/self.cellSize)
        cellY = math.floor(mouseY/scale/self.cellSize)
        highlightedCell = self.cells[cellX][cellY]

        for x in range(len(self.cells)):
            for y in range(len(self.cells[0])):
                rect = pygame.Rect(x * self.cellSize * scale, y * self.cellSize * scale, self.cellSize * scale, self.cellSize * scale)
                
                #if self.cells[x][y].isAir:
                pygame.draw.rect(screen, (66, 0, 0), rect, 1)
                #else:
                #    pygame.draw.rect(screen, pygame.Color(0, 0, 255, a=100), rect)


        if drawEdges:
            #vertical
            for x in range(len(self.verticalEdges)):
                for y in range(len(self.verticalEdges[0])):
                    edge = self.verticalEdges[x][y]
                    if edge.openEdge == 0:
                        pygame.draw.circle(screen, (255, 0, 0), (x * cellSize * scale, (y + .5) * cellSize * scale), 3 * scale)
                    elif edge in [highlightedCell.edge_right, highlightedCell.edge_left]:
                        edge.draw(x, y + .5, scale, cellSize, 1, 0, (0, 255, 0), 2)
                    else:
                        edge.draw(x, y + .5, scale, cellSize, 1, 0, (0, 0, 0), 1)
            
            #horizontal
            for x in range(len(self.horizontalEdges)):
                for y in range(len(self.horizontalEdges[0])):
                    edge = self.horizontalEdges[x][y]
                    if edge.openEdge == 0:
                        pygame.draw.circle(screen, (255, 0, 0), ((x + .5) * cellSize * scale, y * cellSize * scale), 3 * scale)
                    elif edge in [highlightedCell.edge_top, highlightedCell.edge_bottom]: 
                        edge.draw(x + .5, y, scale, cellSize, 0, 1, (0, 255, 0), 2)
                    else:
                        edge.draw(x + .5, y, scale, cellSize, 0, 1, (0, 0, 0), 1)


def particlesToGrid():
    for cell_row in grid.cells:
        for cell in cell_row:
            cell.reset()

    for edge_row in grid.verticalEdges:
        for edge in edge_row:
            edge.reset()
    
    for edge_row in grid.horizontalEdges:
        for edge in edge_row:
            edge.reset()

    for particle in particles:
        cellX = math.floor(particle.xPos/grid.cellSize)
        cellY = math.floor(particle.yPos/grid.cellSize)
        
        cell = grid.cells[cellX][cellY]
        cell.addParticle(particle)


def solveGrid(maxIterations, maxDivergence, overrelaxation): #make in/out flow 0 (because it is roughly incompressible)
    #loop through all cells
    i = 0
    divergence = maxDivergence + 1
    while divergence > maxDivergence and i <= maxIterations:
        i += 1
        divergence = 0
        for cell_row in grid.cells:
            for cell in cell_row:
                newDivergence = cell.solve(overrelaxation)

                if newDivergence > divergence:
                    divergence = newDivergence
    #print(f"{i}/{maxIterations}")


def updateDensity():
    for cell_row in grid.cells:
        for cell in cell_row:
            cell.updateDensity()


def gridToParticles():
    for edge_row in grid.verticalEdges:
        for edge in edge_row:
            if edge.weight != 0:
                edge.velocity /= edge.weight

    for edge_row in grid.horizontalEdges:
        for edge in edge_row:
            if edge.weight != 0:
                edge.velocity /= edge.weight

    #loop through cells
    for cell_row in grid.cells:
        for cell in cell_row:
            cell.updateParticles()


def drawParticles(scale):
    for particle in particles:
        particle.draw(scale, (0, 0, 255))


def drawInfo():
    #fps
    fps = "FPS: " + ("9999" if dt == 0 else str(round(1/dt)))
    textToScreen(fps, (0, 0, 0), (1, 1))


def addVelocity(xVel, yVel):
    for particle in particles:
        particle.addVel(xVel, yVel)


def moveParticles(dt):
    for particle in particles:
        particle.move(dt)


def seperateParticles(maxIterations):
    for i in range(maxIterations):
        for particle_1 in particles:
            for particle_2 in particles:
                seperateTwoParticles(particle_1, particle_2)

def seperateTwoParticles(particle_1, particle_2):
    if particle_1 == particle_2:
        return

    dx = particle_2.xPos - particle_1.xPos
    dy = particle_2.yPos - particle_1.yPos

    distance = math.sqrt(dx**2 + dy**2)
    if distance < particleRadius - particleRadius * .05: #is overlaping
        overlap = particleRadius - distance
        
        # Calculate the direction in which to move the circles
        angle = math.atan2(dy, dx)
        
        # Move the circles away from each other
        move_x = overlap * math.cos(angle) / 2
        move_y = overlap * math.sin(angle) / 2
        
        particle_1.xPos -= move_x
        particle_1.yPos -= move_y
        particle_2.xPos += move_x
        particle_2.yPos += move_y


#info
gravity = 50
gridWidth = 50
gridHeight = 35
cellSize = 20
particleCount = 500
particleRadius = 5
#seperationGridCellSize = particleRadius * 2
#seperationGridXCount = 
gridItterations = 1
maxDivergence = .00001
maxParticleItterations = 5
overrelaxation = 1
particleMinDistance = particleRadius*2
scale = 1.3 #for visuals

#particle bounds
maxX = gridWidth * cellSize - .01
maxY = gridHeight * cellSize - .01

dt = 0
lastFrameTime = time.time()


#start display
pygame.init()
screenWidth = gridWidth * cellSize * scale
screenHeight = gridHeight * cellSize * scale
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("PIC Fluid simulation")
font = pygame.font.Font(None, 36)

#initialize data
particles = []
for i in range(particleCount):
    particles.append(Particle(cellSize * gridWidth, cellSize * gridHeight))


grid = Grid(cellSize, gridWidth, gridHeight)

clock = pygame.time.Clock()

#simulation loop
while True:
    #check interaction events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    #get dt (for frame independance)
    dt = time.time() - lastFrameTime
    lastFrameTime = time.time()

    ### particle stuff:
    #apply gravity
    mouseX, mouseY = pygame.mouse.get_pos()
    #particles[0].xPos = mouseX/scale
    #particles[0].yPos = mouseY/scale
    addVelocity(0, gravity * dt)

    #move particles 
    moveParticles(dt)
    #seperate particles
    seperateParticles(maxParticleItterations)
    #push out of obstacles
    #pushParticlesOutOfObstacles()

    ### grid stuff:
    # particles to grid
    particlesToGrid()
    #to push particles apart
    updateDensity()
    # make incompressible
    solveGrid(gridItterations, maxDivergence, overrelaxation)
    # grid to particles
    gridToParticles()



    ### visuals:
    screen.fill((100, 100, 100))
    #grid.draw(scale, True)
    drawParticles(scale)
    drawInfo()

    #update screen
    pygame.display.flip()

    clock.tick(30)