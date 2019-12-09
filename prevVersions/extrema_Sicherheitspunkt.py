import pygame, sys, random, copy
from pygame.locals import *

# constants

FPS = 1

#             R   G   B
WHITE =     (230,230,230)
GRAY  =     (128,128,128)
BLACK =     (  0,  0,  0)
BROWN =     (165, 42, 42)
LIGHTGRAY = (165,165,165)
BGCOLOR = BLACK

IMG_NONE = None
IMG_LADDER_DOWN = pygame.image.load('D:\Bilder\LeiterAbwaerts.png')
IMG_FOUNTAIN = pygame.image.load('D:\Bilder\Quelle.png')
IMG_TREASURE = pygame.image.load('D:\Bilder\Schatz2.png')
IMG_TEST = pygame.image.load('D:\Bilder\groesse.png')
IMG_GHOST = pygame.image.load('D:\Bilder\Geist.png')
IMG_IMP = pygame.image.load('D:\Bilder\KoboltA.png')
IMG_IMPWARRIOR = pygame.image.load('D:\Bilder\KoboltB.png')
IMG_PLAYER = IMG_NONE

WINDOWWIDTH = 1550
WINDOWHEIGHT = 845
BOARDHEIGHT = 40
BOARDWIDTH = 55
BLOCKSIZE = int(WINDOWHEIGHT / BOARDHEIGHT)
WALLWIDTH = 2
LINEDISTANCE = int(BLOCKSIZE / 3)
FIELDRADIUS = int(BLOCKSIZE / 6)
BODYSIZE = int(BLOCKSIZE / 5)
DOORINDENT = (int((BLOCKSIZE / WALLWIDTH) / 2) - 1) * WALLWIDTH

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
HORIZONTALLY = 'horizontally'
PERPENDICULAR = 'perpendidular'

X = 0   	# use it for tuples which
Y = 1		# contain x, y coordinates
TUPEL = type(())
DICT = type({})

# damage types
THRUST = 'thrust'
CHOP = 'chop'
SLASH = 'slash'
LIGHTNING = 'lightning'
FIRE = 'fire'
ICE = 'ice'
PARALYZE = 'paralyze'

ROOMROWWIDTH = 3
ROOMROWLENGTH = 3
ROOMRECT = (int(BOARDWIDTH / ROOMROWWIDTH), int(BOARDHEIGHT / ROOMROWLENGTH)) # area in which a room can be located 
MISSINGROOMS = 2
ROOMTALLY = ROOMROWWIDTH * ROOMROWLENGTH - MISSINGROOMS

# set up the window und pygame
pygame.init()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption("extrema")
FPSCLOCK = pygame.time.Clock()


