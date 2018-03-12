# Robot Snake Documentation

The idea of the PyCon SK programming contest was to write a snake robot program that earns the highest score in a game.
A single game ends when all snakes are dead or the game's frame limit is reached.

1. [Basic rules](#basic-rules)
1. [MyRobotSnake class](#myrobotsnake-class)
	1. [next_direction()](#next_direction)
1. [Snake world](#snake-world)
1. [Logging](#logging)
1. [Examples](#examples)


## Basic rules

- Use arrows to control the snake.
- Eat digits to grow up (score += digit).
- Do not bite: stones (#), snakes, borders.
- Earn points by killing other snakes (score += 1000).
- Invite friends and have fun together!


## MyRobotSnake class

The robot snake class must inherit from `snakepit.robot_snake.RobotSnake` and must implement the [next_direction()](#next_direction) method. The [snake's world](#snake-world) is represented by a two-dimensional array that changes during each frame. The `RobotSnake` class has the following attributes and properties available for use in your methods:

```python
class BaseSnake:
    COLOR_0 = World.COLOR_0
    CH_VOID = World.CH_VOID
    CH_STONE = World.CH_STONE

    CH_HEAD = '@'
    CH_BODY = '*'
    CH_TAIL = '$'
    BODY_CHARS = frozenset([CH_HEAD, CH_BODY, CH_TAIL])

    CH_DEAD_HEAD = 'x'
    CH_DEAD_BODY = '+'
    CH_DEAD_TAIL = '%'
    DEAD_BODY_CHARS = frozenset([CH_DEAD_HEAD, CH_DEAD_BODY, CH_DEAD_TAIL])

    UP = Vector(0, -1)
    DOWN = Vector(0, 1)
    LEFT = Vector(-1, 0)
    RIGHT = Vector(1, 0)

    DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

    color = None
    alive = False

class RobotSnake(BaseSnake):
    @property
    def world(self):
        return self._world

    def next_direction(self, initial=False):
        raise NotImplementedError


class MyRobotSnake(RobotSnake):
    def next_direction(self, initial=False):
        return None  # Implement this
```

### next_direction()

This method sends the next direction of the robot snake to the game server. The robot snake's direction is changed on the next frame load. The return value should be one of: `UP`, `DOWN`, `LEFT`, `RIGHT` or `None` (keep the current direction).


## Snake world

The snake's world (`world`) is a two-dimensional array that changes during each frame load. The dimensions of the array are specified by `world.FIELD_SIZE_X` and `world.FIELD_SIZE_Y`. Each point in the matrix is a two-item tuple `(char, color)`. The first item - `char` can be one of the following:

- `CH_VOID` - empty space - a snake can move here;
- `CH_HEAD`, `CH_BODY`, `CH_TAIL` - parts of a snake's living body;
- `CH_DEAD_HEAD`, `CH_DEAD_BODY`, `CH_DEAD_TAIL` - parts of a snake's dead body;
- `CH_STONE` - a stone that should be avoided;
- *growth digit* - a number (`range(1,10)`), which when eaten by a snake will grow its body during next `n` frame(s), where `n`=*growth digit* value (i.e. the body will grow proportionally to the value of the eaten number); The tail will stay in its position as the snake is growing during each frame. **NOTE:** The actual type of the growth digit in the world is `str` (**string**).

The second item of a point in the world - `color` - is an integer (color code). Since each living snake has a different color, the `color` code can be used to classify other living snakes in the world. Empty spaces, stones, and dead snakes have the color `0`. Living snakes and *growth digits* have various colors (`range(1,7)`). Your robot snake's color is available in the `color` attribute of the object.

The `world` object implements a `__str__()` method. An example world can look like this:

```
+----------------------------------------+
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                          ***           |
|                          $ @           |
|                                        |
|                                        |
|             1                          |
|                                        |
|          2                             |
|                                        |
|                                        |
|                                        |
|            $                           |
|            *                           |
|            *                 9         |
|            *                           |
|            @                           |
|                                     8  |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
|                                        |
+----------------------------------------+
```


## Logging

During each game, the output of the robot snake is visible on stdout or can be logged into a file. Since the output from the `print()` function is buffered by default, you should use the [`flush=True`](https://docs.python.org/3/library/functions.html#print) parameter. Also, the Python standard logging module is available.


## Examples

- [RandomRobotSnake](https://github.com/pyconsk/snakepit-game/blob/master/snakepit/robot_snake.py#L23)
- [WallGrinderRobotSnake](https://github.com/pyconsk/snakepit-game/blob/master/snakepit/robot_snake.py#L28)
- [TailChasingRobotSnake](https://github.com/pyconsk/snakepit-game/blob/master/snakepit/robot_snake.py#L104)

