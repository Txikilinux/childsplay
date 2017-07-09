# $Id: ScrollBar.py,v 1.46.2.4 2007/01/27 11:10:37 marcusva Exp $
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

"""A widget, which allows scrolling using buttons and a slider."""

from pygame import K_KP_PLUS, K_PLUS, K_RIGHT, K_DOWN, K_KP_MINUS, K_MINUS
from pygame import K_LEFT, K_UP, K_PAGEUP, K_PAGEDOWN, K_HOME, K_END, Rect
from Range import Range
from Constants import *
from StyleInformation import StyleInformation
import base

# Timer value for the button press delay.
_TIMER = 25

class ScrollBar (Range):
    """ScrollBar () -> ScrollBar

    An abstract widget class, which is suitable for scrolling.

    The ScrollBar widget works much the same like a Scale widget except
    that it supports buttons for adjusting the value and that its
    minimum value always is 0. It is suitable for widgets which need
    scrolling ability and a scrolling logic.

    Inheriting widgets have to implement the _get_value_from_coords()
    and _get_coords_from_value() methods, which calculate the value of
    the ScrollBar using a pair of coordinates and vice versa. Example
    implementations can be found in the HScrollBar and VScrollBar widget
    classes. They also need to implement the _get_button_coords()
    method, which has to return a tuple of the both button coordinates
    [(x, y, width, height)].
    
    Default action (invoked by activate()):
    Give the ScrollBar the input focus.
    
    Mnemonic action (invoked by activate_mnemonic()):
    None

    Signals:
    SIG_MOUSEDOWN - Invoked, when a mouse button is pressed on the
                    ScrollBar.
    SIG_MOUSEUP   - Invoked, when a mouse buttor is released on the
                    ScrollBar.
    SIG_MOUSEMOVE - Invoked, when the mouse moves over the ScrollBar.

    Attributes:
    button_dec - Indicates, if the decrease button is pressed.
    button_inc - Indicates, if the increase button is pressed.
    """
    def __init__ (self):
        Range.__init__ (self, 0, 1, 1)

        # Signals.
        self._signals[SIG_MOUSEDOWN] = []
        self._signals[SIG_MOUSEMOVE] = []
        self._signals[SIG_MOUSEUP] = []
        self._signals[SIG_KEYDOWN] = None # Dummy for keyboard activation.
        self._signals[SIG_TICK] = None # Dummy for automatic scrolling.
        
        # Internal state handlers for the events. Those need to be known by
        # the inheritors.
        self._buttondec = False
        self._buttoninc = False

        self._timer = _TIMER
        self._click = False

    def activate (self):
        """S.activate () -> None

        Activates the ScrollBar default action.

        Activates the ScrollBar default action. This usually means giving
        the ScrollBar the input focus.
        """
        if not self.sensitive:
            return
        self.focus = True
    
    def _get_button_coords (self, area):
        """S._get_button_coords (...) -> tuple

        Gets a tuple with the coordinates of the in- and decrease buttons.
        
        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError

    def _get_coords_from_value (self):
        """S._get_coords_from_value () -> float

        Calculates the slider coordinates for the ScrollBar.
        
        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError

    def _get_value_from_coords (self, area, coords):
        """S._get_value_from_coords (...) -> float

        Calculates the slider coordinates for the ScrollBar.
        
        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError

    def _get_slider_size (self):
        """S._get_slider_size (...) -> int

        Calculates the size of the slider knob.
        
        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError
    
    def _check_collision (self, pos, rect):
        """S._check_collirion (...) -> bool

        Checks the collision of the given position with the passed rect.
        """
        # Rect: (x, y, width, height), pos: (x, y).
        return (pos[0] >= rect[0]) and (pos[0] <= (rect[2] + rect[0])) and \
               (pos[1] >= rect[1]) and (pos[1] <= (rect[3] + rect[1]))
    
    def set_minimum (self, minimum):
        """S.set_minimum (...) -> Exception

        This method does not have any use.
        """
        pass

    def notify (self, event):
        """S.notify (...) -> None

        Notifies the ScrollBar about an event.
        """
        if not self.sensitive:
            return

        if event.signal in SIGNALS_MOUSE:
            eventarea = self.rect_to_client ()
            collision = eventarea.collidepoint (event.data.pos)
            if event.signal == SIG_MOUSEDOWN and collision:
                self.focus = True
                # Act only on left clicks or scrollwheel events.
                if event.data.button == 1:
                    self.state = STATE_ACTIVE
                self.run_signal_handlers (SIG_MOUSEDOWN, event.data)

                if event.data.button == 1:
                    buttons = self._get_button_coords (eventarea)
                    if self._check_collision (event.data.pos, buttons[0]):
                        self._buttondec = True
                        self._buttoninc = False
                        self._click = False
                        self.decrease ()
                    elif self._check_collision (event.data.pos, buttons[1]):
                        self._buttoninc = True
                        self._buttondec = False
                        self._click = False
                        self.increase ()
                    else:
                        self._click = True
                        self._buttondec = False
                        self._buttoninc = False
                        val = self._get_value_from_coords (eventarea,
                                                           event.data.pos)
                        if val != self.value:
                            self.value = val
                # Mouse wheel.
                elif event.data.button == 4:
                    self.decrease ()
                elif event.data.button == 5:
                    self.increase ()
                event.handled = True

            elif event.signal == SIG_MOUSEMOVE:
                dirty = False
                if collision:
                    self.focus = True
                    if self.state == STATE_NORMAL:
                        self.state = STATE_ENTERED
                    self.run_signal_handlers (SIG_MOUSEMOVE, event.data)

                    buttons = self._get_button_coords (eventarea)
                    if not self._check_collision (event.data.pos, buttons[0]) \
                           and self._buttondec:
                        self._buttondec = False
                        dirty = True
                    if not self._check_collision (event.data.pos, buttons[1]) \
                           and self._buttoninc:
                        self._buttoninc = False
                        dirty = True
                    if self._click:
                        val = self._get_value_from_coords (eventarea,
                                                           event.data.pos)
                        if val != self.value:
                            self.value = val
                            dirty = False
                    self.dirty = dirty
                    event.handled = True

                elif self.state == STATE_ENTERED:
                    self.state = STATE_NORMAL

            elif event.signal == SIG_MOUSEUP:
                if self._click or self._buttoninc or self._buttondec:
                    self._buttondec = False
                    self._buttoninc = False
                    self._click = False

                if collision:
                    if event.data.button == 1:
                        if self.state == STATE_ACTIVE:
                            self.state = STATE_ENTERED
                    self.run_signal_handlers (SIG_MOUSEUP, event.data)
                    event.handled = True
                else:
                    self.state = STATE_NORMAL
                # Reset timer
                self._timer = _TIMER

        # The user holds the mouse clicked over one button.
        elif (self._buttondec or self._buttoninc) and \
                 (event.signal == SIG_TICK):
            # Wait half a second before starting to in/decrease.
            if self._timer > 0:
                self._timer -= 1
            else:
                if self._buttondec:
                    self.decrease ()
                elif self._buttoninc:
                    self.increase ()

        # Keyboard activation.
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

    button_dec = property (lambda self: self._buttondec,
                           doc = """Indicates, whether the decrease
                           button is pressed.""")
    button_inc = property (lambda self: self._buttoninc,
                           doc = """Indicates, whether the increase
                           button is pressed.""")
        
