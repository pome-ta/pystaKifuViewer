from pathlib import Path


def load_kifu():
    _path = Path('./kifu.csa')
    with _path.open(encoding='utf-8') as f:
        _kifu_data = f.readlines()
    return _kifu_data


class KifuReader:
    def __init__(self, data):
        self.sente_hand = []  # `+` 先手
        self.gote_hand = []  # `-` 後手

        self.after = 0
        self.piece_name = 0

        _header = data[:8]
        self.board_init = data[8:17]
        # self.prompter = [i.strip() for i in data[17:-1]]
        self.prompter = [i.strip() for i in data[17:]]
        self.game_board = self.init_board(self.board_init)

    @staticmethod
    def init_board(board):
        setup_board = []
        for setup in board:
            # 3つのchar として分離させる
            x_line = '_' + setup.strip()
            one_line = [x_line[i:i + 3].strip() for i in range(0, len(x_line), 3)]
            setup_board.append(one_line[1:])

        return setup_board

    def __print_board(self):
        out_txt = f'後手手駒: {self.gote_hand}\n'
        out_txt += '  9  8  7  6  5  4  3  2  1\n'
        out_txt += '+---------------------------+\n'
        kanji = ['一', '二', '三', '四', '五', '六', '七', '八', '九']
        for n, board in enumerate(self.game_board):
            line = ' '
            for piece in board:
                if piece == '*':
                    piece = ' * '
                line += piece
            out_txt += line + f'\t{kanji[n]}\n'
        out_txt += '+---------------------------+\n'
        out_txt += f'先手手駒: {self.sente_hand}\n'
        return out_txt

    def looper(self, turn=0):
        for loop in range(turn + 1):
            print(f'loop: {loop}')
            self.__purser(loop)
        '''
        turn_num = turn + 1
        if turn_num == 1:
            self.game_board = self.init_board(self.board_init)

        for loop in range(turn_num):
            for prompt in self.prompter[:loop]:
                self.__purser(prompt)
        '''

        field = ''
        after = self.after if self.after else 0
        piece_name = self.piece_name if self.piece_name else 0

        field += f'{turn:03d}手目: {after}{piece_name}\n'
        board = self.__print_board()
        field += board
        return field

    def __init_turn(self):
        pass

    def __purser(self, num):
        instruction = self.prompter[num]
        print(instruction)
        if len(instruction) == 1:
            self.game_board = self.init_board(self.board_init)
            return

        if '%' in instruction:
            self.after = '終了'
            return

        sg = instruction[0]
        before = instruction[1:3]
        after = instruction[3:5]
        piece_name = sg + instruction[5:]

        # xxx: if の反転したけど、直感に反する？
        if '00' in before:
            piece_pop = piece_name[1:]
            if '+' in piece_name:
                self.sente_hand.remove(piece_pop)
            if '-' in piece_name:
                self.gote_hand.remove(piece_pop)
        else:
            be_y = 9 - int(before[0])
            be_x = int(before[1]) - 1
            self.game_board[be_x][be_y] = '*'

        af_y = 9 - int(after[0])
        af_x = int(after[1]) - 1
        if self.game_board[af_x][af_y] != '*':
            piece_get = self.game_board[af_x][af_y]
            self.__get_piece(piece_get)
        self.game_board[af_x][af_y] = piece_name

        self.after = after
        self.piece_name = piece_name

    def __get_piece(self, get):
        piece = self.__convert_piece(get)
        if '+' in get:
            self.gote_hand.append(piece)
            self.gote_hand.sort()

        if '-' in get:
            self.sente_hand.append(piece)
            self.sente_hand.sort()

    @staticmethod
    def __convert_piece(piece):
        if 'TO' in piece:
            piece = 'FU'
        elif 'NY' in piece:
            piece = 'KY'
        elif 'NK' in piece:
            piece = 'KE'
        elif 'NG' in piece:
            piece = 'GI'
        elif 'UM' in piece:
            piece = 'KA'
        elif 'RY' in piece:
            piece = 'HI'
        else:
            piece = piece[1:]
        return piece


if __name__ == '__main__':
    game = KifuReader(load_kifu())
    prm_len = len(game.prompter) - 1
    stage = game.looper(prm_len)
    print(stage)
