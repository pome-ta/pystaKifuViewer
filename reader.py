#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path


def load_kifu():
  _path = Path('./kifu.csa')
  with _path.open(encoding='utf-8') as f:
    _kifu_data = f.readlines()
  return _kifu_data


class KifuReader:
  def __init__(self, data):
    _header = data[:8]
    self.board_init = data[8:17]
    self.prompter = [i.strip() for i in data[17:-1]]
    self.game_board = self.init_board(self.board_init)

  def init_board(self, board):
    # `+` 先手
    self.sente_hand = []
    # `-` 後手
    self.gote_hand = []

    setup_board = []
    for setup in board:
      # 3つのchar として分離させる
      x_line = '_' + setup.strip()
      one_line = [x_line[i:i + 3].strip() for i in range(0, len(x_line), 3)]
      setup_board.append(one_line[1:])
    return setup_board

  def print_board(self):
    out_txt = f'後手手駒: {self.gote_hand}\n'
    out_txt += '  9  8  7  6  5  4  3  2  1\n'
    out_txt += '+---------------------------+\n'
    #print(f'後手手駒: {self.gote_hand}')
    #print('+---------------------------+')
    kanji = ['一', '二', '三', '四', '五', '六', '七', '八', '九']
    for n, board in enumerate(self.game_board):
      line = ' '
      for piece in board:
        if piece == '*':
          piece = ' * '
        line += piece
      out_txt += line + f'\t{kanji[n]}\n'
      #print(line)
    #print('+---------------------------+')
    #print(f'先手手駒: {self.sente_hand}')
    #print('_')
    out_txt += '+---------------------------+\n'
    out_txt += f'先手手駒: {self.sente_hand}\n'
    #print('_')
    return out_txt
  
  
  def looper(self, turn):
    turn_num = turn + 1
    for loop in range(turn_num):
      for prompt in self.prompter[:loop]:
        self.__purser(prompt)
    
    field = ''
    after = self.after if self.after else 0
    piece_name = self.piece_name if self.piece_name else 0

    field += f'{turn_num:03d}手目: {after}{piece_name}\n'
    board = self.print_board()
    field += board
    return field

  def __purser(self, instruction):
    self.after = 0
    self.piece_name = 0
    if len(instruction) == 1:
      print('開始')
      self.game_board = self.init_board(self.board_init)
      return

    if '%' in instruction:
      return

    sg = instruction[0]
    before = instruction[1:3]
    after = instruction[3:5]
    piece_name = sg + instruction[5:]

    if not '00' in before:
      be_y = 9 - int(before[0])
      be_x = int(before[1]) - 1
      self.game_board[be_x][be_y] = '*'
    else:
      be_y = None
      be_x = None
      piece_pop = piece_name[1:]
      if '+' in piece_name:
        self.sente_hand.remove(piece_pop)
      if '-' in piece_name:
        self.gote_hand.remove(piece_pop)

    af_y = 9 - int(after[0])
    af_x = int(after[1]) - 1
    if self.game_board[af_x][af_y] != '*':
      piece_get = self.game_board[af_x][af_y]
      self.get_piece(piece_get)
    self.game_board[af_x][af_y] = piece_name
    
    self.after = after
    self.piece_name = piece_name

  def get_piece(self, get):
    piece = self.__convert_piece(get)
    if '+' in get:
      self.gote_hand.append(piece)
      self.gote_hand.sort()

    if '-' in get:
      self.sente_hand.append(piece)
      self.sente_hand.sort()

  def __convert_piece(self, piece):
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
  from pprint import pprint
  kifu_data = load_kifu()
  kifu = KifuReader(kifu_data)
  print(kifu.looper(99))
  