class HScrollBar (ScrollBar):
    """HScrollBar (width, scroll) -> HScrollBar

    A horizontal ScrollBar widget.

    A ScrollBar widget with a horizontal orientation. By default, its
    height is the sum of the button height (HSCROLLBAR_BUTTON_SIZE) and
    the border drawn around it (2 * SCROLLBAR_BORDER) and has the passed
    width. The scrolling area is the passed scroll value minus the width
    of the ScrollBar.

    Thus, if the area to scroll is 200 pixels wide and the ScrollBar is
    about 100 pixels long, the ScrollBar its value range will go from 0
    to 100 (maximum = scroll - width). If the ScrollBar is longer than
    the area to scroll (scroll < width), then the value range will be 0.

    Note: The minimum size of the scrollbar is at least twice its
    size[1] parameter. This means, that it can display the both
    scrolling buttons next to each other. This will override the passed
    width value in the constructor, if necessary.
    """
    def __init__ (self, width, scroll):
        ScrollBar.__init__ (self)
        # Minimum size for the two scrolling buttons next to each other
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("SCROLLBAR_BORDER")) * 2
        height = StyleInformation.get ("HSCROLLBAR_BUTTON_SIZE")[1] + border
        if width < 2 * height:
            width = 2 * height

        self.lock ()
        self.minsize = (width, height) # Default size.
        self.maximum = scroll
        self.unlock ()

    def set_maximum (self, maximum):
        """H.set_maximum (...) -> None

        Sets the maximum value to scroll.

        The passed maximum value differs from maximum value of the
        slider. The HScrollBar also subtracts its own height from the
        scrolling maximum, so that the real maximum of its value range
        can be expressed in the formula:

        real_maximum = maximum - self.minsize[1]

        That means, that if the HScrollBar is 100 pixels high and the
        passed maximum value is 200, the scrolling range of the
        HScrollBar will go from 0 to 100 (100 + size = 200).

        Raises a ValueError, if the passed argument is smaller than
        the first element of the ScrollBar its size.
        """
        if maximum < self.minsize[0]:
            raise ValueError ("maximum must be greater than or equal to %d"
                              % self.minsize[0])
        ScrollBar.set_maximum (self, maximum - self.minsize[0])
        self.dirty = True

    def _get_button_coords (self, area):
        """H._get_button_coords (...) -> tuple

        Gets a tuple with the coordinates of the in- and decrease buttons.
        """
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("SCROLLBAR_BORDER"))
        # Respect the set shadow for the ScrollBar.
        button1 = (area.left + border, area.top + border,
                   area.height - 2 * border, area.height - 2 * border)
        button2 = (area.left + area.width - area.height - border,
                   area.top + border, area.height - 2 * border,
                   area.height - 2 * border)
        return (button1, button2)

    def _get_slider_size (self):
        """H._get_slider_size () -> int

        Calculates the size of the slider knob.
        """
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("SCROLLBAR_BORDER"))
        
        # Minimum slider size, if the scrollbar is big enough.
        minsize = 10
        fullsize = self.size[0] - 2 * self.size[1]
        if fullsize == 0:
            # If only the both scrolling buttons can be displayed, we will
            # completely skip the slider.
            return 0

        # Full size.
        fullsize += 2 * border
        slider_width = fullsize
        if self.maximum != 0:
            slider_width = fullsize / (float (self.maximum) + fullsize) * \
                           fullsize
            if slider_width < minsize:
                slider_width = minsize
        return int (slider_width)
    
    def _get_coords_from_value (self):
        """H._get_coords_from_value () -> int

        Calculates the slider coordinates for the HScrollBar.
        """
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("SCROLLBAR_BORDER"))

        val = 0
        if self.maximum > 0:
            slider = self._get_slider_size ()
            # Start offset for scrolling - this is the height
            # (button + 2 * border) - border plus the half of the
            # slider.
            sl_x = self.minsize[1] - border + float (slider) / 2

            # Valid sliding range.
            slide = self.minsize[0] - 2 * sl_x
            step = self.maximum / float (slide)
            val = self.value / step + sl_x
            return val
        return self.size[0] / 2
    
    def _get_value_from_coords (self, area, coords):
        """H._get_value_from_coords (...) -> float

        Calculates the slider coordinates for the HScrollBar.
        """
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("SCROLLBAR_BORDER"))

        val = 0
        if self.maximum > 0:
            slider = self._get_slider_size ()
            sl_x = self.minsize[1] - border + float (slider) / 2
            slide = self.minsize[0] - 2 * sl_x
            n = coords[0] - area.left - sl_x
            step = self.maximum / float (slide)
            val = n * step
            if val > self.maximum:
                val = self.maximum
            elif val < 0:
                val = 0
        return val
    
    def draw_bg (self):
        """H.draw_bg () -> Surface

        Draws the HScrollBar background surface and returns it.

        Creates the visible surface of the HScrollBar and returns it to
        the caller.
        """
        return base.GlobalStyle.engine.draw_scrollbar (self,
                                                       ORIENTATION_HORIZONTAL)

    def draw (self):
        """H.draw () -> None

        Draws the HScrollBar surface and places its Buttons and slider on it.
        """
        ScrollBar.draw (self)

        cls = self.__class__
        style = base.GlobalStyle
        st = self.style or style.get_style (cls)
        rect = self.image.get_rect ()
        draw_rect = style.engine.draw_rect
        draw_border = style.engine.draw_border
        draw_arrow = style.engine.draw_arrow

        # Create both buttons.
        border = style.get_border_size \
                 (cls, st, StyleInformation.get ("SCROLLBAR_BORDER"))
        button_type = StyleInformation.get ("SCROLLBAR_BUTTON_BORDER")

        width_button = rect.height - 2 * border

        # We use a temporary state here, so that just the buttons will
        # have the typical sunken effect.
        tmp_state = self.state
        if self.state == STATE_ACTIVE:
            tmp_state = STATE_NORMAL

        # First button.
        state_button = tmp_state
        if self.button_dec:
            state_button = STATE_ACTIVE
        button1 = draw_rect (width_button, width_button, state_button, cls, st)
        draw_border (button1, state_button, cls, st, button_type)
        rect_button1 = button1.get_rect ()

        # Draw the arrow.
        draw_arrow (button1, ARROW_LEFT, state_button, cls, st)
        rect_button1.x = border
        rect_button1.centery = rect.centery
        self.image.blit (button1, rect_button1)

        # Second button
        state_button = tmp_state
        if self.button_inc:
            state_button = STATE_ACTIVE
        
        button2 = draw_rect (width_button, width_button, state_button, cls, st)
        draw_border (button2, state_button, cls, st, button_type)
        rect_button2 = button2.get_rect ()

        # Draw the arrow.
        draw_arrow (button2, ARROW_RIGHT, state_button, cls, st)
        rect_button2.x = rect.width - width_button - border
        rect_button2.centery = rect.centery
        self.image.blit (button2, rect_button2)

        # Create the slider.
        slider_size = self._get_slider_size ()
        if slider_size > 0:
            sl = style.engine.draw_slider (slider_size, width_button,
                                           tmp_state, cls, st)
            r = sl.get_rect ()
            r.centerx = self._get_coords_from_value ()
            r.centery = rect.centery
            self.image.blit (sl, r)

