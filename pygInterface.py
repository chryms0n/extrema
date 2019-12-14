import pygame, sys


####################################################################
# colors

#				R   G   B
WHITE		= (215,215,215)
GRAY		= (128,128,128)
BLACK       = (  0,  0,  0)
BLUE        = (  0,  0,255)
RED         = (255,  0,  0)
GREEN		= (  0,255,  0)
BROWN       = (165, 42, 42)
LIGHTGRAY   = (165,165,165)
BGCOLOR = BLACK


#####################################################################
# set up the window

WINDOWWIDTH = 1600
WINDOWHEIGHT = 900
BOARDHEIGHT = 30
BOARDWIDTH = 40
BLOCKSIZE = int(WINDOWHEIGHT / BOARDHEIGHT)

FPS = 30

#####################################################################
# setting drawing- and size-standards

WALLWIDTH = 2
LINEDISTANCE = int(BLOCKSIZE / 3)
FIELDRADIUS = int(BLOCKSIZE / 6)
BODYSIZE = int(BLOCKSIZE / 5)
DOORINDENT = (int((BLOCKSIZE / WALLWIDTH) / 2) - 1) * WALLWIDTH


#####################################################################
# load the image files

IMAGE_PATH = './data/images/'
def imagewrapper(loader):
    def inner(path):
        return pygame.transform.scale(loader(path), (BLOCKSIZE, BLOCKSIZE))
    return inner
pygame.image.load = imagewrapper(pygame.image.load)

IMG_NONE = pygame.image.load(IMAGE_PATH + '/NoneA.png')
IMG_PLAYER_ROOM = pygame.image.load(IMAGE_PATH + '/Hero15.png')
IMG_PLAYER_HALLWAY = pygame.image.load(IMAGE_PATH + '/Hero_Hallway1.png')
IMG_LADDER_DOWN = pygame.image.load(IMAGE_PATH + '/LeiterAbwaerts.png')
IMG_LADDER_UP =  pygame.image.load(IMAGE_PATH + '/LeiterAufwaerts.png')
IMG_FOUNTAIN = pygame.image.load(IMAGE_PATH + '/Quelle.png')
IMG_TREASURE = pygame.image.load(IMAGE_PATH + '/Schatz3.png')
#IMG_TEST = pygame.image.load(IMAGE_PATH + '/groesse.png')
#IMG_GHOST = pygame.image.load(IMAGE_PATH + '/Geist.png')
IMG_IMP = pygame.image.load(IMAGE_PATH + '/KoboltA.png')
IMG_IMPWARRIOR = pygame.image.load(IMAGE_PATH + '/KoboltB.png')
IMG_SKELETON = pygame.image.load(IMAGE_PATH + '/Magic_effect3.png')
IMG_ATTACKIMPACT = pygame.image.load(IMAGE_PATH + '/AttackPointA.png')
IMG_GRASS_1 = pygame.image.load(IMAGE_PATH + 'Grass1.png')



#####################################################################
# identifiers

X = 0       # use it for tuples which
Y = 1		# contain x, y coordinates

def drawLine(color, point1, point2, width=1):
    pygame.draw.line(DISPLAYSURF, color, point1, point2, width)


def drawRect(color, rect):
    pygame.draw.rect(DISPLAYSURF, color, rect)

def drawCircle(color, center, radius, width=1):
    pygame.draw.circle(DISPLAYSURF, color, center, radius, width)


def drawGrid():
        for line in range(0, WINDOWHEIGHT, BLOCKSIZE):
                drawLine(WHITE, (0, line), (BLOCKSIZE * BOARDWIDTH, line)) # horizontally
        for column in range(0, BLOCKSIZE * BOARDWIDTH + 1, BLOCKSIZE):
                drawLine(WHITE, (column, 0), (column, WINDOWHEIGHT)) # perpendicularly


def drawField(x, y):
        centerX = (x - 1) * BLOCKSIZE + int(BLOCKSIZE / 2)
        centerY = (y - 1) * BLOCKSIZE + int(BLOCKSIZE / 2)
        drawCircle(WHITE, (centerX, centerY), FIELDRADIUS, 1)


def drawHallway(hallwayPart):
	
	if hallwayPart[0][X] == hallwayPart[1][X]:
		differenceY = hallwayPart[0][Y] - hallwayPart[1][Y]		# the number of blocks the endpoints are away from each other
		for blockY in range(abs(differenceY) + 1):
			if differenceY != 0:
				blockCoordY = (hallwayPart[0][Y] + (blockY * (differenceY / abs(differenceY))) * -1 - 1) * BLOCKSIZE
				drawRect(GRAY, ((hallwayPart[0][X] - 1) * BLOCKSIZE, blockCoordY, BLOCKSIZE, BLOCKSIZE))
	elif hallwayPart[0][Y] == hallwayPart[1][Y]:
		differenceX = hallwayPart[0][X] - hallwayPart[1][X]		# the number of block the endpoints are away from each other
		for blockX in range(abs(differenceX) + 1):
			if differenceX != 0:
				blockCoordX = (hallwayPart[0][X] + (blockX * (differenceX / abs(differenceX))) * -1 - 1) * BLOCKSIZE	
				drawRect(GRAY, (blockCoordX, (hallwayPart[0][Y] - 1) * BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))




