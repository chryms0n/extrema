#! python3
# extrema - a simple roguelike dungeoncrawler
# last changes:	
#               
import pygame, random, copy, time, logging, pygInterface as pyIF, utility as util, world
from pygame.locals import *
from utility import pos


#################################################################################
### create some constants #######################################################
#################################################################################

####################################################################
# identifiers


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
LOOKING = 'looking'

X = 0       # use it for tuples which
Y = 1		# contain x, y coordinates
TUPEL = type(())
DICT = type({})


pyIF.setupPygame()

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')

def main():

    ####################################################################
    # set up the game state variables

    moved = True
    lvlchange = 0
    mpo = 1		# movement priority order
    actionMode = MOVING
    intendedDirection = False
    objects = []		# objects in the players room
    monsters = []		# monsters in the players room
    roomfilled = True	# determines weather monster and objects are spawned in the current room
    currentLevelNr = 0
    isLandscape = False


    levels = [world.Level(levelnr, 3, 3, 2) for levelnr in range(9)]
    overworld = world.Level(11)
    overworld.createLandscape()
    level = overworld
    for i in range(len(levels)):
        oldLevel = level
        level = levels[i]
        level.create()
        level.currentRoom = level.specialRooms[world.LADDER_UP]
        room = level.currentRoom
        print(i)

        if i != 0:
            oldRoom = oldLevel.specialRooms[world.LADDER_DOWN]
            exitPoint = oldRoom.attributeObjs[world.LADDER_DOWN]
        else:
            exitPoint = overworld.specialRooms[world.LADDER_DOWN].attributeObjs[world.LADDER_DOWN]
        entryPoint = room.attributeObjs[world.LADDER_UP]
        exitPoint.startRoom = level.specialRooms[world.LADDER_UP]
        exitPoint.otherEnd = entryPoint
        exitPoint.nextLevel = level
        entryPoint.otherEnd = exitPoint
        entryPoint.nextLevel = oldLevel

    level = levels[0]


    player = world.Object(world.PLAYER, world.randomPositionIn(level.currentRoom), False)
    print()
    print(player.position)


    ########################################################################
    ### the main game loop #################################################
    ########################################################################

    while True:

        room = level.currentRoom
        ########################################################################	
        # update gamestate #####################################################
        ########################################################################

        direction = None
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
                        entry = world.LADDER_DOWN
                        ext = world.LADDER_UP
                        lvlchange = -1
                    elif event.key == K_d:
                        entry = world.LADDER_UP
                        ext = world.LADDER_DOWN
                        lvlchange = 1
                    if (ext in room.attributeObjs) and player.position == room.attributeObjs[ext].position:
                        exitPoint = room.attributeObjs[ext]
                        level = exitPoint.nextLevel
                        level.currentRoom = level.specialRooms[entry]
                        player.position = exitPoint.otherEnd.position
                    else:
                        print((not (ext in room.attributeObjs)))
                        print("Attribute Objs", *[obj for key, obj in room.attributeObjs.items()])
                        try:
                            print(player.position != room.attributeObjs[ext].position)
                        except KeyError:
                            pass
                        print("Player Position at {0}".format(player.position))
                        print('No ladder')

                elif event.key == K_l:
                    actionMode = LOOKING

                if actionMode == MOVING and direction != NONE:
                    world.updatePositionalData(player, level)	# gets hallway moving options as well as the overall position when leaving a room
                    world.movePlayer(player, direction, level.currentRoom)

                    direction = None
                    moved = True

                elif actionMode == LOOKING and direction != None:
                    print("Looking at {0}".format(level.giveInfoOn(util.toPosition(direction)+player.position)))
                    actionMode =  MOVING


                elif actionMode == ATTACKING:
                    print('attack')
                    actionMode = MOVING

                if moved:


                    #######################################################
                    # spawning and deleting enemies and treasures when entering/leaving a room

                    if level.currentRoom and not roomfilled:
                            monsters = level.currentRoom.monsters
                            roomfilled = True

                    if not level.currentRoom and roomfilled:
                            monsters = []
                            roomfilled = False

                    #######################################################
                    # enemy AI

                    for monster in monsters:
                        pass

                    mpo = util.count(mpo, 2)

                            # TODO: make the AI circumvent obstacles withoutil.too mutil.h trial and error.

                            # TODO: build a simple fighting AI

                    moved = False

                    ###########################################################
                    # space for console commentary

        pyIF.drawBackground()
        pyIF.drawGrid()
        if level.isLandscape:

            for tile in util.iter2D(level.landscape):
                if tile.objects:
                    pyIF.drawObject(tile.objects[0])
                else:
                    pyIF.drawObject(tile.base)
        else:
            for hallway in level.hallways:
                for i in range(len(hallway.geometry) - 2):
                    hallwayPartNr = i + 1
                    pyIF.drawHallway(hallway.geometry[hallwayPartNr])
            for r in util.iter2D(level.rooms):
                if r:	# check weather there is a room to draw
                    pyIF.drawRoom(r)
                    pyIF.drawRoomContent(r)

        for monster in monsters:
            pyIF.drawObject(monster)
#        for x in range(len(level.landscape)):
#            for y in range(len(level.landscape[x])):
#                if not level.landscape[x][y].base.moveable:
#                    pyIF.paintBlock(pos(x, y))
        pyIF.drawObject(player)
        pyIF.endFrame()

    ########################################################################
    # main game loop end ###################################################
    ########################################################################				

    return






if __name__ == '__main__':
	main()
