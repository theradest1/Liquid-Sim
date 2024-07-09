import pygame
import time

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
        self.yPos += self.yVel * dt

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
    #grid = particlesToGrid()
    # make incompressible
    #solveGrid()
    # grid to particles
    #particles = gridToParticles()


    ### visuals:
    screen.fill((255, 255, 255))
    drawParticles(3)
    drawInfo()

    #update screen
    pygame.display.flip()