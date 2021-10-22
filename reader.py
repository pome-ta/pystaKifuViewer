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
        board_init = data[8:17]
        self.prompt = [i.strip() for i in data[17:-1]]
        self.game_board = self.init_board(board_init)

    @staticmethod
    def init_board(board):
        setup_board = []
        for setup in board:
            # 3つのchar として分離さす
            x_line = '_' + setup.strip()
            one_line = [x_line[i: i + 3].strip() for i in range(0, len(x_line), 3)]
            setup_board.append(one_line[1:])
        return setup_board


if __name__ == '__main__':
    from pprint import pprint

    kifu_data = load_kifu()
    kifu = KifuReader(kifu_data)
    pprint(kifu.prompt)
