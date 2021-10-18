from colorsys import hsv_to_rgb
import ui

# todo: 9 x 9 の盤面
MTRX = 9

# xxx: 良きように振り分け
row_num = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
clm_num = []


class Cell(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self._text = ''
    #self.bg_color = 'cyan'
    self.border_color = 0
    self.border_width = 0.5

    self.label = ui.Label()
    self.label.alignment = ui.ALIGN_CENTER
    self.label.text = '0, 0'
    self.label.text_color = 0
    self.label.font = ('Source Code Pro', 12)
    self.label.flex = 'WH'
    self.add_subview(self.label)

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

    self.cells = [[(Cell()) for y in range(MTRX)] for x in range(MTRX)]

    [[self.add_subview(y) for y in x] for x in self.cells]

    self.dots = [[Dot() for dy in range(2)] for dx in range(2)]
    [[self.add_subview(dy) for dy in dx] for dx in self.dots]

  def set_matrix(self, parent_size):
    self.width = parent_size
    self.height = parent_size
    x_pos = 0
    y_pos = 0
    counter = 0
    len_cells = sum(len(l) for l in self.cells)
    cell_size = parent_size / MTRX
    for x, cells in enumerate(self.cells):
      for y, cell in enumerate(cells):
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
        cell.bg_color = 'gray' if boolen else 'darkgray'
        #cell.label.bg_color = color

        cell.width = cell_size
        cell.height = cell_size
        cell.x = x_pos
        cell.y = y_pos
        # xxx: 配列明記不要になったら`enumerate` を消す
        cell.text = f'{x}, {y}'
        counter += 1
        x_pos += cell_size
      x_pos = 0
      y_pos += cell_size
    self.set_dot()

  def set_dot(self):
    size = self.width / 32
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
      clm.text = str(row_num[n])
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

