# $Id: ImageButton.py,v 1.33.2.2 2006/11/14 12:46:15 marcusva Exp $
#
# Copyright (c) 2004-2006, Marcus von Appen
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

"""A button widget, which can display an image."""

from pygame import Surface
from childsplay_sp.ocempgui.draw import Image
from ButtonBase import ButtonBase
from Label import Label
from Constants import *
from StyleInformation import StyleInformation
import base

class ImageButton (ButtonBase):
    """ImageButton (image) -> ImageButton

    A button widget class which can display an image.

    The ImageButton widget is able to display nearly any kind of
    image, while providing all the features of the Button widget.

    The image to display can be set with the 'picture' attribute or
    set_picture() method. The image can be either a file name from which
    the image should be loaded or a pygame.Surface object to display.

    button.picture = './image.png'
    button.set_picture (image_surface)

    If the displayed image is loaded from a file, its file path will be
    saved in the 'path' attribute. This also can be used to determine,
    whether the image was loaded from a file ('path' contains a file
    path) or not ('path' is None).

    The ImageButton supports different border types by setting its
    'border' attribute to a valid value of the BORDER_TYPES constants.

    button.border = BORDER_SUNKEN
    button.set_border (BORDER_SUNKEN)

    Default action (invoked by activate()):
    See the ButtonBase class.
    
    Mnemonic action (invoked by activate_mnemonic()):
    See the ButtonBase class.
    
    Attributes:
    text    - The text to display on the ImageButton.
    picture - A pygame.Surface of the set image.
    path    - The path of the set image (if it is loaded from a file).
    border  - The border style to set for the ImageButton.
    """
    def __init__ (self, image=None):
        ButtonBase.__init__ (self)
        self._border = BORDER_RAISED
        self._picture = None
        self._path = None
        self.set_picture (image)

    def set_border (self, border):
        """I.set_border (...) -> None

        Sets the border type to be used by the ImageButton.

        Raises a ValueError, if the passed argument is not a value from
        BORDER_TYPES
        """
        if border not in BORDER_TYPES:
            raise ValueError ("border must be a value from BORDER_TYPES")
        self._border = border
        self.dirty = True

    def set_picture (self, image):
        """I.set_picture (...) -> None

        Sets the image to be displayed on the ImageButton.

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
    
    def set_text (self, text=None):
        """I.set_text (...) -> None

        Sets the text to display on the ImageButton by referring to the
        'text' attribute of its child Label.
        """
        if text != None:
            if self.child:
                self.child.set_text (text)
            else:
                self.child = Label (text)
        else:
            self.child = None

    def get_text (self):
        """I.get_text () -> string

        Returns the set text of the ImageButton.

        Returns the text set on the Label of the ImageButton.
        """
        if self.child:
            return self.child.text
        return ""

    def set_child (self, child=None):
        """I.set_child (...) -> None

        Sets the Label to display on the ImageButton.

        Creates a parent-child relationship from the ImageButton to a
        Label and causes the Label to set its mnemonic widget to the
        ImageButton.

        Raises a TypeError, if the passed argument does not inherit
        from the Label class.
        """
        self.lock ()
        if child and not isinstance (child, Label):
            raise TypeError ("child must inherit from Label")
        ButtonBase.set_child (self, child)
        if child:
            child.set_widget (self)
            if not child.style:
                child.style = self.style or \
                              base.GlobalStyle.get_style (self.__class__)
        self.unlock ()

    def set_state (self, state):
        """I.set_state (...) -> None

        Sets the state of the ImageButton.

        Sets the state of the ImageButton and causes its child to set
        its state to the same value.
        """
        if self.state == state:
            return

        self.lock ()
        if self.child:
            self.child.state = state
        ButtonBase.set_state (self, state)
        self.unlock ()

    def draw_bg (self):
        """I.draw_bg () -> Surface

        Draws the background surface of the ImageButton and returns it.

        Creates the visible surface of the image button and returns it
        to the caller.
        """
        return base.GlobalStyle.engine.draw_imagebutton (self)

    def draw (self):
        """I.draw () -> None

        Draws the ImageButton surface and places its picture and Label on it.
        """
        ButtonBase.draw (self)

        spacing = StyleInformation.get ("IMAGEBUTTON_SPACING")
        rect_img = None
        rect_child = None
        rect = self.image.get_rect ()
        
        if self.picture:
            rect_img = self.picture.get_rect ()
            rect_img.center = rect.center
            if self.child:
                rect_img.right -= (self.child.width / 2 + spacing)
            rect_img.centery = rect.centery
            self.image.blit (self.picture, rect_img)
        
        if self.child:
            self.child.center = rect.center
            if self.picture:
                self.child.left = rect_img.right + spacing
            rect_child = self.child.rect
            self.image.blit (self.child.image, rect_child)

    text = property (lambda self: self.get_text (),
                     lambda self, var: self.set_text (var),
                     doc = "The text of the ImageButton.")
    path = property (lambda self: self._path,
                     doc = "The file path of the image.")
    picture = property (lambda self: self._picture,
                        lambda self, var: self.set_picture (var),
                        doc = "The image to display on the ImageButton.")
    border = property (lambda self: self._border,
                       lambda self, var: self.set_border (var),
                       doc = "The border style to set for the ImageButton.")
