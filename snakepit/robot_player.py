import asyncio
import signal
import json
from logging import getLogger
from aiohttp import ClientSession, WSMsgType

from .world import World
from .datatypes import Char
from .messaging import Messaging
from .robot_snake import RobotSnake

logger = getLogger(__name__)


class RobotPlayer(Messaging):
    def __init__(self, name, snake_class=RobotSnake, url='http://localhost:8000/connect'):
        self._first_render_sent = False
        self.frame = 0
        self.speed = 0
        self.loop = None
        self.running = False
        self.name = name
        self.url = url
        self.id = None
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

    def _handle_ws_message(self, data):
        tick = start = stop = False

        for args in data:
            cmd = args[0]

            if cmd == self.MSG_HANDSHAKE:
                self.name = args[1]
                self.id = args[2]
                self.snake._game_settings = settings = args[3]
                self.speed = settings['speed']
                self.frame = settings['frame']
            elif cmd == self.MSG_RESET_WORLD:
                self.world.reset()
            elif cmd == self.MSG_ERROR:
                raise SystemError(args[1])
            elif cmd == self.MSG_WORLD:
                self.world.load(args[1])
            elif cmd == self.MSG_RENDER:
                self.frame, self.speed = args[1], args[2]
                x, y = args[3], args[4]
                self.world[y][x] = Char(args[5], args[6])

                if self._first_render_sent:
                    tick = True
                else:
                    self._first_render_sent = start = True

            elif cmd == self.MSG_P_JOINED:
                player_id = args[1]
                logger.info('New player: %s', args)
                self.players[player_id] = args[1:]

                if player_id == self.id:
                    self.snake.color = args[3]

            elif cmd == self.MSG_P_GAMEOVER:
                player_id = args[1]
                logger.info('Game over for player: %s' % self.players.pop(player_id, None))

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

    async def ws_session(self):
        async with ClientSession() as session:
            async with session.ws_connect(self.url) as ws:
                await ws.send_json([self.MSG_NEW_PLAYER, self.name])
                await ws.send_json([self.MSG_JOIN])

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
                                await ws.send_json(response_msg)

                    elif msg.type == WSMsgType.CLOSED:
                        logger.info('Connection closed')
                        break
                    elif msg.type == WSMsgType.ERROR:
                        raise SystemError('Connection error')
                    else:
                        logger.warning('Unknown message type: %s', msg.type)

            logger.warning('Connection closed')

    def run(self):
        if self.running:
            raise RuntimeError('Already running')

        self.running = True
        self.loop = asyncio.get_event_loop()
        self.loop.add_signal_handler(signal.SIGTERM, self.stop)

        try:
            self.loop.run_until_complete(self.ws_session())
        except RuntimeError as exc:
            logger.warning('%s', exc)
        except KeyboardInterrupt as exc:
            logger.warning('Stopping %r (%r)', self, exc)
        finally:
            self.loop.close()
            self.running = False

    def stop(self):
        if self.running and self.loop:
            logger.warning('Stopping %r', self)
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
