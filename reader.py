#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path


def load_kifu():
    _path = Path('./kifu.csa')
    with _path.open() as f:
        kifu_data = f.readlines()
    return kifu_data


class KifuReader:
    def __init__(self, kifu_data):
        self.header = kifu_data[:8]
        self.board_init = kifu_data[8:17]
        self.prompt = [i.strip() for i in kifu_data[17:-1]]


if __name__ == '__main__':
    kifu = load_kifu()
    KifuReader(kifu)
