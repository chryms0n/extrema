#! python3
# extrema - a simple roguelike dungeoncrawler
# last changes:	-added TODOs to enemy AI and level methods
#				-simplefied and abbrevieted the code to place the player, objs, etc... to rooms
#				-made long parameter lists more confortable
#				-renamed the player images
#				-created the levels-list with list-comprehensions


import pygame, random, copy, time, logging, pygInterface as pyIF, utility as util
from pygame.locals import *
from utility import pos


#################################################################################
### create some constants #######################################################
#################################################################################


LEVELHEIGHT = 30
LEVELWIDTH = 40



####################################################################
# identifiers

LADDER_DOWN = 'ladder_down'
LADDER_UP = 'ladder_up'
FOUNTAIN = 'fountain'
TREASURE = 'treasure'

UP = 1
DOWN = 3
LEFT = 2
RIGHT = 0
NONE = None
DIRECTIONS = [RIGHT, UP, LEFT, DOWN]
HORIZONTALLY = 'horizontally'
PERPENDICULAR = 'perpendidular'

MOVING = 'moving'
ATTACKING = 'attacking'

X = 0       # use it for tuples which
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

LEVELTALLY = 9

# will be redundent when there is more than one possible level per game
ROOMROWWIDTH = 3
ROOMROWLENGTH = 3
ROOMRECT = (int(LEVELWIDTH / ROOMROWWIDTH), int(LEVELHEIGHT / ROOMROWLENGTH)) # area in which a room can be located 
MISSINGROOMS = 2


pyIF.setupPygame()

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')

def main():

	####################################################################
	# set up the game state variables

	moved = True
	lvlchange = 0
	mpo = 1		# movement priority order
	actionMode = MOVING
	direction = None
	intendedDirection = False
	objects = []		# objects in the players room
	monsters = []		# monsters in the players room
	roomfilled = True	# determines weather monster and objects are spawned in the current room
	currentLevelNr = 0

	levels = [Level(levelnr, ROOMROWWIDTH, ROOMROWLENGTH, MISSINGROOMS) for levelnr in range(LEVELTALLY)]
	level = levels[currentLevelNr]
	level.create()
	player = Hero(level.roomKlimb, level)


