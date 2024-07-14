import pygame
import random
#import math

def textToScreen(text, color, position):
    screen.blit(font.render(text, True, color), position)

pygame.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Testing")
font = pygame.font.Font(None, 36)

def clamp(value, minValue, maxValue):
    return max(min(value, maxValue), minValue)

class Edge():
    def __init__(self, velocity = None):
        self.velocity = random.random() * 100 if velocity is None else velocity
    
    def draw(self, x, y, radius, xDir, yDir):
        screenPos = (x * scale + 100, y * scale + 100)
        endScreenPos = (x * scale + 100 + self.velocity * xDir, y * scale + 100 + self.velocity * yDir)

        pygame.draw.circle(screen, (0, 0, 0), screenPos, radius)
        pygame.draw.line(screen, (0, 0, 0), screenPos, endScreenPos)   

class Particle():
    def __init__(self, xVel = None, yVel = None, xPos = None, yPos = None):
        self.xVel = xVel if xVel is not None else random.random() * 100
        self.yVel = yVel if yVel is not None else random.random() * 100
        self.xPos = xPos if xPos is not None else random.random()
        self.yPos = yPos if yPos is not None else random.random()

    def draw(self, radius):
        screenPos = (self.xPos * scale + 100, self.yPos * scale + 100)
        endScreenPos = (self.xPos * scale + 100 + self.xVel, self.yPos * scale + 100 + self.yVel)

        pygame.draw.circle(screen, (0, 0, 255), screenPos, radius)
        pygame.draw.line(screen, (0, 0, 255), screenPos, endScreenPos)

class Corner():
    def __init__(self):
        self.xVel = 0
        self.yVel = 0

    def draw(self, x, y, radius):
        screenPos = (x * scale + 100, y * scale + 100)
        endScreenPos = (x * scale + 100 + self.xVel, y * scale + 100 + self.yVel)

        pygame.draw.circle(screen, (0, 255, 0), screenPos, radius)
        pygame.draw.line(screen, (0, 255, 0), screenPos, endScreenPos)   
    

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
    left.draw(0, .5, 5, 1, 0,)
    right.draw(1, .5, 5, 1, 0)
    top.draw(.5, 0, 5, 0, -1)
    bottom.draw(.5, 1, 5, 0, -1)

    top_left.draw(0, 0, 5)
    top_right.draw(1, 0, 5)
    bottom_left.draw(0, 1, 5)
    bottom_right.draw(1, 1, 5)

    particle.draw(5)
    pygame.display.flip()
    waitForPress()

def solveGrid():
    #solve grid
    openEdges = 4
    divergence = (right.velocity - left.velocity + top.velocity - bottom.velocity)
    splitDivergence = divergence/openEdges

    right.velocity -= splitDivergence
    left.velocity += splitDivergence
    top.velocity -= splitDivergence
    bottom.velocity += splitDivergence

def getWeights(particle):
    top_left_weight = (1 - particle.xPos) * particle.yPos
    top_right_weight = particle.xPos * particle.yPos
    bottom_left_weight = (1 - particle.xPos) * (1 - particle.yPos)
    bottom_right_weight = particle.xPos * (1 - particle.yPos)

    return top_left_weight, top_right_weight, bottom_left_weight, bottom_right_weight

def to_grid(particle):
    """Transfer particle velocities to grid velocities (PIC)"""

    # Reset the velocity grids and delta arrays
    u = 0
    v = 0
    
    tx = particle.xPos
    ty = particle.yPos

    weight_x0 = 1.0 - tx
    weight_y0 = 1.0 - ty

    weight0 = weight_x0 * weight_y0
    weight1 = tx * weight_y0
    weight2 = tx * ty
    weight3 = weight_x0 * ty

    index0 = cell_x0 * num_cells_y + cell_y0
    index1 = cell_x1 * num_cells_y + cell_y0
    index2 = cell_x1 * num_cells_y + cell_y1
    index3 = cell_x0 * num_cells_y + cell_y1

    # Transfer particle velocities to grid velocities
    particle_velocity = particle_vel[2 * i + component]
    velocity_field[index0] += particle_velocity * weight0
    delta_velocity[index0] += weight0
    velocity_field[index1] += particle_velocity * weight1
    delta_velocity[index1] += weight1
    velocity_field[index2] += particle_velocity * weight2
    delta_velocity[index2] += weight2
    velocity_field[index3] += particle_velocity * weight3
    delta_velocity[index3] += weight3

    # Normalize the grid velocities by the accumulated weights
    for i in range(len(velocity_field)):
        if delta_velocity[i] > 0.0:
            velocity_field[i] /= delta_velocity[i]

    # Restore velocities in solid cells to zero
    for i in range(num_cells_x):
        for j in range(num_cells_y):
            is_solid = cell_type[i * num_cells_y + j] == SOLID_CELL
            if is_solid or (i > 0 and cell_type[(i - 1) * num_cells_y + j] == SOLID_CELL):
                u[i * num_cells_y + j] = 0
            if is_solid or (j > 0 and cell_type[i * num_cells_y + j - 1] == SOLID_CELL):
                v[i * num_cells_y + j] = 0

def particleToGrid():
    #particle to corners
    top_left_weight, top_right_weight, bottom_left_weight, bottom_right_weight = getWeights(particle)
    
    top_left.xVel = particle.xVel * top_left_weight
    top_right.xVel = particle.xVel * top_right_weight
    bottom_left.xVel = particle.xVel * bottom_left_weight
    bottom_right.xVel = particle.xVel * bottom_right_weight

    top_left.yVel = particle.yVel * top_left_weight
    top_right.yVel = particle.yVel * top_right_weight
    bottom_left.yVel = particle.yVel * bottom_left_weight
    bottom_right.yVel = particle.yVel * bottom_right_weight

    #corners to edges
    top.velocity = (top_left.yVel + top_right.yVel) / 2
    right.velocity = (top_right.xVel + bottom_right.xVel) / 2
    left.velocity = (top_left.xVel + bottom_left.xVel) / 2
    bottom.velocity = (bottom_left.yVel + bottom_right.yVel) / 2

def gridToParticle():
    #edges to corners
    top.velocity = (top_left.yVel + top_right.yVel) / 2
    right.velocity = (top_right.xVel + bottom_right.xVel) / 2
    left.velocity = (top_left.xVel + bottom_left.xVel) / 2
    bottom.velocity = (bottom_left.yVel + bottom_right.yVel) / 2

    #corners to particles
    top_left_weight, top_right_weight, bottom_left_weight, bottom_right_weight = getWeights(particle)

    top_left.xVel = particle.xVel * top_left_weight
    top_right.xVel = particle.xVel * top_right_weight
    bottom_left.xVel = particle.xVel * bottom_left_weight
    bottom_right.xVel = particle.xVel * bottom_right_weight

    top_left.yVel = particle.yVel * top_left_weight
    top_right.yVel = particle.yVel * top_right_weight
    bottom_left.yVel = particle.yVel * bottom_left_weight
    bottom_right.yVel = particle.yVel * bottom_right_weight




#initialize
scale = 300 #only visual
left = Edge(0)
right = Edge(0)
top = Edge(0)
bottom = Edge(0)

top_left = Corner()
top_right = Corner()
bottom_left = Corner()
bottom_right = Corner()

particle = Particle()

#show
drawAll()

particleToGrid()

drawAll()

solveGrid()

drawAll()

gridToParticle()

drawAll()

exit()