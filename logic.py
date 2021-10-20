from pathlib import Path

kifu_path = Path('./kifu.csa')

with kifu_path.open(encoding='utf-8') as f:
  kifu_data = f.readlines()

#歩,香,桂,銀,金,角,飛,王(玉)
#FU,KY,KE,GI,KI,KA,HI,OU
#と,成,圭,全,馬,竜
#TO,NY,NK,NG,UM,RY

#FU -> TO
#KY -> NY
#KE -> NK
#GI -> NG
#KA -> UM
#HI -> RY


class GameLogic:
  def __init__(self, kifu):
    self.header = kifu[:8]
    self.board_sets = kifu[8:17]
    self.prompt = [i.strip() for i in kifu[17:-1]]
    self.length_turn = len(self.prompt)
    self.game_board = self.init_board()

    # '+'
    self.sente_hand = []
    # '-'
    self.gote_hand = []
    self.turn_num = 0

  def init_board(self):
    setlist = []
    for set in self.board_sets:
      # todo: 3つのchar で処理させ、分割させる
      x_line = '_' + set.strip()
      line = [x_line[i:i + 3].strip() for i in range(0, len(x_line), 3)]
      setlist.append(line[1:])
    return setlist

  def turn_purser(self, turn_data):
    if len(turn_data) == 1:
      self.game_board = self.init_board()
      print('開始')
      return None
    if '%' in turn_data:
      print('終了')
      return None

    turn = turn_data[0]
    _before = turn_data[1:3]
    _after = turn_data[3:5]
    piece_name = turn + turn_data[5:]
    print(f'{self.turn_num:03d}手目: {_after}{piece_name}')

    if not '00' in _before:
      be_y = 9 - int(_before[0])
      be_x = int(_before[1]) - 1
      self.game_board[be_x][be_y] = '*'
    else:
      be_y = None
      be_x = None
      piece_pop = piece_name[1:]
      if '+' in piece_name:
        self.sente_hand.remove(piece_pop)
      if '-' in piece_name:
        self.gote_hand.remove(piece_pop)
    af_y = 9 - int(_after[0])
    af_x = int(_after[1]) - 1
    if self.game_board[af_x][af_y] != '*':
      piece_get = self.game_board[af_x][af_y]
      self.get_piece(piece_get)
    self.game_board[af_x][af_y] = piece_name
    self.turn_num += 1

  def get_piece(self, get):
    piece = self._convert_piece(get)
    if '+' in get:
      self.gote_hand.append(piece)
      self.gote_hand.sort()

    if '-' in get:
      self.sente_hand.append(piece)
      self.sente_hand.sort()

  def _convert_piece(self, piece):
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

  def print_board(self):
    print(f'後手手駒: {self.gote_hand}')
    print('+---------------------------+')
    for board in self.game_board:
      line = ' '
      for piece in board:
        if '*' in piece:
          piece = ' * '
        line += piece
      print(line)
    print('+---------------------------+')
    print(f'先手手駒: {self.sente_hand}')


if __name__ == '__main__':
  game = GameLogic(kifu_data)
  for p in game.prompt:
    game.turn_purser(p)
    game.print_board()
    #input()

