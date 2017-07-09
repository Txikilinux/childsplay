# $Id: ImageMap.py,v 1.5.2.4 2007/01/26 22:51:33 marcusva Exp $
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

"""A widget, which can display images and reacts upon mouse events."""

from pygame import Surface, Rect
from childsplay_sp.ocempgui.draw import Image
from BaseWidget import BaseWidget
from Constants import *
from StyleInformation import StyleInformation
import base

class ImageMap (BaseWidget):
    """ImageMap (image) -> ImageMap

    A widget class, which displays images and acts upon mouse events.

    The ImageMap widget can - as the ImageButton - load and display
    images, but additionally keeps track of mouse events and their
    relative position on the widget.

    The image to display can be set with the 'picture' attribute or
    set_picture() method. The image can be either a file name from which
    the image should be loaded or a pygame.Surface object to display.

    imagemap.image = './image.png'
    imagemap.set_image (image_surface)

    If the displayed image is loaded from a file, its file path will be
    saved in the 'path' attribute. This also can be used to determine,
    whether the image was loaded from a file ('path' contains a file
    path) or not ('path' is None).

    To keep track of mouse events, the ImageMap stores the last event,
    which occured on it in the 'last_event' attribute.

    if imagemap.last_event.signal == SIG_MOUSEDOWN:
        ...

    To allow easy acces of the real coordinates on the displayed image,
    the ImageMap contains a 'relative_position' attribute, which returns
    the absolute position of the mouse on the ImageMap widget.

    if imagemap.relative_position == (10, 40):
        ...
    
    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None
    
    Signals:
    SIG_MOUSEDOWN - Invoked, when a mouse button is pressed on the
                    ImageMap.
    SIG_MOUSEUP   - Invoked, when a mouse button is released on the
                    ImageMap.
    SIG_MOUSEMOVE - Invoked, when the mouse moves over the ImageMap.
    SIG_CLICKED   - Invoked, when the left mouse button is pressed AND
                    released over the ImageMap.

    Attributes:
    image             - A pygame.Surface of the set image.
    path              - The path of the set image (if it is loaded from a
                        file).
    last_event        - The last event, which occured on the ImageMap.
    relative_position - The last relative position of the event on the
                        ImageMap.
    """
    def __init__ (self, image):
        BaseWidget.__init__ (self)
        self._picture = None
        self._path = None

        self.__click = False
        self._lastevent = None
        
        self._signals[SIG_MOUSEDOWN] = []
        self._signals[SIG_MOUSEUP] = []
        self._signals[SIG_CLICKED] = []
        self._signals[SIG_MOUSEMOVE] = []

        self.set_picture (image)

    def set_picture (self, image):
        """I.set_picture (...) -> None

        Sets the image to be displayed on the ImageMap.

        The image can be either a valid pygame.Surface object or the
        path to an image file. If the argument is a file, the 'path'
        attribute will be set to the file path, otherwise it will be
        None.

        Raises a TypeError, if the passed argument is not a string,
        unicode or pygame.Surface.
        """
        if image:
            if type (image) in (str, unicode):
                self._path = image
                self._picture = Image.load_image (image)
            elif isinstance (image, Surface):
                self._path = None
                self._picture = image
            else:
                raise TypeError ("image must be a string, unicode or a " \
                                 "pygame.Surface")
        else:
            self._path = None
            self._picture = None
        self.dirty = True

    def _get_relative_position (self):
        """I._get_relative_position () -> int, int

        Gets the last relative position of the mouse on the ImageMap
        (absolute position on it).

        If the last position could not be determined -1, -1 will be
        returned instead.
        """
        if self.last_event:
            border = base.GlobalStyle.get_border_size \
                     (self.__class__, self.style,
                      StyleInformation.get ("IMAGEMAP_BORDER"))
            area = self.rect_to_client ()
            
            return self.last_event.data.pos[0] - border - area.x, \
                   self.last_event.data.pos[1] - border - area.y
        return -1, -1

    def invalidate (self, rect):
        """I.invalidate (...) -> None

        Invalidates a rectangular portion of the ImageMap its picture.

        Invalidates a rectangular portion of the shown image of the
        ImageMap and causes the rendering mechanisms to update that
        region.

        The set IMAGEMAP_BORDER of the StyleInformation settings will be
        taken into account automatically and added to the rect offsets.

        Raises a TypeError, if the passed argument is not a pygame.Rect.
        """
        if type (rect) != Rect:
            raise TypeError ("rect must be a pygame.Rect")

        self._lock += 1
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("IMAGEMAP_BORDER"))

        x, y = rect.x + border, rect.y + border
        self._image.blit (self.picture, (x, y), rect)
        self._image.set_alpha (self.opacity)
        if self.parent:
            rect.x = x + self.x
            rect.y = y + self.y
            self.parent.update (children={ self : rect }, resize=False)
        self._lock -= 1

    def notify (self, event):
        """I.notify (...) -> None

        Notifies the ImageMap about an event.
        """
        if not self.sensitive:
            return

        if event.signal in SIGNALS_MOUSE:
            eventarea = self.rect_to_client ()
            if event.signal == SIG_MOUSEDOWN:
                if eventarea.collidepoint (event.data.pos):
                    self._lastevent = event
                    if event.data.button == 1:
                        self.state = STATE_ACTIVE
                        self.__click = True
                    self.run_signal_handlers (SIG_MOUSEDOWN, event.data)
                    event.handled = True
            
            elif event.signal == SIG_MOUSEUP:
                if eventarea.collidepoint (event.data.pos):
                    self._lastevent = event
                    self.run_signal_handlers (SIG_MOUSEUP, event.data)
                    if event.data.button == 1:
                        if self.state == STATE_ACTIVE:
                            self.state = STATE_ENTERED
                        else:
                            self.state = STATE_NORMAL
                        if self.__click:
                            self.__click = False
                            self.run_signal_handlers (SIG_CLICKED)
                    event.handled = True
                elif (event.data.button == 1) and (self.state == STATE_ACTIVE):
                    self.__click = False
                    self.state = STATE_NORMAL

            elif event.signal == SIG_MOUSEMOVE:
                if eventarea.collidepoint (event.data.pos):
                    self._lastevent = event
                    if self.state == STATE_NORMAL:
                        self.state = STATE_ENTERED
                    self.run_signal_handlers (SIG_MOUSEMOVE, event.data)
                    event.handled = True
                elif self.state == STATE_ENTERED:
                    self.state = STATE_NORMAL

        BaseWidget.notify (self, event)

    def draw_bg (self):
        """I.draw_bg () -> Surface
 
        Draws the background surface of the ImageMap and returns it.

        Creates the visible surface of the ImageMap and returns it to
        the caller.
        """
        return base.GlobalStyle.engine.draw_imagemap (self)

    def draw (self):
        """I.draw () -> None

        Draws the ImageMap surface and places its picture on it.
        """
        BaseWidget.draw (self)
        rect = self.picture.get_rect ()
        rect.center = self.image.get_rect ().center
        self.image.blit (self.picture, rect)

    path = property (lambda self: self._path,
                     doc = "The file path of the image.")
    picture = property (lambda self: self._picture,
                        lambda self, var: self.set_picture (var),
                        doc = "The image to display on the ImageMap.")
    last_event = property (lambda self: self._lastevent,
                           doc = "The last event occured on the ImageMap.")
    relative_position = property (lambda self: self._get_relative_position (),
                                  doc = "The last relative position of the " \
                                  "mouse.")
