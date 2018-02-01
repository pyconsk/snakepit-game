import asyncio

try:
    # noinspection PyUnresolvedReferences
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from logging import getLogger
from aiohttp import web

from . import settings
from .game import Game
from .utils import get_client_address, validate_settings, validate_player_name, validate_player_id
from .messaging import json, Messaging
from .exceptions import ValidationError

logger = getLogger(__name__)


def _get_new_player_info(data):
    try:
        player_name = data[1]
    except IndexError:
        raise ValidationError('Missing player name.')
    else:
        player_name = validate_player_name(player_name)

    try:
        player_id = data[2]
    except IndexError:
        player_id = None
    else:
        if player_id:
            player_id = validate_player_id(player_id)
        else:
            player_id = None

    return player_name, player_id


async def ws_handler(request):
    client_address = get_client_address(request)
    logger.info('Connected to "%s" from %s', request.url, client_address)
    game = request.app['game']
    player = None
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.tp == web.MsgType.TEXT:
            logger.debug('Got message from %s: %s', client_address, msg.data)

            try:
                data = json.loads(msg.data)
            except ValueError:
                logger.error('Invalid JSON data from %s: %s', client_address, msg.data)
                continue

            # noinspection PyUnresolvedReferences
            if isinstance(data, int) and player:
                # Interpret as key code
                player.keypress(data)
            elif not isinstance(data, list) or not data:
                logger.error('Invalid data from %s: %s', client_address, data)
                continue
            elif data[0] == Messaging.MSG_PING:
                logger.debug('Received ping from %s (%s)', client_address, data[1:])
                await ws.send_json([Messaging.MSG_PONG] + data[1:], dumps=json.dumps)
            elif data[0] == Messaging.MSG_NEW_PLAYER:
                if not player:
                    try:
                        # noinspection PyTypeChecker
                        player_name, player_id = _get_new_player_info(data)
                    except ValidationError as exc:
                        logger.error('Invalid new player request: %r', exc)
                        await ws.send_json([Messaging.MSG_ERROR, str(exc)])
                        break
                    else:
                        player = await game.new_player(player_name, ws, player_id=player_id)
                        logger.info('Connected %r to the game', player)
            elif data[0] == Messaging.MSG_JOIN:
                if not game.running:
                    await game.reset_world()
                    logger.info('Starting game loop by %r', player)

                    try:
                        asyncio.ensure_future(game_loop(game))
                    except asyncio.CancelledError:
                        pass

                await game.join(player)

        elif msg.tp == web.MsgType.CLOSE:
            break
        else:
            logger.warning('Unknown message type from %s: %s', client_address, msg.type)

    if player:
        await game.player_disconnected(player)

    logger.info('Closed connection from %s: %r', client_address, player)

    return ws


async def game_loop(game):
    server_shutdown = False
    game.running = True
    game_sleep = 1.0 / game.speed
    game_speed_max = settings.GAME_SPEED_MAX
    game_speed_increase = settings.GAME_SPEED_INCREASE
    game_speed_increase_rate = settings.GAME_SPEED_INCREASE_RATE
    game_frames_max = settings.GAME_FRAMES_MAX

    try:
        while True:
            await game.next_frame()

            if not game.players_alive_count:
                logger.info('Stopping game loop - no players alive')
                break

            if game_frames_max and game.frame >= game_frames_max:
                logger.info('Maximum frames reached - killing all players')
                await game.kill_all()

                if settings.GAME_SHUTDOWN_ON_FRAMES_MAX:
                    await game.shutdown(message='Server shutdown because frames limit reached')
                    server_shutdown = True
                    break

            if (game_speed_increase and game_speed_increase <= game.frame and
                    (not game_speed_max or game.speed < game_speed_max)):
                game.speed = round(game.speed + game.speed * game_speed_increase_rate, 6)
                game_sleep = 1.0 / game.speed

            await asyncio.sleep(game_sleep)

            await game.disconnect_closed()
    except BaseException as exc:
        await game.send_error_all("Internal server error: %s" % exc)
        raise
    finally:
        game.running = False

    if server_shutdown:
        import os
        import signal
        os.kill(os.getpid(), signal.SIGTERM)


async def on_shutdown(app):
    logger.warning('Server shutdown')
    game = app.get('game', None)

    if game:
        await game.shutdown()


def run(host=settings.SERVER_HOST, port=settings.SERVER_PORT, debug=settings.DEBUG):
    validate_settings(settings)

    app = web.Application(debug=debug)
    app['game'] = Game()

    app.router.add_route('GET', '/connect', ws_handler)
    app.router.add_static('/', settings.WEB_ROOT)

    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host=host, port=port)
