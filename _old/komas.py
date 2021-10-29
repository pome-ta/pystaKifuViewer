from math import sin, cos, pi
import ui

# https://ameblo.jp/bane-0604/entry-12687852122.html
# https://rskmoi.hatenablog.com/entry/2018/01/21/104029

possize = 11.140625
cellsize = 44.5625 * 2

#    玉    飛    金    桂    香    歩
# h 32.5, 31.5, 30.5, 29.5, 29.5, 28.3
# b 29.3, 28.3, 27.3, 26.3, 24.1, 23.1
# a 1.109,1.113,1.117,1.1216730038022813

#    h    l    a
# 玉 32.5, 29.3 1.1092150170648465 1
# 飛 31.5, 28.3 1.1130742049469964 0.9692307692307692
# 金 30.5, 27.3 1.1172161172161172 0.9384615384615385
# 桂 29.5, 26.3 1.1216730038022813 0.9076923076923077
# 香 29.5, 24.1 1.2240663900414936 0.9076923076923077
# 歩 28.3, 23.1 1.225108225108225 0.8707692307692307


class Piece:
  def __init__(self, h, l):
    self.height_aspect = h / l
    self.bottom_aspect = l / 29.3


ou = Piece(32.5, 29.3)
hi = Piece(31.5, 28.3)
ki = Piece(30.5, 27.3)
ke = Piece(29.5, 26.3)
ky = Piece(29.5, 24.1)
fu = Piece(28.3, 23.1)

index = [['玉', ou, 42], ['飛', hi, 40], ['金', ki, 32], ['桂', ke, 32],
         ['香', ky, 32], ['歩', fu, 30]]


class Cell(ui.View):
  def __init__(self, i, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'goldenrod'
    self.width, self.height = [cellsize] * 2
    self.label = ui.Label()
    self.label.text_color = 'black'
    self.label.alignment = ui.ALIGN_CENTER
    self.label.font = ('Source Code Pro', i[2])
    #self.label.flex = 'WH'
    self.label.text = i[0]
    self.label.width, self.label.height = [cellsize] * 2
    #self.label.bg_color = 'red'
    self.add_subview(self.label)
    self.i = i

  def draw(self):
    ui.set_color('gold')
    #line = ui.Path()
    #mx, my, lx1, ly1, lx2, ly2 = self.set_piece(self.width, self.height)

    line = self.set_piece(self.i[1], self.width, self.height)
    line.close()
    line.fill()
    ui.set_color(0)
    line.stroke()

  @staticmethod
  def set_piece(koma, width, height):
    bottomline_length = height * 0.8 * koma.bottom_aspect
    top_degree = 146
    bottom_degree = 81
    aspect_ratio = koma.height_aspect
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


class RootView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'slategray'
    self.subs = []
    for i in range(len(index)):
      _cell = Cell(index[i])
      self.add_subview(_cell)
      self.subs.append(_cell)

  def layout(self):
    x = 0
    y = 0
    for sub in self.subs:
      sub.x = self.width / 2 - sub.width / 2
      sub.y = y
      x += cellsize * 1.024
      y += cellsize * 1.024


if __name__ == '__main__':
  # xxx: `path`
  root = RootView()
  root.present(style='fullscreen', orientations=['portrait'])