########################################################################
### the main game loop #################################################
########################################################################

	while True:

		########################################################################	
		# update gamestate #####################################################
		########################################################################


		for event in pygame.event.get():
			if event.type == QUIT:
					pyIF.terminate()
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
						pyIF.terminate()
				elif event.key == K_UP:
						direction = UP
				elif event.key == K_DOWN:
						direction = DOWN
				elif event.key == K_RIGHT:
						direction = RIGHT
				elif event.key == K_LEFT:
						direction = LEFT
				elif event.key == K_SPACE:
						moved = True

				# player actions			
				elif event.key == K_a:
						actionMode = ATTACKING

				# TODO: after adding the create method to level-class-objects ship this code to function, in order to tidy up the main game loop
				# descent

				elif event.key in (K_d, K_k):
					if event.key == K_k:
							entry = 'ladder_down'
							ext = 'ladder_up'
							lvlchange = -1
					elif event.key == K_d:
							entry = 'ladder_up'
							ext = 'ladder_down'
							lvlchange = 1
					if (not (ext in player.room.attributeObjs)) or player.returnpos() != player.room.attributeObjs[ext].returnpos():
							print('No ladder')
					else:
							currentLevelNr += lvlchange
							level = levels[currentLevelNr]
							if not level.build:
									level.create()
							player.level = level
							player.room = [room for column in level.rooms for room in column if room and entry in room.attributeObjs][0]
							player.positionX, player.positionY = player.room.attributeObjs[entry].returnpos()

				if direction != NONE and isPassable(player, direction, player.room):
					player.move(direction)


					direction = None
					moved = True

				elif actionMode == ATTACKING:
					print('attack')
					actionMode = MOVING

				if moved:

					player.updatePositionalData()	# gets hallway moving options as well as the overall position when leaving a room

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
						if mpo == 1:
								if monster.positionY > player.positionY + 1 or (monster.positionY > player.positionY and monster.positionX != player.positionX):
										intendedDirection = UP
								elif monster.positionY < player.positionY - 1 or (monster.positionY < player.positionY and monster.positionX != player.positionX):
										intendedDirection = DOWN
								elif monster.positionX < player.positionX - 1 or (monster.positionX < player.positionX and monster.positionY != player.positionY):
										intendedDirection = RIGHT
								elif monster.positionX > player.positionX + 1 or (monster.positionX > player.positionX and monster.positionY != player.positionY):
										intendedDirection = LEFT
						if mpo == 2:
								if monster.positionX < player.positionX - 1 or (monster.positionX < player.positionX and monster.positionY != player.positionY):
										intendedDirection = RIGHT
								elif monster.positionX > player.positionX + 1 or (monster.positionX > player.positionX and monster.positionY != player.positionY):
										intendedDirection = LEFT
								elif monster.positionY > player.positionY + 1 or (monster.positionY > player.positionY and monster.positionX != player.positionX):
										intendedDirection = UP
								elif monster.positionY < player.positionY - 1 or (monster.positionY < player.positionY and monster.positionX != player.positionX):
										intendedDirection = DOWN

						if intendedDirection and isPassable(monster, intendedDirection, player.room):
								monster.move(intendedDirection)
						intendedDirection = False
					mpo = util.count(mpo, 2)

							# TODO: make the AI circumvent obstacles withoutil.too mutil.h trial and error.

							# TODO: build a simple fighting AI

					moved = False
					if player.room:
							player.room.updateImpassableObjs()

					###########################################################
					# space for console commentary

		pyIF.drawBackground()
		pyIF.drawGrid()
		for hallway in level.hallways:
				for i in range(len(hallway) - 2):
						hallwayPartNr = i + 1
						pyIF.drawHallway(hallway[hallwayPartNr])
		for i in range(level.roomRowWidth):
				for room in level.rooms[i]:
						if room:	# check weather there is a room to draw
							pyIF.drawRoom(room)
							pyIF.drawRoomContent(room)
		for monster in monsters:
			pyIF.drawGameObject(monster)
		pyIF.drawGameObject(player)
		pyIF.endFrame()

########################################################################
# main game loop end ###################################################
########################################################################				

	return





def getDoorPairs(doorList):

	doorPairs = []
	addPair = False # shows wether two are a pair
	for door in doorList:
		otherDoorNr = 0
		for otherDoor in doorList:
			directionVec = util.toPosition(door['direction'])
			if otherDoor['direction'] == util.getOppositeDirection(door['direction']) and otherDoor['roomRectPos'] == door['roomRectPos'] + directionVec:
				addPair = True
			if addPair:
				doorPairs.append((door, otherDoor))
				del doorList[otherDoorNr]	# delete the second door so it cannot be paired with the first one again.
				addPair = False
				break
			otherDoorNr += 1
	return doorPairs


def isDoor(position, doors):

        if type(doors[0]) == TUPEL:
                for door in doors:
                        if door[X] == position[X] and door[Y] == position[Y]:
                                return True

        elif type(doors[0]) == DICT:
                for door in doors:
                        if door['x'] + door['roomx'] == position[X] and door['y'] + door['roomy'] == position[Y]:
                                return True
        else:
            for door in doors:
                if door == position:
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


def getHallwayMovementOptions(hallway, position):

	movementOptions = {UP: False , DOWN: False , LEFT: False , RIGHT: False}
	for hallwayPart in hallway:
		if hallwayPart[0] == position.x:
			if hallwayPart[0][Y] > hallwayPart[1][Y]:
				movementOptions[UP] = hallwayPart[1]
			elif hallwayPart[0][Y] < hallwayPart[1][Y]:
				movementOptions[DOWN] = hallwayPart[1]
			elif hallwayPart[0][X] < hallwayPart[1][X]:
				movementOptions[RIGHT] = hallwayPart[1]
			elif hallwayPart[0][X] > hallwayPart[1][X]:
				movementOptions[LEFT] = hallwayPart[1]
		if hallwayPart[1] == position.y:
			if hallwayPart[1][Y] > hallwayPart[0][Y]:
				movementOptions[UP] = hallwayPart[0]
			elif hallwayPart[1][Y] < hallwayPart[0][Y]:
				movementOptions[DOWN] = hallwayPart[0]
			elif hallwayPart[1][X] < hallwayPart[0][X]:
				movementOptions[RIGHT] = hallwayPart[0]
			elif hallwayPart[1][X] > hallwayPart[0][X]:
				movementOptions[LEFT] = hallwayPart[0]
	return movementOptions


