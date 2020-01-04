import random, utility as util, copy, itertools
from utility import pos, getAt, setAt
from collections import namedtuple


LEVELHEIGHT = 30
LEVELWIDTH = 40

UP = 1
DOWN = 3
LEFT = 2
RIGHT = 0
NONE = None
DIRECTIONS = [RIGHT, UP, LEFT, DOWN]
HORIZONTALLY = 'horizontally'
PERPENDICULAR = 'perpendidular'

X = 0       # use it for tuples which
Y = 1		# contain x, y coordinates

LEVELTALLY = 9

LADDER_DOWN = 'ladder_down'
LADDER_UP = 'ladder_up'
FOUNTAIN = 'fountain'
TREASURE = 'treasure'

NONE = "NONE"
PLAYER_ROOM = "PLAYER_ROOM"
PLAYER_HALLWAY = "PLAYER_HALLWAY"
PLAYER = PLAYER_ROOM
LADDER_DOWN = "LADDER_DOWN"
LADDER_UP = "LADDER_UP"
FOUNTAIN = "FOUNTAIN"
TREASURE = "TREASURE"
#TEST = "TEST"
#GHOST = "GHOST"
IMP = "IMP"
IMPWARRIOR = "IMPWARRIOR"
SKELETON = "SKELETON"
ATTACKIMPACT = "ATTACKIMPACT"
GRASS_1 = "GRASS_1"



def randomPositionIn(room):
    return room.origin + pos(random.randint(1, room.width - 2), random.randint(1, room.length - 2))

def isDoor(position, doors):
    for door in doors:
        if door.pos == position:
            return door
    return None


def isPassable(obj, direction, room):

    if isinstance(room, Room):
        nextField = util.getNextField(direction, obj.position)
        if nextField in room.impassableObjs:
            return False
        else:
            return True
    else:
        return True


Door = namedtuple('Door', 'pos direction room')
Hallway = namedtuple('Hallway', 'doors geometry')


class Object:

    def __init__(self, name, position, moa = True):

        self.name = name
        assert isinstance(position, pos)

        self.position = position
        self.moveable = moa # determines weather you can just walk over the object

        self.movementOptions = None  # and the movingoptions in a hallway.


    def __str__(self):
        return ('%s Object at %s' % (self.name, self.position))
    def __repr__(self):
        return ('%s Object at %s' % (self.name, self.position))



    #####################################################################
    # define basic inroom movement	

def moveObject(obj, direction, room):

    # look where the next field lies, then look wether you can go there
    nextField = util.getNextField(direction, obj.position)

    if util.isClamped(nextField, room.origin, pos(room.width - 1, room.length -1) + room.origin) or isDoor(nextField, room.doors):
        obj.position = util.getNextField(direction, obj.position)
    if isDoor(nextField, room.doors):
        print("There is a door")




	############################################################################	
	# move the player	

def movePlayer(obj, direction, room):
    if isinstance(room, Room):
        moveObject(obj, direction, room)

    elif not isinstance(room, Room):
        if obj.movementOptions[direction]:
                obj.position = obj.movementOptions[direction]



	##################################################################################
	# change between room and hallwaysettings if needed

# TODO: make level
def updatePositionalData(obj, level):

    def getCurrentHallway(hallways, position):

        hallwayNr = 0
        for hallway in hallways:
            hallwayPartNr = 0
            for hallwayPart in hallway.geometry:
                if hallwayPart[0] == position or hallwayPart[1] == position:
                    return hallways[hallwayNr]
                hallwayPartNr += 1
            hallwayNr += 1
    def getHallwayMovementOptions(hallway, position):

        movementOptions = {UP: False , DOWN: False , LEFT: False , RIGHT: False}
        for hallwayPart in hallway.geometry:
            for pointNr in range(len(hallwayPart)):
                if hallwayPart[pointNr] == position:
                    otherPoint = hallwayPart[(pointNr+1)%2]
                    direction = util.getDirection(otherPoint - position)
                    movementOptions[direction] = otherPoint
        return movementOptions

    # check weather the Hereo left the room
    room = level.currentRoom
    if isinstance(room, Room) and not util.isClamped(obj.position, room.origin-pos(1, 1), room.origin + pos(room.width, room.length)):
        print("HABE RAUM VERLASSEN!!!")
        # leaving the room
        level.currentRoom = getCurrentHallway([door.room for door in level.currentRoom.doors], obj.position)
        assert level.currentRoom
        obj.movementOptions = getHallwayMovementOptions(level.currentRoom, obj.position)

    elif not isinstance(room, Room):
        obj.movementOptions = getHallwayMovementOptions(room, obj.position)
        if isDoor(obj.position, room.doors):
            level.currentRoom = isDoor(obj.position, room.doors).room
            print("HABE RAUM BETRETEN")
            print(level.currentRoom.attributeObjs)


