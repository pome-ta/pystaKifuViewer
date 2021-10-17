from colorsys import hsv_to_rgb
import ui


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


class Board(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'magenta'
    self.mtrx = 9
    self.cells = [[Cell() for y in range(self.mtrx)] for x in range(self.mtrx)]

    [[self.add_subview(y) for y in x] for x in self.cells]

  def layout_stage(self, parent_size):

    size = min(parent_size)
    self.width = size
    self.height = size

    x_pos = 0
    y_pos = 0
    counter = 0
    len_cells = len(self.subviews)
    cell_size = size / self.mtrx

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


class MainView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'slategray'
    self.board = Board()
    self.add_subview(self.board)

  def layout(self):
    size = [self.width, self.height]
    self.board.layout_stage(size)


if __name__ == '__main__':
  view = MainView()
  view.present(style='fullscreen', orientations=['portrait'])