def getRoomAtDoor(pos, doors):

	for door in doors:
		if door['pos'] + door['roomPos'] == pos:
			return door['roomRectPos']


def isPassable(obj, direction, rm):

	if rm:
		nextField = util.getNextField(direction, obj.position)
		if nextField in rm.impassableObjs:
			return False
		else:
			return True
	else:
		return True






#############################################################################
### Create new Classes ###################################################### 
#############################################################################


class Item:

	def __init__(self, name, dmgtype, dmg, reachMin, reachMax):

		self.name = name
		self.damagetype = dmgtype
		self.damage = dmg
		self.reachMin = reachMin
		self.reachMax = reachMax


class Object:

	def __init__(self, name, rm, img, moa = True):

		self.name = name
		self.image = img

		self.room = rm
		self.position = pos(random.randint(1, self.room.width - 2), random.randint(1, self.room.length - 2))

		self.moveable = moa # determines weather you can just walk over the object

		self.inventory = [] # things that get dropped when dying or getting used

	def returnpos(self):

		return self.position


	def __str__(self):
		return ('%s Object at %s in room &s' % (self.__name__, self.position, self.room))


class Creature(Object):

    def __init__(self, name, rm, lp = 50, stg = 10, dex = 10, ma = 0, img = pyIF.IMG_SKELETON):

        Object.__init__(self, name, rm, img, False)

        # player stats	
        self.strength = stg ## 0176 9787 6526
        self.dexterity = dex
        self.magic = ma

        self.weaponEquiped = Item('fist', CHOP, 1, 1, 1)

    #####################################################################
    # define basic inroom movement	

    def move(self, direction):

                # look where the next field lies, then look wether you can go there
                nextField = util.getNextField(direction, self.position)

                if util.isClamped(nextField,  pos(0, 0), pos(self.room.width - 1, self.room.length -1)) or isDoor(nextField, self.room.doors):
                        self.position = util.getNextField(direction, self.position)
                if isDoor(nextField, self.room.doors):
                    print("There is a door")


    def attack(self, direction):
        pass

    def giveDamageFeedback(self, dmg):
        pass



class Hero(Creature):

	def __init__(self, rm, level, name = 'player', lp = 100, stg = 20, dex = 20, ma = 0, img = pyIF.IMG_PLAYER_ROOM): # constructor 

		Creature.__init__(self, name, rm, lp, stg, dex, ma, img)

		# attributes necessary to move in a hallway	
		self.positionOverall = pos(0, 0)  # You start in a room so you  do not need an overall position.
		self.currentHallway = None # same thing for the hallway
		self.movementOptions = None  # and the movingoptions in a hallway.
		self.level = level

		self.weaponEquiped = Item('dagger', THRUST, 5, 1, 1)

	############################################################################	
	# move the player	

	def move(self, direction):

            if self.room:
                    Creature.move(self, direction)

            elif not self.room:
                    if self.movementOptions[direction]:
                            self.positionOverall = self.movementOptions[direction]

            print(str(self.room.doors))
            print("Size: {0}, Position: {1}, Room Position {2}".format(self.room.size, self.position, self.room.topLeftCorner))


	##################################################################################
	# change between room and hallwaysettings if needed

	def updatePositionalData(self):

		# check weather the Hereo left the room
		if self.room and (self.position.x < 0 or self.position.x > self.room.width - 1 or self.position.y < 0 or self.position.y > self.room.length - 1):
			# getting the position of the player outil.ide of the room
			self.positionOverall = self.position + self.room.topLeftCorner
			# leaving the room
			self.room = False
			self.currentHallway = getCurrentHallway(self.level.hallways, self.positionOverall)
			self.movementOptions = getHallwayMovementOptions(self.currentHallway, self.positionOverall)
			self.image = pyIF.IMG_PLAYER_HALLWAY

		elif not self.room:
			self.movementOptions = getHallwayMovementOptions(self.currentHallway, self.positionOverall)
			if isDoor((self.positionOverallX, self.positionOverallY), self.level.allDoors):
				rc = getRoomAtDoor(self.positionOverall, self.level.allDoors)
				self.room = self.level.rooms[rc.x][rc.y]
				self.position= self.positionOverall - self.room.topLeftCorner
				self.image = pyIF.IMG_PLAYER_ROOM
				self.currentHallway = []


