import curses
from random import randrange, choice
from collections import defaultdict
import os

actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
lettercode = [ord(ch) for ch in 'WASDRQwasdrq']

actions_dict = dict(zip(lettercode, actions * 2))

class GameField(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height = height       # 高
        self.width = width         # 宽
        self.win_value = 2048      # 过关分数
        self.score = 0             # 当前分数
        self.highscore = 0         # 最高分
        self.reset()               # 棋盘重置

    def spawn(self):
        # 从 100 中取一个随机数，如果这个随机数大于 89，new_element 等于 4，否则等于 2
        new_element = 4 if randrange(100) > 89 else 2
        # 得到一个随机空白位置的元组坐标
        (i, j) = choice([(i, j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element

    def reset(self):
        # 更新分数
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        # 初始化游戏开始界面
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.spawn()
        self.spawn()
        
    def draw(self, screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart  (Q)Exit      '
        gameover_string = '     GAME OVER      '
        win_string = '       YOU WIN!!!      '

        def cast(string):
            screen.addstr(string + '\n')

        def draw_hor_separator():
            line = '+' + ('+------' * self.width + '+')[1:]
            cast(line)

        def draw_row(row):
            cast(''.join('|{: ^6}'.format(num) if num > 0
                         else '|      ' for num in row) + '|')
        screen.clear()
        cast('SCORE: ' + str(self.score))
        if self.highscore != 0:
            cast('HIGHSCORE: ' + str(self.highscore))
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()

        # Some notifications
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)

    def move(self, action):
        def transpose(field):
            return [list(row) for row in zip(*field)]

        def invert(field):
            return [row[::-1] for row in field]


        def row_squeeze_left(row):
            length = len(row)
            for j in range(length - 1):
                if row[j:] == [0] * (length - j):  # determine if it's all zeros
                    break
                while row[j] == 0:
                    for indx in range(j, length - 1):
                        row[indx] = row[indx + 1]
                    row[length - 1] = 0
            return row

        def row_merge_left(row):
            length = len(row)
            is_moved = False
            for j in range(length - 1):
                if row[j] == row[j+1] and row[j] != 0:
                    is_moved = True
                    row[j] = row[j] * 2
                    self.score += row[j]
                    row[j+1] = 0
            return row, is_moved

        def move_left(field):
            nrow = len(field)
            while True:
                is_moved = 0
                for i in range(nrow):
                    field[i] = row_squeeze_left(field[i])
                    field[i], flag = row_merge_left(field[i])
                    if flag:
                        is_moved += 1
                if is_moved == 0:
                    break
            return field


        # move = {}
        # move['Left'] = lambda field: move_left()
        original = self.field
        if action == 'Left':
            self.field = move_left(self.field)
        elif action == 'Up':
            self.field = transpose(move_left(transpose(self.field)))
        elif action == 'Right':
            self.field = invert(move_left(invert(self.field)))
        elif action == 'Down':
            self.field = transpose(invert(move_left(invert(transpose(self.field)))))
        else:
            pass
        if original == self.field:
            return False
        else:
            self.spawn()
        return True

    def is_win(self):
        return any(any(i >= self.win_value for i in row) for row in self.field)


    def is_gameover(self):
        def transpose(field):
            return [list(row) for row in zip(*field)]

        flatten = [element for row in self.field for element in row]
        if 0 in flatten:
            return False
        nrow = self.height
        ncol = self.width

        for i in range(nrow - 1):
            is_identical = [c[0] == c[1] for c in zip(self.field[i], self.field[i + 1])]
            if True in is_identical:
                return False

        field = transpose(self.field)
        for j in range(ncol - 1):
            is_identical = [c[0] == c[1] for c in zip(field[j], field[j + 1])]
            if True in is_identical:
                return False
        return True

def get_user_action(keyboard):
    char = 'N'
    while char not in actions_dict:
        char = keyboard.getch()
    return actions_dict[char]

def main(stdscr):
    def init():
        ''' initialize the gameboard '''
        game_field.reset()
        return 'Game'

    def not_game(state):
        '''
        Games over --Two options:
        -> restart  -> exit
        '''
        game_field.draw(stdscr)
        action = get_user_action(stdscr)
        responses = defaultdict(lambda: state)
        responses['Restart'], responses['exit'] = 'Init', 'Exit'
        return responses[action]

    def game():
        game_field.draw(stdscr)
        action = get_user_action(stdscr)
        
        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'

        if game_field.move(action):
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'

    state_actions = {
        'Init': init,
        'Win': lambda: not_game('Win'),
        'Gameover': lambda: not_game('Gameover'),
        'Game': game
    }

    curses.use_default_colors()

    game_field = GameField(win=2048)

    state = 'Init'

    while state != 'Exit':
        state = state_actions[state]()

curses.wrapper(main)
