from pathlib import Path
from colorsys import hsv_to_rgb
import ui

# 9 x 9 の盤面
MTRX = 9


def load_kifu():
  _path = Path('./static/kifu.csa')
  with _path.open(encoding='utf-8') as f:
    _kifu_data = f.readlines()
  return _kifu_data


# --- reader


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


# xxx: 良きように振り分け
row_num = ['9', '8', '7', '6', '5', '4', '3', '2', '1']
clm_num = ['一', '二', '三', '四', '五', '六', '七', '八', '九']

piece_dic = {}


class Piece:
  def __init__(self):
    self.order = True


def x_board(n):
  return row_num[n]


def y_board(n):
  return clm_num[n]


class Cell(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self._text = ''
    self.label = ui.Label()
    self.label.alignment = ui.ALIGN_CENTER
    #self.label.text = '0, 0'
    self.label.text_color = 0
    self.label.font = ('Source Code Pro', 14)
    self.label.flex = 'WH'
    #self.label.size_to_fit()

    self.pos_x = ui.Label()
    self.pos_x.alignment = ui.ALIGN_CENTER
    self.pos_y = ui.Label()
    self.pos_y.alignment = ui.ALIGN_CENTER
    self.pos_x.font = self.pos_y.font = ('Source Code Pro', 8)
    #self.pos_x.flex = 'WTL'
    #self.pos_y.flex = 'WBR'
    self.add_subview(self.pos_x)
    self.add_subview(self.pos_y)

    self.add_subview(self.label)

  def set_label_pos(self, size, x, y, *args):
    # xxx: `color = args` とりあえず
    color = args[0]
    self.pos_x.bg_color = self.pos_y.bg_color = color

    pos_size = size / 4
    self.pos_x.width, self.pos_x.height = [pos_size] * 2
    self.pos_y.width, self.pos_y.height = [pos_size] * 2
    self.pos_y.x = size - self.pos_y.width
    self.pos_y.y = size - self.pos_y.height
    self.pos_x.text = f'{x_board(x)}'
    self.pos_y.text = f'{y_board(y)}'

  @property
  def text(self):
    self._text = self.label.text
    return self._text

  @text.setter
  def text(self, txt):
    self.label.text = txt
    self._text = self.label.text


class Dot(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 0


class StageMatrix(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    #self.bg_color = 'yellow'

    self.cells = [[(Cell()) for x in range(MTRX)] for y in range(MTRX)]

    [[self.add_subview(x) for x in y] for y in self.cells]

    self.dots = [[Dot() for dx in range(2)] for dy in range(2)]
    [[self.add_subview(dx) for dx in dy] for dy in self.dots]

  def set_matrix(self, parent_size):
    self.width = parent_size
    self.height = parent_size
    x_pos = 0
    y_pos = 0
    counter = 0
    len_cells = sum(len(l) for l in self.cells)
    cell_size = parent_size / MTRX
    for y, cells in enumerate(self.cells):
      for x, cell in enumerate(cells):
        if x % 2 == 0:
          if y % 2 == 0:
            boolen = True
          else:
            boolen = False
        else:
          if y % 2 == 0:
            boolen = False
          else:
            boolen = True
        h = counter / len_cells
        color = hsv_to_rgb(h, h, 1)
        cell.bg_color = color
        cell.bg_color = 'silver' if boolen else 'darkgray'
        #cell.label.bg_color = color
        cell.set_label_pos(cell_size, x, y, color)

        cell.width = cell_size
        cell.height = cell_size
        cell.x = x_pos
        cell.y = y_pos
        # xxx: 配列明記不要になったら`enumerate` を消す
        cell.text = f'{x_board(x)}, {y_board(y)}'
        counter += 1
        x_pos += cell_size
      x_pos = 0
      y_pos += cell_size
    self.set_dot()

  def set_dot(self):
    size = self.width / 64
    pos = self.width / 3
    x_pos = pos
    y_pos = pos
    for dots in self.dots:
      for dot in dots:
        dot.width = size
        dot.height = size
        dot.corner_radius = size
        dot.x = x_pos - (dot.width / 2)
        dot.y = y_pos - (dot.height / 2)
        x_pos += x_pos
      x_pos = pos
      y_pos += y_pos
      
  def set_game(self, board):
    for cells, clm in zip(self.cells, board):
      for cell, piece in zip(cells, clm):
        #print(piece)
        cell.text = piece
        #print(cell.text)


class StageView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'goldenrod'
    self.mtrx = StageMatrix()
    self.add_subview(self.mtrx)

    self.rows = [Cell() for r in range(MTRX)]
    self.clms = [Cell() for c in range(MTRX)]
    [self.add_subview(r) for r in self.rows]
    [self.add_subview(c) for c in self.clms]

  def set_layout(self, parent_size):
    self.width = parent_size
    self.height = parent_size
    min_size = parent_size / 16
    max_size = (parent_size - min_size) / MTRX
    x_pos = 0
    y_pos = min_size
    for n, row in enumerate(self.rows):
      # xxx: index の呼び方検討
      #print(self.rows.index(row))
      row.width = max_size
      row.height = min_size
      row.text = str(row_num[n])
      row.x = x_pos
      x_pos += max_size
    for n, clm in enumerate(self.clms):
      clm.width = min_size
      clm.height = max_size
      clm.text = str(clm_num[n])
      clm.x = x_pos
      clm.y = y_pos
      y_pos += max_size

    self.mtrx.set_matrix(parent_size - min_size)
    self.mtrx.y = min_size


class BoardView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'maroon'
    self.stage = StageView()
    self.add_subview(self.stage)
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
    #self.add_subview(self.field)

    self.update_load()
    #self.stage.mtrx.set_game(self.game.game_board)
    
    
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
    self.stage.mtrx.set_game(self.game.game_board)
    
    

  def layout(self):
    square_size = min(self.width, self.height)
    self.stage.set_layout(square_size)
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
    
    
    self.stage.mtrx.set_game(self.game.game_board)


# --- Root View


class RootView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'slategray'
    self.board = BoardView()
    self.board.flex = 'WH'
    self.add_subview(self.board)


if __name__ == '__main__':
  root = RootView()
  root.present(style='fullscreen', orientations=['portrait'])

