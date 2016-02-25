# coding=utf-8
import pyglet
from ppu import palettes


win = pyglet.window.Window(800, 600)


def draw_palettes():
    init_x = 20
    init_y = 20
    start_x = init_x
    start_y = init_y
    size = 20
    factor = 41
    for row in palettes:
        for t in row:
            x1 = start_x
            y1 = start_y
            x2 = start_x + size
            y2 = start_y + size
            pyglet.graphics.draw(
                4, pyglet.gl.GL_QUADS,
                ('v2i', (x1, y1, x1, y2, x2, y2, x2, y1)),
                ('c3B',
                 (t[0] * factor, t[1] * factor, t[2] * factor,
                  t[0] * factor, t[1] * factor, t[2] * factor,
                  t[0] * factor, t[1] * factor, t[2] * factor,
                  t[0] * factor, t[1] * factor, t[2] * factor)))
            start_x += size
        start_x = init_x
        start_y += size


def test_draw():
    pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES,
    [0, 1, 2, 0, 2, 3],
    ('v2i', (100, 100,
             150, 100,
             150, 150,
             100, 150)))


def test_draw_2():
    x1 = 100
    y1 = 100
    x2 = 200
    y2 = 200
    pyglet.graphics.draw(
        4, pyglet.gl.GL_QUADS,
        100, 100, 100, 200, 200, 200, 200, 100
        ('v2i', (x1, y1, x1, y2, x2, y2, x2, y1)),
        ('c3B', (0, 0, 255, 0, 255, 255, 0, 0, 255, 0, 255, 0)))


@win.event
def on_draw():
    win.clear()
    draw_palettes()


if __name__ == '__main__':
    pyglet.app.run()
