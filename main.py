import pygame
import time
import math

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
    def __init__(self, x, y):
        self.xPos = x
        self.yPos = y
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
        pygame.draw.circle(screen, color, (self.xPos * scale, self.yPos * scale), scale/2)
        

#mainly used for particle -> grid -> particle
class Corner:
    def __init__(self):
        self.reset()

    def reset(self):
        self.xVel = 0
        self.yVel = 0
    
    def draw(self, x, y, scale, cellSize, color, size):

        if self.xVel != 0 and self.yVel != 0:
            pygame.draw.circle(screen, color, (x * cellSize * scale, y * cellSize * scale), size * 3)
            
            xDiff, yDiff = normalize_tuple((self.xVel, self.yVel))
            pygame.draw.line(screen, color, (x * cellSize * scale, y * cellSize * scale), (x * cellSize * scale + xDiff * scale * 3, y * cellSize * scale + yDiff * scale * 3), size)
            #print(f"{self.xVel}, {self.yVel}")

#references to other data (like corners  or edges)
class Cell:
    def __init__(self, x, y, grid):
        self.xPos = x
        self.yPos = y

        self.edge_top = grid.horizontalEdges[x][y]
        self.edge_bottom = grid.horizontalEdges[x][y + 1]
        self.edge_left = grid.verticalEdges[x][y]
        self.edge_right = grid.verticalEdges[x + 1][y]

        self.corner_top_left = grid.corners[x][y]
        self.corner_top_right = grid.corners[x + 1][y]
        self.corner_bottom_left = grid.corners[x][y + 1]
        self.corner_bottom_right = grid.corners[x + 1][y + 1]

        self.reset()

    def reset(self):
        self.isAir = True
        self.particles = []
    
    def addParticle(self, particle):
        self.isAir = False

        remainderX = particle.xPos - self.xPos * cellSize
        remainderY = particle.yPos - self.yPos * cellSize

        particle.weight_top_left = (1 - remainderX/cellSize) * remainderY/cellSize
        particle.weight_top_right = remainderX/cellSize * remainderY/cellSize
        particle.weight_bottom_left = (1 - remainderX/cellSize) * (1 - remainderY/cellSize)
        particle.weight_bottom_right = remainderX/cellSize * (1 - remainderY/cellSize)

        self.corner_top_left.xVel += particle.xVel * particle.weight_top_left
        self.corner_top_right.xVel += particle.xVel * particle.weight_top_right
        self.corner_bottom_left.xVel += particle.xVel * particle.weight_bottom_left
        self.corner_bottom_right.xVel += particle.xVel * particle.weight_bottom_right

        self.corner_top_left.yVel += particle.yVel * particle.weight_top_left
        self.corner_top_right.yVel += particle.yVel * particle.weight_top_right
        self.corner_bottom_left.yVel += particle.yVel * particle.weight_bottom_left
        self.corner_bottom_right.yVel += particle.yVel * particle.weight_bottom_right
    
    def updateParticles(self):
        for particle in self.particles:
            #particle.xVel = 
            pass
    
    def updateEdgeValues():
        #get the edge values from the corners
        raise NotImplementedError

    def updateCornerValues():
        #get the corner values from the corners
        raise NotImplementedError


#for solving for incompressibility once in grid form
class Edge:
    def __init__(self):
        self.velocity = 0
    
    def draw(self, x, y, scale, cellSize, xDir, yDir, color, size):
        pygame.draw.line(screen, color, (x * cellSize * scale, y * cellSize * scale), (x * cellSize * scale + xDir * self.velocity * scale, y * cellSize * scale + yDir * self.velocity * scale), size)


