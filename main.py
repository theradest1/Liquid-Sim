import pygame
import time
import math

from sympy import false


class Particle:
    def __init__(self, x, y):
        self.xPos = x
        self.yPos = y
        self.xVel = 0
        self.yVel = 0

        #in the positions of the quadrants
        #weights for how much cell corners are influenced by particles
        self.w1 = 0
        self.w2 = 0
        self.w3 = 0
        self.w4 = 0
    
    def addVel(self, xVel, yVel):
        self.xVel += xVel
        self.yVel += yVel
    
    def move(self, dt):
        self.xPos += self.xVel * dt
        self.yPos += self.yVel * dt


#mainly used for particle -> grid -> particle
class Corner:
    def __init__(self):
        self.xVel = 0
        self.yVel = 0
        self.isAir = False


#references to other data (like corners  or edges)
class Cell:
    def __init__(self, column, row, grid):
        #get corners
        #get edges
        pass


#for solving for incompressibility once in grid form
class Edge:
    def __init__(self):
        self.velocity = 0


class Grid:
    def __init__(self, cellSize, height, width):
        #create corners
        

        #create edges, horizontal/vertical is based on the actual edge (not the velocity)
        self.verticleEdges = [[Edge()] * (width + 1)] * height
        self.horizontalEdges = [[Edge()] * width] * (height + 1)

        self.edges = self.verticleEdges
        self.edges.extend(self.horizontalEdges)


        #create cells
        self.cells = []
        for column in range(width):
            self.cells.append([])
            for row in range(height):
                self.cells[column].append(Cell(column, row, self))



def particlesToGrid(gridWidth, gridHeight):
    grid = [[None] * gridWidth] * gridHeight
    for particle in particles:
        cellX = math.floor(particle.xPos/gridWidth)
        cellY = math.floor(particle.yPos/gridHeight)
        
        if grid[cellX][cellY] != None:
            grid[cellX][cellY].addParticle(particle)
        else:
            grid[cellX][cellY] = Cell(particle)
    return grid


def solveGrid(): #make in/out flow 0 (because it is roughly incompressible)
    #loop through all cells
    for cellX in range(len(grid)):
        for cellY in range(len(grid[0])):
            cell = grid[cellX][cellY]

            #if cell has particles
            if cell != None:

                #get divergence (flow)
                #divergence = (grid[cellX + 1][cellY].xVel - grid[cellX][cellY].xVel) + (grid[cellX][cellY + 1].yVel - grid[cellX][cellY].yVel)


                #sides = 4
                #if cellX == 0 or cellX == len(grid) - 1:
                #    sides -= 1
                pass


def gridToParticles():
    particles = []
    for cellX in range(len(grid)):
        for cellY in range(len(grid[0])):
            cell = grid[cellX][cellY]
            if cell != None:
                particles.extend(cell.particles)
    return particles


def createParticles(density, width, height, offset):
    particles = []
    for i in range(int(width*density)):
        for j in range(int(height*density)):
            particles.append(Particle(i / density + offset, j / density + offset))

    return particles


def drawParticles(size):
    for particle in particles:
        pygame.draw.circle(screen, (0, 0, 255), (particle.xPos, particle.yPos), size)


def drawInfo():
    #fps
    fps = "∞" if dt == 0 else str(1/dt)
    fps_text = font.render(f"FPS: {fps}", True, (255, 0, 0))
    screen.blit(fps_text, (10, 10))


def addVelocity(xVel, yVel):
    for particle in particles:
        particle.addVel(xVel, yVel)


def moveParticles(dt):
    for particle in particles:
        particle.move(dt)


#start display
pygame.init()
screenWidth = 500
screenHeight = 500
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("FLIP + PIC Fluid simulation")
font = pygame.font.Font(None, 36)

#info
gravity = 700
gridWidth = 50
gridHeight = 50
dt = 0
lastFrameTime = time.time()

particleSize = 5
particles = createParticles(0.1, screenWidth, screenHeight, particleSize)

#loop
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
    addVelocity(0, gravity * dt)
    #move particles 
    moveParticles(dt)
    #seperate particles
    #seperateParticles()
    #push out of obstacles
    #pushParticlesOutOfObstacles()

    ### grid stuff:
    # particles to grid
    grid = particlesToGrid(gridWidth, gridHeight)
    # make incompressible
    solveGrid()
    # grid to particles
    particles = gridToParticles()


    ### visuals:
    screen.fill((255, 255, 255))
    drawParticles(3)
    drawInfo()

    #update screen
    pygame.display.flip()