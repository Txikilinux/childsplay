# $Id: Graph2D.py,v 1.9.2.5 2007/01/26 22:51:33 marcusva Exp $
#
# Copyright (c) 2006-2007, Marcus von Appen
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""A 2D graph widget."""

from pygame import K_PLUS, K_KP_PLUS, K_MINUS, K_KP_MINUS, K_DOWN, K_LEFT
from pygame import K_RIGHT, K_UP
from Diagram import Diagram
from childsplay_sp.ocempgui.draw import Draw
from Constants import *
import base

class Graph2D (Diagram):
    """Graph2D (width, height) -> Graph2D

    A widget displaying graphs on a cartesian coordinate plane.

    The Graph2D widget displays function graphs on a cartesian
    coordinate plane using two axes.

    The axes, scale units and units attributes must have at least two
    values on assignment to fit both, the horizontal and vertical axes.

    self.axes = 't', 'v'     # Set velocity related to time.
    self.set_axes ('x', 'y') # The default.

    # seconds for the time axis, mph for the velocity axis.
    self.scale_units = 's', 'mph' 
    self.set_scale_units ('-', '-') # The default.

    # Each second has a distance of 10px to its neighbours and each mph
    # has a distance of 25px to its neighbours.
    self.units = 10, 25
    self.set_units (10, 10) # The default.
    
    Setting the 'orientation' attribute of the Graph2D widget to
    ORIENTATION_VERTICAL will cause it to be rotated clockwise by 90
    degrees.

    The Graph2D can display the names of the axes and their scale units
    next to the related axes. This can be adjusted using the
    'show_names' attribute and set_show_names() method:

    self.show_names = True # Show the names and scale units.
    self.set_show_names (False) # Do not show them.

    The axes and graph colors can be set to individual values (e.g. to
    outline certain function behaviours) through the 'axis_color' and
    'graph_color' attributes and their respective methods
    set_axis_color() and set_graph_color().

    self.axis_color = (0, 255, 0)
    self.set_axiscolor ((255, 255, 0))

    self.graph_color = (0, 255, 255)
    self.set_graph_color (255, 0, 0)

    The 'zoom_factor' attribute and set_zoom_factor() method set the zoom
    factor for the graph. Values between 0 and 1 will zoom it out while
    values greater than 1 will zoom it out.
    Note: The zoom factor directly modifies the 'units' attribute values,
    which can lead to rounding errors when using floating point zoom factors.
    This usually results in a minor discrepancy, when you try to restore the
    original values.

    # Zoom the x axis out and the y axis in.
    self.zoom_factor = 0.5, 2.0

    # Zoom both axis in.
    self.set_zoom_factor (3.0, 3.0)
    
    Default action (invoked by activate()):
    See the Diagram class.
    
    Mnemonic action (invoked by activate_mnemonic()):
    See the Diagram class.

    Signals:
    SIG_KEYDOWN       - Invoked, when a key is pressed while the Graph2D has
                        the input.
    SIG_MOUSEDOWN     - Invoked, when a mouse button is pressed on the
                        Graph2D.
    SIG_DOUBLECLICKED - Invoked, when a double-click was emitted on the
                        Graph2D.
    
    Attributes:
    show_names  - Indicates, whether the axis names and scale units should
                  be shown or not.
    axis_color  - The color for both axes.
    graph_color - The color for the displayed graph.
    zoom_factor - The zoom factor values for both axes.
    """
    def __init__ (self, width, height):
        Diagram.__init__ (self)

        # Some defaults.
        self._zoom_factor = (1, 1)
        self._units = (20, 20)
        self._scaleunits = ("-", "-")
        self._axes = ("x", "y")

        self._shownames = True

        # Colors.
        self._axiscolor = (0, 0, 0)
        self._graphcolor = (255, 0, 0)

        # Signals.
        self._signals[SIG_KEYDOWN] = []
        self._signals[SIG_MOUSEDOWN] = []
        self._signals[SIG_DOUBLECLICKED] = []
        
        self.minsize = width, height

    def get_scale_units (self):
        """G.get_scale_units (...) -> None

        Gets the scale units of the axes.
        """
        return self._scaleunits
    
    def set_scale_units (self, units):
        """G.set_scale_units (...) -> None

        Sets the scale units of the axes.

        Raises a TypeError, if the passed argument is not a list or tuple.
        Raises a ValueError, if the passed argument values are not strings.
        """
        if type (units) not in (list, tuple):
            raise TypeError ("units must be a list or tuple")
        if len (units) < 2:
            raise ValueError ("units must at least contains 2 values")
        ov = filter (lambda x: type (x) not in (str, unicode), units)
        if len (ov) != 0:
            raise ValueError ("values in units must be strings or unicode")
        self._scaleunits = units
        self.dirty = True

    def get_units (self):
        """G.set_units (...) -> None

        Gets the pixels per unit for dimensioning.
        """
        return self._units
    
    def set_units (self, units):
        """G.set_units (...) -> None

        Sets the pixels per unit for dimensioning.

        Raises a TypeError, if the passed argument is not a list or tuple.
        Raises a ValueError, if the passed argument values are not
        integers greater than 0.
        """
        if type (units) not in (list, tuple):
            raise TypeError ("units must be a list or tuple")
        if len (units) < 2:
            raise ValueError ("units must at least contains 2 values")
        ov = filter (lambda x: (type (x) != int) or (x <= 0), units)
        if len (ov) != 0:
            raise ValueError ("values in units must be positive integers")
        self._units = units
        self.dirty = True

    def get_axes (self):
        """G.get_axes (...) -> None

        Gets the amount and names of the axes.
        """
        return self._axes

    def set_axes (self, axes):
        """G.set_axes (...) -> None

        Sets the amount and names of the axes.

        Raises a TypeError, if the passed argument is not a list or tuple.
        Raises a ValueError, if the passed argument values are not strings.
        """
        if type (axes) not in (list, tuple):
            raise TypeError ("axes must be a list or tuple")
        if len (axes) < 2:
            raise ValueError ("axes must at least contains 2 values")
        ov = filter (lambda x: type (x) not in (str, unicode), axes)
        if len (ov) != 0:
            raise ValueError ("values in axes must be strings or unicode")
        self._axes = axes
        self.dirty = True

    def set_show_names (self, var):
        """G.set_show_names (...) -> None

        Sets, whether the axis names and scale units should be shown.

        If set to True, the names and scale units of both axes will be
        displayed besides and beneath the axes in the form 'name / unit'.
        """
        self._shownames = var
        self.dirty = True

    def set_axis_color (self, var):
        """G.set_axis_color (...) -> None

        Sets the color of the axes of the coordinate plane.
        """
        self._graphcolor = var
        self.dirty = True

    def set_graph_color (self, var):
        """G.set_graph_color (...) -> None

        Sets the color of the graph to draw.
        """
        self._graphcolor = var
        self.dirty = True

    def set_data (self, data):
        """G.set_data (...) -> None

        Sets the data to evaluate.

        Raises a TypeError, if the passed argument is not a list or tuple.
        Raises a ValueError, if the passed argument values are not
        integers or floats.
        """
        if data != None:
            if type (data) not in (list, tuple):
                raise TypeError ("data must be a list, tuple or array")
            ov = filter (lambda x: type (x) not in (int, float), data)
            if len (ov) != 0:
                raise ValueError ("vales in data must be integers or float")
        Diagram.set_data (self, data)

    def set_zoom_factor (self, x, y):
        """G.set_zoom_factor (...) -> None

        Zooms the graph in or out by modifying the pixel per units values.

        Zooms the graph in or out by modifying the pixel per units
        values. Passing 0 as zoom factor will reset the 

        Raises a TypeError, if the passed arguments are not floats or
        integers.
        Raises a ValueError, if the passed arguments are smaller than or
        equal to 0.
        """
        if (type (x) not in (float, int)) or (type (y) not in (float, int)):
            raise TypeError ("x and y must floats or integers")
        if (x <= 0) or (y <= 0):
            raise ValueError ("x and y must be grater than 0")

        ux, uy = 0, 0
        oldx, oldy = self._zoom_factor

        ux = max (1, int ((self._units[0] / oldx) * x))
        uy = max (1, int ((self._units[1] / oldy) * y))
        self._zoomfactor = (x, y)
        if self.units != (ux, uy):
            self.units = ux, uy

    def zoom_in (self):
        """ G.zoom_in () -> None

        Zooms into the graph by factor 2.
        """
        x, y = self.zoom_factor
        self.set_zoom_factor (x * 2.0, y * 2.0)

    def zoom_out (self):
        """G.zoom_out () -> None

        Zoom out of the graph by factor 2.
        """
        x, y = self.zoom_factor
        x /= 2.0
        y /= 2.0
        if x == 0:
            x = self.zoom_factor[0]
        if y == 0:
            y = self.zoom_factor[1]
        self.set_zoom_factor (x, y)
        
    def draw_bg (self):
        """G.draw_bg () -> Surface

        Draws the Graph2D background surface and returns it.

        Creates the visible background surface of the Graph2D and
        returns it to the caller.
        """
        return base.GlobalStyle.engine.draw_graph2d (self)

    def notify (self, event):
        """G.notify (...) -> None

        Notifies the Graph2D about an event.
        """
        if not self.sensitive:
            return

        if event.signal in SIGNALS_MOUSE:
            eventarea = self.rect_to_client ()

            if (event.signal == SIG_MOUSEDOWN) and \
                   eventarea.collidepoint (event.data.pos):
                if event.data.button == 1:
                    self.focus = True

                # Mouse wheel.
                elif event.data.button == 4:
                    self.zoom_out ()
                elif event.data.button == 5:
                    self.zoom_in ()

                self.run_signal_handlers (SIG_MOUSEDOWN, event.data)
                event.handled = True
                
        elif (event.signal == SIG_DOUBLECLICKED):
            eventarea = self.rect_to_client ()

            if eventarea.collidepoint (event.data.pos):
                # The y origin starts at the bottom left, thus we have
                # to invert the y value by using the height.
                self.origin = event.data.pos[0] - eventarea.x, \
                              self.height - event.data.pos[1] + eventarea.y
                self.run_signal_handlers (SIG_DOUBLECLICKED, event.data)
                event.handled = True
                 
        elif self.focus and (event.signal == SIG_KEYDOWN):
            # Zoom in and out.
            if event.data.key in (K_PLUS, K_KP_PLUS):
                self.zoom_in ()
                event.handled = True
            elif event.data.key in (K_MINUS, K_KP_MINUS):
                self.zoom_out ()
                event.handled = True
            # Axis movement.
            elif event.data.key == K_UP:
                self.origin = (self.origin[0], self.origin[1] - 5)
                event.handled = True
            elif event.data.key == K_DOWN:
                self.origin = (self.origin[0], self.origin[1] + 5)
                event.handled = True
            elif event.data.key == K_LEFT:
                self.origin = (self.origin[0] + 5, self.origin[1])
                event.handled = True
            elif event.data.key == K_RIGHT:
                self.origin = (self.origin[0] - 5, self.origin[1])
                event.handled = True

        Diagram.notify (self, event)
    
    def _draw_axes (self, surface, rect, origin, unitx, unity):
        """G._draw_axes (...) -> None

        Draws the coordinate axes on the surface.
        """
        style = base.GlobalStyle
        cls = self.__class__

        if self.orientation == ORIENTATION_VERTICAL:
            right = (origin[0], rect.bottom)
            left = (origin[0], rect.top)
            top = (rect.right, origin[1])
            bottom = (rect.left, origin[1])
        else:
            left = (rect.left, origin[1])
            right = (rect.right, origin[1])
            top = (origin[0], rect.top)
            bottom = (origin[0], rect.bottom)
        start = None
        end = None
        scx = 1
        scy = 1

        # Draw both, positive and negative axes
        if self.negative:
            Draw.draw_line (surface, self._axiscolor, left, right, 1)
            Draw.draw_line (surface, self._axiscolor, bottom, top, 1)
        else:
            Draw.draw_line (surface, self._axiscolor, origin, right, 1)
            Draw.draw_line (surface, self._axiscolor, origin, top, 1)

        # Axis names and units.
        if self.show_names:
            st = "%s / %s " % (self.axes[0], self.scale_units[0])
            surface_x = style.engine.draw_string (st, self.state, cls,
                                                  self.style)

            st = "%s / %s " % (self.axes[1], self.scale_units[1])
            surface_y = style.engine.draw_string (st, self.state, cls,
                                                  self.style)

            rect_sx = surface_x.get_rect()
            rext_sy = surface_y.get_rect()
            if self.orientation == ORIENTATION_VERTICAL:
                surface.blit (surface_x,
                              (right[0] - 1 - 2 * scx - rect_sx.width,
                               right[1] - rect_sx.height))
                surface.blit (surface_y, (top[0] - rect_sy.width,
                                          top[1] + 1 + 2 * scy))
            else:
                surface.blit (surface_x, (right[0] - rect_sx.width,
                                          right[1] + 1 + 2 * scx))
                surface.blit (surface_y, (top[0] + 1 + 2 * scy, top[1]))
        
        # Draw the scale unit marks.
        # From the origin right and up 
        y = origin[1]
        x = origin[0]
        while y > rect.top:
            start = (origin[0] - scy, y)
            end = (origin[0] + scy, y)
            Draw.draw_line (surface, self._axiscolor, start, end, 1)
            y -= unity
        while x < rect.right:
            start = (x, origin[1] - scx)
            end = (x, origin[1] + scx)
            Draw.draw_line (surface, self._axiscolor, start, end, 1)
            x += unitx

        # From the origin down and left.
        if self.negative:
            y = origin[1]
            while y < rect.bottom:
                start = (origin[0] - scy, y)
                end = (origin[0] + scy, y)
                Draw.draw_line (surface, self._axiscolor, start, end, 1)
                y += unity
            x = origin[0]
            while x > rect.left:
                start = (x, origin[1] - scx)
                end = (x, origin[1] + scx)
                Draw.draw_line (surface, self._axiscolor, start, end, 1)
                x -= unitx

    def draw (self):
        """W.draw () -> None

        Draws the Graph2D surface.

        Creates the visible surface of the Graph2D.
        """
        Diagram.draw (self)
        surface = self.image
        rect = surface.get_rect ()

        # Orientation swapped?
        swap = self.orientation == ORIENTATION_VERTICAL
        
        # Coordinates.
        origin = (rect.left + self.origin[0],
                  rect.bottom - self.origin[1] - 1)

        unitx = 1.0
        unity = 1.0
        if self.units and (len (self.units) > 1):
            if self.orientation == ORIENTATION_VERTICAL:
                unitx = self.units[1]
                unity = self.units[0]
            else:
                unitx = self.units[0]
                unity = self.units[1]

        self._draw_axes (surface, rect, origin, unitx, unity)
        
        data = self.data
        values = self.values

        if data and values:
            # Filter negative values.
            if not self.negative:
                data = filter (lambda x: x >= 0, data)
                values = filter (lambda y: y >= 0, values)
            
            # Create the coordinate tuples and take the unit resolution into
            # account.
            coords = []
            org0 = origin[0]
            org1 = origin[1]
            if self.orientation == ORIENTATION_VERTICAL:
                coords = map (lambda x, y: (int (org1 + (x * unitx)),
                                            int (org0 + (y * unity))),
                              data, values)
            else:
                coords = map (lambda x, y: (int (org0 + (x * unitx)),
                                            int (org1 - (y * unity))),
                              data, values)

            # Filter non-visible values.
            width = self.width
            height = self.height
            coords = filter (lambda (x, y): (0 < x < width) and \
                             (0 < y < width), coords)
            
            # Draw them.
            color = self.graph_color
            setat = surface.set_at
            for xy in coords:
                setat (xy, color)

    show_names = property (lambda self: self._shownames,
                           lambda self, var: self.set_show_names (var),
                           doc = "Indicates, whether the axis names should " \
                           "be shown.")
    axis_color = property (lambda self: self._axiscolor,
                           lambda self, var: self.set_axis_color (var),
                           doc = "The color of the axes.")
    graph_color = property (lambda self: self._graphcolor,
                            lambda self, var: self.set_graph_color (var),
                            doc = "The color of the graph.")
    zoom_factor = property (lambda self: self._zoom_factor,
                            lambda self, (x, y): self.set_zoom_factory (x, y),
                            doc = "Zoom factor for the axes.")