def main():

	global hallways, rooms, allRooms, allDoors

	moved = True
	attacking = False
	objects = []		# objects in the players room
	monsters = []		# monsters in the players room
	roomfilled = True	# determines weather monster and objects are spawnt in the current room

	roomNr = 0
	rooms = []
	for i in range(ROOMROWWIDTH):
		rooms.append([])

	# creating the room's attributes
	for rectColumn in range(ROOMROWWIDTH):   # x
		for rectRow in range(ROOMROWLENGTH): # y
			
			xCoord_Room = rectColumn * ROOMRECT[X] + random.randint(2, int(ROOMRECT[X]/ 3))
			yCoord_Room = rectRow * ROOMRECT[Y] + random.randint(2, int(ROOMRECT[Y] / 3))
			roomWidth = random.randint(5, ROOMRECT[X] - (xCoord_Room - rectColumn * ROOMRECT[X]) - 1)
			roomLength = random.randint(4, int(ROOMRECT[Y] * 2 / 3))
			currentRoom = Room(roomNr + 1, xCoord_Room, yCoord_Room, rectColumn, rectRow, roomWidth, roomLength, []) 
			rooms[rectColumn].append(currentRoom)
			roomNr += 1

	# deleting a few rooms
	for i in range(MISSINGROOMS):
		xNumber = random.randint(0, ROOMROWWIDTH - 1)
		yNumber = random.randint(0, ROOMROWLENGTH - 1)
		rooms[xNumber][yNumber] = False

	# getting a list of the rooms with greater range
	newRooms = copy.deepcopy(rooms)
	newRooms.insert(0, [False, False, False, False, False])
	newRooms.append([False, False, False, False, False])
	for column in range(ROOMROWWIDTH + 2):
		newRooms[column].insert(0, False)
		newRooms[column].append(False)

	# creating doors
	roomRectX = 1    	# column of the current room
	for rectColumn in rooms:
		roomRectY = 1	# row of the current room
		for room in rectColumn:	
			if room:
				if newRooms[roomRectX][roomRectY - 1]: # check for a room over the current one
					room.doors.append((random.randint(1, room.width - 2), 0))
				if newRooms[roomRectX][roomRectY + 1]: # check for a room under the current one
					room.doors.append((random.randint(1, room.width - 2), room.length - 1))
				if newRooms[roomRectX + 1][roomRectY]: # check for a room to the right
					room.doors.append((room.width - 1, random.randint(1, room.length - 2)))
				if newRooms[roomRectX - 1][roomRectY]: # check for a room to the left
					room.doors.append((0, random.randint(1, room.length - 2)))
			roomRectY += 1
		roomRectX += 1

	# get a list of all the doors with their properties
	allDoors = []
	rooms_copy = copy.deepcopy(rooms)
	roomRectX = 0
	for rectColumn in rooms_copy:
		roomRectY = 0
		for room in rectColumn:
			if room:
				if room.number != False:
					doorNr = 0
					for door in room.doors:
						if door[0] == 0:
							direction = LEFT
						elif door[0] == room.width - 1:
							direction = RIGHT
						elif door[1] == 0:
							direction = UP
						elif door[1] == room.length - 1:
							direction = DOWN			
						allDoors.append({'doorNr': doorNr, 'rectx': roomRectX, 'recty': roomRectY, 'roomx': room.topLeftCornerX, 'roomy': room.topLeftCornerY, 'x': door[0], 'y': door[1], 'direction': direction})
						doorNr += 1
			roomRectY += 1
		roomRectX += 1		

	# creating the hallways
	allDoorsCopy = copy.deepcopy(allDoors)
	doorPairs = getDoorPairs(allDoorsCopy)
	hallways = []
	for doorPair in doorPairs:
		xCoordDoor1 = doorPair[0]['x'] + doorPair[0]['roomx']
		yCoordDoor1 = doorPair[0]['y'] + doorPair[0]['roomy']
		xCoordDoor2 = doorPair[1]['x'] + doorPair[1]['roomx']
		yCoordDoor2 = doorPair[1]['y'] + doorPair[1]['roomy']
		if doorPair[0]['direction'] == RIGHT:
			xCoordDoor1 += 1
			xCoordDoor2 -= 1
			orient = HORIZONTALLY
		elif doorPair[0]['direction'] == LEFT:
			xCoordDoor1 -= 1
			xCoordDoor2 += 1
			orient = HORIZONTALLY
		elif doorPair[0]['direction'] == UP:
			yCoordDoor1 -= 1
			yCoordDoor2 += 1
			orient = PERPENDICULAR
		elif doorPair[0]['direction'] == DOWN:
			yCoordDoor1 += 1
			yCoordDoor2 -= 1
			orient = PERPENDICULAR	

		if orient == HORIZONTALLY:
			xCoordMiddle = int((xCoordDoor1 + xCoordDoor2) / 2)
			hallways.append((((xCoordDoor1, yCoordDoor1), (xCoordMiddle, yCoordDoor1)), 
			((xCoordMiddle, yCoordDoor1), (xCoordMiddle, yCoordDoor2)), 
			((xCoordMiddle, yCoordDoor2), (xCoordDoor2, yCoordDoor2))))
		elif orient == PERPENDICULAR:
			yCoordMiddle = int((yCoordDoor1 + yCoordDoor2) / 2)
			hallways.append((((xCoordDoor1, yCoordDoor1), (xCoordDoor1, yCoordMiddle)), 
			((xCoordDoor1, yCoordMiddle), (xCoordDoor2, yCoordMiddle)), 
			((xCoordDoor2, yCoordMiddle), (xCoordDoor2, yCoordDoor2))))
			
	# give the hereo a room to start
	for column in rooms:
		for room in column:
			if room:
				startingRoom = room 
				break
								
	# put objects and enemies into rooms
	levelRoomContent = ['start', 'exit', 'heaven']
	while len(levelRoomContent) != ROOMTALLY:
		levelRoomContent.append('treasure')
	random.shuffle(levelRoomContent)	
	for column in rooms:
		for room in column:
			if room and levelRoomContent[0] == 'start':
				startingRoom = room
			elif room and levelRoomContent[0] == 'exit':
				room.objs.append(Object('ladder_down', IMG_LADDER_DOWN, room))
			elif room and levelRoomContent[0] == 'heaven':
				room.objs.append(Object('Fountain', IMG_FOUNTAIN, room))
			elif room and levelRoomContent[0] == 'treasure':
				room.objs.append(Object('treasure', IMG_TREASURE, room))
			if room and levelRoomContent[0] != 'start' and levelRoomContent[0] != 'exit' and levelRoomContent[0] != 'heaven':
				room.monsters.append(Creature("Goblin", 100, 5, 5, 5, IMG_IMPWARRIOR, room))
			if room:
				del levelRoomContent[0]		
	

	# creating the hereo
	player = Hero("schufti", 500, 10, 10, 10, IMG_PLAYER, startingRoom)


