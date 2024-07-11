import pygame
import time
import math

def textToScreen(text, color, position):
    screen.blit(font.render(text, True, color), position)


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
        self.xVel = 7
        self.yVel = 7
        self.isAir = False
    
    def draw(self, x, y, scale, cellSize, color, size):
        pygame.draw.circle(screen, color, (x * cellSize * scale, y * cellSize * scale), size * 3)
        pygame.draw.line(screen, color, (x * cellSize * scale, y * cellSize * scale), (x * cellSize * scale + self.xVel * scale, y * cellSize * scale + self.yVel * scale), size)


#references to other data (like corners  or edges)
class Cell:
    def __init__(self, x, y, grid):
        self.edge_top = grid.horizontalEdges[x][y]
        self.edge_bottom = grid.horizontalEdges[x][y + 1]
        self.edge_left = grid.verticalEdges[x][y]
        self.edge_right = grid.verticalEdges[x + 1][y]

        self.corner_top_left = grid.corners[x][y]
        self.corner_top_right = grid.corners[x + 1][y]
        self.corner_bottom_left = grid.corners[x][y + 1]
        self.corner_bottom_right = grid.corners[x + 1][y + 1]
        
        #self.corners = [grid.corners[x][y], grid.corners[x][y - 1], grid.corners[x - 1][y], grid.corners[x - 1][y - 1]]
        #self.edges = [grid.verticalEdges[x][y], grid.edges[x][y - 1], grid.edges[x - 1][y], grid.edges[x - 1][y - 1]]
        pass

#for solving for incompressibility once in grid form
class Edge:
    def __init__(self):
        self.velocity = 10
    
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

        print(str(len(self.horizontalEdges)) + ", " + str(len(self.horizontalEdges[0])))

        #create cells
        self.cells = []
        for x in range(width):
            self.cells.append([])
            for y in range(height):
                self.cells[x].append(Cell(x, y, self))
    
    def draw(self, scale, drawCorners, drawEdges):
        mouseX, mouseY = pygame.mouse.get_pos()
        cellX = math.floor(mouseX/scale/self.cellSize)
        cellY = math.floor(mouseY/scale/self.cellSize)
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


def particlesToGrid(gridWidth, gridHeight):
    grid = [[None] * gridWidth] * gridHeight
    for particle in particles:
        cellX = math.floor(particle.xPos/gridWidth)
        cellY = math.floor(particle.yPos/gridHeight)
        
        if grid[cellX][cellY] is not None:
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
            if cell is not None:

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
            if cell is not None:
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
    fps = "FPS: " + ("9999" if dt == 0 else str(round(1/dt)))
    textToScreen(fps, (0, 0, 0), (1, 1))


def addVelocity(xVel, yVel):
    for particle in particles:
        particle.addVel(xVel, yVel)


def moveParticles(dt):
    for particle in particles:
        particle.move(dt)


#info
gravity = 700
gridWidth = 5
gridHeight = 5
cellSize = 50
scale = 4 #for visuals
dt = 0
lastFrameTime = time.time()

particleSize = 5
#particles = createParticles(0.1, screenWidth, screenHeight, particleSize)

grid = Grid(cellSize, gridWidth, gridHeight)

#start display
pygame.init()
screenWidth = gridWidth * cellSize * scale
screenHeight = gridHeight * cellSize * scale
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("FLIP + PIC Fluid simulation")
font = pygame.font.Font(None, 36)

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
    #addVelocity(0, gravity * dt)
    #move particles 
    #moveParticles(dt)
    #seperate particles
    #seperateParticles()
    #push out of obstacles
    #pushParticlesOutOfObstacles()

    ### grid stuff:
    # particles to grid
    #grid = particlesToGrid(gridWidth, gridHeight)
    # make incompressible
    #solveGrid()
    # grid to particles
    #particles = gridToParticles()


    ### visuals:
    screen.fill((255, 255, 255))
    grid.draw(scale, True, True)
    #drawParticles(3)
    drawInfo()

    #update screen
    pygame.display.flip()