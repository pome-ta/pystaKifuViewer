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


class Cell(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    #self.bg_color = 'cyan'
    self._text = ''
    self.label = ui.Label()
    self.pos_x = ui.Label()
    self.pos_y = ui.Label()

    self.label.alignment = ui.ALIGN_CENTER
    self.pos_x.alignment = ui.ALIGN_CENTER
    self.pos_y.alignment = ui.ALIGN_CENTER

    self.label.text_color = BLACK
    self.label.font = ('Source Code Pro', 14)
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
    self.field.center = self.center


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

  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'maroon'
    self.flex = 'WH'
    self.stage = StageView()
    self.add_subview(self.stage)

  def layout(self):
    """ layout
    `self.flex = 'WH'` で、サイズfix
    """
    square_size = min(self.width, self.height)
    self.stage.setup_stage(square_size)


class RootView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'slategray'
    self.board = BoardView()
    self.add_subview(self.board)


if __name__ == '__main__':
  root = RootView()
  root.present(style='fullscreen', orientations=['portrait'])

