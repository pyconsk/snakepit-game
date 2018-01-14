import random

from .snake import BaseSnake


class RobotSnake(BaseSnake):
    @property
    def world(self):
        return self._world

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


class WallGrinderRobotSnake(RobotSnake):  # noqa: R701
    def next_direction(self, initial=False):  # noqa: R701
        world = self.world
        # print(world)  # pretty print the world into the log file

        head_position = [0, 0]
        tail_position = [0, 0]

        # lets find out our initial direction and length
        for y in range(world.SIZE_Y):
            for x in range(world.SIZE_X):
                char, color = world[y][x]

                if color == self.color:  # our snake
                    if char == self.CH_TAIL:
                        tail_position = [x, y]
                    elif char == self.CH_HEAD:
                        head_position = [x, y]
                    elif char == self.CH_BODY:
                        pass

        if initial:
            # noinspection PyAttributeOutsideInit
            self.current_direction = None
            # noinspection PyAttributeOutsideInit
            self.changed_direction = False

            if head_position[0] > tail_position[0]:
                self.current_direction = self.RIGHT
            elif head_position[0] < tail_position[0]:
                self.current_direction = self.LEFT
            elif head_position[1] > tail_position[1]:
                self.current_direction = self.DOWN
            elif head_position[1] < tail_position[1]:
                self.current_direction = self.UP

        if self.current_direction:
            next_x = head_position[0] + self.current_direction[0]
            next_y = head_position[1] + self.current_direction[1]
            next_direction = set()

            if next_x < 0:
                if next_y - 1 <= 0:
                    next_direction.add(self.DOWN)
                elif next_y + 1 >= world.SIZE_Y:
                    next_direction.add(self.UP)
                else:
                    next_direction.update([self.UP, self.DOWN])
            elif next_x >= world.SIZE_X:
                if next_y - 1 <= 0:
                    next_direction.add(self.DOWN)
                elif next_y + 1 >= world.SIZE_Y:
                    next_direction.add(self.UP)
                else:
                    next_direction.update([self.UP, self.DOWN])
            elif next_y < 0:
                if next_x - 1 <= 0:
                    next_direction.add(self.RIGHT)
                elif next_x + 1 >= world.SIZE_X:
                    next_direction.add(self.LEFT)
                else:
                    next_direction.update([self.LEFT, self. RIGHT])
            elif next_y >= world.SIZE_Y:
                if next_x - 1 <= 0:
                    next_direction.add(self.RIGHT)
                elif next_x + 1 >= world.SIZE_X:
                    next_direction.add(self.LEFT)
                else:
                    next_direction.update([self.LEFT, self. RIGHT])

            if next_direction:
                # noinspection PyAttributeOutsideInit
                self.current_direction = next_direction.pop()
                self.changed_direction = True
                return self.current_direction

            # noinspection PyAttributeOutsideInit
            self.changed_direction = False
            return None


class TailChasingRobotSnake(RobotSnake):  # noqa: R701
    def next_direction(self, initial=False):  # noqa: R701
        world = self.world
        # print(world)  # pretty print the world into the log file

        if initial:
            # noinspection PyAttributeOutsideInit
            self.current_direction = None
            # noinspection PyAttributeOutsideInit
            self.length = 0
            # noinspection PyAttributeOutsideInit
            self.changed_direction = False

            head_position = [0, 0]
            tail_position = [0, 0]

            # lets find out our initial direction and length
            for y in range(world.SIZE_Y):
                for x in range(world.SIZE_X):
                    char, color = world[y][x]

                    if color == self.color:  # our snake
                        if char == self.CH_TAIL:
                            tail_position = [x, y]
                        elif char == self.CH_HEAD:
                            head_position = [x, y]
                        elif char == self.CH_BODY:
                            pass

                        self.length += 1

            if head_position[0] > tail_position[0]:
                self.current_direction = self.RIGHT
            elif head_position[0] < tail_position[0]:
                self.current_direction = self.LEFT
            elif head_position[1] > tail_position[1]:
                self.current_direction = self.DOWN
            elif head_position[1] < tail_position[1]:
                self.current_direction = self.UP

            return None  # keep direction

        if self.changed_direction:
            self.changed_direction = False
            return None  # keep direction

        if self.current_direction == self.LEFT:
            self.current_direction = self.UP
        elif self.current_direction == self.UP:
            self.current_direction = self.RIGHT
        elif self.current_direction == self.RIGHT:
            self.current_direction = self.DOWN
        else:
            # noinspection PyAttributeOutsideInit
            self.current_direction = self.LEFT

        # noinspection PyAttributeOutsideInit
        self.changed_direction = True
        return self.current_direction
