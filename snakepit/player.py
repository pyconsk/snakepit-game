from logging import getLogger

from .snake import Snake

logger = getLogger(__name__)


class Player:
    snake = None

    def __init__(self, player_id, name, ws):
        self.id = player_id
        self.name = name
        self.ws = ws
        self.score = 0
        self.keymap = {
            37: Snake.LEFT,
            38: Snake.UP,
            39: Snake.RIGHT,
            40: Snake.DOWN,
        }

    def __repr__(self):
        return '<%s [id=%s] [name=%s] [color=%s]>' % (self.__class__.__name__, self.id, self.name, self.color)

    def new_snake(self, game_settings, world, color):
        self.snake = Snake(game_settings, world, color)

    def keypress(self, code):
        if not self.alive:
            return

        direction = self.keymap.get(code)
        snake_direction = self.snake.direction

        if direction and snake_direction:
            # do not move in the opposite direction
            if snake_direction == self.snake.current_direction and not (
                    direction.xdir == -snake_direction.xdir and
                    direction.ydir == -snake_direction.ydir):
                self.snake.direction = direction
                logger.info('%r changed direction to %r', self, direction)

    @property
    def alive(self):
        if self.snake:
            return self.snake.alive
        else:
            return False

    @alive.setter
    def alive(self, value):
        self.snake.alive = value

    @property
    def color(self):
        if self.snake:
            return self.snake.color
        else:
            return None

    @property
    def direction(self):
        if self.snake:
            return self.snake.direction
        else:
            return None
