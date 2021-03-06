"""
Defines screens for drawing objects.
"""

import pyglet.graphics as _graphics
import pyglet.window as _win

from pyglet.gl import *


class Screen:
    """
    Base screen class for drawing things.

    :var x: x coord
    :var y: y coord
    :var w: width
    :var h: height
    :var valset: parent window's value set
    :var bg: background color
    :var visible: if the screen is drawn
    :var active: if the screen is updated
    """

    _vertex_types = ('points', 'lines', 'line_strip', 'triangles', 'quads')

    def __init__(self, parent, x, y, width, height, bg=(255, 255, 255), visible=True, active=True):
        """
        Screen constructor.

        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type width: int
        :param width: width
        :type height: int
        :param height: height
        :type valset: ValSet
        :param valset: the window's value set
        :type bg: list(int * 3)
        :param bg: background color
        :type visible: bool
        :param visible: determines if the screen is drawn
        :type active: bool
        :param active: determines if the screen is updated
        """

        self.parent = parent
        self.valset = parent.valset
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.visible = visible
        self.active = active

        self._batch = _graphics.Batch()
        self._vertex_lists = {}
        self._vertices = {}
        self._colors = {}
        self._vertex_lists['bg'] = None
        for vtype in self._vertex_types:
            self._vertex_lists[vtype] = None
            self._vertices[vtype] = []
            self._colors[vtype] = []

        self.bg = bg
        self.set_bg(bg)

    # region visible and active set functions
    def set_visible(self, visible):
        """
        Sets the screen's visible attribute.
        If True, renders the screen.
        If False, unrenders the screen.

        :type visible: bool
        :param visible: visible
        """
        self.visible = visible
        if visible:
            self.render()
            self.set_bg(self.bg)
        else:
            for vtype in self._vertex_lists.keys():
                if self._vertex_lists[vtype]:
                    self._vertex_lists[vtype].delete()
                self._vertex_lists[vtype] = None

    def set_active(self, active):
        """
        Sets the screen's active attribute.
        The screen is updated when screen.active is True.

        :type active: bool
        :param active: active
        """
        self.active = active

    def on(self):
        """
        Calls set_visible and set_active with True.
        """
        self.set_active(True)
        self.set_visible(True)

    def off(self):
        """
        Calls set_visible and set_active with False.
        """
        self.set_active(False)
        self.set_visible(False)
    # endregion

    # region valset functions
    def get_val(self, name):
        """
        Returns a value from the value set.

        :type name: str
        :param name: the value's name
        :return: the value
        """
        return self.valset.get_val(name)

    def set_val(self, name, new_value):
        """
        Sets a value to a new value.

        :type name: str
        :param name: the value's name
        :param new_value: a new value
        """
        self.valset.set_val(name, new_value)

    def get_valobj(self, name):
        """
        Returns a value object from the value set.

        :type name: str
        :param name: the value's name
        :rtype: Value
        :return: the corresponding value object
        """
        return self.valset.get_valobj(name)
    # endregion

    # region vertex set functions
    def set_points(self, vertexes, colors):
        """
        Sets the vertex and color arrays for points.
        Vertexes and colors must be the same length.

        :type vertexes: list(float)
        :param vertexes: flattened list of 3d vectors
        :type colors: list(float)
        :param colors: flattened list of rgb colors
        """
        self._vertices['points'] = vertexes
        self._colors['points'] = colors

    def set_lines(self, vertexes, colors):
        """
        Sets the vertex and color arrays for lines.
        Vertexes and colors must be the same length.
        Number of vertexes must be divisible by 2.

        :type vertexes: list(float)
        :param vertexes: flattened list of 3d vectors
        :type colors: list(float)
        :param colors: flattened list of rgb colors
        """
        self._vertices['lines'] = vertexes
        self._colors['lines'] = colors

    def set_line_strip(self, vertexes, colors):
        self._vertices['line_strip'] = vertexes
        self._colors['line_strip'] = colors

    def set_triangles(self, vertexes, colors):
        """
        Sets the vertex and color arrays for triangles.
        Vertexes and colors must be the same length.
        Number of vertexes must be divisible by 3.

        :type vertexes: list(float)
        :param vertexes: flattened list of 3d vectors
        :type colors: list(float)
        :param colors: flattened list of rgb colors
        """
        self._vertices['triangles'] = vertexes
        self._colors['triangles'] = colors

    def set_quads(self, vertexes, colors):
        """
        Sets the vertex and color arrays for quads.
        Vertexes and colors must be the same length.
        Number of vertexes must be divisible by 4.

        :type vertexes: list(float)
        :param vertexes: flattened list of 3d vectors
        :type colors: list(float)
        :param colors: flattened list of rgb colors
        """
        self._vertices['quads'] = vertexes
        self._colors['quads'] = colors
    # endregion

    # region to be implemented functions
    def set_bg(self, bg):
        raise NotImplementedError

    def add_point(self, *args, **kwargs):
        raise NotImplementedError

    def add_points(self, *args, **kwargs):
        raise NotImplementedError

    def add_line(self, *args, **kwargs):
        raise NotImplementedError

    def add_triangle(self, *args, **kwargs):
        raise NotImplementedError

    def add_quad(self, *args, **kwargs):
        raise NotImplementedError
    # endregion

    def draw(self):
        """
        Draws the batch.
        """
        self._batch.draw()

    def render(self):
        """
        Renders the screen.
        All calls to add points, lines, etc. should be here.
        self.flush() must be called at the end.
        Should be overridden.
        """
        pass

    def flush(self):
        """
        If the screen is visible, adds the vertexes in the buffer to the batch.
        Then deletes the current vertex lists and clears the vertex and color arrays.
        Should be called at the end of self.render()
        Should not be overridden.
        """
        for vtype in self._vertex_types:
            if self._vertex_lists[vtype]:
                self._vertex_lists[vtype].delete()
                del self._vertex_lists[vtype]
            if not self.visible:
                continue

            if vtype == 'points':
                vlist = self._batch.add(len(self._vertices[vtype]) // 3, GL_POINTS, None,
                                        ('v3f', self._vertices[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'lines':
                vlist = self._batch.add(len(self._vertices[vtype]) // 3, GL_LINES, None,
                                        ('v3f', self._vertices[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'line_strip':
                vlist = self._batch.add(len(self._vertices[vtype]) // 3, GL_LINE_STRIP, None,
                                        ('v3f', self._vertices[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'triangles':
                vlist = self._batch.add(len(self._vertices[vtype]) // 3, GL_TRIANGLES, None,
                                        ('v3f', self._vertices[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'quads':
                vlist = self._batch.add(len(self._vertices[vtype]) // 3, GL_QUADS, None,
                                        ('v3f', self._vertices[vtype]), ('c3B', self._colors[vtype]))
            else:
                vlist = None

            self._vertex_lists[vtype] = vlist

        self._clear()

    def _clear(self):
        """
        Clears the buffer arrays.
        """
        for vtype in self._vertex_types:
            del self._vertices[vtype]
            del self._colors[vtype]
            self._vertices[vtype] = []
            self._colors[vtype] = []

    def mouse_move(self, x, y, dx, dy):
        """
        Called when the mouse moves.
        Can be overridden.
        Refer to pyglet for documentation.
        """
        pass

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """
        Called when the mouse is dragged.
        Can be overridden.
        Refer to pyglet for documentation.
        """
        pass

    def mouse_down(self, x, y, button, modifier):
        """
        Called when the a mouse button is pressed.
        Can be overridden.
        Refer to pyglet for documentation.
        """
        pass

    def mouse_up(self, x, y, button, modifiers):
        """
        Called when a mouse button is released.
        Can be overridden.
        Refer to pyglet for documentation.
        """
        pass

    def key_down(self, symbol, modifiers):
        """
        Called when a key is pressed.
        Can be overridden.
        Refer to pyglet for documentation.
        """
        pass

    def key_up(self, symbol, modifiers):
        """
        Called when a key is released.
        Can be overridden.
        Refer to pyglet for documentation.
        """
        pass

    def tick(self, dt):
        """
        Called by the window's tick function.
        Can be overridden.
        """
        pass

    def resize(self, width, height):
        """
        Called when the window is resized.
        The screen's position and dimensions should be updated here.

        :type width: int
        :param width: window width
        :type height: int
        :param height: window height
        """
        pass

    def is_inside(self, x, y):
        """
        Returns if (x, y) is inside the screen

        :type x: int
        :param x: x
        :type y: int
        :param y: y
        :rtype: bool
        """
        return 0 <= x - self.x < self.w and 0 <= y - self.y < self.h

    def on_resize(self, width, height):
        self.resize(width, height)
        self.set_bg(self.bg)

    def set_pos(self, x, y):
        """
        Sets the screen's position

        :type x: int
        :param x: x
        :type y: int
        :param y: y
        """
        self.x = x
        self.y = y

    def set_size(self, width, height):
        """
        Sets the screen's dimensions

        :type w: int
        :param w: width
        :type h: int
        :param h: height
        :return:
        """
        self.w = width
        self.h = height


class Screen2D(Screen):
    """
    A 2D implementation of Screen.

    :var x: screen's x coord
    :var y: screen's y coord
    :var w: screen's width
    :var h: screen's height
    :var valset: parent window's value set
    :var bg: screen's background color
    :var visible: if the screen is drawn
    :var active: if the screen is updated
    """

    def draw(self):
        """
        Draws the batch in glOrtho perspective.
        """
        xr = self.parent.real_width / self.parent.width
        yr = self.parent.real_height / self.parent.height

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.parent.width, 0, self.parent.height, -101, 101)
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_SCISSOR_TEST)
        glScissor(int(self.x * xr), int(self.y * yr), int(self.w * xr), int(self.h * yr))

        glPushMatrix()
        glTranslatef(self.x + .1, self.y + .1, 0)

        self._batch.draw()

        glPopMatrix()

        glDisable(GL_SCISSOR_TEST)
        glDisable(GL_DEPTH_TEST)

    def set_bg(self, bg):
        """
        Sets the background color.

        :type color: list(int * 3)
        :param color: background color
        """
        if self._vertex_lists['bg']:
            self._vertex_lists['bg'].delete()
        vlist = self._batch.add(4, GL_QUADS, None,
                                ('v3f', (0, 0, -100, self.w, 0, -100,
                                         self.w, self.h, -100, 0, self.h, -100)),
                                ('c3B', bg * 4))
        self.bg = bg
        self._vertex_lists['bg'] = vlist

    def add_point(self, x, y, z=0, color=(0, 0, 0)):
        """
        Adds a point to be drawn.

        :type x: float
        :param x: x
        :type y: float
        :param y: y
        :type z: float
        :param z: z
        :type color: list(int * 3)
        :param color: color
        """
        self._vertices['points'].extend((x, y, z))
        self._colors['points'].extend(color)

    def add_points(self, points, colors):
        """
        Adds a list of points to be drawn.
        Points and colors must be the same length.

        :type points: list(float)
        :param points: flattened list of 3d vectors
        :type colors: list(int)
        :param colors: flattened list of rgb colors
        """
        if len(points) != len(colors):
            raise IndexError('Points and colors must have same length!')
        self._vertices['points'].extend(points)
        self._colors['points'].extend(colors)

    def add_line(self, x1, y1, x2, y2, z=0, color=(0, 0, 0)):
        """
        Adds a line to be drawn.

        :type x1: float
        :param x1: x1
        :type y1: float
        :param y1: y1
        :type x2: float
        :param x2: x2
        :type y2: float
        :param y2: y2
        :type z: float
        :param z: z
        :type color: list(int * 3)
        :param color: color
        """
        self._vertices['lines'].extend((x1, y1, z, x2, y2, z))
        self._colors['lines'].extend(color * 2)

    def add_triangle(self, x1, y1, x2, y2, x3, y3, z=0, color=(0, 0, 0), uniform=True, colors=None):
        """
        Adds a triangle to be drawn.
        If uniform, draws using color parameter.
        If non-uniform, draws using colors parameter.

        :type x1: float
        :param x1: x1
        :type y1: float
        :param y1: y1
        :type x2: float
        :param x2: x2
        :type y2: float
        :param y2: y2
        :type x3: float
        :param x3: x3
        :type y3: float
        :param y3: y3
        :type z: float
        :param z: z
        :type color: list(int * 3)
        :param color: color
        :type uniform: bool
        :param uniform: uniform coloring
        :type colors: list(int * 9)
        :param colors: non-uniform coloring
        """
        self._vertices['triangles'].extend((x1, y1, z, x2, y2, z, x3, y3, z))
        if uniform:
            self._colors['triangles'].extend(color * 3)
        else:
            self._colors['triangles'].extend(colors)

    def add_quad(self, x1, y1, x2, y2, x3, y3, x4, y4, z=0, color=(0, 0, 0), uniform=True, colors=None):
        """
        Adds a quadrilateral to be drawn.
        If uniform, draws using color parameter.
        If non-uniform, draws using colors parameter.

        :type x1: float
        :param x1: x1
        :type y1: float
        :param y1: y1
        :type x2: float
        :param x2: x2
        :type y2: float
        :param y2: y2
        :type x3: float
        :param x3: x3
        :type y3: float
        :param y3: y3
        :type x4: float
        :param x4: x4
        :type y4: float
        :param y4: y4
        :type z: float
        :param z: z
        :type color: list(int * 3)
        :param color: color
        :type uniform: bool
        :param uniform: uniform coloring
        :type colors: list(int * 12)
        :param colors: non-uniform coloring
        """
        self._vertices['quads'].extend((x1, y1, z, x2, y2, z, x3, y3, z, x4, y4, z))
        if uniform:
            self._colors['quads'].extend(color * 4)
        else:
            self._colors['quads'].extend(colors)


class GraphScreen(Screen2D):
    """
    An implementation of Screen2D with zoom.

    :var x: screen's x coord
    :var y: screen's y coord
    :var w: screen's width
    :var h: screen's height
    :var valset: parent window's value set
    :var bg: screen's background color
    :var visible: if the screen is drawn
    :var active: if the screen is updated
    :var gx: graph's center x coord
    :var gy: graph's center y coord
    :var gw: graph's width
    :var gh: graph's height
    :var min_gx: graph's minimum gx drawn
    :var max_gx: graph's maximum gx drawn
    :var min_gy: graph's minimum gy drawn
    :var max_gy: graph's maximum gy drawn
    """

    def __init__(self, parent, x, y, width, height, gx, gy, gw, gh, zoom_val_name, bg=(255, 255, 255), visible=True, active=True):
        """
        GraphScreen constructor.

        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type width: int
        :param width: width
        :type height: int
        :param height: height
        :type gx: float
        :param gx: graph center x coord
        :type gy: float
        :param gy: graph center y coord
        :type gw: float
        :param gw: graph width
        :type gh: float
        :param gh: graph height
        :type valset: ValSet
        :param valset: the window's value set
        :type zoom_val_name: str
        :param zoom_val_name: the zoom ratio value's name
        :type bg: list(int * 3)
        :param bg: background color
        :type visible: bool
        :param visible: determines if the screen is drawn
        :type active: bool
        :param active: determines if the screen is updated
        """
        self.set_graph_coords(gx, gy, gw, gh)
        self._set_graph_minmax()
        self.reset_to(gx, gy, gw, gh)
        super().__init__(parent, x, y, width, height, bg, visible, active)
        # original width / height
        self._ow = width
        self._oh = height

        self.zoom_valobj = self.get_valobj(zoom_val_name)
        self.total_zoom = 1
        self.drag = False
        # offset for drag
        self.offsx = 0
        self.offsy = 0

    def _set_graph_minmax(self):
        self.min_gx = self.gx - self.gw / 2
        self.max_gx = self.gx + self.gw / 2
        self.min_gy = self.gy - self.gh / 2
        self.max_gy = self.gy + self.gh / 2

    def reset_screen(self):
        """
        Resets the graph to its original view and renders the screen.
        """
        self.reset_graph()
        self.set_bg(self.bg)
        self.render()

    def reset_graph(self):
        """
        Only resets the graph to its original view. Does not render the screen.
        """
        self.gx = self._ogx
        self.gy = self._ogy
        self.gw = self._ogw * (self.w / self._ow)
        self.gh = self._ogh * (self.h / self._oh)
        self._set_graph_minmax()
        self.total_zoom = 1

    def reset_to(self, gx, gy, gw, gh):
        """
        Changes the graph coordinates the graph resets to.

        :type gx: float
        :param gx: graph center x
        :type gy: float
        :param gy: graph center y
        :type gw: float
        :param gw: graph width
        :type gh: float
        :param gh: graph height
        """
        self._ogx = gx
        self._ogy = gy
        self._ogw = gw
        self._ogh = gh

    def set_graph_coords(self, gx, gy, gw, gh):
        """
        Sets the graph coordinates.

        :type gx: float
        :param gx: graph center x
        :type gy: float
        :param gy: graph center y
        :type gw: float
        :param gw: graph width
        :type gh: float
        :param gh: graph height
        """
        self.gx = gx
        self.gy = gy
        self.gw = gw
        self.gh = gh

    def set_graph_view(self, gx, gy, zoom):
        """
        Sets the graph coordinates given the center and a zoom with respect to the original coordinates.

        :type gx: float
        :param gx: graph center x
        :type gy: float
        :param gy: graph center y
        :type zoom: float
        :param zoom: graph zoom
        """
        self.gx = gx
        self.gy = gy
        self.total_zoom = zoom
        sqrt_z = zoom ** .5
        self.gw = self._ogw / sqrt_z
        self.gh = self.gw * self.h / self.w

    def resize(self, width, height):
        """
        Called when the window is resized.
        The screen's position and dimensions should be updated here.
        If overridden, should use self.refit(width, height) to set new dimensions.

        :type width: int
        :param width: window width
        :type height: int
        :param height: window height
        """
        self.refit(width, width)

    def refit(self, width, height):
        """
        Refits the screen and graph to a given dimension.

        :type width: int
        :param width: screen width
        :type height: int
        :param height: screen height
        """
        old_gw = self.gw
        old_gh = self.gh
        self.gw *= width / self.w
        self.gh *= height / self.h
        self._set_graph_minmax()
        # self.total_zoom *= (old_gw * old_gh) / (self.gw * self.gh)
        self.w = width
        self.h = height

    def set_bg(self, bg):
        """
        Sets the background color.

        :type color: list(int * 3)
        :param color: background color
        """
        if self._vertex_lists['bg']:
            self._vertex_lists['bg'].delete()
        vlist = self._batch.add(4, GL_QUADS, None,
                                ('v3f', (self.min_gx, self.min_gy, -100, self.max_gx, self.min_gy, -100,
                                         self.max_gx, self.max_gy, -100, self.min_gx, self.max_gy, -100)),
                                ('c3B', bg * 4))
        self.bg = bg
        self._vertex_lists['bg'] = vlist

    def draw(self):
        """
        Draws the batch in glOrtho perspective with zoom.
        """
        xr = self.parent.real_width / self.parent.width
        yr = self.parent.real_height / self.parent.height

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.parent.width, 0, self.parent.height, -101, 101)
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_SCISSOR_TEST)
        glScissor(int(self.x * xr), int(self.y * yr), int(self.w * xr), int(self.h * yr))

        glPushMatrix()

        glTranslatef(self.x + self.w / 2 - self.gx * self.w / self.gw + .1, self.y + self.h / 2 - self.gy * self.h / self.gh + .1, 0)
        glScalef(self.w / self.gw, self.h / self.gh, 1)

        self._batch.draw()

        glPopMatrix()

        glDisable(GL_SCISSOR_TEST)
        glDisable(GL_DEPTH_TEST)

    # region graph move functions
    def up(self):
        """
        Moves the graph center up.
        """
        self.gy += self.gh / 5
        self._set_graph_minmax()
        self.set_bg(self.bg)
        self.render()

    def down(self):
        """
        Moves the graph center down.
        """
        self.gy -= self.gh / 5
        self._set_graph_minmax()
        self.set_bg(self.bg)
        self.render()

    def left(self):
        """
        Moves the graph center left.
        """
        self.gx -= self.gw / 5
        self._set_graph_minmax()
        self.set_bg(self.bg)
        self.render()

    def right(self):
        """
        Moves the graph center right.
        """
        self.gx += self.gw / 5
        self._set_graph_minmax()
        self.set_bg(self.bg)
        self.render()
    # endregion

    def on_screen(self, x, y):
        """
        Transforms a point on the graph to the corresponding point on the screen.

        :type x: float
        :param x: x
        :type y: float
        :param y: y
        :rtype: list(float * 2)
        :return: the point on the screen
        """
        return (x - self.gx + self.gw / 2) * self.w / self.gw, (y - self.gy + self.gh / 2) * self.h / self.gh

    def on_plot(self, x, y):
        """
        Transforms a point on the screen to the corresponding point on the graph.

        :type x: float
        :param x: screen x
        :type y: float
        :param y: screen y
        :rtype: list(float * 2)
        :return: the point on the graph
        """
        return x * self.gw / self.w + self.gx - self.gw / 2, y * self.gh / self.h + self.gy - self.gh / 2

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.drag:
            self.offsx = x - self.mdownx
            self.offsy = y - self.mdowny

    def mouse_down(self, x, y, button, modifier):
        if button == _win.mouse.MIDDLE:
            self.drag = True
            self.mdownx = x
            self.mdowny = y

    def mouse_up(self, x, y, button, modifiers):
        if button == _win.mouse.LEFT:
            self.gx = self.gx - self.gw / 2 + x * self.gw / self.w
            self.gy = self.gy - self.gh / 2 + y * self.gh / self.h
            self.gw *= self.zoom_valobj.value
            self.gh *= self.zoom_valobj.value
            self._set_graph_minmax()
            self.total_zoom *= (1 / self.zoom_valobj.value) ** 2
            # print('zoomed to %.5f,%.5f with size %.9f,%.9f' % (self.gx, self.gy, self.gw, self.gh))
        elif button == _win.mouse.RIGHT:
            self.gx = self.gx - self.gw / 2 + x * self.gw / self.w
            self.gy = self.gy - self.gh / 2 + y * self.gh / self.h
            self.gw /= self.zoom_valobj.value
            self.gh /= self.zoom_valobj.value
            self._set_graph_minmax()
            self.total_zoom /= (1 / self.zoom_valobj.value) ** 2
            # print('zoomed to %.5f,%.5f with size %.9f,%.9f' % (self.gx, self.gy, self.gw, self.gh))
        elif button == _win.mouse.MIDDLE:
            self.drag = False
            msx1, msy1 = self.on_plot(self.mdownx, self.mdowny)
            msx2, msy2 = self.on_plot(x, y)
            self.gx -= msx2 - msx1
            self.gy -= msy2 - msy1
            self._set_graph_minmax()
            self.offsx = 0
            self.offsy = 0
        self.set_bg(self.bg)
        self.render()

    def key_down(self, symbol, modifiers):
        if symbol == _win.key.LEFT:
            self.left()
        elif symbol == _win.key.RIGHT:
            self.right()
        elif symbol == _win.key.UP:
            self.up()
        elif symbol == _win.key.DOWN:
            self.down()


class Screen3D(Screen):
    """
    A 3D implementation of Screen.

    :var x: screen's x coord
    :var y: screen's y coord
    :var w: screen's width
    :var h: screen's height
    :var valset: parent window's value set
    :var bg: screen's background color
    :var visible: if the screen is drawn
    :var active: if the screen is updated
    """

    def __init__(self, parent, x, y, width, height, camera, rotation, offset, bg=(0, 0, 0), visible=True, active=True):
        """
        Screen3D constructor.

        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type width: int
        :param width: width
        :type height: int
        :param height: height
        :type camera: Vector(3d)
        :param camera: camera vector
        :type rotation: Vector(3d)
        :param rotation: rotation vector
        :type offset: Vector(3d)
        :param offset: offset vector=
        :type bg: list(int * 3)
        :param bg: background color
        :type visible: bool
        :param visible: determines if the screen is drawn
        :type active: bool
        :param active: determines if the screen is updated
        """

        self.camera = camera
        self.rotation = rotation
        self.offset = offset
        super().__init__(parent, x, y, width, height, bg, visible, active)

    def set_bg(self, bg):
        """
        Sets the background color.

        :type bg: list(int * 3)
        :param bg: background color
        """

        if self._vertex_lists['bg']:
            self._vertex_lists['bg'].delete()
        points = []
        points.extend((-900, -900, -900, 900, -900, -900, 900, 900, -900, -900, 900, -900))
        points.extend((-900, -900, -900, 900, -900, -900, 900, -900, 900, -900, -900, 900))
        points.extend((900, -900, -900, 900, 900, -900, 900, 900, 900, 900, -900, 900))
        points.extend((900, 900, -900, -900, 900, -900, -900, 900, 900, 900, 900, 900))
        points.extend((-900, 900, -900, -900, -900, -900, -900, -900, 900, -900, 900, 900))
        points.extend((-900, -900, 900, 900, -900, 900, 900, 900, 900, -900, 900, 900))
        colors = [*bg] * 24
        vlist = self._batch.add(24, GL_QUADS, None, ('v3f', points), ('c3B', colors))
        self.bg = bg
        self._vertex_lists['bg'] = vlist

    def draw(self):
        """
        Draws the batch in gluPerspective mode.

        Positive z is towards the eye.
        Rotation rotates about original center.
        BC push has backwards order?
        """
        xr = self.parent.real_width / self.parent.width
        yr = self.parent.real_height / self.parent.height

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        ar = self.w / self.h
        gluPerspective(60, ar, .01, 5000)

        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_SCISSOR_TEST)
        glScissor(int(self.x * xr), int(self.y * yr), int(self.w * xr), int(self.h * yr))

        glPushMatrix()

        '''
        Walk view
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glTranslatef(*self.camera)
        glTranslatef(*self.offset)
        '''

        # Centered view
        # dist has to be z value ???
        #glTranslatef(self.x, self.y, 0)
        glTranslatef(0, 0, 0)
        glTranslatef(*self.camera)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        #glTranslatef(*self.offset)

        self._batch.draw()

        glPopMatrix()

        glDisable(GL_SCISSOR_TEST)
        glDisable(GL_DEPTH_TEST)

    def add_point(self, x, y, z, color=(255, 255, 255)):
        """
        Adds a point to be drawn.

        :type x: float
        :param x: x
        :type y: float
        :param y: y
        :type z: float
        :param z: z
        :type color: list(int * 3)
        :param color: color
        """
        self._vertices['points'].extend((x, y, z))
        self._colors['points'].extend(color)

    def add_points(self, points, colors):
        """
        Adds a list of points to be drawn.
        Points and colors must be the same length.

        :type points: list(float)
        :param points: flattened list of 3d vectors
        :type colors: list(int)
        :param colors: flattened list of rgb colors
        """
        self._vertices['points'].extend(points)
        self._colors['points'].extend(colors)

    def add_line(self, x1, y1, z1, x2, y2, z2, color=(255, 255, 255)):
        """
        Adds a line to be drawn.

        :type x1: float
        :param x1: x1
        :type y1: float
        :param y1: y1
        :type z1: float
        :param z1: z1
        :type x2: float
        :param x2: x2
        :type y2: float
        :param y2: y2
        :type z2: float
        :param z2: z2
        :type color: list(int * 3)
        :param color: color
        """
        self._vertices['lines'].extend((x1, y1, z1, x2, y2, z2))
        self._colors['lines'].extend(color * 2)

    def set_line_strip(self, lines, colors):
        self._vertices['line_strip'] = lines
        self._colors['line_strip'] = colors

    def add_triangle(self, x1, y1, z1, x2, y2, z2, x3, y3, z3, color=(255, 255, 255), uniform=True, colors=None):
        """
        Adds a triangle to be drawn.
        If uniform, draws using color parameter.
        If non-uniform, draws using colors parameter.

        :type x1: float
        :param x1: x1
        :type y1: float
        :param y1: y1
        :type z1: float
        :param z1: z1
        :type x2: float
        :param x2: x2
        :type y2: float
        :param y2: y2
        :type z2: float
        :param z2: z2
        :type x3: float
        :param x3: x3
        :type y3: float
        :param y3: y3
        :type z3: float
        :param z3: z3
        :type color: list(int * 3)
        :param color: color
        :type uniform: bool
        :param uniform: uniform coloring
        :type colors: list(int * 9)
        :param colors: non-uniform coloring
        """
        self._vertices['triangles'].extend((x1, y1, z1, x2, y2, z2, x3, y3, z3))
        if uniform:
            self._colors['triangles'].extend(color * 3)
        else:
            self._colors['triangles'].extend(colors)

    def add_quad(self, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, color=(255, 255, 255), uniform=True, colors=None):
        """
        Adds a quadrilateral to be drawn.
        If uniform, draws using color parameter.
        If non-uniform, draws using colors parameter.

        :type x1: float
        :param x1: x1
        :type y1: float
        :param y1: y1
        :type z1: float
        :param z1: z1
        :type x2: float
        :param x2: x2
        :type y2: float
        :param y2: y2
        :type z2: float
        :param z2: z2
        :type x3: float
        :param x3: x3
        :type y3: float
        :param y3: y3
        :type z3: float
        :param z3: z3
        :type x4: float
        :param x4: x4
        :type y4: float
        :param y4: y4
        :type z4: float
        :param z4: z4
        :type color: list(int * 3)
        :param color: color
        :type uniform: bool
        :param uniform: uniform coloring
        :type colors: list(int * 12)
        :param colors: non-uniform coloring
        """
        self._vertices['quads'].extend((x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4))
        if uniform:
            self._colors['quads'].extend(color * 4)
        else:
            self._colors['quads'].extend(colors)

    def key_down(self, symbol, modifiers):
        if symbol == _win.key.LEFT:
            self.rotation[2] += 5
        elif symbol == _win.key.RIGHT:
            self.rotation[2] -= 5
        elif symbol == _win.key.UP:
            self.rotation[0] += 5
        elif symbol == _win.key.DOWN:
            self.rotation[0] -= 5
        elif symbol == _win.key.X:
            self.rotation[1] -= 5
        elif symbol == _win.key.Z:
            self.rotation[1] += 5
        elif symbol == _win.key.S:
            self.camera[2] += 10
            if self.camera[2] > 400:
                self.camera[2] = 400
        elif symbol == _win.key.A:
            self.camera[2] -= 10
            if self.camera[2] < -400:
                self.camera[2] = -400
        elif symbol == _win.key.J:
            self.camera[0] += 2
        elif symbol == _win.key.L:
            self.camera[0] -= 2
        elif symbol == _win.key.I:
            self.camera[1] -= 2
        elif symbol == _win.key.K:
            self.camera[1] += 2
