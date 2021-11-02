from pathlib import Path
from math import pi, sin, cos
import ui

BLACK = 0.24
RED = 'red'

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
  'OU': [['玉', '王'], BLACK],
  'HI': ['飛', BLACK],
  'KA': ['角', BLACK],
  'KI': ['金', BLACK],
  'GI': ['銀', BLACK],
  'KE': ['桂', BLACK],
  'KY': ['香', BLACK],
  'FU': ['歩', BLACK],
  'TO': ['と', RED],
  'NY': ['杏', RED],
  'NK': ['圭', RED],
  'NG': ['全', RED],
  'UM': ['馬', RED],
  'RY': ['龍', RED]
}

TEBAN = {'+': '☖', '-': '☗'}

SENTE_rad = ui.Transform.rotation(0)
GOTE_rad = ui.Transform.rotation(pi)


def load_kifu(path=0):
  # xxx: path の取り回し
  load_path = Path(path) if path else Path('./kifu.csa')
  with load_path.open(encoding='utf-8') as f:
    data = f.readlines()
  return data


def split_data(data):
  HEAD = 8
  BOARD = 17
  PROMPT = data[BOARD:] if '%' in data[-1] else data[BOARD:-1]

  head = data[:HEAD]
  board = data[HEAD:BOARD]
  prompt = [i.strip() for i in PROMPT]
  return board, prompt


def sujidan_to_index(sujidan_str) -> [int, int]:
  suji_int = int(sujidan_str[0])
  dan_int = int(sujidan_str[1])
  x = dan_int - 1
  y = 9 - suji_int
  return x, y


def index_to_sujidan():
  pass


class KifuReader:
  def __init__(self, data, debug=0):
    self.game_board: list  # 現在のboard 上の状態
    self.board_init: list  # 初手盤面
    self.prompter: list  # 一手づつの指示情報

    self.sente_hand: list = []  # `+` 先手保持手駒
    self.gote_hand: list = []  # `-` 後手保持手駒
    self.after: str = ''
    self.piece_name: str = ''
    self.debug = debug  #+ 1

    self.board_init, self.prompter = split_data(data)
    self.game_board = self.init_board()

  def init_board(self):
    """
    最初の配置盤面を返す
    """
    self.sente_hand = []
    self.gote_hand = []
    self.after = '開始'
    self.piece_name = ''
    setup_board = []
    for setup in self.board_init:
      # 3つのchar として分離させる
      x_line = '_' + setup.strip()
      one_line = [x_line[i:i + 3].strip() for i in range(0, len(x_line), 3)]
      setup_board.append(one_line[1:])
    return setup_board

  def looper(self, turn=0):
    # todo: 毎回初手から、指定(`turn`) 手目までを回す
    [self.__purser(loop) for loop in range(turn + 1)]
    # todo: `debug` の`bool` により判定
    self.__print_board(turn) if self.debug else None

  def __purser(self, num):
    instruction = self.prompter[num]
    # todo: `num = 0` は、初期盤面で即時return
    if len(instruction) == 1:  # `+` 一文字のため
      self.game_board = self.init_board()
      return None
    # todo: 終局場面は即時return
    if '%' in instruction:  # `%TORYO` などをキャッチ
      self.after = instruction
      return None

    teban = instruction[0]
    before = instruction[1:3]
    after = instruction[3:5]
    piece = instruction[5:]

    # xxx: if の反転したけど、直感に反する？
    if '00' in before:
      if '+' in teban:
        self.sente_hand.remove(piece)
      if '-' in teban:
        self.gote_hand.remove(piece)
    else:
      be_x, be_y = sujidan_to_index(before)
      self.game_board[be_x][be_y] = '*'

    af_x, af_y = sujidan_to_index(after)
    if self.game_board[af_x][af_y] != '*':
      self.__get_piece(self.game_board[af_x][af_y])
    self.game_board[af_x][af_y] = teban + piece

    self.after = after
    self.piece_name = teban + piece

  def __get_piece(self, teban_piece):
    piece = self.__convert_piece(teban_piece)
    if '+' in teban_piece:
      self.gote_hand.append(piece)
      self.gote_hand.sort()

    if '-' in teban_piece:
      self.sente_hand.append(piece)
      self.sente_hand.sort()

  @staticmethod
  def __convert_piece(teban_piece):
    if 'TO' in teban_piece:
      piece = 'FU'
    elif 'NY' in teban_piece:
      piece = 'KY'
    elif 'NK' in teban_piece:
      piece = 'KE'
    elif 'NG' in teban_piece:
      piece = 'GI'
    elif 'UM' in teban_piece:
      piece = 'KA'
    elif 'RY' in teban_piece:
      piece = 'HI'
    else:
      piece = teban_piece[1:]
    return piece

  # xxx: 雑ゾーン
  def print_prompt(self, prompt_num) -> str:
    """
    header に手を表示
    """
    # xxx: View に持たせる？
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
    # 手駒を盤面に出す
    b = '打つ' if '00' in _b else f'{_b[0]}{num_kan[int(_b[1])]}'

    a = f'{_a[0]}{num_kan[int(_a[1])]}'
    p = KOMA[instruction[5:]][0]
    if len(p) == 2:
      if '+' in instruction:
        p = p[0]
      if '-' in instruction:
        p = p[1]
    telop = instruction
    return f'{prompt_num:03d}手目: {teban}{a}{p}({b})'

  def __print_board(self, turn):
    # 盤面を`str` で返す
    # テスト用
    field = ''
    field += f'{turn:03d}手目: {self.after}{self.piece_name}\n'

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

    board = out_txt
    field += board
    print(field)