class VScrollBar (ScrollBar):
    """VScrollBar (height, scroll) -> VScrollBar

    A vertical ScrollBar widget.

    A ScrollBar widget with a vertical orientation. By default, its
    width is the sum of the button width (VSCROLLBAR_BUTTON_SIZE) and
    the border drawn around it (2 * SCROLLBAR_BORDER) and has the passed
    height. The scrolling area is the passed scroll value minus the
    height of the ScrollBar.

    Thus, if the area to scroll is 200 pixels high and the ScrollBar is
    about 100 pixels high, the ScrollBar its value range will go from 0
    to 100 (maximum = scroll - height). If the ScrollBar is longer than
    the area to scroll (scroll < height), then the value range will be 0.

    Note: The minimum size of the scrollbar is at least twice its
    size[0] parameter. This means, that it can display the both
    scrolling buttons next to each other. This will override the passed
    width value in the constructor, if necessary.
    """
    def __init__ (self, height, scroll):
        ScrollBar.__init__ (self)
        # Minimum size for the two scrolling buttons next to each other.
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("SCROLLBAR_BORDER")) * 2
        
        width = StyleInformation.get ("VSCROLLBAR_BUTTON_SIZE")[0] + border
        if height < 2 * width:
            height = 2 * width

        self.lock ()
        self.minsize = (width, height) # Default size.
        self.maximum = scroll
        self.unlock ()

    def set_maximum (self, maximum):
        """V.set_maximum (...) -> None

        Sets the maximum value to scroll.

        The passed maximum value differs from maximum value of the
        slider. The VScrollBar also subtracts its own width from the
        scrolling maximum, so that the real maximum of its value range
        can be expressed in the formula:

        real_maximum = maximum - self.minsize[0]

        That means, that if the VScrollBar is 100 pixels long and the
        passed maximum value is 200, the scrolling range of the
        VScrollBar will go from 0 to 100 (100 + size = 200).

        Raises a ValueError, if the passed argument is smaller than
        the second element of the ScrollBar its size.
        """
        if maximum < self.minsize[1]:
            raise ValueError ("maximum must be greater than or equal to %d"
                              % self.minsize[1])
        ScrollBar.set_maximum (self, maximum - self.minsize[1])
        self.dirty = True

    def _get_button_coords (self, area):
        """V._get_button_coords (...) -> tuple

        Gets a tuple with the coordinates of the in- and decrease buttons.
        """
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("SCROLLBAR_BORDER"))

        # Respect the set shadow for the ScrollBar.
        button1 = (area.left + border, area.top + border,
                   area.width - 2 * border, area.width - 2 * border)
        button2 = (area.left + border,
                   area.top + area.height - area.width - border,
                   area.width - 2 * border, area.width - border)
        return (button1, button2)

    def _get_slider_size (self):
        """V._get_slider_size () -> int

        Calculates the size of the slider knob.
        """
        # Minimum slider size.
        minsize = 10
        if (self.size[1] - 2 * self.size[0]) == 0:
            # If only the both scrolling buttons can be displayed, we will
            # completely skip the slider.
            return 0
        
        # Full size.
        fullsize = self.size[1] - 2 * self.size[0]
        slider_height = fullsize
        if self.maximum != 0:
            slider_height = fullsize / (float (self.maximum) + fullsize) * \
                            fullsize
            if slider_height < minsize:
                slider_height = minsize
        return int (slider_height)
    
    def _get_coords_from_value (self):
        """V._get_coords_from_value () -> int

        Calculates the slider coordinates for the VScrollBar.
        """
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("SCROLLBAR_BORDER"))
        
        val = 0
        if self.maximum > 0:
            slider = self._get_slider_size ()
            sl_y = self.minsize[0] - border + float (slider) / 2
            slide = self.minsize[1] - 2 * sl_y
            step = self.maximum / float (slide)
            val = self.value / step + sl_y
            return val
        return self.size[1] / 2
    
    def _get_value_from_coords (self, area, coords):
        """V._get_value_from_coords (...) -> float

        Calculates the slider coordinates for the VScrollBar.
        """
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("SCROLLBAR_BORDER"))

        val = 0
        if self.maximum > 0:
            slider = self._get_slider_size ()

            # Start offset for scrolling - this is the width
            # (button + 2 * border) - border plus the half of the
            # slider.
            sl_y = self.minsize[0] - border + float (slider) / 2

            # Valid sliding range.
            slide = self.minsize[1] - 2 * sl_y
            
            n = coords[1] - area.top - sl_y
            step = self.maximum / float (slide)
            val = n * step
            if val > self.maximum:
                val = self.maximum
            elif val < 0:
                val = 0
        return val
    
    def draw_bg (self):
        """V.draw_bg (...) -> Surface

        Draws the VScrollBar background surface and returns it.

        Creates the visible surface of the VScrollBar and returns it to
        the caller.
        """
        return base.GlobalStyle.engine.draw_scrollbar (self,
                                                       ORIENTATION_VERTICAL)

    def draw (self):
        """V.draw () -> None

        Draws the VScrollBar surface and places its Buttons and slider on it.
        """
        ScrollBar.draw (self)
        cls = self.__class__
        style = base.GlobalStyle
        st = self.style or style.get_style (cls)
        rect = self.image.get_rect ()
        draw_rect = style.engine.draw_rect
        draw_border = style.engine.draw_border
        draw_arrow = style.engine.draw_arrow
        
        # Create both buttons.
        border = style.get_border_size \
                 (cls, st, StyleInformation.get ("SCROLLBAR_BORDER"))
        button_type = StyleInformation.get ("SCROLLBAR_BUTTON_BORDER")
        
        width_button = rect.width - 2 * border

        # We use a temporary state here, so that just the buttons will
        # have the typical sunken effect.
        tmp_state = self.state
        if self.state == STATE_ACTIVE:
            tmp_state = STATE_NORMAL

        # First button.
        state_button = tmp_state
        if self.button_dec:
            state_button = STATE_ACTIVE
        button1 = draw_rect (width_button, width_button, state_button, cls, st)
        draw_border (button1, state_button, cls, st, button_type)
        rect_button1 = button1.get_rect ()

        # Draw the arrow.
        draw_arrow (button1, ARROW_UP, state_button, cls, st)
        rect_button1.y = border
        rect_button1.centerx = rect.centerx
        self.image.blit (button1, rect_button1)

        # Second button
        state_button = tmp_state
        if self.button_inc:
            state_button = STATE_ACTIVE
        
        button2 = draw_rect (width_button, width_button, state_button, cls, st)
        draw_border (button2, state_button, cls, st, button_type)
        rect_button2 = button2.get_rect ()

        # Draw the arrow.
        draw_arrow (button2, ARROW_DOWN, state_button, cls, st)
        rect_button2.y = rect.height - width_button - border
        rect_button2.centerx = rect.centerx
        self.image.blit (button2, rect_button2)

        # Create the slider.
        slider_size = self._get_slider_size ()
        if slider_size > 0:
            sl = style.engine.draw_slider (width_button, slider_size,
                                           tmp_state, cls, st)
            r = sl.get_rect ()
            r.centerx = rect.centerx
            r.centery = self._get_coords_from_value ()
            self.image.blit (sl, r)
