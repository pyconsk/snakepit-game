#!/usr/bin/env python
import sys
from importlib import import_module

from snakepit.robot_player import RobotPlayer
from snakepit.robot_snake import RobotSnake


robot_class = 'snakepit.robot_snake.NoopRobotSnake'
robot_name = 'RobotSnake'

if len(sys.argv) > 1:
    robot_name = sys.argv[1]

    if len(sys.argv) > 2:
        robot_class = sys.argv[-1]

module_name, class_name = robot_class.rsplit('.', 1)

mod = import_module(module_name)
cls = getattr(mod, class_name)

if not issubclass(cls, RobotSnake):
    raise TypeError('Robot class %s does not inherit from RobotSnake' % cls)

print('Creating new robot player "%s" using snake %r' % (robot_name, cls))
player = RobotPlayer(robot_name, snake_class=cls)
player.run()
