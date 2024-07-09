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
        recalculateColors()

        #print each point
        for row in range(rows):
            for column in range(columns):
                color = getColor(grid[column][row])
                pygame.draw.rect(screen, color, (column * scale, row * scale, scale, scale))

def clamp(value, minValue, maxValue):
    return max(min(value, maxValue), minValue)

def getColor(value):
    percent = value/maxPressure
    num = int(percent * 255)
    return (num, num, num)

def recalculateColors():
    global maxPressure, grid

    maxPressure = grid[0][0]
    for column in range(columns):
            for row in range(rows):
                if grid[column][row] > maxPressure:
                    maxPressure = grid[column][row]

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
            
            if column + 1 < len(grid):
                grid[column + 1][row] += dispersedPressure
            else:
                newPressure += dispersedPressure
            
            if column - 1 >= 0:
                grid[column - 1][row] += dispersedPressure
            else:
                newPressure += dispersedPressure
            
            if row + 1 < len(grid[0]):
                grid[column][row + 1] += dispersedPressure
            else:
                newPressure += dispersedPressure
            
            if row - 1 >= 0:
                grid[column][row - 1] += dispersedPressure
            else:
                newPressure += dispersedPressure
            
            grid[column][row] = newPressure


#move fluid down
def applyGravity(multiplier):
    for column in range(columns):
        for row in range(rows):
            if row + 1 < len(grid[0]):
                dispersedPressure = grid[column][row] * multiplier
                grid[column][row] -= dispersedPressure
                grid[column][row + 1] += dispersedPressure


def text_to_screen(screen, text, x, y, size=50, color=(200, 000, 000), font_type=pygame.font.get_default_font()):
	text = str(text)
	font = pygame.font.Font(font_type, size)
	text = font.render(text, True, color)
	screen.blit(text, (x, y))


#start display
pygame.init()
screen = pygame.display.set_mode((rows * scale, columns * scale))
pygame.display.set_caption("Fluid simulation")

#info
grid = createGrid(rows, columns)
gravity = 30
speed = 30
dt = 0
maxPressure = 0 #not a limit, this is for coloring
lastFrameTime = time.time()
font = pygame.font.Font(None, 36)

#loop
while True:
    #check interaction events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    #grid[int(columns/2)][int(rows/2)] = 1
    grid[10][int(10)] += 1
    
    disperse(speed * dt)
    applyGravity(gravity * dt)

    printGrid(screen)

    dt = time.time() - lastFrameTime
    lastFrameTime = time.time()
    fps_text = font.render(f"FPS: {int(1/dt)}", True, (255, 0, 0))
    screen.blit(fps_text, (10, 10))
    #printGrid()

    pygame.display.flip()