import pygame
import math

windowWidth = 1000
windowHeight = 500

pygame.init()
screen = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption("Testing-3")

simHeight = 3.0	
cScale = windowHeight / simHeight
simWidth = windowWidth / cScale

U_FIELD = 0
V_FIELD = 1

FLUID_CELL = 0
AIR_CELL = 1
SOLID_CELL = 2

cnt = 0

def clamp(value, minValue, maxValue):
    return max(min(value, maxValue), minValue)

def fillList(list, value = 0):
    return [value] * len(list)

# ----------------- start of simulator ------------------------------

class FlipFluid:
    def __init__(this, density, width, height, spacing, particleRadius, maxParticles):

        # fluid

        this.density = density
        this.fNumX = math.floor(width / spacing) + 1
        this.fNumY = math.floor(height / spacing) + 1
        this.h = max(width / this.fNumX, height / this.fNumY)
        this.fInvSpacing = 1.0 / this.h
        this.fNumCells = this.fNumX * this.fNumY

        this.u = [0] * this.fNumCells
        this.v = [0] * this.fNumCells
        this.du = [0] * this.fNumCells
        this.dv = [0] * this.fNumCells
        this.prevU = [0] * this.fNumCells
        this.prevV = [0] * this.fNumCells
        this.p = [0] * this.fNumCells
        this.s = [0] * this.fNumCells
        this.cellColor = [0] * (3 * this.fNumCells)

        this.cellType = [0] * this.fNumCells

        # particles

        this.maxParticles = maxParticles

        this.particlePos = [0] * (2 * this.maxParticles)
        this.particleColor = [0] * (3 * this.maxParticles)
        for i in range(this.maxParticles):
            this.particleColor[3 * i + 2] = 1.0

        this.particleVel = [0] * (2 * this.maxParticles)
        this.particleDensity = [0] * (this.fNumCells)
        this.particleRestDensity = 0.0

        this.particleRadius = particleRadius
        this.pInvSpacing = 1.0 / (2.2 * particleRadius)
        this.pNumX = math.floor(width * this.pInvSpacing) + 1
        this.pNumY = math.floor(height * this.pInvSpacing) + 1
        this.pNumCells = this.pNumX * this.pNumY

        this.numCellParticles = [0] * (this.pNumCells)
        this.firstCellParticle = [0] * (this.pNumCells + 1)
        this.cellParticleIds = [0] * (maxParticles)

        this.numParticles = 0

    def drawParticles(this):
        for i in range(this.numParticles):
            particleX = this.particlePos[2 * i] * windowWidth
            particleY = this.particlePos[2 * i + 1] * windowHeight
            pygame.draw.circle(screen, (0, 0, 0), (particleX, particleY), 3)

    def integrateParticles(this, dt, gravity):
        for i in range(this.numParticles):
            this.particleVel[2 * i + 1] += dt * gravity
            this.particlePos[2 * i] += this.particleVel[2 * i] * dt
            this.particlePos[2 * i + 1] += this.particleVel[2 * i + 1] * dt

    def pushParticlesApart(this, numIters):
        colorDiffusionCoeff = 0.001

        # count particles per cell

        this.numCellParticles = fillList(this.numCellParticles, 0)

        for i in range(this.numParticles):
            x = this.particlePos[2 * i]
            y = this.particlePos[2 * i + 1]

            xi = clamp(math.floor(x * this.pInvSpacing), 0, this.pNumX - 1)
            yi = clamp(math.floor(y * this.pInvSpacing), 0, this.pNumY - 1)
            cellNr = xi * this.pNumY + yi
            this.numCellParticles[cellNr] += 1

        # partial sums

        first = 0

        for i in range(this.pNumCells):
            first += this.numCellParticles[i]
            this.firstCellParticle[i] = first
        
        this.firstCellParticle[this.pNumCells] = first		# guard

        # fill particles into cells

        for i in range(this.numParticles):
            x = this.particlePos[2 * i]
            y = this.particlePos[2 * i + 1]

            xi = clamp(math.floor(x * this.pInvSpacing), 0, this.pNumX - 1)
            yi = clamp(math.floor(y * this.pInvSpacing), 0, this.pNumY - 1)
            cellNr = xi * this.pNumY + yi
            this.firstCellParticle[cellNr] -= 1
            this.cellParticleIds[this.firstCellParticle[cellNr]] = i

        # push particles apart

        minDist = 2.0 * this.particleRadius
        minDist2 = minDist * minDist

        for iter in range(numIters):
            for i in range(this.numParticles):
                px = this.particlePos[2 * i]
                py = this.particlePos[2 * i + 1]

                pxi = math.floor(px * this.pInvSpacing)
                pyi = math.floor(py * this.pInvSpacing)
                x0 = max(pxi - 1, 0)
                y0 = max(pyi - 1, 0)
                x1 = min(pxi + 1, this.pNumX - 1)
                y1 = min(pyi + 1, this.pNumY - 1)

                for xi in range(x0, x1 + 1):
                    for yi in range(y0, y1 + 1):
                        cellNr = xi * this.pNumY + yi
                        first = this.firstCellParticle[cellNr]
                        last = this.firstCellParticle[cellNr + 1]
                        for j in range(first, last):
                            id = this.cellParticleIds[j]
                            if (id == i):
                                continue
                            qx = this.particlePos[2 * id]
                            qy = this.particlePos[2 * id + 1]

                            dx = qx - px
                            dy = qy - py
                            d2 = dx * dx + dy * dy
                            if (d2 > minDist2 or d2 == 0.0):
                                continue
                            d = math.sqrt(d2)
                            s = 0.5 * (minDist - d) / d
                            dx *= s
                            dy *= s
                            this.particlePos[2 * i] -= dx
                            this.particlePos[2 * i + 1] -= dy
                            this.particlePos[2 * id] += dx
                            this.particlePos[2 * id + 1] += dy

                            # diffuse colors

                            for k in range(3):
                                color0 = this.particleColor[3 * i + k]
                                color1 = this.particleColor[3 * id + k]
                                color = (color0 + color1) * 0.5
                                this.particleColor[3 * i + k] = color0 + (color - color0) * colorDiffusionCoeff
                                this.particleColor[3 * id + k] = color1 + (color - color1) * colorDiffusionCoeff

    def handleParticleCollisions(this, obstacleX, obstacleY, obstacleRadius):
        h = 1.0 / this.fInvSpacing
        r = this.particleRadius
        _or = obstacleRadius
        minDist = obstacleRadius + r
        minDist2 = minDist * minDist

        minX = h + r
        maxX = (this.fNumX - 1) * h - r
        minY = h + r
        maxY = (this.fNumY - 1) * h - r


        for i in range(this.numParticles):
            x = this.particlePos[2 * i]
            y = this.particlePos[2 * i + 1]

            dx = x - obstacleX
            dy = y - obstacleY
            d2 = dx * dx + dy * dy

            # obstacle collision

            if (d2 < minDist2):

                # d = Math.sqrt(d2)
                # s = (minDist - d) / d
                # x += dx * s
                # y += dy * s

                this.particleVel[2 * i] = scene["obstacleVelX"]
                this.particleVel[2 * i + 1] = scene["obstacleVelY"]

            # wall collisions

            if (x < minX):
                x = minX
                this.particleVel[2 * i] = 0.0
            if (x > maxX):
                x = maxX
                this.particleVel[2 * i] = 0.0
            if (y < minY):
                y = minY
                this.particleVel[2 * i + 1] = 0.0
            if (y > maxY):
                y = maxY
                this.particleVel[2 * i + 1] = 0.0
            this.particlePos[2 * i] = x
            this.particlePos[2 * i + 1] = y

    def updateParticleDensity(this):
        n = this.fNumY
        h = this.h
        h1 = this.fInvSpacing
        h2 = 0.5 * h

        d = f.particleDensity

        d = fillList(d, 0)

        for i in range(this.numParticles):
            x = this.particlePos[2 * i]
            y = this.particlePos[2 * i + 1]

            x = clamp(x, h, (this.fNumX - 1) * h)
            y = clamp(y, h, (this.fNumY - 1) * h)

            x0 = math.floor((x - h2) * h1)
            tx = ((x - h2) - x0 * h) * h1
            x1 = min(x0 + 1, this.fNumX-2)
            
            y0 = math.floor((y-h2)*h1)
            ty = ((y - h2) - y0*h) * h1
            y1 = min(y0 + 1, this.fNumY-2)

            sx = 1.0 - tx
            sy = 1.0 - ty

            if (x0 < this.fNumX and y0 < this.fNumY): 
                d[x0 * n + y0] += sx * sy
            if (x1 < this.fNumX and y0 < this.fNumY): 
                d[x1 * n + y0] += tx * sy
            if (x1 < this.fNumX and y1 < this.fNumY): 
                d[x1 * n + y1] += tx * ty
            if (x0 < this.fNumX and y1 < this.fNumY): 
                d[x0 * n + y1] += sx * ty

        if (this.particleRestDensity == 0.0):
            sum = 0.0
            numFluidCells = 0

            for i in range(this.fNumCells):
                if (this.cellType[i] == FLUID_CELL):
                    sum += d[i]
                    numFluidCells += 1

            if (numFluidCells > 0):
                this.particleRestDensity = sum / numFluidCells