class Room:

	def __init__(self, nr, x, y, rx, ry, wd, ln, doors): # constructor

            self.number = nr
            self.topLeftCorner = pos(x, y)
            self.rectColumn = rx
            self.rectRow = ry
            self.length = ln
            self.width = wd
            self.doors = doors
            self.size = pos(ln, wd)

            self.attributeObjs = {}	# room-specific things that need to be called directly
            self.massObjs = []		# stuff that does not move (treasures, loot, etc.)
            self.monsters = []
            self.impassableObjs = []

	def updateImpassableObjs(self):

		self.impassableObjs = []
		for piece in self.massObjs + self.monsters:
			if not piece.moveable:
				self.impassableObjs.append((piece.positionX, piece.positionY))

	def returnMassObjectAt(self, coordX, coordY):

		for obj in self.massObjs:
			if (obj.positionX, obj.positionY) == (coordX, coordY):
				return obj


	def __str__(self):
		return ('Room Object, x = %s, y = %s, length = %s, width = %s')


class Level:

    def __init__(self, nr, rowWidth, rowLength, missingRooms):

        self.nr = nr
        self.roomRowWidth = rowWidth
        self.roomRowLength = rowLength
        self.missingRooms = missingRooms
        self.roomRect = (int(LEVELWIDTH / self.roomRowWidth), int(LEVELHEIGHT / self.roomRowLength))
        self.roomtally = 0

        self.allRooms = None
        self.roomDescent = None
        self.roomKlimb = None
        self.allDoors = []
        self.rooms = []     # 2D array where the rooms are stored '[column, row]'
        self.hallways = []

        self.possibleContent = []

        self.build = False	# the actual levelproperties aren't created in the initializer butil.in an extra funktion.
                            # The 'build'-attributes determines weather this function has already been called on the levelobject.


    def create(self):
        # TODO: build a new level from scratch based on the code on the beginning of the main game loop.
        roomNr = 0
        for i in range(self.roomRowWidth):
            self.rooms.append([])

        # creating the room's attributes
        for rectColumn in range(self.roomRowWidth):   # x
            for rectRow in range(self.roomRowLength): # y
                xCoord_Room = rectColumn * self.roomRect[X] + random.randint(2, int(self.roomRect[X]/ 3))
                yCoord_Room = rectRow * self.roomRect[Y] + random.randint(2, int(self.roomRect[Y] / 3))
                roomWidth = random.randint(5, self.roomRect[X] - (xCoord_Room - rectColumn * self.roomRect[X]) - 1)
                roomLength = random.randint(4, int(self.roomRect[Y] * 2 / 3))
                currentRoom = Room(roomNr + 1, xCoord_Room, yCoord_Room, rectColumn, rectRow, roomWidth, roomLength, [])
                self.rooms[rectColumn].append(currentRoom)
                roomNr += 1

        # deleting a few rooms
        for i in range(self.missingRooms):
            xNumber = random.randint(0, self.roomRowWidth - 1)
            yNumber = random.randint(0, self.roomRowLength - 1)
            self.rooms[xNumber][yNumber] = False

        # counting the number of rooms 
        for column in self.rooms:
            for room in column:
                if room:
                    self.roomtally += 1

        ###################################################################################
        # place doors where doors are needed and store there coordinates as well as their properties

        # getting a list of the rooms with greater range
        newRooms = copy.deepcopy(self.rooms)
        newRooms.insert(0, [False for i in range(self.roomRowWidth)])
        newRooms.append([False for i in range(self.roomRowWidth)])
        for column in range(self.roomRowWidth + 2):
            newRooms[column].insert(0, False)
            newRooms[column].append(False)

        # creating doors
        roomRectX = 1           # column of the current room
        for rectColumn in self.rooms:
            roomRectY = 1	# row of the current room
            for room in rectColumn:
                if room:
                    roomPos = pos(roomRectX, roomRectY)
                    for direction in DIRECTIONS:
                        directionVector = util.toPosition(direction)
                        otherRoomPos = roomPos + directionVector
                        radial = pos((room.width-1)*int((directionVector.x+1)*0.5), (room.length-1)*int((directionVector.y+1)*0.5))
                        tangential = pos(random.randint(1, room.width-2)*abs(directionVector.y), random.randint(1, room.length-2)*abs(directionVector.x))
                        if newRooms[otherRoomPos.x][otherRoomPos.y]: # check for a room in the current direction
                            room.doors.append(radial+tangential)
                            self.allDoors.append({'roomRectPos': roomPos, 'roomPos': room.topLeftCorner, 'pos': radial+tangential, 'direction': direction})
                roomRectY += 1
            roomRectX += 1


        ###################################################################################################
        # Create Hallways
        allDoorsCopy = copy.deepcopy(self.allDoors)
        doorPairs = getDoorPairs(allDoorsCopy)
        for doorPair in doorPairs:
            CoordDoor1 = doorPair[0]['pos'] + doorPair[0]['roomPos']
            CoordDoor2 = doorPair[1]['pos'] + doorPair[1]['roomPos']
            CoordIndent1 = CoordDoor1
            CoordIndent2 = CoordDoor2

            directionVec = util.toPosition(doorPair[0]['direction'])
            CoordIndent1 += directionVec
            CoordIndent2 -= directionVec
            orient = util.toOrientation(doorPair[0]['direction'])

            Middle = int(((CoordDoor2 - CoordDoor1)*directionVec) / 2)
            CoordMiddle1 = CoordDoor1 + Middle*directionVec
            CoordMiddle2 = CoordDoor2 + ((CoordDoor1-CoordDoor2)*directionVec + Middle)*directionVec
            self.hallways.append(((CoordDoor1, CoordIndent1),
            (CoordIndent1, CoordMiddle1),
            (CoordMiddle1, CoordMiddle2),
            (CoordMiddle2, CoordIndent2),
            (CoordDoor2, CoordIndent2)))


        ####################################################################################
        # Set up the player, monsters and other things in the rooms 		

        # give the hereo a room to start
        for column in self.rooms:
            for room in column:
                if room:
                    startingRoom = room
                    break

        # put objects and enemies into rooms
        possibleContent = util.shuffle(['start', 'exit', 'heaven'] + ['treasure' for i in range(self.roomtally - 3)])
        self.possibleContent = (item for item in possibleContent)
        for column in self.rooms:
            for room in column:
                if room:
                    item = next(self.possibleContent)
                    if item == 'start':
                        if self.nr > 0:
                            room.attributeObjs['ladder_up'] = Object(LADDER_UP, room, pyIF.IMG_LADDER_UP)
                        self.roomKlimb = room
                    elif item == 'exit' and self.nr < LEVELTALLY - 1:
                        room.attributeObjs['ladder_down'] = Object(LADDER_DOWN, room, pyIF.IMG_LADDER_DOWN)
                        self.roomDescent = room
                    elif item == 'heaven':
                        room.attributeObjs['fountain'] = Object(FOUNTAIN, room, pyIF.IMG_FOUNTAIN)
                    elif item == 'treasure':
                        room.massObjs.append(Object(TREASURE, room, pyIF.IMG_TREASURE))
                    if not item in ['start', 'exit', 'heaven']:
                        room.monsters.append(Creature("Goblin", room))

        # finish the level
        self.build = True


    def dismantle(self):
        # TODO: save the level's state in the least amount of data possible.
        pass

    def build(self):
        # TODO: rebuild a saved level.
        pass



if __name__ == '__main__':
	main()
