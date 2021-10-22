#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path


def load_kifu():
    _path = Path('./kifu.csa')
    with _path.open() as f:
        _kifu_data = f.readlines()
    return _kifu_data


class KifuReader:
    def __init__(self, data):
        _header = data[:8]
        self.board_init = data[8:17]
        self.prompt = [i.strip() for i in data[17:-1]]
        self.game_board = self.init_board(self.board_init)

    @staticmethod
    def init_board(board):
        setup_board = []
        for setup in board:
            # 3つのchar として分離さす
            x_line = '_' + setup.strip()
            one_line = [x_line[i: i + 3].strip() for i in range(0, len(x_line), 3)]
            setup_board.append(one_line[1:])
        return setup_board

    def looper(self, turn):
        if len(turn) == 1:
            self.game_board = self.init_board(self.board_init)

        if '%' in turn:
            return
        sg = turn[0]
        before = turn[1:3]
        after = turn[3:5]
        piece_name = sg + turn[5:]
        a = 1


if __name__ == '__main__':
    kifu_data = load_kifu()
    kifu = KifuReader(kifu_data)
    for p in range(len(kifu.prompt)):
        pass

