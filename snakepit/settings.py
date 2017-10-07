import os

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
WEB_ROOT = os.path.join(PROJECT_DIR, 'var', 'www')
TOP_SCORES_FILE = os.path.join(PROJECT_DIR, 'var', 'top_scores.txt')

DEBUG = False

# Snake-pit settings
GAME_SPEED = 2.3  # fps, the more the faster

MAX_PLAYERS = 10
MAX_TOP_SCORES = 15
NUM_COLORS = 6  # set according to the number of css classes

FIELD_SIZE_X = 50  # game field size in characters
FIELD_SIZE_Y = 25

INIT_LENGTH = 3

DIGIT_MIN = 1
DIGIT_MAX = 9

STONES_ENABLED = True

DIGIT_SPAWN_RATE = 6  # probability to spawn per frame in %
STONE_SPAWN_RATE = 6  # digit spawn is calculated for every snake while stone spawn is calculated once per frame

try:
    from .local_settings import *
except ImportError:
    pass
