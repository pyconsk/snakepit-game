import asyncio
import json
from aiohttp import web

from . import settings
from .game import Game
from .messaging import Messaging


async def wshandler(request):
    print("Connected")
    game = request.app['game']
    player = None
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    while True:
        msg = await ws.receive()

        if msg.tp == web.MsgType.text:
            print("Got message %s" % msg.data)
            data = json.loads(msg.data)

            if isinstance(data, int) and player:
                # Interpret as key code
                player.keypress(data)
            elif not isinstance(data, list):
                print("Invalid data")
                continue
            elif not player:
                if data[0] == Messaging.MSG_NEW_PLAYER:
                    print("Creating new player")
                    player = game.new_player(data[1], ws)
            elif data[0] == Messaging.MSG_JOIN:
                if not game.running:
                    game.reset_world()

                    print("Starting game loop")
                    asyncio.ensure_future(game_loop(game))

                game.join(player)
            else:
                print("Doing nothing")

        elif msg.tp == web.MsgType.close:
            break

    if player:
        game.player_disconnected(player)

    print("Closed connection")

    return ws


async def game_loop(game):
    game.running = True

    while True:
        game.next_frame()

        if not game.players_alive_count:
            print("Stopping game loop")
            break

        await asyncio.sleep(1./settings.GAME_SPEED)

    game.running = False


def run(host=None, port=8000, debug=settings.DEBUG):
    event_loop = asyncio.get_event_loop()
    event_loop.set_debug(True)

    app = web.Application(debug=debug)
    app['game'] = Game()

    app.router.add_route('GET', '/connect', wshandler)

    if debug:
        app.router.add_static('/', settings.WEB_ROOT)

    web.run_app(app, host=host, port=port)