class Room:

    def __init__(self, nr, x, y, rx, ry, wd, ln, doors): # constructor

        self.number = nr
        self.origin = pos(x, y)
        self.length = ln
        self.width = wd
        self.doors = doors
        self.hallways = {}
        self.size = pos(ln, wd)

        self.attributeObjs = {}	# room-specific things that need to be called directly
        self.massObjs = []		# stuff that does not move (treasures, loot, etc.)
        self.monsters = []
        self.impassableObjs = []

    def updateImpassableObjs(self):

        self.impassableObjs = []
        for piece in self.massObjs + self.monsters:
                if not piece.moveable:
                        self.impassableObjs.append(piece.position)

    def returnMassObjectAt(self, coordX, coordY):

        for obj in self.massObjs:
                if (obj.positionX, obj.positionY) == (coordX, coordY):
                        return obj


    def __str__(self):
        return ('Room Object, pos = {0}, length = {1}, width = {2}'.format(self.origin, self.width, self.length))


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
        self.currentRoom = None

        self.possibleContent = []

        self.build = False	# the actual levelproperties aren't created in the initializer butil.in an extra funktion.
                            # The 'build'-attributes determines weather this function has already been called on the levelobject.


    def create(self):
        # TODO: build a new level from scratch based on the code on the beginning of the main game loop.
        roomNr = 0
        rooms = self.rooms
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
        visited = [[False for i in range(self.roomRowLength)] for i in range(self.roomRowWidth)]
        # creating doors
        # TODO: Implement range() for loops instead of 'roomRectX' variables
        for roomRectX, roomRectY, direction in itertools.product(range(rectRow), range(rectColumn), DIRECTIONS):
            roomPos = pos(roomRectX, roomRectY)
            setAt(visited, roomPos, True)
            otherDirection = util.getOppositeDirection(direction)
            directionVector = util.toPosition(direction)
            otherDirectionVector = util.toPosition(otherDirection)
            otherRoomPos = roomPos + directionVector
            room = rooms[roomRectX][roomRectY]
            if util.isInBounds(rooms, otherRoomPos) and room and getAt(rooms, otherRoomPos) and not getAt(visited, otherRoomPos):
                print(roomPos, otherRoomPos)
                otherRoom = rooms[otherRoomPos.x][otherRoomPos.y]
                radial = pos(
                    (room.width-1)*int((directionVector.x+1)*0.5), 
                    (room.length-1)*int((directionVector.y+1)*0.5))
                otherRadial = pos(
                    (otherRoom.width-1)*int((otherDirectionVector.x+1)*0.5), 
                    (room.length-1)*int((otherDirectionVector.y+1)*0.5))
                tangential = pos(
                    random.randint(1, room.width-2)*abs(directionVector.y), 
                    random.randint(1, room.length-2)*abs(directionVector.x))
                otherTangential = pos(
                    random.randint(1, otherRoom.width-2)*abs(otherDirectionVector.y), 
                    random.randint(1, otherRoom.length-2)*abs(otherDirectionVector.x))
###################################################################################################
# Create Hallways

                CoordDoor1 = radial+tangential + room.origin
                CoordDoor2 = otherRadial+otherTangential + otherRoom.origin

                directionVec = util.toPosition(direction)
                CoordIndent1 = CoordDoor1 + directionVec
                CoordIndent2 = CoordDoor2 - directionVec
                orient = util.toOrientation(direction)

                Middle = int(((CoordDoor2 - CoordDoor1)*directionVec) / 2)
                CoordMiddle1 = CoordDoor1 + Middle*directionVec
                CoordMiddle2 = CoordDoor2 + ((CoordDoor1-CoordDoor2)*directionVec + Middle)*directionVec

                newHallwayGeo =((CoordDoor1, CoordIndent1),
                (CoordIndent1, CoordMiddle1),
                (CoordMiddle1, CoordMiddle2),
                (CoordMiddle2, CoordIndent2),
                (CoordDoor2, CoordIndent2))
                newHallway = Hallway((Door(CoordDoor1, direction, room), Door(CoordDoor2, otherDirection, otherRoom)), newHallwayGeo)
                self.hallways.append(newHallway)


                room.doors.append(Door(CoordDoor1, direction, newHallway))
                otherRoom.doors.append(Door(CoordDoor2, otherDirection, newHallway))
                # Tell the rooms about there new doors


        ####################################################################################
        # Set up the player, monsters and other things in the rooms 		


        # put objects and enemies into rooms
        possibleContent = util.shuffle(['start', 'exit', 'heaven'] + ['treasure' for i in range(self.roomtally - 3)])

        self.possibleContent = (item for item in possibleContent)
        for column in self.rooms:
            for room in column:
                if room:
                    item = next(self.possibleContent)
                    if item == 'start':
                        if self.nr > 0:
                            room.attributeObjs[LADDER_UP] = Object(LADDER_UP, randomPositionIn(room))
                        self.roomKlimb = room
                    elif item == 'exit' and self.nr < LEVELTALLY - 1:
                        room.attributeObjs[LADDER_DOWN] = Object(LADDER_DOWN, randomPositionIn(room))
                        self.roomDescent = room
                    elif item == 'heaven':
                        room.attributeObjs[FOUNTAIN] = Object(FOUNTAIN, randomPositionIn(room))
                    elif item == 'treasure':
                        room.massObjs.append(Object(TREASURE, randomPositionIn(room)))
                    if not item in ['start', 'exit', 'heaven']:
                        room.monsters.append(Object(IMPWARRIOR, randomPositionIn(room)))

        print("LEVELNUMBER", self.nr)

        # finish the level
        self.build = True


    def dismantle(self):
        # TODO: save the level's state in the least amount of data possible.
        pass

    def build(self):
        # TODO: rebuild a saved level.
        pass

def createWorld():
    levels = [Level(levelnr, 3, 3, 2) for levelnr in range(9)]
    return levels

def changeLevel(levelNr, levels):
    level = levels[levelNr]
    if not level.build:
            level.create()
    level.currentRoom = level.roomKlimb
    return level

if __name__ == '__main__':
    pass