########################################################################	
# main game loop #######################################################
########################################################################

	while True: 
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					terminate()
				elif event.key == K_UP:
					player.move(UP)
				elif event.key == K_DOWN:
					player.move(DOWN)
				elif event.key == K_RIGHT:
					player.move(RIGHT)
				elif event.key == K_LEFT:
					player.move(LEFT)
				elif event.key == K_SPACE:
					pass		
				moved = True
				if event.key == K_a:
					attacking = True
				elif event.key == K_c:
					casting = True			

		if moved:

			player.checkPosition()

			#######################################################
			# spawning and deleting enemies and treasures when entering/leaving a room

			if player.room and not roomfilled:
				monsters = player.room.monsters
				roomfilled = True

			if not player.room and roomfilled:
				monsters = []
				roomfilled = False	 

			#######################################################
			# enemy AI

			for monster in monsters:
				if monster.positionY > player.positionY + 1 or (monster.positionY > player.positionY and monster.positionX != player.positionX):
					monster.move(UP)
				elif monster.positionY < player.positionY - 1 or (monster.positionY < player.positionY and monster.positionX != player.positionX):
					monster.move(DOWN)
				elif monster.positionX < player.positionX - 1 or (monster.positionX < player.positionX and monster.positionY != player.positionY):
					monster.move(RIGHT)
				elif monster.positionX > player.positionX + 1 or (monster.positionX > player.positionX and monster.positionY != player.positionY):
					monster.move(LEFT)

			moved = False
		DISPLAYSURF.fill(BGCOLOR)
		for hallway in hallways:
			for hallwayPart in hallway:
				drawHallway(hallwayPart)
		for i in range(ROOMROWWIDTH):
			for room in rooms[i]:
				if room:	# check weather there is a room to draw
					room.drawRoom()
					room.drawContent()	
		for monster in monsters:
			monster.draw()							
		player.draw()
			
		pygame.display.update()
		FPSCLOCK.tick(FPS)

########################################################################
# main game loop end ###################################################
########################################################################				
	
	return


def drawGrid():
	
	for line in range(0, WINDOWHEIGHT, BLOCKSIZE):
		pygame.draw.line(DISPLAYSURF, WHITE, (0, line), (BLOCKSIZE * BOARDWIDTH, line)) # horizontally
	for column in range(0, BLOCKSIZE * BOARDWIDTH + 1, BLOCKSIZE):
		pygame.draw.line(DISPLAYSURF, WHITE, (column, 0), (column, WINDOWHEIGHT)) # perpendicularly


def drawField(x, y):
	
	centerX = (x - 1) * BLOCKSIZE + int(BLOCKSIZE / 2)
	centerY = (y - 1) * BLOCKSIZE + int(BLOCKSIZE / 2)
	pygame.draw.circle(DISPLAYSURF, WHITE, (centerX, centerY), FIELDRADIUS, 1)


