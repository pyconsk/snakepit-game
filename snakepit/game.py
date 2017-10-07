from random import randint, choice
import json

from . import settings
from .player import Player
from .messaging import Messaging
from .datatypes import Char, Draw


class Game(Messaging):
    COLOR_BLACK = 0
    CH_STONE = '#'
    CH_VOID = ' '
    VOID_CHAR = Char(CH_VOID, COLOR_BLACK)
    TOP_SCORES_FILE = settings.TOP_SCORES_FILE

    def __init__(self):
        self._last_id = 0
        self._colors = []
        self._players = {}
        self._top_scores = self._read_top_scores()
        self._world = self._create_world()
        self.running = False

    def _send_msg(self, player, *args):
        self._send_one(player.ws, [args])

    def _send_msg_all_multi(self, messages):
        wss = (player.ws for player in self._players.values())
        self._send_all(wss, messages)

    def _send_msg_all(self, *args):
        self._send_msg_all_multi([args])

    def _read_top_scores(self):
        try:
            with open(self.TOP_SCORES_FILE, 'r+') as fp:
                content = fp.read()

                if content:
                    top_scores = json.loads(content)
                else:
                    top_scores = []
        except FileNotFoundError:
            top_scores = []

        return top_scores

    def _store_top_scores(self):
        with open(self.TOP_SCORES_FILE, 'w') as fp:
            fp.write(json.dumps(self._top_scores))
            fp.close()

    def _calc_top_scores(self, player):
        if not player.score:
            return

        ts_dict = dict(self._top_scores)

        if player.score <= ts_dict.get(player.name, 0):
            return

        ts_dict[player.name] = player.score
        self._top_scores = sorted(ts_dict.items(), key=lambda x: -x[1])[:settings.MAX_TOP_SCORES]

    @staticmethod
    def _pick_random_color():
        return randint(1, settings.NUM_COLORS)

    def _pick_player_color(self):
        # pick a random color
        if not len(self._colors):
            # color 0 is reserved for interface and stones
            self._colors = list(range(1, settings.NUM_COLORS + 1))

        color = choice(self._colors)
        self._colors.remove(color)

        return color

    def _return_player_color(self, color):
        self._colors.append(color)

    @staticmethod
    def _render_text(text, color):
        # render in the center of play field
        pos_y = int(settings.FIELD_SIZE_Y / 2)
        pos_x = int(settings.FIELD_SIZE_X / 2 - len(text)/2)
        render = []

        for i in range(0, len(text)):
            render.append(Draw(pos_x + i, pos_y, text[i], color))

        return render

    def _apply_render(self, render):
        messages = []

        for draw in render:
            # apply to local
            self._world[draw.y][draw.x] = Char(draw.char, draw.color)
            # send messages
            messages.append([self.MSG_RENDER] + list(draw))

        self._send_msg_all_multi(messages)

    def _create_world(self):
        world = []

        for y in range(0, settings.FIELD_SIZE_Y):
            world.append([self.VOID_CHAR] * settings.FIELD_SIZE_X)

        return world

    def reset_world(self):
        for y in range(0, settings.FIELD_SIZE_Y):
            for x in range(0, settings.FIELD_SIZE_X):
                if self._world[y][x].char != self.CH_VOID:
                    self._world[y][x] = self.VOID_CHAR

        self._send_msg_all(self.MSG_RESET_WORLD)

    def _get_spawn_place(self):
        x, y = None, None

        for i in range(0, 2):
            x = randint(0, settings.FIELD_SIZE_X - 1)
            y = randint(0, settings.FIELD_SIZE_Y - 1)

            if self._world[y][x].char == self.CH_VOID:
                break

        return x, y

    def spawn_digit(self, right_now=False):
        render = []

        if right_now or randint(1, 100) <= settings.DIGIT_SPAWN_RATE:
            x, y = self._get_spawn_place()

            if x and y:
                char = str(randint(settings.DIGIT_MIN, settings.DIGIT_MAX))
                color = self._pick_random_color()
                render += [Draw(x, y, char, color)]

        return render

    def spawn_stone(self, right_now=False):
        render = []

        if right_now or randint(1, 100) <= settings.STONE_SPAWN_RATE:
            x, y = self._get_spawn_place()

            if x and y:
                render += [Draw(x, y, self.CH_STONE, self.COLOR_BLACK)]

        return render

    @property
    def top_scores(self):
        return [(t[0], t[1], randint(1, settings.NUM_COLORS)) for t in self._top_scores]

    @property
    def players_alive_count(self):
        return sum(int(p.alive) for p in self._players.values())

    def new_player(self, name, ws):
        self._last_id += 1
        player = Player(self._last_id, name, ws)

        self._send_msg(player, self.MSG_HANDSHAKE, player.name, player.id)
        self._send_msg(player, self.MSG_WORLD, self._world)
        self._send_msg(player, self.MSG_TOP_SCORES, self.top_scores)

        for p in self._players.values():
            if p.alive:
                self._send_msg(player, self.MSG_P_JOINED, p.id, p.name, p.color, p.score)

        self._players[player.id] = player

        return player

    def join(self, player):
        if player.alive:
            return

        if self.players_alive_count == settings.MAX_PLAYERS:
            self._send_msg(player, self.MSG_ERROR, "Maximum players reached")
            return

        color = self._pick_player_color()

        # init snake
        player.new_snake(color)
        # notify all about new player
        self._send_msg_all(self.MSG_P_JOINED, player.id, player.name, player.color, player.score)

    def game_over(self, player):
        player.alive = False
        self._send_msg_all(self.MSG_P_GAMEOVER, player.id)
        self._return_player_color(player.color)
        self._calc_top_scores(player)
        self._send_msg_all(self.MSG_TOP_SCORES, self.top_scores)

        render = player.render_game_over()

        if not self.players_alive_count:
            render += self._render_text(" >>> GAME OVER <<< ", self._pick_random_color())
            self._store_top_scores()

        return render

    def player_disconnected(self, player):
        player.ws = None

        if player.alive:
            render = self.game_over(player)
            self._apply_render(render)

        del self._players[player.id]
        del player

    def next_frame(self):
        messages = []
        render_all = []

        for p_id, p in self._players.items():
            if not p.alive:
                continue

            # check if snake already exists
            if len(p.snake):
                # check next position's content
                pos = p.next_position()
                # check bounds
                if pos.x < 0 or pos.x >= settings.FIELD_SIZE_X or\
                   pos.y < 0 or pos.y >= settings.FIELD_SIZE_Y:
                    render_all += self.game_over(p)
                    continue

                char = self._world[pos.y][pos.x].char
                grow = 0

                if char.isdigit():
                    # start growing next turn in case we eaten a digit
                    grow = int(char)
                    p.score += grow
                    messages.append([self.MSG_P_SCORE, p_id, p.score])

                elif char != self.CH_VOID:
                    render_all += self.game_over(p)
                    continue

                render_all += p.render_move()
                p.grow += grow

                # spawn digits proportionally to the number of snakes
                render_all += self.spawn_digit()
            else:
                # newborn snake
                render_all += p.render_new_snake()
                # and it's birthday present
                render_all += self.spawn_digit(right_now=True)

        if settings.STONES_ENABLED:
            render_all += self.spawn_stone()

        # send all render messages
        self._apply_render(render_all)

        # send additional messages
        if messages:
            self._send_msg_all_multi(messages)
