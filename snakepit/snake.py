from collections import deque
from random import randint

from . import settings
from .datatypes import Vector, Position, Draw
from .constants import CH_VOID


class BaseSnake:
    CH_VOID = CH_VOID
    CH_HEAD = '%'
    CH_BODY = '@'
    CH_TAIL = '*'

    CH_DEAD_HEAD = 'x'
    CH_DEAD_BODY = '@'
    CH_DEAD_TAIL = '+'

    UP = Vector(0, -1)
    DOWN = Vector(0, 1)
    LEFT = Vector(-1, 0)
    RIGHT = Vector(1, 0)

    DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

    color = None
    alive = False
    direction = None

    def __init__(self, color):
        self.color = color
        self.alive = True

    def __repr__(self):
        return '<%s [color=%s]>' % (self.__class__.__name__, self.color)


class Snake(BaseSnake):
    grow = 0
    body = ()

    def __init__(self, *args, **kwargs):
        super(Snake, self).__init__(*args, **kwargs)
        self.body = deque()

    def render_new(self):
        # try to spawn snake at some distance from world's borders
        distance = settings.INIT_LENGTH + 2
        x = randint(distance, settings.FIELD_SIZE_X - distance)
        y = randint(distance, settings.FIELD_SIZE_Y - distance)
        self.direction = self.DIRECTIONS[randint(0, 3)]
        # create snake from tail to head
        render = []
        pos = Position(x, y)

        for i in range(0, settings.INIT_LENGTH):
            self.body.appendleft(pos)

            if i == 0:
                char = self.CH_TAIL
            elif i == settings.INIT_LENGTH - 1:
                char = self.CH_HEAD
            else:
                char = self.CH_BODY

            render.append(Draw(pos.x, pos.y, char, self.color))
            pos = self.next_position()

        return render

    def next_position(self):
        # next position of the snake's head
        return Position(self.body[0].x + self.direction.xdir,
                        self.body[0].y + self.direction.ydir)

    def render_move(self):
        # moving snake to the next position
        render = []
        new_head = self.next_position()
        self.body.appendleft(new_head)
        # draw head in the next position
        render.append(Draw(new_head.x, new_head.y, self.CH_HEAD, self.color))
        # draw body in the old place of head
        render.append(Draw(self.body[1].x, self.body[1].y, self.CH_BODY, self.color))

        # if we grow this turn, the tail remains in place
        if self.grow > 0:
            self.grow -= 1
        else:
            # otherwise the tail moves
            old_tail = self.body.pop()
            render.append(Draw(old_tail.x, old_tail.y, self.CH_VOID, 0))
            new_tail = self.body[-1]
            render.append(Draw(new_tail.x, new_tail.y, self.CH_TAIL, self.color))

        return render

    def render_game_over(self):
        render = []

        # dead snake
        for i, pos in enumerate(self.body):
            if i == 0:
                render.append(Draw(pos.x, pos.y, self.CH_DEAD_HEAD, 0))
            elif i == len(self.body) - 1:
                render.append(Draw(pos.x, pos.y, self.CH_DEAD_TAIL, 0))
            else:
                render.append(Draw(pos.x, pos.y, self.CH_DEAD_BODY, 0))

        return render