def drawHallway(hallwayPart):
	
	if hallwayPart[0][X] == hallwayPart[1][X]:
		differenceY = hallwayPart[0][Y] - hallwayPart[1][Y]		# the number of block the endpoints are away from each other
		for blockY in range(abs(differenceY) + 1):
			if differenceY != 0:
				blockCoordY = (hallwayPart[0][Y] + (blockY * (differenceY / abs(differenceY))) * -1 - 1) * BLOCKSIZE
				pygame.draw.rect(DISPLAYSURF, GRAY, ((hallwayPart[0][X] - 1) * BLOCKSIZE, blockCoordY, BLOCKSIZE, BLOCKSIZE))
	elif hallwayPart[0][Y] == hallwayPart[1][Y]:
		differenceX = hallwayPart[0][X] - hallwayPart[1][X]		# the number of block the endpoints are away from each other
		for blockX in range(abs(differenceX) + 1):
			if differenceX != 0:
				blockCoordX = (hallwayPart[0][X] + (blockX * (differenceX / abs(differenceX))) * -1 - 1) * BLOCKSIZE	
				pygame.draw.rect(DISPLAYSURF, GRAY, (blockCoordX, (hallwayPart[0][Y] - 1) * BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))


def drawPerson(x, y, xStandart, yStandart, img):
	
	if img == None:
		posX = (x + xStandart - 1) * BLOCKSIZE + int(BLOCKSIZE / 2)
		posY = (y + yStandart - 1) * BLOCKSIZE + int(BLOCKSIZE / 2)
		pygame.draw.circle(DISPLAYSURF, WHITE, (posX, posY), BODYSIZE)	
	else:
		posX = (x + xStandart - 1) * BLOCKSIZE
		posY = (y + yStandart - 1) * BLOCKSIZE
		DISPLAYSURF.blit(img, (posX, posY))	


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
	pygame.draw.line(DISPLAYSURF, BROWN, (outerEdgesLeftx, outerEdgesUpy), (outerEdgesRightx, outerEdgesUpy), WALLWIDTH)
	pygame.draw.line(DISPLAYSURF, BROWN, (innerEdgesLeftx, innerEdgesUpy), (innerEdgesRightx, innerEdgesUpy), WALLWIDTH)
	pygame.draw.line(DISPLAYSURF, BROWN, (outerEdgesLeftx, outerEdgesDowny), (outerEdgesRightx, outerEdgesDowny), WALLWIDTH) 
	pygame.draw.line(DISPLAYSURF, BROWN, (innerEdgesLeftx, innerEdgesDowny), (innerEdgesRightx, innerEdgesDowny), WALLWIDTH)
	pygame.draw.line(DISPLAYSURF, BROWN, (outerEdgesLeftx, outerEdgesUpy), (outerEdgesLeftx, outerEdgesDowny), WALLWIDTH)
	pygame.draw.line(DISPLAYSURF, BROWN, (innerEdgesLeftx, innerEdgesUpy), (innerEdgesLeftx, innerEdgesDowny), WALLWIDTH)
	pygame.draw.line(DISPLAYSURF, BROWN, (innerEdgesRightx, innerEdgesUpy), (innerEdgesRightx, innerEdgesDowny), WALLWIDTH)
	pygame.draw.line(DISPLAYSURF, BROWN, (outerEdgesRightx, outerEdgesUpy), (outerEdgesRightx, outerEdgesDowny), WALLWIDTH)


