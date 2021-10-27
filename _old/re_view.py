from pathlib import Path
from math import pi
import ui

BLACK = 0.24

MATRIX = 9
num_kan = {
  1: '一',
  2: '二',
  3: '三',
  4: '四',
  5: '五',
  6: '六',
  7: '七',
  8: '八',
  9: '九'
}

KOMA = {
  'OU': [['玉', '王'], 'black'],
  'HI': ['飛', 'black'],
  'KA': ['角', 'black'],
  'KI': ['金', 'black'],
  'GI': ['銀', 'black'],
  'KE': ['桂', 'black'],
  'KY': ['香', 'black'],
  'FU': ['歩', 'black'],
  'TO': ['と', 'red'],
  'NY': ['杏', 'red'],
  'NK': ['圭', 'red'],
  'NG': ['全', 'red'],
  'UM': ['馬', 'red'],
  'RY': ['龍', 'red']
}

TEBAN = {'+': '☖', '-': '☗'}

SENTE_rad = ui.Transform.rotation(0)
GOTE_rad = ui.Transform.rotation(pi)


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

  def print_prompt(self, prompt_num) -> str:
    instruction = self.prompter[prompt_num]
    if len(instruction) == 1:
      telop = '開始'
      return '開始'
    if '%' in instruction:
      return f'{prompt_num:03d}手目: 終局'
    teban = TEBAN[instruction[0]]
    _b = instruction[1:3]
    _a = instruction[3:5]
    # xxx: 雑処理
    if '00' in _b:
      b = '00'
    else:
      b = f'{_b[0]}{num_kan[int(_b[1])]}'
    a = f'{_a[0]}{num_kan[int(_a[1])]}'
    p = KOMA[instruction[5:]][0]
    if len(p) == 2:
      if '+' in instruction:
        p = p[0]
      if '-' in instruction:
        p = p[1]
    telop = instruction
    return f'{prompt_num:03d}手目: {teban}{a}{p}({b})'

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


# --- View


