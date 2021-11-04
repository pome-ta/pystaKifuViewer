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
  # xxx: 反転？🤔
  suji_str = str(MATRIX - x)
  dan_str = NUMtoKAN[y + 1]
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
    #self.__print_board(turn) if self.debug else None

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


class Cell(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    #self.bg_color = 'magenta'
    self.pos_x = ui.Label()
    self.pos_y = ui.Label()
    self.pos_x.alignment = ui.ALIGN_CENTER
    self.pos_y.alignment = ui.ALIGN_CENTER
    self.pos_x.font, self.pos_y.font = [('Source Code Pro', 8)] * 2
    self.add_subview(self.pos_x)
    self.add_subview(self.pos_y)

  def set_label_pos(self, x, y):
    x_pos = self.width / 4
    y_pos = self.height / 4
    #self.pos_x.bg_color, self.pos_y.bg_color = ['cyan'] * 2
    self.pos_x.width, self.pos_y.width = [x_pos] * 2
    self.pos_x.height, self.pos_y.height = [y_pos] * 2
    self.pos_y.x = self.width - self.pos_y.width
    self.pos_y.y = self.height - self.pos_y.height

    self.pos_x.text, self.pos_y.text = index_to_dansuji(x, y)


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

  def layout(self):
    w = self.width
    h = self.height
    self.setup_cells(w, h)

  def setup_cells(self, width, height):
    w = width / MATRIX
    h = height / MATRIX
    x_pos = 0
    y_pos = 0
    for y in range(MATRIX):
      for x in range(MATRIX):
        cell = self.cells[x][y]
        cell.width, cell.height = [w, h]
        cell.x, cell.y = [x_pos, y_pos]
        cell.set_label_pos(x, y)
        x_pos += w
      x_pos = 0
      y_pos += h

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
    self.field.height = sq_size * (34.8 / 31.7)
    self.field.x = (w - self.field.width) / 2
    self.field.y = (h - self.field.height) / 2

  def draw(self):
    # xxx: サイズ確認用
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

    self.init_setup()
    self.stage = StageView()

    self.btm = ui.View()
    self.btm.flex = 'W'
    self.btm.bg_color = self.parts_color

    self.btm.add_subview(self.sl)
    self.btm.add_subview(self.back_btn)
    self.btm.add_subview(self.forward_btn)
    self.add_subview(self.btm)
    self.add_subview(self.stage)

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
    self.setup_reader()
    self.setup_slider()
    self.setup_btns()

  def setup_reader(self):
    self.game = KifuReader(load_kifu())
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
    #self.update_game()

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
    #self.update_game()


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
  #root.present()