def drawDoor(x, y, xstandart, ystandart, xmax, ymax):
	
	if x == xmax - 1 or x == 0:
		xCoord = (x + xstandart - 1) * BLOCKSIZE
		yCoord = (y + ystandart - 1) * BLOCKSIZE + DOORINDENT
		pygame.draw.line(DISPLAYSURF, BROWN, (xCoord, yCoord), (xCoord + BLOCKSIZE, yCoord), WALLWIDTH)
		yCoord += WALLWIDTH
		pygame.draw.line(DISPLAYSURF, BGCOLOR, (xCoord, yCoord), (xCoord + BLOCKSIZE, yCoord), WALLWIDTH)
		yCoord += WALLWIDTH
		pygame.draw.line(DISPLAYSURF, BROWN, (xCoord, yCoord), (xCoord + BLOCKSIZE, yCoord), WALLWIDTH)

	if y == ymax - 1 or y == 0:
		xCoord = (x + xstandart - 1) * BLOCKSIZE + DOORINDENT
		yCoord = (y + ystandart - 1) * BLOCKSIZE
		pygame.draw.line(DISPLAYSURF, BROWN, (xCoord, yCoord), (xCoord, yCoord + BLOCKSIZE), WALLWIDTH)		
		xCoord += WALLWIDTH
		pygame.draw.line(DISPLAYSURF, BGCOLOR, (xCoord, yCoord), (xCoord, yCoord + BLOCKSIZE), WALLWIDTH)
		xCoord += WALLWIDTH
		pygame.draw.line(DISPLAYSURF, BROWN, (xCoord, yCoord), (xCoord, yCoord + BLOCKSIZE), WALLWIDTH)	


def getOppositeDirection(direction):
	
	if direction == RIGHT:
		return LEFT
	elif direction == LEFT:
		return RIGHT
	elif direction == UP:
		return DOWN
	elif direction == DOWN:
		return UP


def getDoorPairs(doorList):
	
	doorPairs = []
	addPair = False
	for door in doorList:
		otherDoorNr = 0
		for otherDoor in doorList:
			if door['direction'] == RIGHT:
				if otherDoor['direction'] == LEFT and otherDoor['rectx'] == door['rectx'] + 1 and otherDoor['recty'] == door['recty']:
					addPair = True
			elif door['direction'] == LEFT:
				if otherDoor['direction'] == RIGHT and otherDoor['rectx'] == door['rectx'] - 1 and otherDoor['recty'] == door['recty']:
					addPair = True
			elif door['direction'] == UP:
				if otherDoor['direction'] == DOWN and otherDoor['rectx'] == door['rectx'] and otherDoor['recty'] == door['recty'] - 1:
					addPair = True
			elif door['direction'] == DOWN:
				if otherDoor['direction'] == UP and otherDoor['rectx'] == door['rectx'] and otherDoor['recty'] == door['recty'] + 1:
					addPair = True
			if addPair:
				doorPairs.append((door, otherDoor))
				del doorList[otherDoorNr]	# delete the second door so it wount be paired with the first one again.
				addPair = False
				break
			otherDoorNr += 1	
	return doorPairs	


def isDoor(direction, pp, doors):
	
	if type(doors[0]) == TUPEL:
		for door in doors:
			if direction == RIGHT and door[X] == pp[X] + 1 and door[Y] == pp[Y]:
				return True
			elif direction == LEFT and door[X] == pp[X] - 1 and door[Y] == pp[Y]:
				return True
			elif direction == UP and door[Y] == pp[Y] - 1 and door[X] == pp[X]:
				return True
			elif direction == DOWN and door[Y] == pp[Y] + 1  and door[X] == pp[X]:
				return True
			elif direction == 0 and door[X] == pp[X] and door[Y] == pp[Y]:
				return True
				
	elif type(doors[0]) == DICT:
		for door in doors:
			if direction == RIGHT and door['roomx'] == pp[X] + 1 and door['y'] + door['roomy'] == pp[Y]:
				return True
			elif direction == LEFT and door['x'] + door['roomx'] == pp[X] - 1 and door['y'] + door['roomy'] == pp[Y]:
				return True
			elif direction == UP and door['y'] + door['roomy'] == pp[Y] - 1 and door['x'] + door['roomx'] == pp[X]:
				return True
			elif direction == DOWN and door['roomy'] == pp[Y] + 1 and door['x'] + door['roomx'] == pp[X]:
				return True
			elif direction == 0 and door['x'] + door['roomx'] == pp[X] and door['y'] + door['roomy'] == pp[Y]:
				return True