# --- View

#pentagon


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

    self.pos_x.font, self.pos_y.font = [('Source Code Pro', 6)] * 2
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

  def draw(self):
    if self.text:
      self.setup_piece()

  def setup_piece(self):
    ui.set_color('gold')
    line = self.set_piece(self.width, self.height)
    line.close()
    line.fill()
    ui.set_color(0)
    line.stroke()

  @staticmethod
  def set_piece(width, height):
    bottomline_length = height * 0.64  # * koma.bottom_aspect
    top_degree = 146
    bottom_degree = 81
    aspect_ratio = 1.1  #koma.height_aspect
    top_radian = top_degree * (pi / 180)
    bottom_radian = bottom_degree * (pi / 180)
    a = bottomline_length * (
      aspect_ratio * cos(bottom_radian) -
      (sin(bottom_radian) / 2)) / cos(bottom_radian + (top_radian / 2))

    qx = a * sin(top_radian / 2)
    qy = a * cos(top_radian / 2)
    rx = bottomline_length / 2
    ry = bottomline_length * aspect_ratio
    center = (height - bottomline_length) / 4

    _line = ui.Path()
    _line.move_to(width / 2, center)
    _line.line_to(qx + (width / 2), qy + center)
    _line.line_to(rx + (width / 2), ry + center)
    _line.line_to(-rx + (width / 2), ry + center)
    _line.line_to(-qx + (width / 2), qy + center)

    #return [0, 0, qx,qy, rx, ry]
    return _line

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
    for y in range(MATRIX):
      for x in range(MATRIX):
        _cell = self.cells[x][y]
        _cell.bg_color = None
    if len(prompt) == 1:
      return
    if '%' in prompt:
      return

    _a = prompt[3:5]
    a_x, a_y = sujidan_to_index(_a)
    self.cells[a_x][a_y].bg_color = 'peru'

    _b = prompt[1:3]
    if '00' in _b:
      pass
    else:
      b_x, b_y = sujidan_to_index(_b)
      self.cells[b_x][b_y].bg_color = 'khaki'

  def setup_field(self, parent_size):
    self.width = parent_size
    self.height = parent_size

    cell_size = parent_size / MATRIX
    #print(cell_size)
    x_pos = 0
    y_pos = 0
    for y in range(MATRIX):
      for x in range(MATRIX):
        _cell = self.cells[x][y]
        _cell.width, _cell.height = [cell_size] * 2
        _cell.x = x_pos
        _cell.y = y_pos
        _cell.set_label_pos((MATRIX - x), (y + 1), 'red')
        y_pos += cell_size
      y_pos = 0
      x_pos += cell_size
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
        # xxx: `OU`, `GY` 処理をスマートにしたい
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
    w = self.width
    h = self.height
    square_size = min(w, h)

    self.stage.setup_stage(square_size)
    self.stage.field.set_game(self.game.game_board)

    #self.stage.y = (square_size / 2) - (self.stage.height / 4)

    self.back_btn.y, self.forward_btn.y = [
      (self.stage.y + self.stage.height) * 1.024
    ] * 2
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
  #root.present(style='fullscreen', orientations=['portrait'])
  root.present()

