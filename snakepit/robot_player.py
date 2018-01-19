import asyncio
import signal
from time import time
from logging import getLogger
from aiohttp import ClientSession, WSMsgType

from .world import World
from .datatypes import Char
from .messaging import json, Messaging
from .robot_snake import RobotSnake

logger = getLogger(__name__)


class RobotPlayer(Messaging):
    def __init__(self, name, player_id=None, snake_class=RobotSnake, url='http://localhost:8000/connect'):
        self._first_render_sent = False
        self._last_ping = None
        self._ws = None
        self.frame = 0
        self.speed = 0
        self.latency = 0
        self.loop = None
        self.running = False
        self.name = name
        self.url = url
        self.id = player_id
        self.world = World()
        self.players = {}
        self.top_scores = []
        self.snake = snake_class({}, self.world, None)
        self.keymap = {
            RobotSnake.LEFT: 37,
            RobotSnake.UP: 38,
            RobotSnake.RIGHT: 39,
            RobotSnake.DOWN: 40,
        }

    def __repr__(self):
        return '<%s [id=%s] [name=%s] [color=%s]>' % (self.__class__.__name__, self.id, self.name, self.snake.color)

    def _handle_ws_message(self, data):  # noqa: R701
        tick = start = stop = False

        for args in data:
            cmd = args[0]

            if cmd == self.MSG_PONG:
                if self._last_ping == args[1]:
                    # noinspection PyTypeChecker
                    self.latency = time() * 1000 - self._last_ping
                    self._last_ping = None
                    logger.debug('Current latency: %s ms', round(self.latency, 2))
            elif cmd == self.MSG_SYNC:
                self.frame = args[1]
                self.speed = args[2]
            elif cmd == self.MSG_RENDER:
                x, y = args[1], args[2]
                self.world[y][x] = Char(args[3], args[4])

                if self._first_render_sent:
                    tick = True
                else:
                    self._first_render_sent = start = True
            elif cmd == self.MSG_HANDSHAKE:
                self.name = args[1]
                self.id = args[2]
                self.snake._game_settings = args[3]
            elif cmd == self.MSG_RESET_WORLD:
                self.world.reset()
            elif cmd == self.MSG_ERROR:
                raise SystemError(args[1])
            elif cmd == self.MSG_WORLD:
                self.world.load(args[1])
            elif cmd == self.MSG_P_JOINED:
                player_id = args[1]
                logger.info('New player: %s', args)
                self.players[player_id] = args[1:]

                if player_id == self.id:
                    self.snake.color = args[3]
            elif cmd == self.MSG_P_GAMEOVER:
                player_id = args[1]
                logger.info('Game over for player: %s', self.players.pop(player_id, None))

                if player_id == self.id:
                    stop = True

            elif cmd == self.MSG_P_SCORE:
                self.players[args[1]] = args[2]
            elif cmd == self.MSG_TOP_SCORES:
                self.top_scores[:] = args[1]
            else:
                logger.warning('Unknown message: %s', args)

        if tick or stop or start:
            response_msg = self.tick(start=start, stop=stop)

            if stop:
                raise RuntimeError('Game over')
        else:
            response_msg = None

        return response_msg

    async def ping_pong(self):
        while True:
            if self._ws and not self._last_ping:
                now = time() * 1000
                await self._ws.send_json([Messaging.MSG_PING, now, self.latency], dumps=json.dumps)
                self._last_ping = now

            if self.running:
                try:
                    await asyncio.sleep(1)
                except asyncio.CancelledError:
                    pass
            else:
                break

    async def ws_session(self):
        async with ClientSession() as session:
            async with session.ws_connect(self.url) as ws:
                await ws.send_json([self.MSG_NEW_PLAYER, self.name, self.id], dumps=json.dumps)
                await ws.send_json([self.MSG_JOIN], dumps=json.dumps)
                self._ws = ws

                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        logger.debug('Got message: %s', msg.data)
                        data = json.loads(msg.data)

                        if not isinstance(data, list) or len(data) < 1:
                            logger.error('Invalid data: %s', data)
                            break

                        if not isinstance(data[0], list):
                            data = [data]

                        try:
                            response_msg = self._handle_ws_message(data)
                        except RuntimeError as exc:
                            logger.info('%s', exc)
                            break
                        else:
                            if response_msg:
                                logger.info('Sending message: %s', response_msg)
                                await ws.send_json(response_msg, dumps=json.dumps)

                    elif msg.type == WSMsgType.CLOSED:
                        logger.info('Connection closed')
                        break
                    elif msg.type == WSMsgType.ERROR:
                        raise SystemError('Connection error')
                    else:
                        logger.warning('Unknown message type: %s', msg.type)

            self._ws = None
            logger.warning('Connection closed')

    def run(self):
        if self.running:
            raise RuntimeError('Already running')

        self.running = True
        self.loop = asyncio.get_event_loop()
        self.loop.add_signal_handler(signal.SIGTERM, self.stop)
        asyncio.ensure_future(self.ping_pong(), loop=self.loop)

        try:
            self.loop.run_until_complete(self.ws_session())
        except RuntimeError as exc:
            logger.warning('%s', exc)
        except KeyboardInterrupt as exc:
            logger.warning('Stopping %r (%r)', self, exc)
        except asyncio.CancelledError:
            pass
        finally:
            self.stop()
            self.running = False

    def stop(self):
        if self.running and self.loop:
            logger.warning('Stopping %r', self)

            for task in asyncio.Task.all_tasks():
                task.cancel()

            self.loop.stop()

    def tick(self, start=False, stop=False):
        response_msg = None

        if self.snake:
            if stop:
                self.snake.game_over()
            else:
                direction = self.snake.next_direction(initial=start)
                response_msg = self.keymap.get(direction, None)

        return response_msg