def getCurrentHallway(hallways, position):
	
	hallwayNr = 0
	for hallway in hallways:
		hallwayPartNr = 0
		for hallwayPart in hallway:
			if hallwayPart[0] == position or hallwayPart[1] == position:
				return hallways[hallwayNr]					
			hallwayPartNr += 1
		hallwayNr += 1


def getHallwayMovingOptions(hallway, position):
	
	movingOptions = {'up': False , 'down': False , 'left': False , 'right': False}
	for hallwayPart in hallway:
		if hallwayPart[0] == position:
			if hallwayPart[0][Y] > hallwayPart[1][Y]:
				movingOptions['up'] = hallwayPart[1]
			elif hallwayPart[0][Y] < hallwayPart[1][Y]:
				movingOptions['down'] = hallwayPart[1]
			elif hallwayPart[0][X] < hallwayPart[1][X]:
				movingOptions['right'] = hallwayPart[1]
			elif hallwayPart[0][X] > hallwayPart[1][X]:
				movingOptions['left'] = hallwayPart[1]
		if hallwayPart[1] == position:
			if hallwayPart[1][Y] > hallwayPart[0][Y]:
				movingOptions['up'] = hallwayPart[0]
			elif hallwayPart[1][Y] < hallwayPart[0][Y]:
				movingOptions['down'] = hallwayPart[0]
			elif hallwayPart[1][X] < hallwayPart[0][X]:
				movingOptions['right'] = hallwayPart[0]
			elif hallwayPart[1][X] > hallwayPart[0][X]:
				movingOptions['left'] = hallwayPart[0]
	return movingOptions


def getRoomAtDoor(posX, posY):
	
	for door in allDoors:
		if door['x'] + door['roomx'] == posX and door['y'] + door['roomy'] == posY:
			return door['rectx'], door['recty']
		elif door['x'] + door['roomx'] == posX and door['y'] + door['roomy'] == posY:
			return door['rectx'], door['recty']
		elif door['y'] + door['roomy'] == posY and door['x']+ door['roomx']  == posX:
			return door['rectx'], door['recty']
		elif door['y'] + door['roomy'] == posY and door['x']+ door['roomx']  == posX:
			return door['rectx'], door['recty']
		elif door['x'] + door['roomx'] == posX and door['y'] + door['roomy'] == posY:
			return door['rectx'], door['recty']

	
def terminate():
	
	pygame.quit()
	sys.exit()
	
	
def s():
	print()
	
	
class Item:
	
	def __init__(self, dmgtype, dmg, reachMin, reachMax, img):
		
		self.damagetype = dmgtype
		self.damage = dmg
		self.img = img
		self.reachMin = reachMin
		self.reachMax = reachMax
			
		
class Object:
	
	def __init__(self, name, img, rm):
		
		self.name = name
		self.image = img
		
		self.room = rm	
		self.positionX = random.randint(1, self.room.width - 2)
		self.positionY = random.randint(1, self.room.length - 2)
		
		self.inventory = [] # things that get dropped when dying or getting used
		
	def draw(self):
		
		if self.room:
			drawPerson(self.positionX, self.positionY, self.room.topLeftCornerX, self.room.topLeftCornerY, self.image)
		else: # handling playermovement outside of rooms
			drawPerson(self.positionOverallX, self.positionOverallY, 0 , 0, self.image)		


class Creature(Object):
	
	def __init__(self, name, lp, stg, dex, ma , img, rm):	
		
		Object.__init__(self, name, img, rm)
		
		# player stats	
		self.strength = stg
		self.dexterity = dex
		self.magic = ma
		
		self.weaponEquiped = None
		
	def move(self, direction):
		
		if direction == UP and (self.positionY != 1 or isDoor(UP, (self.positionX, self.positionY), self.room.doors)):
			self.positionY -= 1
			
		if direction == DOWN and (self.positionY != self.room.length - 2 or isDoor(DOWN, (self.positionX, self.positionY), self.room.doors)):
			self.positionY += 1
			
		if direction == RIGHT and (self.positionX != self.room.width - 2 or isDoor(RIGHT, (self.positionX, self.positionY), self.room.doors)):
			self.positionX += 1
				
		if direction == LEFT and (self.positionX != 1 or isDoor(LEFT, (self.positionX, self.positionY), self.room.doors)):
			self.positionX -= 1	
		


