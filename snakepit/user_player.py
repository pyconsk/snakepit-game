import asyncio
from logging import getLogger

from .robot_player import RobotPlayer
from .user_snake import UserSnake, SteeringUserSnake

logger = getLogger(__name__)


class UserPlayer(RobotPlayer):
    DEFAULT_SNAKE_CLASS = UserSnake

    def process_cmd(self, cmd):
        if not self.snake:
            logger.error('Cannot process user command "%s" - snake is not initialized', cmd)
            return

        if cmd == self.CMD_LEFT:
            self.snake.set_left()
        elif cmd == self.CMD_RIGHT:
            self.snake.set_right()
        elif cmd == self.CMD_UP:
            self.snake.set_up()
        elif cmd == self.CMD_DOWN:
            self.snake.set_down()
        else:
            logger.warning('Got unknown user command: "%s"', cmd)
            return

        logger.info('Got user command: "%s"', cmd)


class RemoteControlledPlayer(UserPlayer):
    class UDPServerProtocol(asyncio.DatagramProtocol):
        transport = None

        def __init__(self, player):
            self.player = player

        def connection_made(self, transport):
            self.transport = transport

        def datagram_received(self, data, addr):
            msg = data.decode()
            logger.debug('Received UDP message %r from %s', msg, addr)

            try:
                cmd = int(msg)
            except (TypeError, ValueError):
                cmd = msg

            self.player.process_cmd(cmd)

    def __init__(self, *args, udp_server_addr='127.0.0.1', udp_server_port=3401, **kwargs):
        super().__init__(*args, **kwargs)
        self.udp_server = None
        self.udp_server_addr = udp_server_addr
        self.udp_server_port = udp_server_port

    def on_loop_start(self):
        if self.udp_server_addr and self.udp_server_port:
            local_addr = (self.udp_server_addr, self.udp_server_port)
            coro = self.loop.create_datagram_endpoint(lambda: self.UDPServerProtocol(self), local_addr=local_addr)
            logger.info('Starting UDP server on %s:%s', *local_addr)
            self.udp_server = self.loop.create_task(coro)

    def on_loop_stop(self):
        if self.udp_server:
            self.udp_server.cancel()


class SteeringUserPlayer(RemoteControlledPlayer):
    DEFAULT_SNAKE_CLASS = SteeringUserSnake
