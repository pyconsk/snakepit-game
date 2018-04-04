from .robot_snake import RobotSnake


class UserSnake(RobotSnake):
    _next_direction = None

    def next_direction(self, initial=False):
        next_direction = self._next_direction
        self._next_direction = None

        return next_direction

    def set_left(self):
        self._next_direction = self.LEFT

    def set_right(self):
        self._next_direction = self.RIGHT

    def set_up(self):
        self._next_direction = self.UP

    def set_down(self):
        self._next_direction = self.DOWN


class SteeringUserSnake(RobotSnake):
    _next_direction = None
    current_direction = None

    def get_current_direction(self):
        head_position = [0, 0]
        tail_position = [0, 0]

        # lets find out our direction
        for y in range(self.world.SIZE_Y):
            for x in range(self.world.SIZE_X):
                char, color = self.world[y][x]

                if color == self.color:  # our snake
                    if char == self.CH_TAIL:
                        tail_position = [x, y]
                    elif char == self.CH_HEAD:
                        head_position = [x, y]
                    elif char == self.CH_BODY:
                        pass

        if tail_position[0] == head_position[0]:
            if tail_position[1] > head_position[1]:
                return self.UP
            else:
                return self.DOWN
        else:
            if tail_position[0] > head_position[0]:
                return self.LEFT
            else:
                return self.RIGHT

    def next_direction(self, initial=False):
        if initial:
            self.current_direction = self.get_current_direction()

        next_direction = self._next_direction
        self._next_direction = None

        try:
            return next_direction
        finally:
            if next_direction:
                self.current_direction = next_direction

    def set_left(self):
        if self.current_direction == self.UP:
            new_direction = self.LEFT
        elif self.current_direction == self.LEFT:
            new_direction = self.DOWN
        elif self.current_direction == self.DOWN:
            new_direction = self.RIGHT
        elif self.current_direction == self.RIGHT:
            new_direction = self.UP
        else:
            return

        self._next_direction = new_direction

    def set_right(self):
        if self.current_direction == self.UP:
            new_direction = self.RIGHT
        elif self.current_direction == self.LEFT:
            new_direction = self.UP
        elif self.current_direction == self.DOWN:
            new_direction = self.LEFT
        elif self.current_direction == self.RIGHT:
            new_direction = self.DOWN
        else:
            return

        self._next_direction = new_direction
