import pygame


class Draw:
	
	def drawGrid():
		for line in range(0, WINDOWHEIGHT, BLOCKSIZE):
			pygame.draw.line(DISPLAYSURF, WHITE, (0, line), (BLOCKSIZE * BOARDWIDTH, line)) # horizontally
		for column in range(0, BLOCKSIZE * BOARDWIDTH + 1, BLOCKSIZE):
			pygame.draw.line(DISPLAYSURF, WHITE, (column, 0), (column, WINDOWHEIGHT)) # perpendicularly


	def drawField(x, y):
		centerX = (x - 1) * BLOCKSIZE + int(BLOCKSIZE / 2)
		centerY = (y - 1) * BLOCKSIZE + int(BLOCKSIZE / 2)
		pygame.draw.circle(DISPLAYSURF, WHITE, (centerX, centerY), FIELDRADIUS, 1)


	def drawHallwayPart(hallwayPart):
		if hallwayPart[0][X] == hallwayPart[1][X]:
			differenceY = hallwayPart[0][Y] - hallwayPart[1][Y]		# the number of blocks the endpoints are away from each other
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
					
					
	def drawHallway(hallway):
		for part in hallway[1:(len(hallway) - 2)]: # leave out the first and the last hallwaypart because it's the door
			drawHallwayPart(part)			


	def drawObject(x, y, xStandart, yStandart, img):
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


class time:
	pass			
			
def load(path):
	return pygame.image.load(path)
	
def setupPygame():
	pygame.init()
			