def drawObject(x, y, img):
    posX = (x - 1) * BLOCKSIZE
    posY = (y - 1) * BLOCKSIZE
    DISPLAYSURF.blit(img, (posX, posY))	


def drawGameObject(gameObject):
    
    if gameObject.room:
            drawObject(gameObject.positionX + gameObject.room.topLeftCornerX, gameObject.positionY + gameObject.room.topLeftCornerY, gameObject.image)
    else: # handling playermovement outside of rooms
            drawObject(gameObject.positionOverallX, gameObject.positionOverallY, gameObject.image)


def drawRoom(room):
        
# draw the walls 
        drawWalls(room.topLeftCornerX, room.topLeftCornerY, room.width, room.length)

# draw the floor
        for row in range(room.topLeftCornerY + 1, room.topLeftCornerY + room.length - 1):
                for field in range(room.topLeftCornerX + 1, room.topLeftCornerX +  room.width - 1):
                        drawField(field, row)

# draw the doors
        for door in room.doors:
                drawDoor(door[0], door[1], room.topLeftCornerX, room.topLeftCornerY, room.width, room.length)


def drawRoomContent(room):
        
        for obj in room.massObjs:
                drawGameObject(obj)
        for key in room.attributeObjs:
                drawGameObject(room.attributeObjs[key])
        for monster in room.monsters:
                drawGameObject(monster)


def drawWalls(posx, posy, width, length):
    # get the pixel-coords for the start- and endpoints
    outerEdgesLeftx = (posx - 1) * BLOCKSIZE + LINEDISTANCE
    innerEdgesRightx = outerEdgesLeftx + (width - 1) * BLOCKSIZE
    innerEdgesLeftx = (posx - 1) * BLOCKSIZE + LINEDISTANCE * 2
    outerEdgesRightx = innerEdgesLeftx + (width - 1) * BLOCKSIZE
    outerEdgesUpy = (posy - 1) * BLOCKSIZE + LINEDISTANCE
    innerEdgesDowny = outerEdgesUpy + (length - 1) * BLOCKSIZE
    innerEdgesUpy = (posy - 1) * BLOCKSIZE + LINEDISTANCE * 2
    outerEdgesDowny = (innerEdgesUpy) + (length - 1) * BLOCKSIZE
    # draw the room walls
    drawLine(BROWN, (outerEdgesLeftx, outerEdgesUpy), (outerEdgesRightx, outerEdgesUpy), WALLWIDTH)
    drawLine(BROWN, (innerEdgesLeftx, innerEdgesUpy), (innerEdgesRightx, innerEdgesUpy), WALLWIDTH)
    drawLine(BROWN, (outerEdgesLeftx, outerEdgesDowny), (outerEdgesRightx, outerEdgesDowny), WALLWIDTH) 
    drawLine(BROWN, (innerEdgesLeftx, innerEdgesDowny), (innerEdgesRightx, innerEdgesDowny), WALLWIDTH)
    drawLine(BROWN, (outerEdgesLeftx, outerEdgesUpy), (outerEdgesLeftx, outerEdgesDowny), WALLWIDTH)
    drawLine(BROWN, (innerEdgesLeftx, innerEdgesUpy), (innerEdgesLeftx, innerEdgesDowny), WALLWIDTH)
    drawLine(BROWN, (innerEdgesRightx, innerEdgesUpy), (innerEdgesRightx, innerEdgesDowny), WALLWIDTH)
    drawLine(BROWN, (outerEdgesRightx, outerEdgesUpy), (outerEdgesRightx, outerEdgesDowny), WALLWIDTH)


def drawDoor(x, y, xstandart, ystandart, xmax, ymax):
    if x == xmax - 1 or x == 0:
        xCoord = (x + xstandart - 1) * BLOCKSIZE
        yCoord = (y + ystandart - 1) * BLOCKSIZE + DOORINDENT
        drawLine(BROWN, (xCoord, yCoord), (xCoord + BLOCKSIZE, yCoord), WALLWIDTH)
        yCoord += WALLWIDTH
        drawLine(BGCOLOR, (xCoord, yCoord), (xCoord + BLOCKSIZE, yCoord), WALLWIDTH)
        yCoord += WALLWIDTH
        drawLine(BROWN, (xCoord, yCoord), (xCoord + BLOCKSIZE, yCoord), WALLWIDTH)
    if y == ymax - 1 or y == 0:
        xCoord = (x + xstandart - 1) * BLOCKSIZE + DOORINDENT
        yCoord = (y + ystandart - 1) * BLOCKSIZE
        drawLine(BROWN, (xCoord, yCoord), (xCoord, yCoord + BLOCKSIZE), WALLWIDTH)		
        xCoord += WALLWIDTH
        drawLine(BGCOLOR, (xCoord, yCoord), (xCoord, yCoord + BLOCKSIZE), WALLWIDTH)
        xCoord += WALLWIDTH
        drawLine(BROWN, (xCoord, yCoord), (xCoord, yCoord + BLOCKSIZE), WALLWIDTH)


def drawBackground():
    DISPLAYSURF.fill(BGCOLOR)

			
def load(path):
	return pygame.image.load(path)
	
def setupPygame():
    global DISPLAYSURF, FPSCLOCK
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("extrema")
    FPSCLOCK = pygame.time.Clock()


def endFrame():
    pygame.display.update()
    FPSCLOCK.tick(FPS)

def terminate():
	
	pygame.quit()
	sys.exit()
