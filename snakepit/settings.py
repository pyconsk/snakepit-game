import os
import logging

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
WEB_ROOT = os.path.join(PROJECT_DIR, 'var', 'www')
TOP_SCORES_FILE = os.path.join(PROJECT_DIR, 'var', 'run', 'top_scores.txt')

DEBUG = False

# Logging
LOG_FORMAT = '%(asctime)s %(levelname)-8s %(name)s: %(message)s'
LOG_LEVEL = logging.INFO

# Snake-pit settings
GAME_SPEED = 6.0  # fps, the more the faster
GAME_SPEED_INCREASE = None  # frame number after which the game should get faster (see GAME_SPEED_INCREASE_RATE)
GAME_SPEED_INCREASE_RATE = 0.001  # apply this factor to current game speed during each frame
GAME_SPEED_MAX = None  # fps limit when GAME_SPEED_INCREASE is active
GAME_FRAMES_MAX = None  # maximum number of frames; the game ends at this point

MAX_PLAYERS = 6
MAX_TOP_SCORES = 15
NUM_COLORS = 6  # set according to the number of css classes

FIELD_SIZE_X = 40  # game field size in characters
FIELD_SIZE_Y = 40

INIT_LENGTH = 5
INIT_MIN_DISTANCE_BORDER = 2
INIT_RETRIES = 10  # number of snake rendering retries (sometimes the snake just cannot be rendered)

DIGIT_MIN = 1
DIGIT_MAX = 9

KILL_POINTS = 1000  # player points for a successful kill

STONES_ENABLED = False

DIGIT_SPAWN_RATE = 6  # probability to spawn per frame in %
STONE_SPAWN_RATE = 6  # digit spawn is calculated for every snake while stone spawn is calculated once per frame

try:
    from .local_settings import *
except ImportError:
    pass

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
