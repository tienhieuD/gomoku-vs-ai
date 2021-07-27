import math
import turtle
from pprint import pprint as print

import functools
import time


def timer(name=None):
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            t1 = time.time()
            res = func(*args, **kwargs)
            t2 = time.time()
            print(name + " " + str(t2 - t1))
            return res

        return wrapper

    return inner


class Config:
    EMPTY = ' '
    SIZE_WIDTH = 480
    SIZE_HEIGHT = 480
    BG_COLOR = '#EFEFEF'
    BORDER_COLOR = '#999'
    RESULT_COLOR = '#333'
    TRACER = 2
    PLAYER_X_COLOR = "#f44336"
    PLAYER_O_COLOR = "#3f51b5"
    DEFAULT_FONT = lambda size: ('Consolas', round(15 * 24 / size), 'bold')
    DEFAULT_FONT_CENTER_OFFSET = (0.235, 1.05)
    WIN_COUNT = 3


class Player:
    X = "x"
    O = "o"

    _x = None
    _o = None

    @staticmethod
    def getTurtle(player: str):
        if not Player._x:
            Player._x = turtle.Turtle()
            Player._x.color(Config.PLAYER_X_COLOR)
            Player._x.ht()

        if not Player._o:
            Player._o = turtle.Turtle()
            Player._o.color(Config.PLAYER_O_COLOR)
            Player._o.ht()

        if player == Player.X:
            return Player._x

        if player == Player.O:
            return Player._o


