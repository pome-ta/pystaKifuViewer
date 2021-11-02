from pathlib import Path
import ui


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


class BoardView(ui.View):
  def __init__(self, parent, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.parent = parent
    self.bg_color = 'maroon'
    self.flex = 'WH'
    self.init_setup()

  def layout(self):
    # xxx: 親呼ぶ
    square_size = min(self.width, self.height)
    margin_size = square_size * 0.2
    w = self.width - margin_size
    h = self.height - margin_size

    # スライダー長さ確定
    self.sl.width = w - (self.back_btn.width + self.forward_btn.width)
    self.sl.height = min(self.back_btn.height, self.forward_btn.height)

    # ボタン類位置左右振り
    self.back_btn.x = 0
    self.forward_btn.x = w - self.forward_btn.width
    self.sl.x = self.back_btn.width

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
    self.sl.bg_color = 'darkgray'
    self.sl.flex = 'W'
    self.sl.action = self.steps_slider
    self.sl.continuous = False
    self.add_subview(self.sl)

  def steps_slider(self, sender):
    self.step = int(sender.value * self.max)
    #self.update_game()

  def setup_btns(self):
    self.back_btn = self.set_btn('iob:ios7_arrow_back_32', 0)
    self.forward_btn = self.set_btn('iob:ios7_arrow_forward_32', 1)
    self.add_subview(self.back_btn)
    self.add_subview(self.forward_btn)

  def set_btn(self, img, back_forward):
    # forward: 1
    # back: 0
    icon = ui.Image.named(img)
    btn = ui.Button(title='')
    btn.width = 64
    btn.height = 128
    btn.bg_color = 'darkgray'
    btn.image = icon
    btn.back_forward = back_forward
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
    self.board = BoardView(self)
    self.add_subview(self.board)


if __name__ == '__main__':
  # xxx: `path`
  root = RootView()
  #root.present(style='fullscreen', orientations=['portrait'])
  root.present()
