# $Id: Scale.py,v 1.40.2.5 2007/01/26 22:51:33 marcusva Exp $
#
# Copyright (c) 2004-2007, Marcus von Appen
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

"""Slider widgets for selecting a value from a range."""

from pygame import K_KP_PLUS, K_PLUS, K_RIGHT, K_DOWN, K_KP_MINUS, K_MINUS
from pygame import K_LEFT, K_UP, K_PAGEUP, K_PAGEDOWN, K_HOME, K_END, Rect
from Range import Range
from childsplay_sp.ocempgui.draw import Draw
from Constants import *
from StyleInformation import StyleInformation
import base

class Scale (Range):
    """Scale (minimum, maximum, step=1.0) -> Scale

    An abstract scaling widget class for numerical value selections.

    The Scale is an abstract widget class, which enhances the Range by
    different events and an activation method. Concrete implementations
    of it are the HScale, a horizontal scale widget, and the VScale,
    vertical scale widget.
    
    Inheriting widgets have to implement the _get_value_from_coords()
    method, which calculates the value of the Scale using a pair of
    absolute screen coordinates relative to a given area. Example
    implementations can be found in the HScale and VScale widget
    classes.
    
    Default action (invoked by activate()):
    Give the Scale the input focus.
    
    Mnemonic action (invoked by activate_mnemonic()):
    None

    Signals:
    SIG_MOUSEDOWN - Invoked, when a mouse button is pressed on the
                    Scale.
    SIG_MOUSEUP   - Invoked, when a mouse buttor is released on the
                    Scale.
    SIG_MOUSEMOVE - Invoked, when the mouse moves over the Scale.
    """
    def __init__ (self, minimum, maximum, step=1.0):
        Range.__init__ (self, minimum, maximum, step)

        # Internal click and mouse enter detection.
        self.__click = False

        self._signals[SIG_MOUSEDOWN] = []
        self._signals[SIG_MOUSEMOVE] = []
        self._signals[SIG_MOUSEUP] = []
        self._signals[SIG_KEYDOWN] = None # Dummy for keyboard activation.

    def activate (self):
        """S.activate () -> None

        Activates the Scale default action.

        Activates the Scale default action. This usually means giving
        the Scale the input focus.
        """
        if not self.sensitive:
            return
        self.focus = True
    
    def _get_value_from_coords (self, area, coords):
        """S._get_value_from_coords (...) -> float

        Calculates the float value of the Scale.

        Calculates the float value of the Scale from the passed
        absolute coordinates tuple relative to the area.

        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError

    def notify (self, event):
        """S.notify (...) -> None

        Notifies the Scale about an event.
        """
        if not self.sensitive:
            return

        if event.signal in SIGNALS_MOUSE:
            eventarea = self.rect_to_client ()

            if event.signal == SIG_MOUSEDOWN:
                if eventarea.collidepoint (event.data.pos):
                    self.focus = True
                    if event.data.button == 1:
                        # Guarantee a correct look, if the signal
                        # handlers run a long time
                        self.state = STATE_ACTIVE
                    self.run_signal_handlers (SIG_MOUSEDOWN, event.data)
                    if event.data.button == 1: # Only react upon left clicks.
                        self.__click = True
                        val = self._get_value_from_coords (eventarea,
                                                           event.data.pos)
                        if val != self.value:
                            self.value = val
                    # Mouse wheel.
                    elif event.data.button == 4:
                        val = self.value - 2 * self.step
                        if val > self.minimum:
                            self.value = val
                        else:
                            self.value = self.minimum
                    elif event.data.button == 5:
                        val = self.value + 2 * self.step
                        if val < self.maximum:
                            self.value = val
                        else:
                            self.value = self.maximum
                    event.handled = True

            elif event.signal == SIG_MOUSEUP:
                if eventarea.collidepoint (event.data.pos):
                    if event.data.button == 1:
                        if self.state == STATE_ACTIVE:
                            self.state = STATE_ENTERED
                        else:
                            self.state = STATE_NORMAL
                        self.__click = False
                    self.run_signal_handlers (SIG_MOUSEUP, event.data)
                    event.handled = True
                elif (event.data.button == 1) and self.__click:
                    self.state = STATE_NORMAL
                    self.__click = False
        
            elif event.signal == SIG_MOUSEMOVE:
                if eventarea.collidepoint (event.data.pos):
                    self.focus = True
                    self.run_signal_handlers (SIG_MOUSEMOVE, event.data)
                    if self.__click and self.focus:
                        val = self._get_value_from_coords (eventarea,
                                                           event.data.pos)
                        if val != self.value:
                            self.value = val

                    self.entered = True
                    event.handled = True
                else:
                    self.entered = False

        elif (event.signal == SIG_KEYDOWN) and self.focus:
            if event.data.key in (K_KP_PLUS, K_PLUS, K_RIGHT, K_DOWN):
                self.increase ()
                event.handled = True
            elif event.data.key in (K_KP_MINUS, K_MINUS, K_LEFT, K_UP):
                self.decrease ()
                event.handled = True
            elif event.data.key == K_PAGEUP:
                val = self.value - 10 * self.step
                if val > self.minimum:
                    self.value = val
                else:
                    self.value = self.minimum
                event.handled = True
            elif event.data.key == K_PAGEDOWN:
                val = self.value + 10 * self.step
                if val < self.maximum:
                    self.value = val
                else:
                    self.value = self.maximum
                event.handled = True
            elif event.data.key == K_END:
                self.value = self.maximum
                event.handled = True
            elif event.data.key == K_HOME:
                self.value = self.minimum
                event.handled = True

        Range.notify (self, event)

class HScale (Scale):
    """HScale (minimum, maximum, step=1.0) -> HScale

    A horizontal scaling widget for selecting numerical values.

    The HScale widget is a scaling widget with a horizontal orientation
    and allows the user to select and adjust a value from a range moving
    a slider.

    Default action (invoked by activate()):
    See the Scale class.
    
    Mnemonic action (invoked by activate_mnemonic()):
    See the Scale class.
    """
    def __init__ (self, minimum, maximum, step=1.0):
        Scale.__init__ (self, minimum, maximum, step)
        self.minsize = 120, 20 # Default size.

    def _get_value_from_coords (self, area, coords):
        """H._get_value_from_coords (...) -> float

        Calculates the float value of the HScale.

        Calculates the float value of the HScale from the passed
        absolute coordinates tuple relative to the area.
        """
        # We need this for a proper calculation.
        slider = StyleInformation.get ("HSCALE_SLIDER_SIZE")
        
        # The slide range, in which the slider can move.
        slide = self.width - slider[0]

        # Calculate the absolute current position
        n = coords[0] - area.left - slider[0] / 2.0

        # Step range in dependance of the width and value range of the
        # Scale.
        step = (self.maximum - self.minimum) / float (slide)

        # Calculate it.
        val = self.minimum + step * n
        if val > self.maximum:
            val = self.maximum
        elif val < self.minimum:
            val = self.minimum
        return val

    def _get_coords_from_value (self):
        """H._get_coords_from_value () -> float

        Calculates the coordinates from the current value of the HScale.

        Calculates the relative coordinates on the HScale from the
        current value.
        """
        # We need this for a proper calculation.
        slider = StyleInformation.get ("HSCALE_SLIDER_SIZE")

        width = self.width
        
        # The slide range in which the slider can move.
        slide = width - slider[0]

        # Step range in dependance of the width and value range of the
        # Scale.
        step = (self.maximum - self.minimum) / float (slide)

        # Calculate the value
        val  = (self.value - self.minimum) / step + slider[0] / 2.0
        return val

    def draw_bg (self):
        """H.draw_bg () -> Surface

        Draws the background surface of the HScale and returns it.

        Creates the visible surface of the HScale and returns it to the
        caller.
        """
        return base.GlobalStyle.engine.draw_scale (self,
                                                   ORIENTATION_HORIZONTAL)

    def draw (self):
        """H.draw () -> None

        Draws the HScale surface and its slider.
        """
        Scale.draw (self)
        cls = self.__class__
        style = base.GlobalStyle
        active = StyleInformation.get ("ACTIVE_BORDER")
        border = style.get_border_size (cls, self.style,
                                        StyleInformation.get ("SCALE_BORDER"))
        border_active = style.get_border_size (cls, self.style, active)
        slider = StyleInformation.get ("HSCALE_SLIDER_SIZE")

        # Creates the slider surface.
        sf_slider = style.engine.draw_slider (slider[0], slider[1],
                                              self.state, cls, self.style)
        rect_slider = sf_slider.get_rect ()

        # Dashed border.
        if self.focus:
            b = border + border_active
            r = Rect (b, b, rect_slider.width - 2 * b,
                      rect_slider.height - 2 * b)
            style.engine.draw_border \
                            (sf_slider, self.state, cls, self.style, active, r,
                             StyleInformation.get ("ACTIVE_BORDER_SPACE"))

        size = self.width - 2 * border, self.height / 3 - 2 * border

        # Fill the scale line.
        sf_fill = Draw.draw_rect (size[0], size[1],
                                  StyleInformation.get ("SCALE_COLOR"))
        self.image.blit (sf_fill, (border, self.height / 3 + border))

        # Blit slider at the correct position.
        rect_slider.centerx = self._get_coords_from_value ()
        rect_slider.centery = self.image.get_rect ().centery
        self.image.blit (sf_slider, rect_slider)
        
        # Fill until the slider start.
        if rect_slider.x > 0:
            sf_fill = Draw.draw_rect (rect_slider.x - border, size[1],
                                      StyleInformation.get ("PROGRESS_COLOR"))
            self.image.blit (sf_fill, (border, self.height / 3 + border))

class VScale (Scale):
    """VScale (minimum, maximum, step=1.0) -> VScale

    A vertical scaling widget for selecting numerical values.

    The VScale widget is a scaling widget with a vertical orientation
    and allows the user to select and adjust a value from a range moving
    a slider.
    
    Default action (invoked by activate()):
    See the Scale class.
    
    Mnemonic action (invoked by activate_mnemonic()):
    See the Scale class.
    """
    def __init__ (self, minimum, maximum, step=1.0):
        Scale.__init__ (self, minimum, maximum, step)
        self.minsize = 20, 120 # Default size.
    
    def _get_value_from_coords (self, area, coords):
        """V._get_value_from_coords (...) -> float

        Calculates the float value of the VScale.

        Calculates the float value of the VScale from the passed
        absolute coordinates tuple relative to the area.
        """
        # We need this for a proper calculation.
        slider = StyleInformation.get ("VSCALE_SLIDER_SIZE")
        
        # The slide range, in which the slider can move.
        slide = self.height - slider[1]

        # Calculate the absolute current position
        n = coords[1] - area.top - slider[1] / 2.0

        # Step range in dependance of the width and value range of the
        # Scale.
        step = (self.maximum - self.minimum) / float (slide)

        # Calculate it.
        val = self.minimum + step * n
        if val > self.maximum:
            val = self.maximum
        elif val < self.minimum:
            val = self.minimum
        return val

    def _get_coords_from_value (self):
        """V.get_coords_from_value () -> float

        Calculates the coordinates from the current value of the VScale.

        Calculates the relative coordinates on the VScale from the
        current value.
        """
        # We need this for a proper calculation.
        slider = StyleInformation.get ("VSCALE_SLIDER_SIZE")
        height = self.height
        
        # The slide range in which the slider can move.
        slide = height - slider[1]

        # Step range in dependance of the width and value range of the
        # Scale.
        step = (self.maximum - self.minimum) / float (slide)

        # Calculate the value
        val  = (self.value - self.minimum) / step + slider[1] / 2.0
        return val

    def draw_bg (self):
        """V.draw_bg () -> Surface

        Draws the VScale background surface and returns it.

        Creates the visible surface of the VScale and returns it to the
        caller.
        """
        return base.GlobalStyle.engine.draw_scale (self, ORIENTATION_VERTICAL)

    def draw (self):
        """V.draw () -> None

        Draws the VScale surface and its slider.
        """
        Scale.draw (self)
        cls = self.__class__
        style = base.GlobalStyle
        border = style.get_border_size (cls, self.style,
                                        StyleInformation.get ("SCALE_BORDER"))
        active = StyleInformation.get ("ACTIVE_BORDER")
        border_active = style.get_border_size (cls, self.style, active)
        slider = StyleInformation.get ("VSCALE_SLIDER_SIZE")

        # Creates the slider surface.
        sf_slider = style.engine.draw_slider (slider[0], slider[1], self.state,
                                              cls, self.style)
        rect_slider = sf_slider.get_rect ()

        # Dashed border.
        if self.focus:
            b = border + border_active
            r = Rect (b, b, rect_slider.width - 2 * b,
                      rect_slider.height - 2 * b)
            style.engine.draw_border \
                            (sf_slider, self.state, cls, self.style, active, r,
                             StyleInformation.get ("ACTIVE_BORDER_SPACE"))

        size = self.width / 3 - 2 * border, self.height - 2 * border

        # Fill the scale line.
        sf_fill = Draw.draw_rect (size[0], size[1],
                                  StyleInformation.get ("SCALE_COLOR"))
        self.image.blit (sf_fill, (self.width / 3 + border, border))

        # Blit slider at the correct position.
        rect_slider.centerx = self.image.get_rect ().centerx
        rect_slider.centery = self._get_coords_from_value ()
        self.image.blit (sf_slider, rect_slider)

        # Fill until the slider start.
        if rect_slider.y > 0:
            sf_fill = Draw.draw_rect (size[0], rect_slider.y - border,
                                      StyleInformation.get ("PROGRESS_COLOR"))
            self.image.blit (sf_fill, (self.width / 3 + border, border))

