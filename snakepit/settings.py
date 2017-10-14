import os
import logging

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
WEB_ROOT = os.path.join(PROJECT_DIR, 'var', 'www')
TOP_SCORES_FILE = os.path.join(PROJECT_DIR, 'var', 'run', 'top_scores.txt')

DEBUG = True

# Logging
LOG_FORMAT = '%(asctime)s %(levelname)-8s %(name)s: %(message)s'
LOG_LEVEL = logging.DEBUG

# Snake-pit settings
GAME_SPEED = 2.3  # fps, the more the faster

MAX_PLAYERS = 6
MAX_TOP_SCORES = 15
NUM_COLORS = 6  # set according to the number of css classes

FIELD_SIZE_X = 50  # game field size in characters
FIELD_SIZE_Y = 25

INIT_LENGTH = 5
INIT_MIN_DISTANCE_BORDER = 2
INIT_RETRIES = 10  # number of snake rendering retries (sometimes the snake just cannot be rendered)

DIGIT_MIN = 1
DIGIT_MAX = 9

KILL_POINTS = 1000  # player points for a successful kill

STONES_ENABLED = True

DIGIT_SPAWN_RATE = 6  # probability to spawn per frame in %
STONE_SPAWN_RATE = 6  # digit spawn is calculated for every snake while stone spawn is calculated once per frame

try:
    from .local_settings import *
except ImportError:
    pass

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
