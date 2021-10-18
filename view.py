from colorsys import hsv_to_rgb
import ui

# todo: 9 x 9 の盤面
MTRX = 9


class Cell(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self._text = ''
    self.bg_color = 'cyan'
    self.border_color = 1
    self.border_width = 1

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


class StageMatrix(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'yellow'

    self.cells = [[Cell() for y in range(MTRX)] for x in range(MTRX)]

    [[self.add_subview(y) for y in x] for x in self.cells]

  def set_layout(self, parent_size):
    self.width = parent_size
    self.height = parent_size
    x_pos = 0
    y_pos = 0
    counter = 0
    len_cells = len(self.subviews)
    cell_size = parent_size / MTRX

    for x, cells in enumerate(self.cells):
      for y, cell in enumerate(cells):
        h = counter / len_cells
        color = hsv_to_rgb(h, h, 1)
        #cell.bg_color = color
        cell.label.bg_color = color

        cell.width = cell_size
        cell.height = cell_size
        cell.x = x_pos
        cell.y = y_pos
        cell.text = f'{x}, {y}'
        counter += 1
        x_pos += cell_size
      x_pos = 0
      y_pos += cell_size


class Board(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'magenta'
    self.stage = StageMatrix()
    self.add_subview(self.stage)
    #[self.add_subview(r) for r in self.rows]
    #[self.add_subview(c) for c in self.clms]

  def set_layout(self, parent_size):
    self.width = parent_size
    self.height = parent_size
    self.stage.set_layout(parent_size)


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

