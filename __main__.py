from math import sin, cos, pi
from pathlib import Path
import ui

BLACK = 0.24
RED = 'red'

MATRIX = 9

NUMtoKAN = {
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

# --- komas size
H1 = {'center_height': 32.5, 'bottom_width': 29.3}  # OU
H2 = {'center_height': 31.5, 'bottom_width': 28.3}  # HI
H3 = {'center_height': 30.5, 'bottom_width': 27.3}  # KI
H4 = {'center_height': 29.5, 'bottom_width': 26.3}  # KE
H5 = {'center_height': 29.5, 'bottom_width': 24.1}  # KY
H6 = {'center_height': 28.3, 'bottom_width': 23.1}  # FU

# --- komas attribute
OU = {'face': '王', 'size': H1, 'color': BLACK, 'back': None}
GY = {'face': '玉', 'size': H1, 'color': BLACK, 'back': None}
HI = {'face': '飛', 'size': H2, 'color': BLACK, 'back': None}
KA = {'face': '角', 'size': H2, 'color': BLACK, 'back': None}
KI = {'face': '金', 'size': H3, 'color': BLACK, 'back': None}
GI = {'face': '銀', 'size': H3, 'color': BLACK, 'back': None}
KE = {'face': '桂', 'size': H4, 'color': BLACK, 'back': None}
KY = {'face': '香', 'size': H5, 'color': BLACK, 'back': None}
FU = {'face': '歩', 'size': H6, 'color': BLACK, 'back': None}

TO = {'face': 'と', 'size': H6, 'color': RED, 'back': 'FU'}
NY = {'face': '杏', 'size': H5, 'color': RED, 'back': 'KY'}
NK = {'face': '圭', 'size': H4, 'color': RED, 'back': 'KE'}
NG = {'face': '全', 'size': H3, 'color': RED, 'back': 'GI'}
UM = {'face': '馬', 'size': H2, 'color': RED, 'back': 'KA'}
RY = {'face': '龍', 'size': H2, 'color': RED, 'back': 'HI'}

CATALOG = {
  'OU': OU,
  'GY': GY,
  'HI': HI,
  'KA': KA,
  'KI': KI,
  'GI': GI,
  'KE': KE,
  'KY': KY,
  'FU': FU,
  'TO': TO,
  'NY': NY,
  'NK': NK,
  'NG': NG,
  'UM': UM,
  'RY': RY
}


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


# todo: 段=x 漢字, 筋=y 英数字
def sujidan_to_index(sujidan_str) -> (int, int):
  suji_int = int(sujidan_str[0])
  dan_int = int(sujidan_str[1])
  x = dan_int - 1
  y = MATRIX - suji_int
  return x, y


def index_to_dansuji(x: int, y: int) -> (str, str):
  suji_str = str(MATRIX - y)
  dan_str = NUMtoKAN[x + 1]
  return suji_str, dan_str


class KifuReader:
  def __init__(self, data, debug=0):
    self.game_board: list  # 現在のboard 上の状態
    self.board_init: list  # 初手盤面
    self.prompter: list  # 一手づつの指示情報

    self.sente_hand: list = []  # `+` 先手保持手駒
    self.gote_hand: list = []  # `-` 後手保持手駒
    self.after: str = ''
    self.piece_name: str = ''
    self.debug = debug  # 1

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
    print(self.__print_board()) if self.debug else None

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
    # xxx: いつかは、class か何かに統合
    #print(CATALOG[teban_piece[1:]])
    _piece = CATALOG[teban_piece[1:]]['back']
    __piece = _piece if _piece else teban_piece[1:]
    print(__piece)

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

  def __print_board(self):
    # 盤面を`str` で返す
    # テスト用
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
    #print(out_txt)
    return out_txt


class Piece(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    #self.bg_color = 'magenta'
    #self.flex = 'WH'
    #self.border_color = BLACK
    #self.border_width = 1
    self.name_label = ui.Label()
    self.name_label.flex = 'WH'
    self.name_label.alignment = ui.ALIGN_CENTER
    self.name_label.font = ('Source Code Pro', 16)
    self.name_label.text_color = BLACK
    self.name_label.text = ''
    self.add_subview(self.name_label)

  def make_up(self, teban_piece):
    if len(teban_piece) == 1:
      self.name_label.text = ''
      return
    # なんとなく後手を`玉`
    teban_piece = '-GY' if '-OU' in teban_piece else teban_piece

    piece = CATALOG[teban_piece[1:]]

    h = piece['size']['center_height']
    l = piece['size']['bottom_width']
    self.face = piece['face']
    self.height_aspect = h / l
    self.bottom_aspect = l / 29.3
    self.name_label.text = self.face
    self.name_label.text_color = piece['color']

  def draw(self):
    self.set_needs_display()
    if self.name_label.text == '*' or self.name_label.text == '':
      return
    ui.set_color('gold')
    line = self.set_piece(self.width, self.height)
    line.close()
    line.fill()
    ui.set_color(BLACK)
    line.stroke()

  def set_piece(self, width, height):
    # https://ameblo.jp/bane-0604/entry-12687852122.html
    # https://rskmoi.hatenablog.com/entry/2018/01/21/104029

    bottomline_length = height * 0.8 * self.bottom_aspect
    top_degree = 146
    bottom_degree = 81
    aspect_ratio = self.height_aspect
    top_radian = top_degree * (pi / 180)
    bottom_radian = bottom_degree * (pi / 180)
    self.name_label.y = bottom_radian
    a = bottomline_length * (
      aspect_ratio * cos(bottom_radian) -
      (sin(bottom_radian) / 2)) / cos(bottom_radian + (top_radian / 2))

    qx = a * sin(top_radian / 2)
    qy = a * cos(top_radian / 2)
    rx = bottomline_length / 2
    ry = bottomline_length * aspect_ratio
    center = (height - bottomline_length) / 4

    vector = ui.Path()
    vector.move_to(width / 2, center)
    vector.line_to(qx + (width / 2), qy + center)
    vector.line_to(rx + (width / 2), ry + center)
    vector.line_to(-rx + (width / 2), ry + center)
    vector.line_to(-qx + (width / 2), qy + center)

    #return [0, 0, qx,qy, rx, ry]
    return vector


class Cell(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    #self.bg_color = 'magenta'
    self.pos_x = ui.Label()
    self.pos_y = ui.Label()
    self.pos_x.alignment = ui.ALIGN_CENTER
    self.pos_y.alignment = ui.ALIGN_CENTER
    self.pos_x.font, self.pos_y.font = [('Source Code Pro', 10)] * 2
    self.add_subview(self.pos_x)
    self.add_subview(self.pos_y)

    self.koma = Piece()
    self.add_subview(self.koma)

  def setup_koma(self, _x, _y):
    _w, _h = self.__set_label_pos(_x, _y)
    w = self.width - (_w * 1.024)
    h = self.height - (_h * 1.024)
    self.koma.width, self.koma.height = [w, h]
    self.koma.x = (self.width - self.koma.width) / 2
    self.koma.y = (self.height - self.koma.height) / 2

  def __set_label_pos(self, x, y):
    x_pos = self.width / 4
    y_pos = self.height / 4
    #self.pos_x.bg_color, self.pos_y.bg_color = ['cyan'] * 2
    self.pos_x.alpha, self.pos_y.alpha = [0.5] * 2
    self.pos_x.text_color, self.pos_y.text_color = [BLACK] * 2
    self.pos_x.width, self.pos_y.width = [x_pos] * 2
    self.pos_x.height, self.pos_y.height = [y_pos] * 2
    self.pos_y.x = self.width - self.pos_y.width
    self.pos_y.y = self.height - self.pos_y.height
    self.pos_x.text, self.pos_y.text = index_to_dansuji(x, y)
    return x_pos, y_pos


class FieldMatrix(ui.View):
  """
  盤面そのもの
  """

  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'goldenrod'
    self.border_color = BLACK
    self.border_width = 1.5

    self.sent_rad = ui.Transform.rotation(0)
    self.gote_rad = ui.Transform.rotation(pi)

    self.cells = [[(Cell()) for x in range(MATRIX)] for y in range(MATRIX)]
    [[self.add_subview(x) for x in y] for y in self.cells]

  def update_field(self, board_Lists):
    for cells, boards in zip(self.cells, board_Lists):
      for cell, koma in zip(cells, boards):
        cell.koma.make_up(koma)

        if '+' in koma:
          cell.koma.transform = self.sent_rad
        if '-' in koma:
          cell.koma.transform = self.gote_rad
        #cell.koma.name_label.text = koma
        cell.koma.draw()

  def layout(self):
    w = self.width
    h = self.height
    self.setup_cells(w, h)

  def setup_cells(self, width, height):
    w = width / MATRIX
    h = height / MATRIX
    x_pos = 0
    y_pos = 0
    # todo: 段=x 漢字, 筋=y 英数字
    for dan in range(MATRIX):
      for suji in range(MATRIX):
        cell = self.cells[suji][dan]
        cell.width, cell.height = [w, h]
        cell.x, cell.y = [x_pos, y_pos]
        cell.setup_koma(suji, dan)
        y_pos += h
      y_pos = 0
      x_pos += w

  def draw(self):
    """
    盤の線を引く、点を打つ
    """
    ui.set_color(BLACK)
    x_line = 0
    y_line = 0
    d_size = 4
    x_div = self.width / MATRIX
    y_div = self.height / MATRIX
    for m in range(MATRIX):
      line_path = ui.Path()
      # x
      line_path.move_to(0, y_line)
      line_path.line_to(self.width, y_line)
      # y
      line_path.move_to(x_line, 0)
      line_path.line_to(x_line, self.height)
      line_path.line_width = 1 if (m % 3 == 0) else 0.5
      line_path.stroke()
      # dot
      if (m % 3 == 0) and (0 < m < MATRIX):
        ux = x_line - (d_size / 2)
        uy = y_line - (d_size / 2)
        ui.Path.oval(ux, uy, d_size, d_size).fill()
        bx = abs(ux - self.width + d_size)
        ui.Path.oval(bx, uy, d_size, d_size).fill()
      x_line += x_div
      y_line += y_div


class StageView(ui.View):
  """
  盤面と駒台
  """

  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    #self.bg_color = 'goldenrod'
    self.field = FieldMatrix()
    self.add_subview(self.field)

  def layout(self):
    w = self.width
    h = self.height
    sq_size = min(w, h)
    self.field.width = sq_size
    # https://sizea.jp/shogi-size/
    self.field.height = sq_size * (34.8 / 31.7)
    self.field.x = (w - self.field.width) / 2
    self.field.y = (h - self.field.height) / 2

  def draw(self):
    # xxx: サイズ確認用（Zのやつ）
    ui.set_color(BLACK)
    line = ui.Path()
    line.line_width = 2
    line.move_to(0, 0)
    line.line_to(self.width, 0)
    line.line_to(0, self.height)
    line.line_to(self.width, self.height)
    line.stroke()


class AreaView(ui.View):
  def __init__(self, parent, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    # xxx: Navigation Bar 操作用
    self.parent = parent
    #self.bg_color = 'maroon'
    self.flex = 'WH'
    self.parts_color = 1  #'silver'
    self.parts_size = 64
    self.data = load_kifu()
    self.game = KifuReader(self.data, debug=0)
    self.stage = StageView()
    self.init_setup()

  def update_game(self):
    self.game.looper(self.step)
    # xxx: こんなに深く呼び出していいもの？
    self.stage.field.update_field(self.game.game_board)

  def layout(self):
    w = self.width
    h = self.height
    square_size = min(w, h)
    margin_size = square_size * 0.064
    # btm set
    self.btm.height = self.parent.frame[1] * 1.024
    self.btm.width = w
    self.btm.x = (w - self.btm.width) / 2
    self.btm.y = h - self.btm.height
    # slider
    self.sl.width = w - (self.parts_size * 2)
    self.sl.x = (w - self.sl.width) / 2
    # Buttons
    self.back_btn.x = 0
    self.forward_btn.x = w - self.parts_size
    # stage
    self.stage.width = w - (margin_size / 2)
    self.stage.height = h - self.btm.height - (margin_size / 2)
    self.stage.x = (w - self.stage.width) / 2
    self.stage.y = margin_size / 4

  def init_setup(self):
    self.btm = ui.View()
    self.btm.flex = 'W'
    self.btm.bg_color = self.parts_color

    self.setup_reader()
    self.setup_slider()
    self.setup_btns()

    self.btm.add_subview(self.sl)
    self.btm.add_subview(self.back_btn)
    self.btm.add_subview(self.forward_btn)
    self.add_subview(self.btm)
    self.add_subview(self.stage)
    self.update_game()

  def setup_reader(self):
    self.max = len(self.game.prompter) - 1
    self.min = 1 / self.max
    self.step = 0
    # `slider` 数値用
    self.step_list = [n * self.min for n in range(self.max + 1)]

  def setup_slider(self):
    self.sl = ui.Slider()
    self.sl.height = self.parts_size
    self.sl.bg_color = self.parts_color
    self.sl.flex = 'W'
    self.sl.action = self.steps_slider
    self.sl.continuous = False

  def steps_slider(self, sender):
    self.step = int(sender.value * self.max)
    self.update_game()

  def setup_btns(self):
    self.back_btn = self.set_btn('iob:ios7_arrow_left_32', 0)
    self.forward_btn = self.set_btn('iob:ios7_arrow_right_32', 1)

  def set_btn(self, img, back_forward):
    # forward: 1, back: 0
    icon = ui.Image.named(img)
    btn = ui.Button(title='')
    btn.back_forward = back_forward
    btn.width = self.parts_size
    btn.height = self.parts_size
    btn.bg_color = self.parts_color
    btn.image = icon
    btn.action = self.steps_btn
    return btn

  def steps_btn(self, sender):
    if sender.back_forward:
      if self.step < self.max:
        self.step += 1
    else:
      if self.step > 0:
        self.step -= 1
    self.sl.value = self.step_list[self.step]
    self.update_game()


class RootView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'slategray'
    #self.bg_color = 'goldenrod'
    self.area = AreaView(self)
    self.add_subview(self.area)


if __name__ == '__main__':
  # xxx: `path`
  root = RootView()
  root.present(style='fullscreen', orientations=['portrait'])

