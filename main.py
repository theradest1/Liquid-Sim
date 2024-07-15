import pygame
import time
import math
import random
import numpy as np

def textToScreen(text, color, position):
    screen.blit(font.render(text, True, color), position)

def waitForInteraction():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
            elif event.type == pygame.KEYDOWN:
                return

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
        pygame.draw.circle(screen, color, (self.xPos * scale + screenPadding, self.yPos * scale + screenPadding), scale * particleRadius)
        

#references to other data (like corners  or edges)
class Cell:
    def __init__(self, x, y, grid):
        self.xPos = x
        self.yPos = y

        self.edge_top = grid.horizontalEdges[y][x]
        self.edge_bottom = grid.horizontalEdges[y + 1][x]
        self.edge_left = grid.verticalEdges[y][x]
        self.edge_right = grid.verticalEdges[y][x + 1]

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

        #get weights
        particle.weight_left = 1 - remainderX/cellSize
        particle.weight_right = remainderX/cellSize
        particle.weight_top = 1 - remainderY/cellSize
        particle.weight_bottom = remainderY/cellSize

        #give edge velocity
        self.edge_left.velocity += particle.xVel * particle.weight_left * self.edge_left.openEdge
        self.edge_right.velocity += particle.xVel * particle.weight_right * self.edge_right.openEdge
        self.edge_top.velocity += particle.yVel * particle.weight_top * self.edge_top.openEdge
        self.edge_bottom.velocity += particle.yVel * particle.weight_bottom * self.edge_bottom.openEdge

        #give edge weights
        self.edge_left.weight += particle.weight_left
        self.edge_right.weight += particle.weight_right
        self.edge_top.weight += particle.weight_top
        self.edge_bottom.weight += particle.weight_bottom

        self.particles.append(particle)

    def updateDensity(self):
        if self.isAir:
            self.density = 0
            return
        
        self.density = self.edge_right.weight + self.edge_left.weight + self.edge_top.weight + self.edge_bottom.weight
        #print(self.density)
    
    def updateParticles(self):
        for particle in self.particles:
            particle.xVel = (self.edge_left.velocity * particle.weight_left + self.edge_right.velocity * particle.weight_right) / (particle.weight_right + particle.weight_left)
            particle.yVel = (self.edge_top.velocity * particle.weight_top + self.edge_bottom.velocity * particle.weight_bottom) / (particle.weight_top + particle.weight_bottom)

    #for incompressibility
    def solve(self, overrelaxation):
        #get how many edges can be changed
        openEdges = self.edge_bottom.openEdge + self.edge_top.openEdge + self.edge_left.openEdge + self.edge_right.openEdge
        
        #calculate pressure, pushes particles away from dense areas - helps the particle seperation
        pressureDivergence = stiffness * (self.density - averageDensity)
        pressureDivergence = clamp(pressureDivergence, 0, abs(pressureDivergence))
        
        #find the divergence - total fluid volume going out of cell
        divergence = overrelaxation * (-self.edge_right.velocity + self.edge_left.velocity + self.edge_top.velocity - self.edge_bottom.velocity) - pressureDivergence
        splitDivergence = divergence/openEdges

        #apply divergence
        self.edge_right.velocity += splitDivergence * self.edge_right.openEdge
        self.edge_left.velocity -= splitDivergence * self.edge_left.openEdge
        self.edge_top.velocity -= splitDivergence * self.edge_top.openEdge
        self.edge_bottom.velocity += splitDivergence * self.edge_bottom.openEdge
        
        #return new divergence for future use
        return self.edge_right.velocity - self.edge_left.velocity + self.edge_top.velocity - self.edge_bottom.velocity

class Edge:
    def __init__(self):
        self.openEdge = 1
        self.reset()

    def reset(self):
        if self.openEdge == 0:
            return

        self.velocity = 0
        self.weight = 0
    
    def draw(self, x, y, scale, cellSize, xDir, yDir, color, size):
        #find start and end position of velocity line
        startPos = (x * cellSize * scale + screenPadding, y * cellSize * scale + screenPadding)
        endPos = (x * cellSize * scale + xDir * self.velocity * scale + screenPadding, y * cellSize * scale + yDir * self.velocity * scale + screenPadding)
        
        #draw
        pygame.draw.line(screen, color, startPos, endPos, size)


