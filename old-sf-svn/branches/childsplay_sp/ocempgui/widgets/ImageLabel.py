# $Id: ImageLabel.py,v 1.1.2.2 2006/08/19 10:33:56 marcusva Exp $
#
# Copyright (c) 2006, Marcus von Appen
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

"""A simple widget, which can display text."""

from pygame import Surface
from childsplay_sp.ocempgui.draw import Image
from BaseWidget import BaseWidget
from Constants import *
import base

class ImageLabel (BaseWidget):
    """ImageLabel (image) -> ImageLabel

    A simple widget class, which can display an image.

    The ImageLabel widget is able to display nearly any kind of image
    and serves as a placeholder widget for simple image displaying.

    The image to display can be set with the 'picture' attribute or
    set_picture() method. The image can be either a file name from which
    the image should be loaded or a pygame.Surface object to display.

    label.picture = './image.png'
    label.set_picture (image_surface)

    If the displayed image is loaded from a file, its file path will be
    saved in the 'path' attribute. This also can be used to determine,
    whether the image was loaded from a file ('path' contains a file
    path) or not ('path' is None).

    The ImageLabel supports different border types by setting its
    'border' attribute to a valid value of the BORDER_TYPES constants.

    label.border = BORDER_SUNKEN
    label.set_border (BORDER_SUNKEN)

    The 'padding' attribute and set_padding() method are used to place a
    certain amount of pixels between the text and the outer edges of the
    Label.

    label.padding = 10
    label.set_padding (10)

    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None

    Attributes:
    padding - Additional padding between text and borders. Default is 2.
    picture - A pygame.Surface of the set image.
    path    - The path of the set image (if it is loaded from a file).
    border  - The border style to set for the ImageLabel.
    """
    def __init__ (self, image):
        BaseWidget.__init__ (self)

        self._padding = 2
        self._border = BORDER_NONE
        self._picture = None
        self._path = None
        self.set_picture (image)
        
    def set_padding (self, padding):
        """I.set_padding (...) -> None

        Sets the padding between the edges and image of the ImageLabel.

        The padding value is the amount of pixels to place between the
        edges of the Label and the displayed text.

        Raises a TypeError, if the passed argument is not a positive
        integer.

        Note: If the 'size' attribute is set, it can influence the
        visible space between the text and the edges. That does not
        mean, that any padding is set.
        """
        if (type (padding) != int) or (padding < 0):
            raise TypeError ("padding must be a positive integer")
        self._padding = padding
        self.dirty = True

    def set_border (self, border):
        """I.set_border (...) -> None

        Sets the border type to be used by the ImageLabel.

        Raises a ValueError, if the passed argument is not a value from
        BORDER_TYPES
        """
        if border not in BORDER_TYPES:
            raise ValueError ("border must be a value from BORDER_TYPES")
        self._border = border
        self.dirty = True

    def set_picture (self, image):
        """I.set_picture (...) -> None

        Sets the image to be displayed on the ImageLabel.

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

    def set_focus (self, focus=True):
        """I.set_focus (...) -> bool

        Overrides the default widget input focus.

        ImageLabels cannot be focused by default, thus this method
        always returns False and does not do anything.
        """
        return False

    def draw_bg (self):
        """I.draw_bg () -> Surface
 
        Draws the ImageLabel background surface and returns it.

        Creates the visible background surface of the ImageLabel and
        returns it to the caller.
        """
        return base.GlobalStyle.engine.draw_imagelabel (self)

    def draw (self):
        """I.draw () -> None

        Draws the ImageLabel surface and places its picture on it.
        """
        BaseWidget.draw (self)

        rect_img = None
        rect_child = None
        rect = self.image.get_rect ()
        
        rect_img = self.picture.get_rect ()
        rect_img.center = rect.center
        rect_img.centery = rect.centery
        self.image.blit (self.picture, rect_img)

    padding = property (lambda self: self._padding,
                        lambda self, var: self.set_padding (var),
                        doc = "Additional padding between image and borders.")
    path = property (lambda self: self._path,
                     doc = "The file path of the image.")
    picture = property (lambda self: self._picture,
                        lambda self, var: self.set_picture (var),
                        doc = "The image to display on the ImageLabel.")
    border = property (lambda self: self._border,
                       lambda self, var: self.set_border (var),
                       doc = "The border style to set for the ImageLabel.")
