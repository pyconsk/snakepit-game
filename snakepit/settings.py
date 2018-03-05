import os
import logging

#
# Base settings
DEBUG = bool(os.environ.get('SNAKEPIT_DEBUG', True))
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
WEB_ROOT = os.path.join(PROJECT_DIR, 'html')

SERVER_HOST = os.environ.get('SNAKEPIT_HOST', None)
SERVER_PORT = int(os.environ.get('SNAKEPIT_PORT', 8111))
SERVER_DEBUG = DEBUG

TOP_SCORES_FILE_DEFAULT = os.path.join(PROJECT_DIR, 'var', 'run', 'top_scores.txt')
TOP_SCORES_FILE = os.environ.get('SNAKEPIT_TOP_SCORES_FILE', TOP_SCORES_FILE_DEFAULT)

#
# Logging
LOG_FORMAT = '%(asctime)s %(levelname)-8s %(name)s: %(message)s'
LOG_LEVEL = logging.INFO

#
# These settings can be changed via environment variables prefixed by SNAKEPIT_
SNAKEPIT_SETTINGS = (
    ('SERVER_NAME', str),
    ('GAME_SPEED', float),
    ('GAME_SPEED_INCREASE', int),
    ('GAME_SPEED_INCREASE_RATE', float),
    ('GAME_SPEED_MAX', float),
    ('GAME_FRAMES_MAX', int),
    ('GAME_SHUTDOWN_ON_FRAMES_MAX', bool),
    ('MAX_PLAYERS', int),
    ('FIELD_SIZE_X', int),
    ('FIELD_SIZE_Y', int),
    ('KILL_POINTS', int),
    ('INIT_LENGTH', int),
    ('DIGIT_MIN', int),
    ('DIGIT_MAX', int),
    ('STONES_ENABLED', bool),
)

#
# Snakepit settings
SERVER_NAME = 'Snakepit1'

GAME_SPEED = 6.0  # fps, the more the faster
GAME_SPEED_INCREASE = None  # frame number after which the game should get faster (see GAME_SPEED_INCREASE_RATE)
GAME_SPEED_INCREASE_RATE = 0.001  # apply this factor to current game speed during each frame
GAME_SPEED_MAX = None  # fps limit when GAME_SPEED_INCREASE is active
GAME_FRAMES_MAX = None  # maximum number of frames; the game ends at this point

GAME_START_WAIT_FOR_PLAYERS = None  # number of connected players before the first frame can be rendered
GAME_SHUTDOWN_ON_FRAMES_MAX = False  # automatically shutdown the server process when GAME_FRAMES_MAX is reached

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

#
# Local settings - allow any settings to be defined in local_settings.py which is ignored by the VCS
try:
    from .local_settings import *  # noqa: F401,F403
except ImportError:
    pass

#
# SNAKEPIT_ environment variables override default and local settings
for setting, type_ in SNAKEPIT_SETTINGS:
    env_var = 'SNAKEPIT_' + setting

    if env_var in os.environ:
        globals()[setting] = type_(os.environ[env_var])

#
# Enabled logging
logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
