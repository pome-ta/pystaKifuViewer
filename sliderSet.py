from pathlib import Path
import ui


def load_kifu():
  _path = Path('./kifu.csa')
  with _path.open(encoding='utf-8') as f:
    _kifu_data = f.readlines()
  return _kifu_data


class KifuReader:
  def __init__(self, data):
    _header = data[:8]
    self.board_init = data[8:17]
    # `data` 最終行の読み取り判断
    end_list = data[17:] if '%' in data[-1] else data[17:-1]
    self.prompter = [i.strip() for i in end_list]
    self.game_board = self.init_board(self.board_init)

  def init_board(self, board):
    self.sente_hand = []  # `+` 先手手駒
    self.gote_hand = []  # `-` 後手手駒

    self.after = '開始'
    self.piece_name = ''

    setup_board = []
    for setup in board:
      # 3つのchar として分離させる
      x_line = '_' + setup.strip()
      one_line = [x_line[i:i + 3].strip() for i in range(0, len(x_line), 3)]
      setup_board.append(one_line[1:])
    return setup_board

  def __print_board(self):
    # 盤面を`str` で返す
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
      self.__purser(loop)
    field = ''
    after = self.after if self.after else 0
    piece_name = self.piece_name if self.piece_name else ''

    field += f'{turn:03d}手目: {after}{piece_name}\n'
    board = self.__print_board()
    field += board
    return field

  def __purser(self, num):
    instruction = self.prompter[num]
    if len(instruction) == 1:
      self.game_board = self.init_board(self.board_init)
      return

    if '%' in instruction:
      self.after = instruction
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


class RootView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'slategray'

    self.game = KifuReader(load_kifu())

    self.max = len(self.game.prompter) - 1
    self.min = 1 / self.max
    self.step = 0
    # `slider` 数値用
    self.step_list = [n * self.min for n in range(self.max + 1)]

    self.sl = ui.Slider()
    self.sl.bg_color = 'red'
    self.sl.flex = 'W'
    self.sl.action = self.steps_slider
    self.sl.continuous = False
    self.add_subview(self.sl)

    self.value = ui.Label()
    self.value.bg_color = 'green'
    self.add_subview(self.value)

    self.back_btn = self.set_btn('iob:ios7_arrow_back_32', 0)
    self.forward_btn = self.set_btn('iob:ios7_arrow_forward_32', 1)
    self.add_subview(self.back_btn)
    self.add_subview(self.forward_btn)

    self.field = ui.TextView()
    self.field.font = ('Source Code Pro', 16)
    self.field.flex = 'W'
    self.field.text = self.game.looper()
    self.add_subview(self.field)

    self.update_load()

  def set_btn(self, img, back_forward):
    # forward: 1
    # back: 0
    _icon = ui.Image.named(img)
    _btn = ui.Button(title='')
    _btn.width = 64
    _btn.height = 128
    _btn.bg_color = 'magenta'
    _btn.image = _icon
    _btn.back_forward = back_forward
    _btn.action = self.steps_btn
    return _btn

  def steps_btn(self, sender):
    if sender.back_forward:
      if self.step < self.max:
        self.step += 1
    else:
      if self.step > 0:
        self.step -= 1
    self.sl.value = self.step_list[self.step]
    self.update_load()

  def steps_slider(self, sender):
    self.step = int(sender.value * self.max)
    self.update_load()

  def update_load(self):
    p = self.game.looper(self.step)
    self.field.text = p
    self.value.text = f'{self.step:03d}'

  def draw(self):
    pass

  def layout(self):
    center_pos = self.width / 2 - self.value.width / 2
    self.value.x = center_pos
    self.sl.y = self.height / 2
    self.value.y = self.sl.y + self.sl.height
    self.field.height = self.sl.y
    self.back_btn.y = self.sl.y + self.sl.height
    self.forward_btn.y = self.sl.y + self.sl.height
    self.back_btn.x = self.forward_btn.x = center_pos
    self.back_btn.x -= self.back_btn.width
    self.forward_btn.x += self.value.width


if __name__ == '__main__':
  root = RootView()
  root.present(style='fullscreen', orientations=['portrait'])

