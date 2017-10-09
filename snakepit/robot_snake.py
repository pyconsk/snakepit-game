import random

from .snake import BaseSnake


class RobotSnake(BaseSnake):
    def __init__(self, world):
        super(RobotSnake, self).__init__(None)
        self.world = world

    def next_direction(self, initial=False):
        raise NotImplementedError

    def game_over(self):
        pass


class NoopRobotSnake(RobotSnake):
    def next_direction(self, initial=False):
        return None


class RandomRobotSnake(RobotSnake):
    def next_direction(self, initial=False):
        return random.choice(self.DIRECTIONS + (None,))


class OldRobotSnake(RobotSnake):
    def next_direction(self, initial=False):
        pass
