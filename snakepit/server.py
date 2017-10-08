import asyncio
import json
from logging import getLogger
from aiohttp import web

from . import settings
from .game import Game
from .messaging import Messaging

logger = getLogger(__name__)


async def ws_handler(request):
    logger.info('Connected to "%s" from %s', request.url, request.host)
    game = request.app['game']
    player = None
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # noinspection PyTypeChecker
    async for msg in ws:
        if msg.tp == web.MsgType.TEXT:
            logger.debug('Got message: %s', msg.data)
            data = json.loads(msg.data)

            if isinstance(data, int) and player:
                # Interpret as key code
                player.keypress(data)
            elif not isinstance(data, list):
                logger.error('Invalid data: %s', data)
                continue
            elif not player:
                if data[0] == Messaging.MSG_NEW_PLAYER:
                    player = game.new_player(data[1], ws)
                    logger.info('Creating new player %s', player)
            elif data[0] == Messaging.MSG_JOIN:
                if not game.running:
                    game.reset_world()
                    logger.debug('Starting game loop for player %s', player)
                    asyncio.ensure_future(game_loop(game))

                game.join(player)

        elif msg.tp == web.MsgType.CLOSE:
            break
        else:
            logger.warning('Unknown message type: %s', msg.type)

    if player:
        game.player_disconnected(player)

    logger.info('Closed connection from player %s', player)

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
    finally:
        game.disconnect_all()
        game.running = False


def run(host=None, port=8000, debug=settings.DEBUG):
    app = web.Application(debug=debug)
    app['game'] = Game()

    app.router.add_route('GET', '/connect', ws_handler)

    if debug:
        app.router.add_static('/', settings.WEB_ROOT)

    web.run_app(app, host=host, port=port)
