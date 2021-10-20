from pathlib import Path

kifu_path = Path('./kifu.csa')

with kifu_path.open(encoding='utf-8') as f:
  kifu_data = f.readlines()


class GameLogic:
  def __init__(self, kifu):
    self.header = kifu[:8]
    self.board_sets = kifu[8:17]
    self.prompt = [i.strip() for i in kifu[17:-1]]
    self.length_turn = len(self.prompt)
    self.game_board = self.init_board()

    self.sen_hand = []
    self.kou_hand = []

  def init_board(self):
    setlist = []
    for set in self.board_sets:
      # todo: 3つのchar で処理させ、分割させる
      x_line = '_' + set.strip()
      line = [x_line[i:i + 3].strip() for i in range(0, len(x_line), 3)]
      setlist.append(line[1:])
    return setlist

  def turn_purser(self, turn_data):
    turn_num = self.prompt.index(turn_data)
    piece_name = 'None'
    af_x = 0
    af_y = 0

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
    print(f'{turn_num: 3d}手目:', _after + piece_name)
    if not '00' in _before:
      be_y = 9 - int(_before[0])
      be_x = int(_before[1]) - 1
      self.game_board[be_x][be_y] = '*'
    else:
      be_y = None
      be_x = None
    af_y = 9 - int(_after[0])
    af_x = int(_after[1]) - 1
    self.game_board[af_x][af_y] = piece_name

  def print_board(self):
    print(f'後攻手駒: {self.kou_hand}')
    print('+---------------------------+')
    for board in self.game_board:
      line = ' '
      for piece in board:
        if '*' in piece:
          piece = ' * '
        line += piece
      print(line)
    print('+---------------------------+')
    print(f'先攻手駒: {self.sen_hand}')


if __name__ == '__main__':
  game = GameLogic(kifu_data)
  for n, p in enumerate(game.prompt):
    game.turn_purser(p)
    game.print_board()
    input()

