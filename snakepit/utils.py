from .exceptions import ImproperlyConfigured
from .game import Game


def normalize_player_name(value):
    return value.strip()[:15]


def get_client_address(request):
    peername = request.transport.get_extra_info('peername')

    if isinstance(peername, (list, tuple)):
        return peername[0]
    else:
        return peername


def validate_settings(settings):
    if settings.MAX_PLAYERS > settings.NUM_COLORS:
        raise ImproperlyConfigured('Invalid MAX_PLAYERS (> NUM_COLORS)')

    if settings.FIELD_SIZE_X < len(Game.GAME_OVER_TEXT):
        raise ImproperlyConfigured('Invalid FIELD_SIZE_X (< %d)' % len(Game.GAME_OVER_TEXT))

    distance = settings.INIT_LENGTH + settings.INIT_MIN_DISTANCE_BORDER

    if settings.FIELD_SIZE_X / 2 < distance:
        raise ImproperlyConfigured('Invalid FIELD_SIZE_X, INIT_LENGTH or INIT_MIN_DISTANCE_BORDER')

    if settings.FIELD_SIZE_Y / 2 < distance:
        raise ImproperlyConfigured('Invalid FIELD_SIZE_Y, INIT_LENGTH or INIT_MIN_DISTANCE_BORDER')