class Grid:
    def __init__(self, cellSize, height, width):
        self.cellSize = cellSize

        #create edges, horizontal/vertical is based on the actual edge (not the velocity)
        self.verticalEdges = [[Edge() for _ in range(width + 1)] for _ in range(height)]
        self.horizontalEdges = [[Edge() for _ in range(width)] for _ in range(height + 1)]

        #make edges closed if on the bottom
        for y in range(len(self.horizontalEdges)):
            for x in range(len(self.horizontalEdges[0])):
                self.horizontalEdges[y][x].openEdge = 0 if y == height else 1

        #make edges closed if on the left or right
        for y in range(len(self.verticalEdges)):
            for x in range(len(self.verticalEdges[0])):
                self.verticalEdges[y][x].openEdge = 0 if x == 0 or x == width else 1
        
        #create cells
        self.cells = []
        for y in range(height):
            self.cells.append([])
            for x in range(width):
                self.cells[y].append(Cell(x, y, self))
    
    def draw(self, scale, draw_grid, draw_grid_colors, draw_edges, draw_edge_vels):
        if draw_grid:
            for y in range(len(self.cells)):
                for x in range(len(self.cells[0])):
                    #setup
                    rect = pygame.Rect(x * self.cellSize * scale + screenPadding, y * self.cellSize * scale + screenPadding, self.cellSize * scale, self.cellSize * scale)
                    
                    #draw blue if there are particles
                    if self.cells[y][x].isAir or not draw_grid_colors:
                        pygame.draw.rect(screen, (66, 0, 0), rect, 1)
                    else:
                        pygame.draw.rect(screen, (0, 0, 100), rect)


        if draw_edges:
            #vertical
            for y in range(len(self.verticalEdges)):
                for x in range(len(self.verticalEdges[0])):
                    edge = self.verticalEdges[y][x]
                    if edge.openEdge == 0:
                        pygame.draw.circle(screen, (255, 0, 0), (x * cellSize * scale, (y + .5) * cellSize * scale), 2 * scale)
                    elif draw_edge_vels:
                        edge.draw(x, y + .5, scale, cellSize, 1, 0, (0, 0, 0), 1)
            
            #horizontal
            for y in range(len(self.horizontalEdges)):
                for x in range(len(self.horizontalEdges[0])):
                    edge = self.horizontalEdges[y][x]
                    if edge.openEdge == 0:
                        pygame.draw.circle(screen, (255, 0, 0), ((x + .5) * cellSize * scale, y * cellSize * scale), 2 * scale)
                    elif draw_edge_vels:
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
        
        cell = grid.cells[cellY][cellX]
        cell.addParticle(particle)

#make in/out flow 0 (because it is roughly incompressible)
def solveGrid(maxIterations, overrelaxation):
    #loop through all cells
    for i in range(maxIterations):
        for cell_row in grid.cells:
            for cell in cell_row:
                #solve if it has particles
                if not cell.isAir:
                    cell.solve(overrelaxation)


def updateDensity():
    for cell_row in grid.cells:
        for cell in cell_row:
            if not cell.isAir:
                cell.updateDensity()


def gridToParticles():
    #take average of velocities
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
    spacing = 20

    #fps
    fps_string = "FPS: " + ("Infinite" if dt == 0 else str(round(1/dt)))
    textToScreen(fps_string, (0, 0, 0), (1, 1))

    #particles
    particles_string = "Particles: " + str(len(particles))
    textToScreen(particles_string, (0, 0, 0), (1, 1 * spacing))

    #seperation of particles
    seperation_string = "Comparisons: " + str(comparisons)
    textToScreen(seperation_string, (0, 0, 0), (1, 2 * spacing))


def addVelocity(xVel, yVel):
    for particle in particles:
        particle.addVel(xVel, yVel)


def moveParticles(dt):
    for particle in particles:
        particle.move(dt)

class seperationCell:
    def __init__(self):
        self.particleIndexes = []
        self.neighborIndexes = []

