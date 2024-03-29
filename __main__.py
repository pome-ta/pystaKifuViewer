from math import sin, cos, pi
from pathlib import Path
import ui

BLACK = 0.24
RED = 'red'

MATRIX = 9
TEBAN = {'+': '☖', '-': '☗'}

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

CATALOG = {
  'OU': {
    'face': '王',
    'size': H1,
    'color': BLACK,
    'back': None
  },
  'GY': {
    'face': '玉',
    'size': H1,
    'color': BLACK,
    'back': None
  },
  'HI': {
    'face': '飛',
    'size': H2,
    'color': BLACK,
    'back': None
  },
  'KA': {
    'face': '角',
    'size': H2,
    'color': BLACK,
    'back': None
  },
  'KI': {
    'face': '金',
    'size': H3,
    'color': BLACK,
    'back': None
  },
  'GI': {
    'face': '銀',
    'size': H3,
    'color': BLACK,
    'back': None
  },
  'KE': {
    'face': '桂',
    'size': H4,
    'color': BLACK,
    'back': None
  },
  'KY': {
    'face': '香',
    'size': H5,
    'color': BLACK,
    'back': None
  },
  'FU': {
    'face': '歩',
    'size': H6,
    'color': BLACK,
    'back': None
  },
  'TO': {
    'face': 'と',
    'size': H6,
    'color': RED,
    'back': 'FU'
  },
  'NY': {
    'face': '杏',
    'size': H5,
    'color': RED,
    'back': 'KY'
  },
  'NK': {
    'face': '圭',
    'size': H4,
    'color': RED,
    'back': 'KE'
  },
  'NG': {
    'face': '全',
    'size': H3,
    'color': RED,
    'back': 'GI'
  },
  'UM': {
    'face': '馬',
    'size': H2,
    'color': RED,
    'back': 'KA'
  },
  'RY': {
    'face': '龍',
    'size': H2,
    'color': RED,
    'back': 'HI'
  },
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

  header = data[:HEAD]
  board = data[HEAD:BOARD]
  prompt = [i.strip() for i in PROMPT]

  return header, board, prompt


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
    self.before: str = ''
    self.after: str = ''
    self.piece_name: str = ''
    self.debug = debug

    self.header, self.board_init, self.prompter = split_data(data)
    self.game_board = self.init_board()

  def init_board(self):
    """
    最初の配置盤面を返す
    """
    self.sente_hand = []
    self.gote_hand = []
    self.before = ''
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

    self.before = before
    self.after = after
    self.piece_name = teban + piece

  def __get_piece(self, teban_piece):
    piece = self.__convert_piece(teban_piece)
    if '-' in teban_piece:
      self.sente_hand.append(piece)
      self.sente_hand.sort()
    if '+' in teban_piece:
      self.gote_hand.append(piece)
      self.gote_hand.sort()

  @staticmethod
  def __convert_piece(teban_piece):
    _piece = CATALOG[teban_piece[1:]]['back']
    piece = _piece if _piece else teban_piece[1:]
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
    return out_txt


class Piece(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.flex = 'WH'

    self.sent_rad = ui.Transform.rotation(0)
    self.gote_rad = ui.Transform.rotation(pi)

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
    self.teban = teban_piece[0]
    self.face = piece['face']
    self.height_aspect = h / l
    self.bottom_aspect = l / 29.3
    self.name_label.text = self.face
    self.name_label.text_color = piece['color']

    if self.teban == '+':
      self.transform = self.sent_rad
    if self.teban == '-':
      self.transform = self.gote_rad

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
    # ガワのサイズ調整用
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

    return vector


class Cell(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.pos_x = ui.Label()
    self.pos_y = ui.Label()
    self.pos_x.alignment = ui.ALIGN_CENTER
    self.pos_y.alignment = ui.ALIGN_CENTER
    self.pos_x.font, self.pos_y.font = [('Source Code Pro', 10)] * 2
    self.add_subview(self.pos_x)
    self.add_subview(self.pos_y)

    # Animation 用のView
    self.piece_wrap = ui.View()
    self.piece_wrap.flex = 'WH'
    self.koma = Piece()
    self.piece_wrap.add_subview(self.koma)
    self.add_subview(self.piece_wrap)

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

    self.cells = [[(Cell()) for x in range(MATRIX)] for y in range(MATRIX)]
    [[self.add_subview(x) for x in y] for y in self.cells]

  def update_field(self, board_Lists):
    for cells, boards in zip(self.cells, board_Lists):
      for cell, koma in zip(cells, boards):
        cell.bg_color = None
        cell.alpha = 1
        cell.koma.make_up(koma)
        cell.koma.draw()
        cell.piece_wrap.alpha = 1
        cell.piece_wrap.y = 0

  def btn_in_after(self, teban):
    ui.cancel_delays()
    if ('開始' in teban) or ('%' in teban):
      return
    x, y = sujidan_to_index(teban)
    ani_cell = self.cells[x][y]
    ani_koma = self.cells[x][y].piece_wrap
    ani_koma.alpha = 0.0
    pre_y = ani_koma.y
    interval = 8
    ani_koma.y = pre_y + interval if ani_cell.koma.teban == '+' else -interval

    def animation_koma_move():
      ani_koma.alpha = 0.0
      ani_koma.y = pre_y

    def animation_cell():
      def in_animation():
        ani_cell.bg_color = 'khaki'
        ani_koma.alpha = 1

      ui.animate(in_animation, duration=0.5)

    ui.animate(animation_koma_move, duration=0.25)
    ui.delay(animation_cell, 0.125)

  def btn_in_before(self, teban):
    if ('00' in teban) or ('' == teban):
      return
    x, y = sujidan_to_index(teban)
    ani_cell = self.cells[x][y]

    def animation_cell():
      ani_cell.bg_color = 'khaki'
      ani_cell.alpha = 0.25

    ui.animate(animation_cell, duration=0.5)

  def sl_in_after(self, teban):
    if ('開始' in teban) or ('%' in teban):
      return
    x, y = sujidan_to_index(teban)
    cell = self.cells[x][y]
    cell.bg_color = 'khaki'

  def sl_in_before(self, teban):
    if ('00' in teban) or ('' == teban):
      return
    x, y = sujidan_to_index(teban)
    cell = self.cells[x][y]
    cell.bg_color = 'khaki'
    cell.alpha = 0.25

  def layout(self):
    w = self.width
    h = self.height
    self.setup_cells(w, h)

  def setup_cells(self, width, height):
    w = width / MATRIX
    h = height / MATRIX
    x_pos, y_pos = [0, 0]
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
    x_line, y_line = [0, 0]
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


class HandCaption(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.set_cap()

  def set_cap(self):
    self.cap = ui.Label()
    self.cap.alignment = ui.ALIGN_CENTER
    self.cap.text = ''
    self.cap.font = ('Source Code Pro', 10)
    self.cap.text_color = BLACK
    self.add_subview(self.cap)

  def layout(self):
    self.cap.width, self.cap.height = [self.width / 4, self.height / 4]
    self.cap.x = self.width - self.cap.width

  def reset_cap(self):
    for view in self.subviews:
      self.remove_subview(view)
    self.set_cap()


class HandStand(ui.View):
  """
  駒台
  """

  def __init__(self, sente_gote, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'goldenrod'
    self.sente_gote = sente_gote
    self.border_color = BLACK
    self.border_width = 1.5
    self.pieces = []
    self.captions = [HandCaption() for i in range(8)]
    [self.add_subview(cap) for cap in self.captions]

  def layout(self):
    w = self.width / 4
    h = self.height / 2
    x_pos = 0
    y_pos = 0
    for n, view in enumerate(self.captions):
      view.width, view.height = [w, h]
      view.x, view.y = [x_pos, y_pos]
      x_pos += w
      if n == 3:
        x_pos = 0
        y_pos += h

  def on_hand(self, hold):
    self.reset_caps()
    if hold:
      set_hold = list(set(hold))
      set_hold.sort()
      hold_num = [hold.count(pi) for pi in set_hold]
      self.pieces = set_hold
      for n, p_str in enumerate(self.pieces):
        p_str = self.sente_gote + p_str
        piece = Piece()
        piece.width = self.captions[n].width * 0.88
        piece.height = self.captions[n].height * 0.88
        piece.x = (self.captions[n].width - piece.width) / 2
        piece.y = (self.captions[n].height - piece.height) / 2
        piece.make_up(p_str)
        piece.draw()
        self.captions[n].cap.text = str(hold_num[n]) if hold_num[n] > 1 else ''
        self.captions[n].add_subview(piece)

  def reset_caps(self):
    for cap in self.captions:
      cap.reset_cap()


class StageView(ui.View):
  """
  盤面と駒台
  """

  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.sente_stand = HandStand('+')
    self.gote_stand = HandStand('-')
    self.add_subview(self.sente_stand)
    self.add_subview(self.gote_stand)
    self.field = FieldMatrix()
    self.add_subview(self.field)

  def layout(self):
    w = self.width
    h = self.height
    sq_size = min(w, h) / 1.024
    self.field.width = sq_size
    # https://sizea.jp/shogi-size/
    self.field.height = sq_size * (34.8 / 31.7)
    self.field.x = (w - self.field.width) / 2
    self.field.y = (h - self.field.height) / 2

    st_h = ((self.height - self.field.height) / 2) * 0.88
    self.sente_stand.height, self.gote_stand.height = [st_h] * 2
    self.sente_stand.width, self.gote_stand.width = [sq_size / 1.28] * 2

    self.sente_stand.y = self.height - self.sente_stand.height
    self.sente_stand.x = self.width - self.sente_stand.width


class AreaView(ui.View):
  def __init__(self, parent, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    # xxx: Navigation Bar 操作用
    self.parent = parent
    self.bg_color = 'slategray'
    self.flex = 'WH'
    self.parts_color = 1  #'silver'
    self.parts_size = 64

    self.update_interval = 0

    self.data = load_kifu()
    # --- debug set
    self.game = KifuReader(self.data, debug=0)
    self.stage = StageView()
    self.init_setup()

  def update(self):
    self.steps_btn(self.forward_btn)

  def update_game(self):
    self.game.looper(self.step)

    self.stage.field.update_field(self.game.game_board)
    self.stage.sente_stand.on_hand(self.game.sente_hand)
    self.stage.gote_stand.on_hand(self.game.gote_hand)
    self.parent.name = self.print_prompt_nav()

  def print_prompt_nav(self) -> str:
    if '開始' in self.game.after:
      return f'{self.game.after}'
    if '%' in self.game.after:
      return f'{self.step:03d}手目: 終局'

    # xxx: 同{駒} はどうするか
    suji_after, dan_after = index_to_dansuji(
      *sujidan_to_index(self.game.after))
    after = suji_after + dan_after

    if '00' in self.game.before:
      before = '打'
    else:
      suji_before, dan_before = index_to_dansuji(
        *sujidan_to_index(self.game.before))
      before = f'({suji_before}{dan_before})'

    teban = TEBAN[self.game.piece_name[0]]
    piece = CATALOG[self.game.piece_name[1:]]['face']

    return f'{self.step:03d}手目: {teban}{after}{piece}{before}'

  def layout(self):
    w, h = [self.width, self.height]
    square_size = min(w, h)
    margin_size = square_size * 0.064
    # btm set
    self.btm.height = self.parent.frame[1] * 1.5  #1.024
    self.btm.width = w
    self.btm.x = (w - self.btm.width) / 2
    self.btm.y = h - self.btm.height
    # slider
    self.sl.width = w - (self.parts_size * 2)
    self.sl.x = (w - self.sl.width) / 2
    # Buttons
    self.back_btn.x = 0
    self.forward_btn.x = w - self.parts_size

    self.play_pause_btn.x = (w - self.play_pause_btn.width) / 2
    self.play_pause_btn.y = self.sl.height / 1.5

    self.start_btn.x = self.play_pause_btn.x - self.start_btn.width
    self.start_btn.y = self.play_pause_btn.y

    self.end_btn.x = self.play_pause_btn.x + self.end_btn.width
    self.end_btn.y = self.play_pause_btn.y

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

    self.btm.add_subview(self.play_pause_btn)
    self.btm.add_subview(self.start_btn)
    self.btm.add_subview(self.end_btn)
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

  def setup_btns(self):
    self.back_btn = self.set_btn('iob:ios7_arrow_left_32', 0)
    self.forward_btn = self.set_btn('iob:ios7_arrow_right_32', 1)
    self.play_pause_btn = self.set_btn('iob:ios7_play_32', 0)
    self.start_btn = self.set_btn('iob:ios7_skipbackward_32', 0)
    self.end_btn = self.set_btn('iob:ios7_skipforward_32', 1)

    self.back_btn.action = self.steps_btn
    self.forward_btn.action = self.steps_btn
    self.play_pause_btn.action = self.change_play_pause
    self.start_btn.action = self.jump_btn
    self.end_btn.action = self.jump_btn

  def set_btn(self, img, boolean):
    # forward: 1, back : 0
    # play   : 1, pause: 0
    # end    : 1, start: 0
    icon = ui.Image.named(img)
    btn = ui.Button(title='')
    btn.boolean = boolean
    btn.width = self.parts_size
    btn.height = self.parts_size
    btn.bg_color = self.parts_color
    btn.image = icon
    return btn

  def change_play_pause(self, sender):
    if sender.boolean:
      sender.image = ui.Image.named('iob:ios7_play_32')
      sender.boolean = 0
      self.update_interval = sender.boolean
      self.bg_color = 'slategray'
    else:
      sender.image = ui.Image.named('iob:ios7_pause_32')
      sender.boolean = 1
      self.update_interval = sender.boolean
      self.bg_color = 'seagreen'

  def jump_btn(self, sender):
    if sender.boolean:
      # end
      self.sl.value = 1
      self.steps_slider(self.sl)
    else:
      # start
      self.sl.value = 0
      self.steps_slider(self.sl)

  def steps_btn(self, sender):
    if sender.boolean:
      # forward
      if self.step < self.max:
        self.step += 1
    else:
      # back
      if self.step > 0:
        self.step -= 1
    self.sl.value = self.step_list[self.step]
    self.update_game()
    self.stage.field.btn_in_before(self.game.before)
    self.stage.field.btn_in_after(self.game.after)

  def steps_slider(self, sender):
    self.step = int(sender.value * self.max)
    self.update_game()
    self.stage.field.sl_in_before(self.game.before)
    self.stage.field.sl_in_after(self.game.after)


class RootView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'slategray'
    self.area = AreaView(self)
    self.add_subview(self.area)


if __name__ == '__main__':
  # xxx: `path`
  root = RootView()
  root.present(style='fullscreen', orientations=['portrait'])