class Hero(Creature):
	
	def __init__(self, name, lp, stg, dex, ma, img, rm): # constructor 

		Creature.__init__(self, name, lp, stg, dex, ma, img, rm)

		# attributes necessary to move in a hallway	
		self.positionOverallX = 0  # You start in a room so you  do
		self.positionOverallY = 0  # not need an overall position.
		self.currentHallway = None # same thing for the hallway
		self.movingOptions = None  # and the movingoptions in a hallway.
		
	def move(self, direction):
		
		if self.room:
			Creature.move(self, direction)
			
		elif not self.room:		
			if direction == UP:
				if self.movingOptions['up']:
					self.positionOverallX, self.positionOverallY = self.movingOptions['up']	
				elif isDoor(UP, (self.positionOverallX, self.positionOverallY), allDoors):
					self.positionOverallY -= 1	
				
			if direction == DOWN:
				if self.movingOptions['down']:
					self.positionOverallX, self.positionOverallY = self.movingOptions['down']
				elif isDoor(DOWN, (self.positionOverallX, self.positionOverallY), allDoors):
					self.positionOverallY += 1
					
			if direction == RIGHT:
				if self.movingOptions['right']:
					self.positionOverallX, self.positionOverallY = self.movingOptions['right']
				elif isDoor(RIGHT, (self.positionOverallX, self.positionOverallY), allDoors):	
					self.positionOverallX += 1
					
			if direction == LEFT:
				if self.movingOptions['left']:
					self.positionOverallX, self.positionOverallY = self.movingOptions['left']
				elif isDoor(LEFT, (self.positionOverallX, self.positionOverallY), allDoors):	
					self.positionOverallX -= 1

			
	def checkPosition(self):
		
		# check weather the Hereo left the room
		if self.room and (self.positionX < 0 or self.positionX > self.room.width - 1 or self.positionY < 0 or self.positionY > self.room.length - 1):
			# getting the position of the player outside of the room
			self.positionOverallX = self.positionX + self.room.topLeftCornerX
			self.positionOverallY = self.positionY + self.room.topLeftCornerY
			# leaving the room
			self.room = False
			self.currentHallway = getCurrentHallway(hallways, (self.positionOverallX, self.positionOverallY))
			self.movingOptions = getHallwayMovingOptions(self.currentHallway, (self.positionOverallX, self.positionOverallY))
		elif not self.room:
			self.movingOptions = getHallwayMovingOptions(self.currentHallway, (self.positionOverallX, self.positionOverallY))
			if isDoor(0 , (self.positionOverallX, self.positionOverallY), allDoors):			
				rc = getRoomAtDoor(self.positionOverallX, self.positionOverallY)
				self.room = rooms[rc[X]][rc[Y]]
				self.positionX, self.positionY = (self.positionOverallX - self.room.topLeftCornerX, self.positionOverallY - self.room.topLeftCornerY)


class Room:
	
	def __init__(self, nr, x, y, rx, ry, wd, ln, doors): # constructor
		
		self.number = nr
		self.topLeftCornerX = x
		self.topLeftCornerY = y
		self.rectColumn = rx
		self.rectRow = ry
		self.length = ln
		self.width = wd
		self.doors = doors
		
		self.objs = []
		self.monsters = []
				
	def drawRoom(self):
		
	# draw the walls 
		drawWalls(self.topLeftCornerX, self.topLeftCornerY, self.width, self.length)
	
	# draw the floor
		for row in range(self.topLeftCornerY + 1, self.topLeftCornerY + self.length - 1):
			for field in range(self.topLeftCornerX + 1, self.topLeftCornerX +  self.width - 1):
				drawField(field, row)
	
	# draw the doors
		for door in self.doors:
			drawDoor(door[0], door[1], self.topLeftCornerX, self.topLeftCornerY, self.width, self.length)
			
	def drawContent(self):
		
		for obj in self.objs:
			obj.draw()
		for monster in self.monsters:
			monster.draw()		



main()	
	 