class Cell(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self._text = ''
    self.label = ui.Label()
    self.pos_x = ui.Label()
    self.pos_y = ui.Label()

    self.label.alignment = ui.ALIGN_CENTER
    self.pos_x.alignment = ui.ALIGN_CENTER
    self.pos_y.alignment = ui.ALIGN_CENTER

    self.label.text_color = 'black'
    self.label.font = ('Source Code Pro', 16)
    self.label.flex = 'WH'

    self.pos_x.font, self.pos_y.font = [('Source Code Pro', 8)] * 2
    self.add_subview(self.pos_x)
    self.add_subview(self.pos_y)
    self.add_subview(self.label)

  def set_label_pos(self, x, y, *args):
    # xxx: `color = args` とりあえず
    color = args[0]
    #self.pos_x.bg_color = self.pos_y.bg_color = color

    pos_size = min(self.width, self.height) / 4
    self.pos_x.alpha, self.pos_y.alpha = [0.25] * 2
    self.pos_x.width, self.pos_x.height = [pos_size] * 2
    self.pos_y.width, self.pos_y.height = [pos_size] * 2
    self.pos_y.x = self.width - self.pos_y.width
    self.pos_y.y = self.height - self.pos_y.height

    self.pos_x.text = f'{x}'
    self.pos_y.text = f'{num_kan[y]}'

  @property
  def text(self):
    self._text = self.label.text
    return self._text

  @text.setter
  def text(self, txt):
    self.label.text = txt
    self._text = self.label.text


class FieldMatrix(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.cells = [[(Cell()) for x in range(MATRIX)] for y in range(MATRIX)]
    [[self.add_subview(x) for x in y] for y in self.cells]

    class Dot(ui.View):
      def __init__(self, *args, **kwargs):
        ui.View.__init__(self, *args, **kwargs)
        self.bg_color = BLACK

    self.dots = [[Dot() for dx in range(2)] for dy in range(2)]
    [[self.add_subview(dx) for dx in dy] for dy in self.dots]

  def move_cells(self, prompt):
    for x in range(MATRIX):
      for y in range(MATRIX):
        _cell = self.cells[x][y]
        _cell.bg_color = None
    if len(prompt) == 1:
      return
    if '%' in prompt:
      return
    
    _a = prompt[3:5]
    a_x = MATRIX - int(_a[0])
    a_y = int(_a[1]) - 1
    self.cells[a_y][a_x].bg_color = 'peru'
    
    _b = prompt[1:3]
    if '00' in _b:
      pass
    else:
      b_x =MATRIX- int(_b[0])
      b_y = int(_b[1]) -1
      self.cells[b_y][b_x].bg_color = 'khaki'
      

  def setup_field(self, parent_size):
    self.width = parent_size
    self.height = parent_size

    cell_size = parent_size / MATRIX
    x_pos = 0
    y_pos = 0
    for x in range(MATRIX):
      for y in range(MATRIX):
        _cell = self.cells[x][y]
        _cell.width, _cell.height = [cell_size] * 2
        _cell.x = x_pos
        _cell.y = y_pos
        _cell.set_label_pos((MATRIX - y), (x + 1), 'red')
        x_pos += cell_size
      x_pos = 0
      y_pos += cell_size
    self.set_dot()

  def draw(self):
    self.set_needs_display()
    ui.set_color(BLACK)
    out_side = ui.Path.rect(0.0, 0.0, self.width, self.height)
    out_side.line_width = 2
    out_side.stroke()

    line = 0
    div = min(self.width, self.height) / MATRIX
    for m in range(MATRIX + 1):
      line_path = ui.Path()
      # x
      line_path.move_to(0, line)
      line_path.line_to(self.width, line)
      # y
      line_path.move_to(line, 0)
      line_path.line_to(line, self.height)
      line_path.line_width = 1 if (m % 3 == 0) else 0.5
      line_path.stroke()
      line += div

  def set_dot(self):
    size = self.width / 64
    pos = self.width / 3
    x_pos, y_pos = pos, pos
    for dots in self.dots:
      for dot in dots:
        dot.width, dot.height = size, size
        dot.corner_radius = size
        dot.x = x_pos - (dot.width / 2)
        dot.y = y_pos - (dot.height / 2)
        x_pos += x_pos
      x_pos = pos
      y_pos += y_pos

  def set_game(self, board):
    for cells, clm in zip(self.cells, board):
      for cell, piece in zip(cells, clm):
        cell.text = ''
        if '*' != piece:
          if piece[1:] == 'OU':
            _ou = KOMA[piece[1:]][0]
            cell.label.text_color = KOMA[piece[1:]][1]
            if piece[0] == '+':
              cell.text = _ou[0]
            if piece[0] == '-':
              cell.text = _ou[1]
          else:
            cell.text = KOMA[piece[1:]][0]
            cell.label.text_color = KOMA[piece[1:]][1]
          if piece[0] == '+':
            cell.label.transform = SENTE_rad
          if piece[0] == '-':
            cell.label.transform = GOTE_rad


class StageView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'goldenrod'
    self.field = FieldMatrix()
    self.add_subview(self.field)

  def setup_stage(self, parent_size):
    self.width = parent_size
    self.height = parent_size
    min_size = parent_size / 32
    # xxx: stage のsize により、変更
    self.field.setup_field(parent_size - min_size)
    self.field.x = (self.width / 2) - (self.field.width / 2)
    self.field.y = (self.height / 2) - (self.field.height / 2)
    
    #self.field.center = self.center


class BoardView(ui.View):
  """ BoardView
  盤面 index
    盤面 9 x 9
  slider
  前後 Button
  など、諸々を合体するところ
  
  RootView 上で、`flex = 'WH'` で全画面サイズ取得
    `self.layout` で、サイズ fix
  """

  def __init__(self, parent, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    #self.bg_color = 'maroon'
    self.parent = parent

    self.game = KifuReader(load_kifu())
    self.max = len(self.game.prompter) - 1
    self.min = 1 / self.max
    self.step = 0
    # `slider` 数値用
    self.step_list = [n * self.min for n in range(self.max + 1)]

    self.flex = 'WH'
    self.stage = StageView()
    self.add_subview(self.stage)

    self.sente = ui.View()
    self.gote = ui.View()
    
    self.sl = ui.Slider()
    self.sl.bg_color = 'darkgray'
    self.sl.flex = 'W'
    self.sl.action = self.steps_slider
    self.sl.continuous = False
    self.add_subview(self.sl)

    self.back_btn = self.set_btn('iob:ios7_arrow_back_32', 0)
    self.forward_btn = self.set_btn('iob:ios7_arrow_forward_32', 1)
    self.add_subview(self.back_btn)
    self.add_subview(self.forward_btn)

    # 盤面初期化
    self.game.looper()
    self.update_game()

  def steps_slider(self, sender):
    self.step = int(sender.value * self.max)
    self.update_game()

  def update_game(self):
    self.game.looper(self.step)
    self.stage.field.set_game(self.game.game_board)
    self.stage.field.move_cells(self.game.prompter[self.step])
    self.parent.name = self.game.print_prompt(self.step)

  def set_btn(self, img, back_forward):
    # forward: 1
    # back: 0
    _icon = ui.Image.named(img)
    _btn = ui.Button(title='')
    _btn.width = 64
    _btn.height = 128
    _btn.bg_color = 'darkgray'
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
    self.update_game()

  def layout(self):
    """ layout
    `self.flex = 'WH'` で、サイズfix
    """
    w = self.width
    h = self.height
    square_size = min(w, h)
    
    self.stage.setup_stage(square_size)
    self.stage.field.set_game(self.game.game_board)
    
    #self.stage.y = (square_size / 2) - (self.stage.height / 4)

    self.back_btn.y, self.forward_btn.y = [(self.stage.y + self.stage.height)* 1.024] * 2
    self.forward_btn.x = w - self.forward_btn.width

    self.sl.width = w - (self.back_btn.width + self.forward_btn.width)
    self.sl.height = min(self.back_btn.height, self.forward_btn.height)
    self.sl.center = self.center
    self.sl.y = min(self.back_btn.y, self.forward_btn.y)
    '''
    self.sl.y = square_size + (self.height - square_size) / 2
    self.back_btn.y = square_size + (self.height - square_size) / 2
    self.forward_btn.y = square_size + (self.height - square_size) / 2
    '''


class RootView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'slategray'
    self.board = BoardView(self)
    self.add_subview(self.board)


if __name__ == '__main__':
  # xxx: `path`
  root = RootView()
  root.present(style='fullscreen', orientations=['portrait'])