# 			for (var xi = 1; xi < this.fNumX; xi++) {
# 				for (var yi = 1; yi < this.fNumY; yi++) {
# 					var cellNr = xi * n + yi;
# 					if (this.cellType[cellNr] != FLUID_CELL)
# 						continue;
# 					var hx = this.h;
# 					var hy = this.h;

# 					if (this.cellType[(xi - 1) * n + yi] == SOLID_CELL || this.cellType[(xi + 1) * n + yi] == SOLID_CELL)
# 						hx -= this.particleRadius;
# 					if (this.cellType[xi * n + yi - 1] == SOLID_CELL || this.cellType[xi * n + yi + 1] == SOLID_CELL)
# 						hy -= this.particleRadius;

# 					var scale = this.h * this.h / (hx * hy)
# 					d[cellNr] *= scale;
# 				}
# 			}

    def transferVelocities(this, toGrid, flipRatio):
        n = this.fNumY
        h = this.h
        h1 = this.fInvSpacing
        h2 = 0.5 * h

        if (toGrid):

            this.prevU = this.u
            this.prevV = this.v

            this.du = fillList(this.du, 0.0)
            this.dv = fillList(this.dv, 0.0)
            this.u = fillList(this.u, 0.0)
            this.v = fillList(this.v, 0.0)

            for i in range(this.fNumCells):
                this.cellType[i] = SOLID_CELL if this.s[i] == 0.0 else AIR_CELL

            for i in range(this.numParticles):
                x = this.particlePos[2 * i]
                y = this.particlePos[2 * i + 1]
                xi = clamp(math.floor(x * h1), 0, this.fNumX - 1)
                yi = clamp(math.floor(y * h1), 0, this.fNumY - 1)
                cellNr = xi * n + yi
                if (this.cellType[cellNr] == AIR_CELL):
                    this.cellType[cellNr] = FLUID_CELL

        for component in range(2):

            dx = 0 if component == 0 else h2
            dy = h2 if component == 0 else 0

            f = this.u if component == 0 else this.v
            prevF = this.prevU if component == 0 else this.prevV
            d = this.du if component == 0 else this.dv

            for i in range(this.numParticles):
                x = this.particlePos[2 * i]
                y = this.particlePos[2 * i + 1]

                x = clamp(x, h, (this.fNumX - 1) * h)
                y = clamp(y, h, (this.fNumY - 1) * h)

                x0 = min(math.floor((x - dx) * h1), this.fNumX - 2)
                tx = ((x - dx) - x0 * h) * h1
                x1 = min(x0 + 1, this.fNumX-2)
                
                y0 = min(math.floor((y-dy)*h1), this.fNumY-2)
                ty = ((y - dy) - y0*h) * h1
                y1 = min(y0 + 1, this.fNumY-2)

                sx = 1.0 - tx
                sy = 1.0 - ty

                d0 = sx*sy
                d1 = tx*sy
                d2 = tx*ty
                d3 = sx*ty

                nr0 = x0*n + y0
                nr1 = x1*n + y0
                nr2 = x1*n + y1
                nr3 = x0*n + y1

                if (toGrid):
                    pv = this.particleVel[2 * i + component]

                    f[nr0] += pv * d0
                    d[nr0] += d0

                    f[nr1] += pv * d1
                    d[nr1] += d1

                    f[nr2] += pv * d2
                    d[nr2] += d2

                    f[nr3] += pv * d3
                    d[nr3] += d3
                else:
                    offset = n if component == 0 else 1
                    valid0 = 1 if this.cellType[nr0] != AIR_CELL or this.cellType[nr0 - offset] != AIR_CELL else 0.0
                    valid1 = 1 if this.cellType[nr1] != AIR_CELL or this.cellType[nr1 - offset] != AIR_CELL else 0.0
                    valid2 = 1 if this.cellType[nr2] != AIR_CELL or this.cellType[nr2 - offset] != AIR_CELL else 0.0
                    valid3 = 1 if this.cellType[nr3] != AIR_CELL or this.cellType[nr3 - offset] != AIR_CELL else 0.0

                    v = this.particleVel[2 * i + component]
                    d = valid0 * d0 + valid1 * d1 + valid2 * d2 + valid3 * d3

                    if (d > 0.0):

                        picV = (valid0 * d0 * f[nr0] + valid1 * d1 * f[nr1] + valid2 * d2 * f[nr2] + valid3 * d3 * f[nr3]) / d
                        corr = (valid0 * d0 * (f[nr0] - prevF[nr0]) + valid1 * d1 * (f[nr1] - prevF[nr1]) + valid2 * d2 * (f[nr2] - prevF[nr2]) + valid3 * d3 * (f[nr3] - prevF[nr3])) / d
                        flipV = v + corr

                        this.particleVel[2 * i + component] = (1.0 - flipRatio) * picV + flipRatio * flipV

            if (toGrid):
                for i in range(len(f)):
                    if (d[i] > 0.0):
                        f[i] /= d[i]

                # restore solid cells

                for i in range(this.fNumX):
                    for j in range(this.fNumY):
                        solid = this.cellType[i * n + j] == SOLID_CELL
                        if solid or (i > 0 and this.cellType[(i - 1) * n + j] == SOLID_CELL):
                            this.u[i * n + j] = this.prevU[i * n + j]
                        if solid or (j > 0 and this.cellType[i * n + j - 1] == SOLID_CELL):
                            this.v[i * n + j] = this.prevV[i * n + j]

    def solveIncompressibility(this, numIters, dt, overRelaxation, compensateDrift = True):

        this.p = fillList(this.p, 0)
        this.prevU = this.u
        this.prevV = this.v

        n = this.fNumY
        cp = this.density * this.h / dt

        for iter in range(numIters):

            for i in range(1, this.fNumX-1):
                for j in range(1, this.fNumY-1):
                    if this.cellType[i*n + j] != FLUID_CELL:
                        continue

                    center = i * n + j
                    left = (i - 1) * n + j
                    right = (i + 1) * n + j
                    bottom = i * n + j - 1
                    top = i * n + j + 1

                    s = this.s[center]
                    sx0 = this.s[left]
                    sx1 = this.s[right]
                    sy0 = this.s[bottom]
                    sy1 = this.s[top]
                    s = sx0 + sx1 + sy0 + sy1

                    if (s == 0.0):
                        continue

                    div = this.u[right] - this.u[center] + this.v[top] - this.v[center]

                    if this.particleRestDensity > 0.0 and compensateDrift:
                        k = 1.0
                        compression = this.particleDensity[i*n + j] - this.particleRestDensity
                        if (compression > 0.0):
                            div = div - k * compression

                    p = -div / s
                    p *= overRelaxation
                    this.p[center] += cp * p

                    this.u[center] -= sx0 * p
                    this.u[right] += sx1 * p
                    this.v[center] -= sy0 * p
                    this.v[top] += sy1 * p

    def updateParticleColors(this):
        # for (var i = 0; i < this.numParticles; i++) {
        # 	this.particleColor[3 * i] *= 0.99; 
        # 	this.particleColor[3 * i + 1] *= 0.99
        # 	this.particleColor[3 * i + 2] = 
        # 		clamp(this.particleColor[3 * i + 2] + 0.001, 0.0, 1.0)
        # }

        # return;

        h1 = this.fInvSpacing

        for i in range(this.numParticles):

            s = 0.01

            this.particleColor[3 * i] = clamp(this.particleColor[3 * i] - s, 0.0, 1.0)
            this.particleColor[3 * i + 1] = clamp(this.particleColor[3 * i + 1] - s, 0.0, 1.0)
            this.particleColor[3 * i + 2] = clamp(this.particleColor[3 * i + 2] + s, 0.0, 1.0)

            x = this.particlePos[2 * i]
            y = this.particlePos[2 * i + 1]
            xi = clamp(math.floor(x * h1), 1, this.fNumX - 1)
            yi = clamp(math.floor(y * h1), 1, this.fNumY - 1)
            cellNr = xi * this.fNumY + yi

            d0 = this.particleRestDensity

            if (d0 > 0.0):
                relDensity = this.particleDensity[cellNr] / d0
                if (relDensity < 0.7):
                    s = 0.8
                    this.particleColor[3 * i] = s
                    this.particleColor[3 * i + 1] = s
                    this.particleColor[3 * i + 2] = 1.0

    def setSciColor(this, cellNr, val, minVal, maxVal):
        val = min(max(val, minVal), maxVal- 0.0001)
        d = maxVal - minVal
        val = .5 if d == 0.0 else (val - minVal) / d
        m = 0.25
        num = math.floor(val / m)
        s = (val - num * m) / m
        #r, g, b

        match num:
            case 0:
                r = 0.0
                g = s
                b = 1.0
            case 1:
                r = 0.0
                g = 1.0
                b = 1.0-s
            case 2:
                r = s
                g = 1.0
                b = 0.0
            case 3:
                r = 1.0
                g = 1.0 - s
                b = 0.0

        this.cellColor[3 * cellNr] = r
        this.cellColor[3 * cellNr + 1] = g
        this.cellColor[3 * cellNr + 2] = b

    def updateCellColors(this):
        this.cellColor = fillList(this.cellColor, 0)

        for i in range(this.fNumCells):

            if this.cellType[i] == SOLID_CELL:
                this.cellColor[3*i] = 0.5
                this.cellColor[3*i + 1] = 0.5
                this.cellColor[3*i + 2] = 0.5
            elif this.cellType[i] == FLUID_CELL:
                d = this.particleDensity[i]
                if this.particleRestDensity > 0.0:
                    d /= this.particleRestDensity
                this.setSciColor(i, d, 0.0, 2.0)

    def simulate(this, dt, gravity, flipRatio, numPressureIters, numParticleIters, overRelaxation, compensateDrift, separateParticles, obstacleX, abstacleY, obstacleRadius):
        numSubSteps = 1
        sdt = dt / numSubSteps

        for step in range(numSubSteps):
            this.integrateParticles(sdt, gravity)
            #if (separateParticles)
            #	this.pushParticlesApart(numParticleIters); 
            #this.handleParticleCollisions(obstacleX, abstacleY, obstacleRadius)
            this.transferVelocities(True, .9)
            this.updateParticleDensity()
            this.solveIncompressibility(numPressureIters, sdt, overRelaxation, compensateDrift)
            this.transferVelocities(False, flipRatio)

        this.updateParticleColors()
        this.updateCellColors()

