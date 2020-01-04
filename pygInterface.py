import pygame, sys
from utility import pos


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

images = {"NONE" :  pygame.image.load(IMAGE_PATH + '/NoneA.png'),
    "PLAYER_ROOM" :  pygame.image.load(IMAGE_PATH + '/Hero15.png'),
    "PLAYER_HALLWAY" :  pygame.image.load(IMAGE_PATH + '/Hero_Hallway1.png'),
    "LADDER_DOWN" :  pygame.image.load(IMAGE_PATH + '/LeiterAbwaerts.png'),
    "LADDER_UP" :   pygame.image.load(IMAGE_PATH + '/LeiterAufwaerts.png'),
    "FOUNTAIN" :  pygame.image.load(IMAGE_PATH + '/Quelle.png'),
    "TREASURE" :  pygame.image.load(IMAGE_PATH + '/Schatz3.png'),
    #"TEST" :  pygame.image.load(IMAGE_PATH + '/groesse.png'),
    #"GHOST" :  pygame.image.load(IMAGE_PATH + '/Geist.png'),
    "IMP" :  pygame.image.load(IMAGE_PATH + '/KoboltA.png'),
    "IMPWARRIOR" :  pygame.image.load(IMAGE_PATH + '/KoboltB.png'),
    "SKELETON" :  pygame.image.load(IMAGE_PATH + '/Magic_effect3.png'),
    "ATTACKIMPACT" :  pygame.image.load(IMAGE_PATH + '/AttackPointA.png'),
    "GRASS_1" :  pygame.image.load(IMAGE_PATH + 'Grass1.png'),
    "DUNGEON": pygame.image.load(IMAGE_PATH + 'Dungeon.png'),
    "MOUNTAIN": pygame.image.load(IMAGE_PATH + 'Mountain2.png'),
    "MOUNTAIN_1": pygame.image.load(IMAGE_PATH + 'Mountain1.png'),
    "FOREST": pygame.image.load(IMAGE_PATH + 'Tree.png'),

    "FOREST_1": pygame.image.load(IMAGE_PATH + 'Tree2.png')}

#####################################################################
# identifiers

UP = 1
DOWN = 3
LEFT = 2
RIGHT = 0
NONE = None
DIRECTIONS = [RIGHT, UP, LEFT, DOWN]
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
    centerX = x * BLOCKSIZE + int(BLOCKSIZE / 2)
    centerY = y * BLOCKSIZE + int(BLOCKSIZE / 2)
    drawCircle(WHITE, (centerX, centerY), FIELDRADIUS, 1)


def drawHallway(hallwayPart):

    if hallwayPart[0].x == hallwayPart[1].x:
        differenceY = hallwayPart[0].y - hallwayPart[1].y		# the number of blocks the endpoints are away from each other
        for blockY in range(abs(differenceY) + 1):
            if differenceY != 0:
                blockCoordY = (hallwayPart[0].y + (blockY * (differenceY / abs(differenceY))) * -1) * BLOCKSIZE
                drawRect(GRAY, ((hallwayPart[0].x) * BLOCKSIZE, blockCoordY, BLOCKSIZE, BLOCKSIZE))
    elif hallwayPart[0].y == hallwayPart[1].y:
        differenceX = hallwayPart[0].x - hallwayPart[1].x		# the number of block the endpoints are away from each other
        for blockX in range(abs(differenceX) + 1):
            if differenceX != 0:
                blockCoordX = (hallwayPart[0].x + (blockX * (differenceX / abs(differenceX))) * -1) * BLOCKSIZE
                drawRect(GRAY, (blockCoordX, (hallwayPart[0].y) * BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))




def drawObject(obj):
    posi = (obj.position) * BLOCKSIZE
    DISPLAYSURF.blit(images[obj.name], (posi.x, posi.y))




def drawRoom(room):

    # draw the walls 
    drawWalls(room.origin.x, room.origin.y, room.width, room.length)

    # draw the floor
    for row in range(room.origin.y + 1, room.origin.y + room.length - 1):
        for field in range(room.origin.x + 1, room.origin.x +  room.width - 1):
            drawField(field, row)

    # draw the doors
    for door in room.doors:
        drawDoor(door)


def drawRoomContent(room):

    for obj in room.massObjs:
        drawObject(obj)
    for key in room.attributeObjs:
        drawObject(room.attributeObjs[key])
    for monster in room.monsters:
        drawObject(monster)


def drawWalls(posx, posy, width, length):
    # get the pixel-coords for the start- and endpoints
    outerEdgesLeftx = posx * BLOCKSIZE + LINEDISTANCE
    innerEdgesRightx = outerEdgesLeftx + (width - 1) * BLOCKSIZE
    innerEdgesLeftx = posx * BLOCKSIZE + LINEDISTANCE * 2
    outerEdgesRightx = innerEdgesLeftx + (width - 1) * BLOCKSIZE
    outerEdgesUpy = posy * BLOCKSIZE + LINEDISTANCE
    innerEdgesDowny = outerEdgesUpy + (length - 1) * BLOCKSIZE
    innerEdgesUpy = posy * BLOCKSIZE + LINEDISTANCE * 2
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


def drawDoor(door):
    x, y = (door.pos.x, door.pos.y)
    if door.direction == LEFT or door.direction == RIGHT:
        xCoord = x * BLOCKSIZE
        yCoord = y * BLOCKSIZE + DOORINDENT
        drawLine(BROWN, (xCoord, yCoord), (xCoord + BLOCKSIZE, yCoord), WALLWIDTH)
        yCoord += WALLWIDTH
        drawLine(BGCOLOR, (xCoord, yCoord), (xCoord + BLOCKSIZE, yCoord), WALLWIDTH)
        yCoord += WALLWIDTH
        drawLine(BROWN, (xCoord, yCoord), (xCoord + BLOCKSIZE, yCoord), WALLWIDTH)
    if door.direction == UP or door.direction == DOWN:
        xCoord = x * BLOCKSIZE + DOORINDENT
        yCoord = y * BLOCKSIZE
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
    print("set up!")
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