#this uses numpy arrays since they are significantly faster
def seperateParticles(maxIterations):
    global comparisons

    cellSize = particleRadius * 2
    gridWidth = math.ceil(screenWidth/scale/cellSize)
    gridHeight = math.ceil(screenHeight/scale/cellSize)

    #cellCount = gridWidth * gridHeight

    cells = np.array([seperationCell() for _ in range(gridWidth * gridHeight)])
    for y in range(gridHeight):
        for x in range(gridWidth):
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    neighborY = y + dy
                    neighborX = x + dx
                    if neighborY >= 0 and neighborY < gridHeight and neighborX >= 0 and neighborX < gridHeight:
                        cells[y * gridWidth + x].neighborIndexes.append(neighborY * gridWidth + neighborX)

    #convert from particle class to arrays
    particle_xPos = np.empty(particleCount)
    particle_yPos = np.empty(particleCount)

    for index, particle in enumerate(particles):
        particle_xPos[index] = particle.xPos
        particle_yPos[index] = particle.yPos

    #seperate particles
    for i in range(maxIterations):
        #clear past particles
        for cell in cells:
            cell.particleIndexes = []

        #add particles to cells
        for particle_i in range(particleCount):
            cellX = math.floor(particle_xPos[particle_i]/cellSize)
            cellY = math.floor(particle_yPos[particle_i]/cellSize)
            cells[cellY * gridWidth + cellX].particleIndexes.append(particle_i)
        
        for cell_y in range(0, gridHeight):
            for cell_x in range(0, gridWidth):
                cell = cells[cell_y * gridWidth + cell_x]
                for particle_i_1 in cell.particleIndexes:
                    for surroundingCell_i in cell.neighborIndexes:
                        surroundingCell = cells[surroundingCell_i]
                        for particle_i_2 in surroundingCell.particleIndexes:
                            if particle_i_1 != particle_i_2:
                                comparisons += 1
                                particle_xPos[particle_i_1], particle_yPos[particle_i_1], particle_xPos[particle_i_2], particle_yPos[particle_i_2] = seperateTwoParticles(particle_xPos[particle_i_1], particle_yPos[particle_i_1], particle_xPos[particle_i_2], particle_yPos[particle_i_2])

    #convert back from numpy arrays to classes
    for index, particle in enumerate(particles):
        particle.xPos = particle_xPos[index]
        particle.yPos = particle_yPos[index]



def seperateTwoParticles(x_1, y_1, x_2, y_2):
    #get distance between particles
    dx = x_2 - x_1
    dy = y_2 - y_1
    distance = math.sqrt(dx**2 + dy**2)

    #if overlaping, move apart
    if distance < minParticleDistance: 
        #find distance to move
        overlap = minParticleDistance - distance
        
        #find direction to move
        angle = math.atan2(dy, dx)
        
        #find the vector to move (with the angle and distance)
        move_x = overlap * math.cos(angle) / 2
        move_y = overlap * math.sin(angle) / 2
        
        #move particles
        x_1 = clamp(x_1 - move_x, 0, maxX)
        y_1 = clamp(y_1 - move_y, 0, maxY)
        x_2 = clamp(x_2 + move_x, 0, maxX)
        y_2 = clamp(y_2 + move_y, 0, maxY)

    return x_1, y_1, x_2, y_2


### settings
#other
gravity = 75
stiffness = 0
averageDensity = 0
overrelaxation = 1.8

#visuals
scale = 3
maxFps = 0 #0 for no max
screenWidth = 1000
screenPadding = 3 * scale #should be the radius of the particles * scale
draw_particles = True
draw_grid = False
draw_grid_colors = False
draw_edges = False
draw_edge_vels = False
screenHeight = screenWidth #just leave this, its annoying

#particles
particleCount = 600
particleRadius = 3
maxParticleItterations = 3
minParticleDistance = particleRadius * 2
maxX = screenWidth/scale - .0001
maxY = screenHeight/scale - .0001

#grid
gridItterations = 3
targetCellSize = particleRadius * 3
gridWidth = math.floor(screenWidth/scale/targetCellSize)
gridHeight = math.floor(screenHeight/scale/targetCellSize)
cellSize = screenWidth/scale/gridWidth

#fix screen height to fit better (to be square)
difference = screenHeight - gridHeight * cellSize * scale
if difference != 0:
    screenHeight -= difference
    print("Screen height was adjusted to", screenHeight, "to fit cells better")

#initialize display
pygame.init()
screen = pygame.display.set_mode((screenWidth + screenPadding*2, screenHeight + screenPadding*2))
pygame.display.set_caption("PIC Fluid simulation")
font = pygame.font.Font(None, 36)

#initialize data
grid = Grid(cellSize, gridWidth, gridHeight)

particles = []
for i in range(particleCount):
    particles.append(Particle(cellSize * gridWidth/2, cellSize * gridHeight/2))

waitForInteraction()

#start time keeping stuffs
clock = pygame.time.Clock()
dt = 0
lastFrameTime = time.time()

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
    addVelocity(0, gravity * dt) #apply gravity
    moveParticles(dt)

    comparisons = 0
    seperateParticles(maxParticleItterations)

    #pushParticlesOutOfObstacles()


    ### grid stuff:
    particlesToGrid()
    updateDensity() #to push particles apart when in clumps
    solveGrid(gridItterations, overrelaxation) # make incompressible
    gridToParticles() # grid to particles

    ### visuals:
    screen.fill((100, 100, 100)) #clear

    #draw things
    grid.draw(scale, draw_grid, draw_grid_colors, draw_edges, draw_edge_vels)
    if draw_particles: 
        drawParticles(scale)
    
    drawInfo()

    #update screen
    pygame.display.flip()

    #lock to fps
    if maxFps != 0:
        clock.tick(maxFps)