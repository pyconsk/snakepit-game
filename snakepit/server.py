import asyncio
import json
from logging import getLogger
from aiohttp import web

from . import settings
from .game import Game
from .utils import normalize_player_name, get_client_address, validate_settings
from .messaging import Messaging

logger = getLogger(__name__)


async def ws_handler(request):
    client_address = get_client_address(request)
    logger.info('Connected to "%s" from %s', request.url, client_address)
    game = request.app['game']
    player = None
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # noinspection PyTypeChecker
    async for msg in ws:
        if msg.tp == web.MsgType.TEXT:
            logger.debug('Got message from %s: %s', client_address, msg.data)
            data = json.loads(msg.data)

            if isinstance(data, int) and player:
                # Interpret as key code
                player.keypress(data)
            elif not isinstance(data, list):
                logger.error('Invalid data from %s: %s', client_address, data)
                continue
            elif not player:
                if data[0] == Messaging.MSG_NEW_PLAYER:
                    player = game.new_player(normalize_player_name(data[1]), ws)
                    logger.info('Creating new %r', player)
            elif data[0] == Messaging.MSG_JOIN:
                if not game.running:
                    game.reset_world()
                    logger.info('Starting game loop by %r', player)
                    asyncio.ensure_future(game_loop(game))

                game.join(player)

        elif msg.tp == web.MsgType.CLOSE:
            break
        else:
            logger.warning('Unknown message type from %s: %s', client_address, msg.type)

    if player:
        game.player_disconnected(player)

    logger.info('Closed connection from %s: %r', client_address, player)

    return ws


async def game_loop(game):
    game.running = True

    try:
        while True:
            game.next_frame()

            if not game.players_alive_count:
                logger.info('Stopping game loop')
                break

            await asyncio.sleep(1./settings.GAME_SPEED)

            game.disconnect_closed()
    finally:
        game.running = False


def run(host=None, port=8000, debug=settings.DEBUG):
    validate_settings(settings)
    app = web.Application(debug=debug)
    app['game'] = Game()

    app.router.add_route('GET', '/connect', ws_handler)

    if debug:
        app.router.add_static('/', settings.WEB_ROOT)

    web.run_app(app, host=host, port=port)
