# $Id: Magnifier.py,v 1.1.2.7 2007/01/23 22:39:23 marcusva Exp $
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

"""Magnification tool for pygame."""

import pygame

class Magnifier (object):
    """Magnifier (size=(20, 20), factor=2) -> Magnifier

    A screen magnification class for the pygame screen.

    The Magnifier class allows to zoom a certain portion of the screen,
    determined by the current mouse position by a specific scaling
    factor. It creates a rectangular zoom area that will be blit on the
    screen. The zooming area will be placed around the current mouse
    position:

    ##############################################
    #                                            #  ###
    #               ---------------              #  # # - pygame screen
    #               |\           /|              #  ###
    #               | \         / |              #
    #               |  \ooooooo/  |              #  ooo
    #               |   o     o   |              #  o o - Area to zoom (size)
    #               |   o  X  o   |              #  ooo
    #               |   o     o   |              #
    #               |  /ooooooo\  |              #  ---
    #               | /         \ |              #  | | - Zoomed area.
    #               |/           \|              #  ---
    #               ---------------              #
    #                                            #   X - Mouse cursor position. 
    ##############################################

    The size of the area to zoom can be adjusted using the 'size'
    attribute and set_size() method.

    # Zoom a 40x40 px area around the mouse cursor.
    magnifier.size = 40, 40
    magnifier.set_size (40, 40)

    The factor by which the area around the mouse cursor should be
    magnified can be set using the 'factor' attribute or set_factor() method.

    # Zoom the wanted area by 3 with a result of an area three times as big
    # as the original one.
    magnifier.factor = 3
    magnifier.set_factor (3)

    By default the Magnifier uses a simple call to pygame.transform.scale(),
    which does not provide optimal results for each surface. The 'zoom_func'
    attribute and set_zoom_func() method allow you to provide an own zoom
    function, which has to return the zoomed surface. It receives the actual
    screen surface, the mouse position the zoomed area will be centered at and
    the sizes and scaling factor to use for zooming.

    def own_zoom_func (screen, mousepos, resultsize, size, factor):
        ...
        return zoomed_surface

    magnifier.zoom_func = own_zoom_func
    magnifier.set_zoom_func (own_zoom_func)
    
    The resultsize is a tuple containing the magnifier size multiplied with the
    set factor of the magnifier:
    resultsize = int (size[0] * factor), int (size[1] * factor)
    size and factor contain the currently set values of the respective
    attributes of the Magnifier instance. An implementation of the default zoom
    functionality of the Magnifier using the 'zoom_func' attribute would look
    like the following:

    def own_zoom_func (screen, mousepos, resultsize, size, factor):
        offset = mousepos[0] - size[0] / 2, mousepos[1] - size[1] / 2
        # Create zoomable surface.
        surface = pygame.Surface ((size[0], size[1]))
        surface.blit (screen, (0, 0), (offset[0], offset[1], size[0], size[1]))
        # Zoom and blit.
        return pygame.transform.scale (surface, (resultsize[0], resultsize[1]))
    
    Attributes:
    factor    - The zoom factor to use for magnification.
    size      - The size of the area around the mouse cursor to zoom.
    border    - Indicates whether a 1px border around the magnified area should
                be drawn.
    zoom_func -
    """
    def __init__ (self, size=(20, 20), factor=2):
        self._factor = factor
        self._size = size
        self._oldsurface = None
        self._oldpos = None # The topleft offset of the area.
        self._mousepos = None  # The mouse position.
        self._border = True
        self._zoomfunc = None

    def set_factor (self, factor):
        """M.set_factor (...) -> None

        Sets the zoom factor to use for magnification.

        Raises a TypeError, if the argument is not an integer or float.
        Raises a ValueError, if the argument is smaller than 1.
        """
        if type (factor) not in (int, float):
            raise TypeError ("factor must be an integer or float")
        if factor < 1:
            raise ValueError ("factor must not be smaller than 1")
        self._factor = factor
        if self._mousepos:
            self._update (self._mousepos)
        
    def set_size (self, width, height):
        """M.set_size (...) -> None

        Sets the width and height of the area to zoom.

        Raises a TypeError, if the arguments are not integers.
        Raises a ValueError, if the arguments are smaller than 1.
        """
        if (type (width) != int) or (type (height) != int):
            raise TypeError ("width and height must be integers")
        if (width < 1) or (height < 1):
            raise ValueError ("width and height must not be smaller than 1")
        self._size = width, height
        if self._mousepos:
            self._update (self._mousepos)

    def enable_border (self, border):
        """M.enable_border (...) -> None

        Enables or disables the display of a 1px border around the zoom area.

        The argument will be interpreted as boolean value.
        """
        self._border = border
        if self._mousepos:
            self._update (self._mousepos)

    def restore (self):
        """M.restore () -> None

        Restores the original screen content.
        """
        screen = pygame.display.get_surface ()
        # Restore old surface area.
        if self._oldsurface:
            screen.blit (self._oldsurface, self._oldpos)
            self._oldsurface = None

    def set_zoom_func (self, func):
        """D.set_zoom_func (...) -> None

        Sets the zoom function to use for the Magnifier..

        Raises a TypeError, if func is not callable.
        """
        if not callable (func):
            raise TypeError ("func must be callable")
        self._zoomfunc = func
        if self._mousepos:
            self._update (self._mousepos)

    def notify (self, *events):
        """M.notify (...) -> bool

        Notifies the Magnifier about a pygame.event.Event.

        The argument must be a pygame.event.Event.
        """
        motion = [e for e in events if e.type == pygame.MOUSEMOTION]
        if motion:
            self._mousepos = motion[-1].pos
            self._update (self._mousepos)
            return True

        # Update the screen for the case it changed.
        if self._mousepos:
            self._update (self._mousepos)
        return False

    def _update (self, position):
        """M._update (...) -> None

        Update the magnification area.
        """
        surface = None
        screen = pygame.display.get_surface ()

        rsize = int (self.size[0] * self.factor), \
                int (self.size[1] * self.factor)
        offset = position[0] - rsize[0] / 2, position[1] - rsize[1] / 2
        zoffset = position[0] - self.size[0] / 2, position[1] - self.size[1] / 2

        # Restore old surface area.
        if self._oldsurface:
            screen.blit (self._oldsurface, self._oldpos)

        # Preserve surface at the position.
        self._oldsurface = pygame.Surface ((rsize[0], rsize[1]))
        self._oldsurface.blit (screen, (0, 0), (offset[0], offset[1],
                                                rsize[0], rsize[1]))

        if self._zoomfunc:
            surface = self.zoom_func (screen, position, rsize, self.size,
                                      self.factor)
        else:
            # Create zoomable surface.
            surface = pygame.Surface ((self.size[0], self.size[1]))
            surface.blit (screen, (0, 0), (zoffset[0], zoffset[1],
                                           self.size[0], self.size[1]))

            # Zoom and blit.
            surface = pygame.transform.scale (surface, (rsize[0], rsize[1]))

        if self.border:
            pygame.draw.line (surface, (0, 0, 0), (0, 0), (0, rsize[1]))
            pygame.draw.line (surface, (0, 0, 0), (0, 0), (rsize[0], 0))
            pygame.draw.line (surface, (0, 0, 0), (rsize[0] - 1, rsize[1] - 1),
                              (0, rsize[1] - 1))
            pygame.draw.line (surface, (0, 0, 0), (rsize[0] - 1, rsize[1] - 1),
                              (rsize[0] - 1, 0))

        screen.blit (surface, offset)
        self._oldpos = offset

    size = property (lambda self: self._size,
                     lambda self, (x, y): self.set_size (x, y),
                     doc = "The size of the magnification area.")
    factor = property (lambda self: self._factor,
                       lambda self, var: self.set_factor (var),
                       doc = "The zoom factor of the magnification area.")
    border = property (lambda self: self._border,
                       lambda self, var: self.enable_border (var),
                       doc = "Indicates whether a border should be shown.")
    zoom_func = property (lambda self: self._zoomfunc,
                          lambda self, var: self.set_zoom_func (var),
                          doc = "The zoom function to use.")
