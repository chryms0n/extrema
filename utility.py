import random


UP = 1
DOWN = 3
LEFT = 2
RIGHT = 0
NONE = None
DIRECTIONS = [RIGHT, UP, LEFT, DOWN]
HORIZONTALLY = 'horizontally'
PERPENDICULAR = 'perpendidular'

def getNextField(direction, position):

    return position+toPosition(direction)


def isClamped(position, border1, border2):
    if not position.x in (border1.x, border2.x) and not position.y in (border1.y, border2.y):
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


class pos:

    def __init__(self, x, y):
        assert not (type(x) is pos)
        self.x=x
        self.y=y

    def __add__(self, other):
        return pos(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return pos(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        assert not (type(self.x) is pos)
        try:
            return self.x*scalar.x + self.y*scalar.y
        except AttributeError:
            return pos(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        assert not (type(self.x) is pos)
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        p = pos(self.x / scalar, self.y / scalar)
        assert p is pos
        return p

    def __str__(self):
        return "pos({0}, {1})".format(self.x, self.y)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.x == other.x and self.y==other.y)

    def toInt(self):
        print(type(self.x), type(self.y))
        return pos(int(self.x), int(self.y))

def getDirection(position):
    x = float(position.x)
    y = float(position.y)
    if x > 0:
        try:
            if abs(x/y) > 1:
                return RIGHT
            elif x/y > 0:
                return DOWN
            elif x/y < 0:
                return UP
        except ZeroDivisionError:
            return RIGHT
    elif x < 0:
        return (getDirection(pos(-x, y)) + 2)%4     # mirror the return from the case 'x>0'
    else:
        if y > 0:
            return DOWN
        elif y < 0:
            return UP
        else:
            return NONE


def getOppositeDirection(direction):
    return (direction+2)%4


def getpos(angle):
    pass


def toPosition(direction):
    if direction == RIGHT:
        return pos(1, 0)
    elif direction == UP:
        return pos(0, -1)
    elif direction == LEFT:
        return pos(-1, 0)
    elif direction ==DOWN:
        return pos(0, 1)

def toOrientation(direction):
    if (direction==RIGHT or direction==LEFT):
        return HORIZONTALLY
    elif (direction==UP or direction == DOWN):
        return PERPENDICULAR

def getAt(arr, pos):
    return arr[pos.x][pos.y]
def setAt(arr, pos, value):
    arr[pos.x][pos.y] = value

def isInBounds(arr, pos):
    try:
        getAt(arr, pos)
        assert pos.x >= 0 and pos.y >= 0
        return True
    except IndexError:
        return False
    except AssertionError:
        return False


if __name__=='__main__':
    #print(getDirection(pos(3,1)), getDirection(pos(2,0)), getDirection(pos(-3, 4)), getDirection(pos(-2,1)))
    print([str(toPosition(direction)) for direction in DIRECTIONS])
    print(2%2)
    h = []
    print(h[3])
