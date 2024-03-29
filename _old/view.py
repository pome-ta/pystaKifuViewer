from enum import Enum
from colorsys import hsv_to_rgb
import ui

# todo: 9 x 9 の盤面
MTRX = 9

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
    #print(args)
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
    #self.corner_radius = 32
    #self.width = 32
    #self.height = 32

  '''
  def draw(self):
    ui.set_color(0)
    dot = ui.Path.oval(0, 0, self.width, self.height)
    dot.fill()
  '''


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


class Board(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    #self.bg_color = 'goldenrod'
    self.stage = StageMatrix()
    self.add_subview(self.stage)

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

    self.stage.set_matrix(parent_size - min_size)
    self.stage.y = min_size


class MainView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'slategray'
    self.board = Board()
    self.add_subview(self.board)

  def layout(self):
    square_size = min(self.width, self.height)
    self.board.set_layout(square_size)


if __name__ == '__main__':
  view = MainView()
  view.present(style='fullscreen', orientations=['portrait'])
  #view.present()

