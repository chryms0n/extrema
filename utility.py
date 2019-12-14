import random


UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
NONE = 'none'
HORIZONTALLY = 'horizontally'
PERPENDICULAR = 'perpendidular'

def getNextField(direct, posx, posy):

	if direct == RIGHT:
		return posx + 1, posy
	elif direct == LEFT:
		return posx - 1, posy
	elif direct == UP:
		return posx, posy - 1
	elif direct == DOWN:
		return posx, posy + 1


def isClamped(value, vmax, vmin):
	if value != vmax and value != vmin:
		return True


def shuffle(_list):
	random.shuffle(_list)
	return _list


def count(nr, nr_max):
	if nr == nr_max:
		nr = 1
	else:
		nr += 1
	return nr
