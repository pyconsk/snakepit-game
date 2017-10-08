from . import settings
from .constants import CH_VOID, VOID_CHAR


class World(list):
    SIZE_X = settings.FIELD_SIZE_X
    SIZE_Y = settings.FIELD_SIZE_Y
    CH_VOID = CH_VOID
    VOID_CHAR = VOID_CHAR

    def __init__(self):
        super(World, self).__init__()
        for y in range(0, settings.FIELD_SIZE_Y):
            self.append([self.VOID_CHAR] * self.SIZE_X)

    def __repr__(self):
        return '<%s [%sx%s]>' % (self.__class__.__name__, self.SIZE_X, self.SIZE_Y)

    def reset(self):
        for y in range(0, settings.FIELD_SIZE_Y):
            for x in range(0, settings.FIELD_SIZE_X):
                if self[y][x][0] != self.CH_VOID:
                    self[y][x] = self.VOID_CHAR

    def load(self, data):
        self[:] = data