class Grid:
    def __init__(self, cellSize, height, width):
        self.cellSize = cellSize

        #create corners
        self.corners = [[Corner() for _ in range(width + 1)] for _ in range(height + 1)]

        #create edges, horizontal/vertical is based on the actual edge (not the velocity)
        self.verticalEdges = [[Edge() for _ in range(width + 1)] for _ in range(height + 1)] #h
        self.horizontalEdges = [[Edge() for _ in range(width + 1)] for _ in range(height + 1)]

        #create cells
        self.cells = []
        for x in range(height):
            self.cells.append([])
            for y in range(width):
                self.cells[x].append(Cell(x, y, self))
    
    def draw(self, scale, drawCorners, drawEdges):
        mouseX, mouseY = pygame.mouse.get_pos()
        cellX = math.floor(mouseX/scale/self.cellSize)
        cellY = math.floor(mouseY/scale/self.cellSize)
        print(cellX)
        highlightedCell = self.cells[cellX][cellY]

        for x in range(len(self.cells)):
            for y in range(len(self.cells[0])):
                rect = pygame.Rect(x * self.cellSize * scale, y * self.cellSize * scale, self.cellSize * scale, self.cellSize * scale)
                pygame.draw.rect(screen, (255, 0, 0), rect, 1)

        if drawCorners:
            #pygame.draw.circle(screen, (0, 255, 0), (cell.xPos * self.cellSize * scale - self.cellSize * scale /2, cell.yPos * self.cellSize * scale - self.cellSize * scale /2), 4)
            for x in range(len(self.corners)):
                for y in range(len(self.corners[0])):
                    corner = self.corners[x][y]
                    if corner in [highlightedCell.corner_top_left, highlightedCell.corner_top_right, highlightedCell.corner_bottom_left, highlightedCell.corner_bottom_right]:
                        corner.draw(x, y, scale, cellSize, (0, 255, 0), 2)
                    else:
                        corner.draw(x, y, scale, cellSize, (0, 0, 0), 1)

        if drawEdges:
            #vertical
            for x in range(len(self.verticalEdges)):
                for y in range(len(self.verticalEdges[0])):
                    edge = self.verticalEdges[x][y]
                    if edge in [highlightedCell.edge_right, highlightedCell.edge_left]:
                        edge.draw(x, y + .5, scale, cellSize, 1, 0, (0, 255, 0), 2)
                    else:
                        edge.draw(x, y + .5, scale, cellSize, 1, 0, (0, 0, 0), 1)
            
            #horizontal edges
            for x in range(len(self.horizontalEdges)):
                for y in range(len(self.horizontalEdges[0])):
                    edge = self.horizontalEdges[x][y]
                    if edge in [highlightedCell.edge_top, highlightedCell.edge_bottom]: 
                        edge.draw(x + .5, y, scale, cellSize, 0, 1, (0, 255, 0), 2)
                    else:
                        edge.draw(x + .5, y, scale, cellSize, 0, 1, (0, 0, 0), 1)


def particlesToGrid():
    for corner_row in grid.corners:
        for corner in corner_row:
            corner.reset()

    for cell_row in grid.cells:
        for cell in cell_row:
            cell.reset()

    for particle in particles:
        cellX = math.floor(particle.xPos/grid.cellSize)
        cellY = math.floor(particle.yPos/grid.cellSize)
        
        #print(f"{cellX}, {cellY}")
        cell = grid.cells[cellX][cellY]
        cell.addParticle(particle)


def solveGrid(): #make in/out flow 0 (because it is roughly incompressible)
    #loop through all cells
    for cellX in range(len(grid)):
        for cellY in range(len(grid[0])):
            cell = grid[cellX][cellY]

            #if cell is not empty
            if not cell.isAir:
                raise NotImplementedError


def gridToParticles():
    #loop through cells
    for cell_row in grid.cells:
        for cell in cell_row:
            cell.updateParticles()


def createParticles(density, width, height, offset):
    particles = []
    for x in range(int(width*density)):
        for y in range(int(height*density)):
            particles.append(Particle(x / density + offset, y / density + offset))

    return particles


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


#info
gravity = 3
gridWidth = 5
gridHeight = 3
cellSize = 30
scale = 7 #for visuals

#particle bounds
maxX = gridWidth * cellSize - .05
maxY = gridHeight * cellSize - .05

dt = 0
lastFrameTime = time.time()


#start display
pygame.init()
screenWidth = gridWidth * cellSize * scale
screenHeight = gridHeight * cellSize * scale
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("FLIP + PIC Fluid simulation")
font = pygame.font.Font(None, 36)

#initialize data
#particles = createParticles(.5, gridWidth * cellSize * .5, gridHeight * cellSize * .5, 1)
particles = [Particle(gridWidth * cellSize / 2, gridWidth * cellSize / 2)]
grid = Grid(cellSize, gridWidth, gridHeight)

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
    #addVelocity(0, gravity * dt)
    #xGrav, yGrav = normalize_tuple((mouseX/scale - particles[0].xPos, mouseY/scale - particles[0].yPos))
    addVelocity((mouseX/scale - particles[0].xPos) * dt * gravity, (mouseY/scale - particles[0].yPos) * dt * gravity)

    #move particles 
    moveParticles(dt)
    #seperate particles
    #seperateParticles()
    #push out of obstacles
    #pushParticlesOutOfObstacles()

    ### grid stuff:
    # particles to grid
    particlesToGrid()
    # make incompressible
    #solveGrid()
    # grid to particles
    gridToParticles()


    ### visuals:
    screen.fill((100, 100, 100))
    grid.draw(scale, True, False)
    drawParticles(scale)
    drawInfo()
    #print(f"{particles[0].xPos}, {particles[0].yPos}")

    #update screen
    pygame.display.flip()