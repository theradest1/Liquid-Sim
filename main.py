import pygame
import time

rows = 100
columns = 100
scale = 5

def printGrid(screen = None):
    global grid, rows, columns

    if screen == None:
        for row in range(rows):
            rowString = ""
            for column in range(columns):
                rowString += f" {grid[column][row]:.3f}"
            print(rowString)
    else:
        #clear
        screen.fill((255, 255, 255))

        #print each point
        for row in range(rows):
            for column in range(columns):
                color = getColor(grid[column][row])
                pygame.draw.rect(screen, color, (column * scale, row * scale, scale, scale))

def clamp(value, minValue, maxValue):
    return max(min(value, maxValue), minValue)

def getColor(value):
    num = clamp(int(value * 255), 0, 255)
    return (num, num, num)

#creates empty grid
def createGrid(rows, columns):
    grid = []
    for column in range(columns):
        grid.append([])
        for row in range(rows):
            grid[column].append(0)
    return grid

#bernoulli's principle (high pressure -> low pressure areas)
def disperse(multiplier):
    for column in range(columns):
        for row in range(rows):
            originalPressure = grid[column][row]
            dispersedPressure = originalPressure * multiplier
            newPressure =  originalPressure - dispersedPressure
            dispersedPressure /= 4
            
            if column + 1 < len(grid) and grid[column + 1][row] < 1:
                grid[column + 1][row] += dispersedPressure
            else:
                newPressure += dispersedPressure
            
            if column - 1 >= 0 and grid[column - 1][row] < 1:
                grid[column - 1][row] += dispersedPressure
            else:
                newPressure += dispersedPressure
            
            if row + 1 < len(grid[0]) and grid[column][row + 1] < 1:
                grid[column][row + 1] += dispersedPressure
            else:
                newPressure += dispersedPressure
            
            if row - 1 >= 0 and grid[column][row - 1] < 1:
                grid[column][row - 1] += dispersedPressure
            else:
                newPressure += dispersedPressure
            
            grid[column][row] = newPressure


#move fluid down
def applyGravity(multiplier):
    for column in range(columns):
        for row in range(rows):
            if row + 1 < len(grid[0]) and grid[column][row + 1] < 1:
                dispersedPressure = grid[column][row] * multiplier
                grid[column][row] -= dispersedPressure
                grid[column][row + 1] += dispersedPressure
        

#start display
pygame.init()
screen = pygame.display.set_mode((rows * scale, columns * scale))
pygame.display.set_caption("Fluid simulation")

#info
grid = createGrid(rows, columns)
gravity = 20
speed = 3
dt = 0
frames = 0
lastFrameTime = time.time()

#loop
while True:
    #check interaction events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    dt = time.time() - lastFrameTime
    lastFrameTime = time.time()
    print(dt)

    #grid[int(columns/2)][int(rows/2)] = 1
    grid[10][int(10)] = 1
    
    disperse(speed * dt)
    applyGravity(gravity * dt)

    printGrid(screen)
    frames += 1
    #printGrid()

    pygame.display.flip()