class Board:
    _data = []
    _size = None
    _screen = None
    _turn = Player.X
    _over = False
    _cache = {}

    # Statistics
    count_minimax = None

    def __init__(self, size: int):
        self._size = size
        self.init_data()
        self._screen = turtle.Screen()

    def set_cache(self, key, value):
        self._cache[key] = value

    def get_cache(self, key):
        return self._cache.get(key)

    # def check_cache(self, key, value):
    #     if not self.get_cache(key):
    #         self.set_cache(key, value)
    #     return self.get_cache(key)

    def init_data(self):
        for i in range(self._size):
            self._data.append([Config.EMPTY] * self._size)

    def switch_turn(self):
        if self._turn == Player.X:
            self._turn = Player.O
        else:
            self._turn = Player.X

    def _undo(self, x, y):
        self.switch_turn()
        self._data[y][x] = Config.EMPTY

    def check_result(self, xx, yy):
        player = self._data[yy][xx]

        # Check horizontal -
        x, y = xx, yy
        count = 0
        while x >= 0 and self._data[y][x] == player:
            x -= 1
        while x + 1 < self._size and self._data[y][x + 1] == player:
            count += 1
            x += 1
        if count == Config.WIN_COUNT:
            return player

        # Check vertical |
        x, y = xx, yy
        count = 0
        while y >= 0 and self._data[y][x] == player:
            y -= 1
        while y + 1 < self._size and self._data[y + 1][x] == player:
            count += 1
            y += 1
        if count == Config.WIN_COUNT:
            return player

        # Check line \
        x, y = xx, yy
        count = 0
        while x >= 0 and y >= 0 and self._data[y][x] == player:
            y -= 1
            x -= 1
        while y + 1 < self._size and x + 1 < self._size and self._data[y + 1][x + 1] == player:
            count += 1
            y += 1
            x += 1
        if count == Config.WIN_COUNT:
            return player

        # Check line /
        x, y = xx, yy
        count = 0
        while x >= 0 and y < self._size and self._data[y][x] == player:
            y += 1
            x -= 1
        while y - 1 >= 0 and x + 1 < self._size and self._data[y - 1][x + 1] == player:
            count += 1
            y -= 1
            x += 1
        if count == Config.WIN_COUNT:
            return player

        # Check if draw
        for row in self._data:
            if any(cell == Config.EMPTY for cell in row):
                return

        return "DRAW"

    def move(self, x, y):
        self._data[y][x] = self._turn

        # Draw X / O
        player_turtle = Player.getTurtle(self._turn)
        player_turtle.penup()
        player_turtle.goto(x + Config.DEFAULT_FONT_CENTER_OFFSET[0], y + Config.DEFAULT_FONT_CENTER_OFFSET[1])
        player_turtle.pendown()
        player_turtle.write(self._turn, font=Config.DEFAULT_FONT(self._size))
        player_turtle.penup()
        player_turtle.ht()
        # End Draw X / O

    def onclick(self, x, y, ai_click=False):
        x, y = math.floor(x), math.floor(y)

        if self._over:
            return

        # click out the board
        if x >= self._size or x < 0 or y >= self._size or y < 0:
            return

        if self._data[y][x] != Config.EMPTY:
            return

        self.move(x, y)

        result = self.check_result(x, y)
        if result:
            self._over = True
            self.write_result("the winner is %s" % result)
            return

        self.switch_turn()

        # AI mode
        if ai_click:
            return
        xx, yy = self.find_best_move(x, y)
        self.onclick(xx, yy, ai_click=True)
        # End - AI move

    def available_move(self):
        moves = []
        for y in range(self._size):
            for x in range(self._size):
                if self._data[y][x] == Config.EMPTY:
                    moves.append((x, y))
        return moves

    def find_best_move(self, x, y):
        self.count_minimax = 0

        best_score = -math.inf
        best_move = None

        for x, y in self.available_move():
            self._data[y][x] = Player.O
            score = self.minimax(x, y, is_max=False, depth=0, alpha=-math.inf, beta=math.inf)
            self._data[y][x] = Config.EMPTY
            print(score)

            if score > best_score:
                best_score = score
                best_move = x, y

        # print(self.count_minimax)
        return best_move

    def minimax(self, x, y, is_max, depth, alpha, beta):
        self.count_minimax += 1

        result = self.check_result(x, y)
        if result == Player.X:
            return -10000000 + depth
        elif result == Player.O:
            return 10000000 - depth
        elif result == "DRAW":
            return 0

        if is_max:
            best_score = -math.inf
            for xx, yy in self.available_move():
                self._data[yy][xx] = Player.O

                score = self.minimax(xx, yy, is_max=False, depth=depth + 1, alpha=alpha, beta=beta)

                self._data[yy][xx] = Config.EMPTY
                best_score = max(best_score, score)

                alpha = max(alpha, score)
                if beta <= alpha:
                    break

            return best_score
        else:
            best_score = math.inf
            for xx, yy in self.available_move():
                self._data[yy][xx] = Player.X
                score = self.minimax(xx, yy, is_max=True, depth=depth + 1, alpha=alpha, beta=beta)
                self._data[yy][xx] = Config.EMPTY
                best_score = min(best_score, score)

                beta = min(beta, score)
                if beta <= alpha:
                    break

            return best_score

    def write_result(self, message):
        x = self._size / 2
        y = self._size / 4
        xx, yy = x + x / 100, y + y / 100
        font = ('Arial', 24, 'normal')
        write = getattr(self._screen, "_write")
        write((xx, yy), message, 'center', font, "#6fbf73")
        write((x, y), message, 'center', font, "#357a38")

    def draw(self):
        self._screen.onclick(self.onclick)
        self._screen.setup(width=Config.SIZE_WIDTH, height=Config.SIZE_HEIGHT)
        self._screen.setworldcoordinates(0, self._size, self._size, 0)
        # self._screen.setup(width=1.0, height=1.0)

        self._screen.bgcolor(Config.BG_COLOR)
        self._screen.tracer(Config.TRACER)

        # Set up border lines
        border = turtle.Turtle()
        border.penup()
        border.ht()
        border.color(Config.BORDER_COLOR)

        for i in range(self._size + 1):
            border.goto(i, 0)
            border.pendown()
            border.goto(i, self._size)
            border.penup()

        for i in range(self._size + 1):
            border.goto(0, i)
            border.pendown()
            border.goto(self._size, i)
            border.penup()
        # End - Set up border lines

        self._screen.listen()
        self._screen.mainloop()


class Game:
    _board = None

    def __init__(self, board: Board):
        self._board = board

    def start(self):
        self._board.draw()


if __name__ == '__main__':
    board = Board(3)
    game = Game(board)
    game.start()
