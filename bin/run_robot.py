#!/usr/bin/env python
import sys
from importlib import import_module

from snakepit.robot_player import RobotPlayer
from snakepit.robot_snake import RobotSnake


robot_class = 'snakepit.robot_snake.NoopRobotSnake'
robot_name = 'RobotSnake'
robot_id = None
argv_len = len(sys.argv)

if argv_len > 1:
    robot_class = sys.argv[1]

    if argv_len > 2:
        robot_name = sys.argv[2]

        if argv_len > 3:
            robot_id = sys.argv[3]

module_name, class_name = robot_class.rsplit('.', 1)

mod = import_module(module_name)
cls = getattr(mod, class_name)

if not issubclass(cls, RobotSnake):
    raise TypeError('Robot class %s does not inherit from RobotSnake' % cls)

print('Creating new robot player "%s" using snake %r' % (robot_name, cls))
player = RobotPlayer(robot_name, player_id=robot_id, snake_class=cls)
player.run()