# ----------------- end of simulator ------------------------------

scene = {
    "gravity" : 1,#-9.81,
    "dt" : 1.0 / 120.0,
    "flipRatio" : 0.9,
    "numPressureIters" : 100,
    "numParticleIters" : 2,
    "frameNr" : 0,
    "overRelaxation" : 1.9,
    "compensateDrift" : True,
    "separateParticles" : True,
    "obstacleX" : 0.0,
    "obstacleY" : 0.0,
    "obstacleRadius": 0.15,
    "paused": True,
    "showObstacle": True,
    "obstacleVelX": 0.0,
    "obstacleVelY": 0.0,
    "showParticles": True,
    "showGrid": False,
    "fluid": None
}

def setupScene():
    global f
    scene["obstacleRadius"] = 0.15
    scene["overRelaxation"] = 1.9

    scene["dt"] = 1.0 / 60.0
    scene["numPressureIters"] = 20 #50
    scene["numParticleIters"] = 2

    res = 10#100
    
    tankHeight = 1.0 * simHeight
    tankWidth = 1.0 * simWidth
    h = tankHeight / res
    density = 1000.0

    relWaterHeight = 0.8
    relWaterWidth = 0.6

    # dam break

    # compute number of particles

    r = 0.3 * h	# particle radius w.r.t. cell size
    dx = 2.0 * r
    dy = math.sqrt(3.0) / 2.0 * dx

    numX = math.floor((relWaterWidth * tankWidth - 2.0 * h - 2.0 * r) / dx)
    numY = math.floor((relWaterHeight * tankHeight - 2.0 * h - 2.0 * r) / dy)
    maxParticles = numX * numY

    # create fluid

    f = scene["fluid"] = FlipFluid(density, tankWidth, tankHeight, h, r, maxParticles)

    # create particles

    f.numParticles = numX * numY
    p = -1
    for i in range(numX):
        for j in range(numY):
            p += 1
            f.particlePos[p] = h + r + dx * i + (0 if j % 2 == 0 else r)
            p += 1
            f.particlePos[p] = h + r + dy * j

    # setup grid cells for tank

    n = f.fNumY

    for i in range(f.fNumX):
        for j in range(f.fNumY):
            s = 1.0	# fluid
            if i == 0 or i == f.fNumX-1 or j == 0:
                s = 0.0	# solid
            f.s[i*n + j] = s

# main -------------------------------------------------------


def simulate():
    scene["fluid"].simulate(
        scene["dt"], scene["gravity"], scene["flipRatio"], scene["numPressureIters"], scene["numParticleIters"], 
        scene["overRelaxation"], scene["compensateDrift"], scene["separateParticles"],
        scene["obstacleX"], scene["obstacleY"], scene["obstacleRadius"])#, scene["colorFieldNr"])
    scene["frameNr"] += 1

def update():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        simulate()

        screen.fill((255, 255, 255))
        f.drawParticles()
        pygame.display.flip()

setupScene()
update()