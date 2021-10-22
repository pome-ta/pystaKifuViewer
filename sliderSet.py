from pathlib import Path
import ui

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

    self.turn_num = 0
    # `+` 先手
    self.sente_hand = []
    # `-` 後手
    self.gote_hand = []
    self._after = 0
    self.piece_name = 0

  def init_board(self):
    setlist = []
    for set in self.board_sets:
      # todo: 3つのchar で処理させ、分割させる
      x_line = '_' + set.strip()
      line = [x_line[i:i + 3].strip() for i in range(0, len(x_line), 3)]
      setlist.append(line[1:])
    return setlist

  def looper(self, n):
    field = ''
    self.init_board()
    for p in self.prompt[:n]:
      self.turn_purser(p)

    turn_num = self.turn_num if self.turn_num else 0
    after = self._after if self._after else 0
    piece_name = self.piece_name if self.piece_name else 0

    field += f'{turn_num:03d}手目: {after}{self.piece_name}\n'
    #print(f'{self.turn_num:03d}手目: {self._after}{self.piece_name}')
    board = self.print_board()
    field += board
    return field

  def turn_purser(self, turn_data):

    if len(turn_data) == 1:
      self.game_board = self.init_board()
      #print('開始')
      return None

    if '%' in turn_data:
      self.turn_num += 1
      #print(f'全{self.turn_num:03d}手 {turn_data}: 終了')
      return None

    turn = turn_data[0]
    _before = turn_data[1:3]
    self._after = turn_data[3:5]
    self.piece_name = turn + turn_data[5:]
    #print(f'{self.turn_num:03d}手目: {_after}{piece_name}')

    if not '00' in _before:
      be_y = 9 - int(_before[0])
      be_x = int(_before[1]) - 1
      self.game_board[be_x][be_y] = '*'
    else:
      be_y = None
      be_x = None
      piece_pop = self.piece_name[1:]
      if '+' in self.piece_name:
        self.sente_hand.remove(piece_pop)
      if '-' in self.piece_name:
        self.gote_hand.remove(piece_pop)

    af_y = 9 - int(self._after[0])
    af_x = int(self._after[1]) - 1
    if self.game_board[af_x][af_y] != '*':
      piece_get = self.game_board[af_x][af_y]
      self.get_piece(piece_get)
    self.game_board[af_x][af_y] = self.piece_name
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


'''
if __name__ == '__main__':
  game = GameLogic(kifu_data)
  """
  for p in game.prompt:
    game.turn_purser(p)
    game.print_board()
    input()
  """
  p = game.looper(67)
  print(p)

'''


class RootView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'slategray'

    self.game = GameLogic(kifu_data)
    p = self.game.looper(0)
    self.max_value = self.game.length_turn

    self.sl = ui.Slider()
    self.sl.bg_color = 'red'
    self.sl.flex = 'W'
    self.sl.action = self.set_value
    self.sl.continuous = False

    self.add_subview(self.sl)

    self.value = ui.Label()
    self.value.bg_color = 'green'
    self.value.text = '0'
    self.add_subview(self.value)

    self.field = ui.TextView()
    self.field.font = ('Source Code Pro', 14)
    self.field.flex = 'W'
    self.field.text = p
    self.add_subview(self.field)

  def set_value(self, sender):
    value = int(sender.value * self.max_value)
    p = self.game.looper(value)
    self.field.text = p
    self.value.text = str(value)
    self.sl.value = value / self.max_value

  def draw(self):
    pass

  def layout(self):
    self.value.x = self.width / 2 - self.value.width / 2
    self.sl.y = self.height / 2
    self.value.y = self.sl.y + self.sl.height
    self.field.height = self.sl.y


if __name__ == '__main__':
  root = RootView()
  root.present(style='fullscreen', orientations=['portrait'])

