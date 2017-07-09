# $Id: DefaultEngine.py,v 1.6.2.10 2007/07/11 07:42:04 marcusva Exp $
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

"""Default drawing engine."""

import os.path
import pygame, pygame.transform
from childsplay_sp.ocempgui.draw import Draw, String, Image
from childsplay_sp.ocempgui.widgets.StyleInformation import StyleInformation
from childsplay_sp.ocempgui.widgets.Constants import *
from childsplay_sp.utils import get_locale

if get_locale()[1]:
    LOCALE_RTL = True
    ALIGN = ALIGN_RIGHT
else:
    LOCALE_RTL = False
    ALIGN = ALIGN_LEFT

# Function cache
array3d = pygame.surfarray.array3d
blit_array = pygame.surfarray.blit_array

class DefaultEngine (object):
    """DefaultEngine (style) -> DefaultEngine

    Default drawing engine for OcempGUI's widget system.

    Drawing engines are used by the widgets of OcempGUI to draw certain
    parts of widgets, such as the background, borders and shadows on a
    surface.

    Attributes:
    style - The Style instance, which makes use of the engine.
    """

    __slots__ = ["style"]
    
    def __init__ (self, style):
        self.style = style

    def get_icon_path (self, size):
        """D.get_icon_path (size) -> path

        Gets the absolute path to the icons for a specific size.
        """
        return os.path.join (os.path.dirname (__file__), "icons", size)

    def draw_rect (self, width, height, state, cls=None, style=None):
        """D.draw_rect (...) -> Surface

        Creates a rectangle surface based on the style information.

        The rectangle will have the passed width and height and will be
        filled with the 'bgcolor'[state] value of the passed style.
        If no style is passed, the method will try to retrieve a style
        using the get_style() method.
        """
        self_style = self.style
        if not style:
            style = self_style.get_style (cls)
        image = self_style.get_style_entry (cls, style, "image", state)
        color = self_style.get_style_entry (cls, style, "bgcolor", state)
        surface =  Draw.draw_rect (width, height, color)
        if image:
            img = pygame.transform.scale (Image.load_image (image),
                                          (width, height))
            surface.blit (img, (0, 0))
        return surface
        
    def draw_border (self, surface, state, cls=None, style=None,
                     bordertype=BORDER_FLAT, rect=None, space=0):
        """D.draw_border (...) -> None

        Draws a border on the passed using a specific border type.

        Dependant on the border type, this method will draw a rectangle
        border on the passed surface.

        The 'rect' argument indicates the drawing area at which's edges
        the border will be drawn. This can differ from the real surface
        rect. A None value (the default) will draw the border around the
        surface.
        
        'space' denotes, how many pixels will be left between each
        border pixel before drawing the next one. A value of 0 thus
        causes the method to draw a solid border while other values will
        draw dashed borders.

        The BORDER_RAISED, BORDER_SUNKEN, BORDER_ETCHED_IN and
        BORDER_ETCHED_OUT border types use the 'lightcolor', 'darkcolor'
        and 'shadow' style entries for drawing, BORDER_FLAT uses the
        'bordercolor' entry.
        
        If no style is passed, the method will try to retrieve a style
        using the get_style() method.
        
        Raises a ValueError, if the passed bordertype argument is
        not a value of the BORDER_TYPES tuple.
        """
        if bordertype not in BORDER_TYPES:
            raise ValueError ("bordertype must be a value from BORDER_TYPES")
        # Do nothing in case, that the border type is none.
        if bordertype == BORDER_NONE:
            return surface
        self_style = self.style

        if not style:
            style = self_style.get_style (cls)

        # The spacing for the lines. space == 0 actually means a solid line,
        # spacing == 1 a dashed one with 1px spaces, etc.
        # Add one pixel for the slicing later on. 
        space += 1
        
        # Maybe pixel3d should be used here, but it does not support 24
        # bit color depths.
        array = array3d (surface)

        # Create the area, the border should surround.
        # We will use the passed padding for it.
        r = rect
        if r == None:
            r = surface.get_rect ()

        # Dependant on the border style, we will care about the used
        # colors. 3D effect such as sunken or raised make use of the
        # light/darkcolor style keys, the flat one uses the fgcolor. If
        # it is a 3D effect, we are going to use the shadow key to
        # determine, how many lines the distinction shall have.
        # 
        # The drawing is done as follows:
        # * First fill the upper row of the (n,m) matrix with the given
        #   color and color only every wanted pixel.
        # * The color the bottom row of the matrix in the same way.
        # * The left column will be colored as well.
        # * The same again with the right column.
        
        if bordertype == BORDER_FLAT:
            color = self_style.get_style_entry (cls, style, "bordercolor",
                                                state)
            array[r.left:r.right:space, r.top] = color
            array[r.left:r.right:space, r.bottom - 1] = color
            array[r.left, r.top:r.bottom:space] = color
            array[r.right - 1, r.top:r.bottom:space] = color

        elif bordertype in (BORDER_SUNKEN, BORDER_RAISED):
            shadow = self_style.get_style_entry (cls, style, "shadow")
            if shadow < 1:
                return surface # No shadow wanted.

            # Create the colors.
            color1 = self_style.get_style_entry (cls, style, "lightcolor",
                                                 state)
            color2 = self_style.get_style_entry (cls, style, "darkcolor",
                                                 state)

            if bordertype == BORDER_SUNKEN:
                color1, color2 = color2, color1

            # By default we will create bevel edges, for which the
            # topleft colors take the most place. Thus the bottomleft
            # array slices will be reduced continously.
            for i in xrange (shadow):
                array[r.left + i:r.right - i:space, r.top + i] = color1
                array[r.left + i:r.right - i:space,
                      r.bottom - (i + 1)] = color2
                array[r.left + i, r.top + i:r.bottom - i:space] = color1
                array[r.right - (i + 1),
                      r.top + i + 1:r.bottom - i:space] = color2

        elif bordertype in (BORDER_ETCHED_IN, BORDER_ETCHED_OUT):
            shadow = self_style.get_style_entry (cls, style, "shadow")
            if shadow < 1:
                return surface # No shadow wanted.
            color1 = self_style.get_style_entry (cls, style, "lightcolor",
                                                 state)
            color2 = self_style.get_style_entry (cls, style, "darkcolor",
                                                 state)
            if bordertype == BORDER_ETCHED_OUT:
                color1, color2 = color2, color1
            s = shadow
            # First (inner) rectangle.
            array[r.left + s:r.right:space, r.top + s:r.top + 2 * s] = color1
            array[r.left + s:r.right:space,r.bottom - s:r.bottom] = color1
            array[r.left + s:r.left + 2 * s, r.top + s:r.bottom:space] = color1
            array[r.right - s:r.right, r.top + s:r.bottom:space] = color1
            # Second (outer) rectangle.
            array[r.left:r.right - s:space, r.top:r.top + s] = color2
            array[r.left:r.right - s:space,
                  r.bottom - 2*s:r.bottom - s] = color2
            array[r.left:r.left + s, r.top:r.bottom - s:space] = color2
            array[r.right - 2 * s:r.right - s,
                  r.top:r.bottom - s:space] = color2

        # Blit the new surface.
        blit_array (surface, array)

    def draw_dropshadow (self, surface, cls=None, style=None):
        """D.draw_dropshadow (...) -> None

        Draws a drop shadow on the surface.

        The drop shadow will be drawn on the right and bottom side of
        the surface and usually uses a black and grey color.
        """
        if not style:
            style = self.style.get_style (cls)
        shadow = self.style.get_style_entry (cls, style, "shadow")
        color = self.style.get_style_entry (cls, style, "shadowcolor")
        if shadow < 2:
            shadow = 2
        half = shadow / 2
        start = max (half, 3)
        rect = surface.get_rect ()
        array = array3d (surface)

        # Right and bottom inner shadow.
        array[rect.left + start:rect.right - half,
              rect.bottom - shadow:rect.bottom - half] = color[0]
        array[rect.right - shadow:rect.right - half,
              rect.top + start:rect.bottom - half] = color[0]

        # Right and bottom outer shadow.
        array[rect.left + start:rect.right - half,
              rect.bottom - half:rect.bottom] = color[1]
        array[rect.right - half:rect.right,
              rect.top + start:rect.bottom] = color[1]
        
        blit_array (surface, array)
    
    def draw_slider (self, width, height, state, cls=None, style=None):
        """D.draw_slider (...) -> Surface

        Creates a rectangle surface with a grip look.

        TODO: At the moment, this method creates a simple rectangle
        surface with raised border. In future versions it will create a
        surface with a grip look.
        """
        if not style:
            style = self.style.get_style (cls)
        
        # Create the surface.
        surface = self.draw_rect (width, height, state, cls, style)
        self.draw_border (surface, state, cls, style, BORDER_RAISED)
        rect = surface.get_rect ()
        
        return surface
    
    def draw_string (self, text, state, cls=None, style=None):
        """D.draw_string (...) -> Surface

        Creates a string surface based on the style information.

        Creates a transparent string surface from the provided text
        based on the style information. The method makes use of the
        'font' style entry to determine the font and size and uses the
        'fgcolor' style entry for the color.

        If no style is passed, the method will try to retrieve a style
        using the get_style() method.
        """
        self_style = self.style
        if not style:
            style = self_style.get_style (cls)
        name = self_style.get_style_entry (cls, style, "font", "name")
        size = self_style.get_style_entry (cls, style, "font", "size")
        alias = self_style.get_style_entry (cls, style, "font", "alias")
        st = self_style.get_style_entry (cls, style, "font", "style")
        color = self_style.get_style_entry (cls, style, "fgcolor", state)
        #print "draw_string", text, name, size, alias, st, color
        return String.draw_string (text, name, size, alias, color, st)
    
    def draw_string_with_mnemonic (self, text, state, mnemonic, cls=None,
                                   style=None):
        """D.draw_string_with_mnemonic (...) -> Surface

        Creates a string surface with an additional underline.

        This method basically does the same as the draw_string()
        method, but additionally underlines the character specified with
        the 'mnemonic' index argument using the 'fgcolor' style entry..

        If no style is passed, the method will try to retrieve a style
        using the get_style() method.
        """
        self_style = self.style
        if not style:
            style = self_style.get_style (cls)
        
        name = self_style.get_style_entry (cls, style, "font", "name")
        size = self_style.get_style_entry (cls, style, "font", "size")
        alias = self_style.get_style_entry (cls, style, "font", "alias")
        st = self_style.get_style_entry (cls, style, "font", "style")
        fgcolor = self_style.get_style_entry (cls, style, "fgcolor", state)

        font = String.create_font (name, size, st)
        surface = String.draw_string (text, name, size, alias, fgcolor)

        left = font.size (text[:mnemonic])
        right = font.size (text[mnemonic + 1:])

        height = surface.get_rect ().height - 2
        width = surface.get_rect ().width
        Draw.draw_line (surface, fgcolor, (left[0], height),
                        (width - right[0], height), 1)
        return surface
    
    def draw_arrow (self, surface, arrowtype, state, cls=None, style=None):
        """D.draw_arrow (...) -> None

        Draws an arrow on a surface.
        
        Draws an arrow with on a surface using the passed arrowtype as
        arrow direction. The method uses a third of the surface width
        (or height for ARROW_TOP/ARROW_DOWN) as arrow width and places
        it on the center of the surface. It also uses the 'fgcolor'
        style entry as arrow color.

        If no style is passed, the method will try to retrieve a style
        using the get_style() method.
        
        Raises a ValueError, if the passed arrowtype argument is not a
        value of the ARROW_TYPES tuple.
        """
        if arrowtype not in ARROW_TYPES:
            raise TypeError ("arrowtype must be a value of ARROW_TYPES")
        
        if not style:
            style = self.style.get_style (cls)

        color = self.style.get_style_entry (cls, style, "fgcolor", state)
        rect = surface.get_rect ()
        array = array3d (surface)

        if arrowtype in (ARROW_LEFT, ARROW_RIGHT):
            arrow_width = rect.width / 3
            center = rect.centery
            if center % 2 == 0:
                center -= 1
            if arrowtype == ARROW_LEFT:
                for i in xrange (arrow_width):
                    col = arrow_width + i
                    array[col:col + arrow_width - i:1, center + i] = color
                    array[col:col + arrow_width - i:1, center - i] = color
            elif arrowtype == ARROW_RIGHT:
                for i in xrange (arrow_width):
                    col = rect.width - arrow_width - i - 1
                    array[col:col - arrow_width + i:-1, center + i] = color
                    array[col:col - arrow_width + i:-1, center - i] = color

        elif arrowtype in (ARROW_UP, ARROW_DOWN):
            arrow_height = rect.height / 3
            center = rect.centerx
            if center % 2 == 0:
                center -= 1

            if arrowtype == ARROW_UP:
                for i in xrange (arrow_height):
                    row = arrow_height + i
                    array[center + i, row:row + arrow_height - i:1] = color
                    array[center - i, row:row + arrow_height - i:1] = color
            elif arrowtype == ARROW_DOWN:
                for i in xrange (arrow_height):
                    row = rect.height - arrow_height - i - 1
                    array[center + i, row:row - arrow_height + i:-1] = color
                    array[center - i, row:row - arrow_height + i:-1] = color
        
        # Blit the new surface.
        blit_array (surface, array)

    def draw_check (self, surface, rect, checked, state, cls=None, style=None):
        """D.draw_check (...) -> None

        Creates a surface with a check box.

        Creates a surface with check box using a width and height of 14
        pixels. The method uses a sunken border effect and makes use of
        the 'lightcolor' and 'darkcolor' style entries for the border.
        Dependant on the passed 'state' argument, the method will either
        use fixed color values of

        (255, 255, 255) for the background and
        (0, 0, 0) for the check,

        which is only drawn, if the 'checked' argument evaluates to
        True. If the 'state' argument is set to STATE_INSENSITIVE the
        'bgcolor' and 'fgcolor' style entries are used instead.
        
        If no style is passed, the method will try to retrieve a style
        using the get_style() method.
        """
        self_style = self.style
        if not style:
            style = self_style.get_style (cls)

        # Some colors we need.
        bg = (255, 255, 255) # Default background color.
        check = (0, 0, 0)    # Check color.
        sh = (150, 150, 150) # Check shadow to make it look smooth.

        array = array3d (surface)

        # Draw the borders and fill the rest.
        dark = self_style.get_style_entry (cls, style, "darkcolor",state)
        light = self_style.get_style_entry (cls, style, "lightcolor", state)

        array[rect.left:rect.left + 2, rect.top:rect.bottom] = dark
        array[rect.left:rect.right, rect.top:rect.top + 2] = dark
        array[rect.right - 2:rect.right, rect.top:rect.bottom] = light
        array[rect.left:rect.right, rect.bottom - 2:rect.bottom] = light
        array[rect.left, rect.bottom - 2] = dark
        array[rect.right - 2, rect.top] = dark

        if state == STATE_INSENSITIVE:
            array[rect.left + 2:rect.right - 2,
                  rect.top + 2:rect.bottom - 2] = \
                  self_style.get_style_entry (cls, style, "bgcolor", state)
            check = self_style.get_style_entry (cls, style, "fgcolor", state)
            sh = check
        else:
            array[rect.left + 2:rect.right - 2,
                  rect.top + 2:rect.bottom - 2] = bg
        
        if checked:
            # Place a check into the drawn box by direct pixel
            # manipulation.
            # TODO: provide a handy matrix for this, so it can be merged
            # and changed quickly and vary in size.
            #
            #                           11  13
            #     0 1 2 3 4 5 6 7 8 9 10  12  
            #    -----------------------------
            # 0  |* * * * * * * * * * * * * *|
            # 1  |* * * * * * * * * * * * * *|
            # 2  |* * 0 0 0 0 0 0 0 0 0 0 * *|
            # 3  |* * 0 0 0 0 0 0 0 0 # # * *|
            # 4  |* * 0 0 0 0 0 0 0 # # # * *|
            # 5  |* * 0 0 0 0 0 0 # # # 0 * *|
            # 6  |* * 0 0 # # 0 # # # 0 0 * *|
            # 7  |* * 0 # # # 0 # # 0 0 0 * *|
            # 8  |* * 0 0 # # # # # 0 0 0 * *|
            # 9  |* * 0 0 0 # # # 0 0 0 0 * *|
            # 10 |* * 0 0 0 0 0 # 0 0 0 0 * *|
            # 11 |* * 0 0 0 0 0 0 0 0 0 0 * *|
            # 12 |* * * * * * * * * * * * * *|
            # 13 |* * * * * * * * * * * * * *|
            #    -----------------------------
            # * = border shadow
            # 0 = unset
            # # = set with a specific color.
            #
            array[rect.left + 3, rect.top + 7] = sh
            array[rect.left + 4, rect.top + 6] = sh
            array[rect.left + 4, rect.top + 7:rect.top + 9] = check
            array[rect.left + 5, rect.top + 6] = sh
            array[rect.left + 5, rect.top + 7:rect.top + 9] = check
            array[rect.left + 5, rect.top + 9] = sh
            array[rect.left + 6, rect.top + 7] = sh
            array[rect.left + 6, rect.top + 8:rect.top + 10] = check
            array[rect.left + 7, rect.top + 6] = sh
            array[rect.left + 7, rect.top + 7:rect.top + 11] = check
            array[rect.left + 8, rect.top + 5:rect.top + 9] = check
            array[rect.left + 9, rect.top + 4:rect.top + 7] = check
            array[rect.left + 10, rect.top + 3:rect.top + 6] = check
            array[rect.left + 11, rect.top + 3:rect.top + 5] = sh

        #self.__checks[style] =
        blit_array (surface, array)

    def draw_radio (self, surface, rect, checked, state, cls=None, style=None):
        """D.draw_radio (...) -> None

        Creates a surface with a radio check box.

        Creates a surface with radio check box using a width and height
        of 14 pixels. The method uses a sunken border effect and makes
        use of the 'lightcolor' and 'darkcolor' style entries for the
        border.  Dependant on the passed 'state' argument, the method
        will either use fixed color values of

        (255, 255, 255) for the background and 
        (0, 0, 0) for the check,

        which is only drawn, if the 'checked' argument evaluates to
        True. If the 'state' argument is set to STATE_INSENSITIVE the
        'bgcolor' and 'fgcolor' style entries are used instead.
        
        If no style is passed, the method will try to retrieve a style
        using the get_style() method.
        """
        if not style:
            style = self.style.get_style (cls)

        # We need some colors for the radio check.
        sh1 = (0, 0, 0)        # Border topleft.
        sh2 = (150, 150, 150)  # Border shadow top- and bottomleft.
        sh3 = (255, 255, 255)  # Outer border shadow bottomleft.
        bg = (255, 255, 255)   # Background color for the check.
        check = (0, 0, 0)      # Color of the radio check.

        if state == STATE_INSENSITIVE:
            bg = self.style.get_style_entry (cls, style, "bgcolor", state)
            check = self.style.get_style_entry (cls, style, "fgcolor", state)
            sh1 = check
            sh2 = self.style.get_style_entry (cls, style, "fgcolor", state)
            sh3 = (240, 240, 240)

        # The complete radio check will be drawn by manipulating pixels
        # of the box.
        # TODO: provide a handy matrix for this, so it can be merged
        # and changed quickly and vary in size.
        #                           11  13
        #     0 1 2 3 4 5 6 7 8 9 10  12  
        #    -----------------------------
        # 0  |x x x x x x x x x x x x x x|
        # 1  |x x x x x * * * * x x x x x|
        # 2  |x x x * * s s s s s * x x x|
        # 3  |x x * s s 0 0 0 0 0 s * x x|
        # 4  |x x * s 0 0 0 0 0 0 0 * x x|
        # 5  |x * s 0 0 0 # # # 0 0 0 * x|
        # 6  |x * s 0 0 # # # # # 0 0 * 8|
        # 7  |x * s 0 0 # # # # # 0 0 * 8|
        # 8  |x * s 0 0 # # # # # 0 0 * 8|
        # 9  |x x s 0 0 0 # # # 0 0 0 * 8|
        # 10 |x x * s 0 0 0 0 0 0 0 * 8 x|
        # 11 |x x x * * 0 0 0 0 0 * * 8 x|
        # 12 |x x x x x * * * * * 8 8 x x|
        # 13 |x x x x x x 8 8 8 8 x x x x|
        #    -----------------------------
        # x = default background color
        # * = border shadow (sh2)
        # s = topleft border (sh1)
        # 0 = background color (bg)
        # 8 = border shadow 2 (sh3)
        # # = check color (check)
        #
        array = array3d (surface)

        array[rect.left + 1, rect.top + 5:rect.top + 9] = sh2
        array[rect.left + 2, rect.top + 3:rect.top + 5] = sh2
        array[rect.left + 2, rect.top + 5:rect.top + 10] = sh1
        array[rect.left + 2, rect.top + 10] = sh2
        array[rect.left + 3:rect.left + 5, rect.top + 2] = sh2
        array[rect.left + 3, rect.top + 3:rect.top + 5] = sh1
        array[rect.left + 3:rect.left + 12, rect.top + 5:rect.top + 10] = bg
        array[rect.left + 3, rect.top + 10] = sh1
        array[rect.left + 3:rect.left + 5, rect.top + 11] = sh2
        array[rect.left + 4, rect.top + 3] = sh1
        array[rect.left + 4:rect.left + 11, rect.top + 4] = bg
        array[rect.left + 4:rect.left + 11, rect.top + 10] = bg
        array[rect.left + 5:rect.left + 9, rect.top + 1] = sh2
        array[rect.left + 5:rect.left + 10, rect.top + 2] = sh1
        array[rect.left + 5:rect.left + 10, rect.top + 3] = bg
        array[rect.left + 5:rect.left + 10, rect.top + 11] = bg
        array[rect.left + 5:rect.left + 10, rect.top + 12] = sh2
        array[rect.left + 6:rect.left + 10, rect.top + 13] = sh3
        array[rect.left + 10, rect.top + 2] = sh2
        array[rect.left + 10, rect.top + 3] = sh1
        array[rect.left + 10:rect.left + 12, rect.top + 11] = sh2
        array[rect.left + 10:rect.left + 12, rect.top + 12] = sh3
        array[rect.left + 11, rect.top + 3:rect.top + 5] = sh2
        array[rect.left + 11, rect.top + 10] = sh2
        array[rect.left + 12, rect.top + 5:rect.top + 10] = sh2
        array[rect.left + 12, rect.top + 10:rect.top + 12] = sh3
        array[rect.left + 13, rect.top + 6:rect.top + 10] = sh3

        if checked:
            array[rect.left + 5:rect.left + 10,
                  rect.top + 6:rect.top + 9] = check
            array[rect.left + 6:rect.left + 9, rect.top + 5] = check
            array[rect.left + 6:rect.left + 9, rect.top + 9] = check

        blit_array (surface, array)

    def draw_caption (self, width, title=None, state=STATE_NORMAL, cls=None,
                      style=None):
        """D.draw_caption (...) -> Surface

        Creates and a caption bar suitable for Window objects.

        Creates a rectangle surface with a flat border and the passed
        'title' text argument. The method uses a fixed color value of
        (124, 153, 173) for the surface.

        The passed 'width' will be ignored, if the size of the title
        text exceeds it. Instead the width of the title text plus an
        additional spacing of 4 pixels will be used.
        The height of the surface relies on the title text height plus
        an additional spacing of 4 pixels.

        If no style is passed, the method will try to retrieve a style
        using the get_style() method.
        """
        if not title:
            title = ""
        if not style:
            style = self.style.get_style (cls)

        # Create the window title.
        surface_text = self.draw_string (title, state, cls, style)
        rect_text = surface_text.get_rect ()

        # Add two pixels for the border and 2 extra ones for spacing.
        cap_height = rect_text.height + 2
        if width < rect_text.width + 2:
            width = rect_text.width + 2

        color = None
        if state == STATE_ACTIVE:
            color = StyleInformation.get ("CAPTION_ACTIVE_COLOR")
        else:
            color = StyleInformation.get ("CAPTION_INACTIVE_COLOR")

        # Create the complete surface.
        surface = Draw.draw_rect (width, cap_height, color)
        self.draw_border (surface, state, cls, style,
                          StyleInformation.get ("CAPTION_BORDER"))
        if LOCALE_RTL:
            x = max(0,width - rect_text.width - 2)
        else:
            x = 2 
        surface.blit (surface_text, (x, 2))
        
        return surface

    def draw_caret (self, surface, x, y, thickness, state, cls=None,
                    style=None):
        """D.draw_caret (...) -> None

        Draws a caret line on a surface.

        Draws a vertical caret line onto the passed surface. The
        position of the caret will be set using the 'x' argument. The
        length of the caret line can be adjusted using the 'y' argument.
        The thickness of the caret line is set by the 'thickness'
        argument. This method makes use of the 'fgcolor' style entry for
        the color of the caret line.

        If no style is passed, the method will try to retrieve a style
        using the get_style() method.
        """
        if not style:
            style = self.style.get_style (cls)
        rect = surface.get_rect ()
        ax = (rect.topleft[0] + x, rect.topleft[1] + y)
        bx = (rect.bottomleft[0] + x, rect.bottomleft[1] - y)
        Draw.draw_line (surface, self.style.get_style_entry (cls, style,
                                                             "fgcolor", state),
                        ax, bx, thickness)
        
    def draw_label (self, label):
        """D.draw_label (...) -> Surface

        Creates the surface for the passed Label widget.
        """
        cls = label.__class__
        st = label.style
        width = 2 * label.padding
        height = 2 * label.padding

        labels = []
        rtext = None
        if not label.multiline:
            # Draw a single line.
            if label.mnemonic[0] != -1:
                rtext = self.draw_string_with_mnemonic (label.text, label.state,
                                                        label.mnemonic[0], cls,
                                                        st)
            else:
                rtext = self.draw_string (label.text, label.state, cls, st)
            rect = rtext.get_rect ()
            width += rect.width
            height += rect.height
            labels.append ((rtext, rect))
        else:
            # Multiple lines.
            cur = 0 # Current postion marker for the mnemonic.
            lines = label.get_lines ()
            mnemonic = label.mnemonic[0]
            last = len(lines) - 1
            for i, line in enumerate(lines):
                if (mnemonic != -1) and (cur <= mnemonic) and \
                   ((cur + len (line)) > mnemonic):
                    rtext = self.draw_string_with_mnemonic (line, label.state,
                                                            mnemonic - cur,
                                                            cls, st)
                else:
                    rtext = self.draw_string (line, label.state, cls, st)
                rect = rtext.get_rect ()
                if width < rect.width:
                    width = rect.width + 2 * label.padding
                if (label.linespace != 0) and (i != last):
                    # Do not consider linespace for the last line
                    rect.height += label.linespace
                height += rect.height
                labels.append ((rtext, rect))
                cur += len (line) + 1
        
        # Guarantee size.
        width, height = label.check_sizes (width, height)

        surface = self.draw_rect (width, height, label.state, cls, st)
        blit = surface.blit
        
        posy = label.padding
        totalheight = 0
        totalwidth = 0
        for rtext, rect in labels:
            totalheight += rect.height
            totalwidth = max (totalwidth, rect.width)
        
        # Blit all in the center using centered justification.
        posx = (width - totalwidth) / 2
        posy = (height - totalheight) / 2
        for rtext, rect in labels:
            rect.topleft = posx, posy
            posy += rect.height

        if label.align & ALIGN_TOP == ALIGN_TOP:
            posy = label.padding
            for rtext, rect in labels:
                rect.top = posy
                posy += rect.height
        
        elif label.align & ALIGN_BOTTOM == ALIGN_BOTTOM:
            posy = height - label.padding - totalheight
            for rtext, rect in labels:
                rect.top = posy
                posy += rect.height

        if label.align & ALIGN_LEFT == ALIGN_LEFT:
            for rtext, rect in labels:
                rect.left = label.padding

        elif label.align & ALIGN_RIGHT == ALIGN_RIGHT:
            right = width - label.padding
            for rtext, rect in labels:
                rect.right = right
        else:
            for rtext, rect in labels:
                rect.left = (width - rect.width) / 2
        
        for rtext, rect in labels:
            blit (rtext, rect)
            
        return surface

    def draw_button (self, button):
        """D.draw_button (...) -> Surface

        Creates the surface for the passed Button widget.
        """
        cls = button.__class__
        border = self.style.get_border_size (cls, button.style, button.border)
        active = StyleInformation.get ("ACTIVE_BORDER")
        border_active = self.style.get_border_size (cls, button.style, active)
        
        # Create the absolute sizes of the surface. This includes the
        # padding as well as the shadow and additional pixels for the
        # dashed border.
        width = 2 * (button.padding + border + border_active)
        height = 2 * (button.padding + border + border_active)

        if button.child:
            width += button.child.width 
            height += button.child.height

        # Guarantee size.
        width, height = button.check_sizes (width, height)

        surface = self.draw_rect (width, height, button.state, cls,
                                  button.style)
        self.draw_border (surface, button.state, cls, button.style,
                          button.border)

        # Draw a dashed border around the label, if the button has
        # focus.
        if button.focus:
            r = None
            if button.child:
                r = button.child.rect
                r.x -= border_active
                r.y -= border_active
                r.width += 2 * border_active
                r.height += 2 * border_active
            else:
                adj = border + 2 * border_active
                r = surface.get_rect ()
                r.topleft = (adj, adj)
                r.width -= 2 * adj
                r.height -= 2 * adj
            self.draw_border (surface, button.state, cls,button.style, active,
                              r, StyleInformation.get ("ACTIVE_BORDER_SPACE"))

        return surface

    def draw_checkbutton (self, button):
        """D.draw_checkbutton (...) -> Surface

        Creates the surface for the passed CheckButton widget.
        """
        cls = button.__class__
        active = StyleInformation.get ("ACTIVE_BORDER")
        border = self.style.get_border_size (cls, button.style, active)
        checksize = StyleInformation.get ("CHECK_SIZE")

        # Create the absolute sizes of the surface, including the
        # padding.
        width = 2 * (button.padding + border)
        height = 2 * (button.padding + border)
        if button.child:
            width += button.child.width
            height += button.child.height

        # Create check box.
        rect_check = pygame.Rect (button.padding, button.padding, checksize,
                                  checksize)

        # The layout looks like:
        #  ----------------
        #  | X | child    |
        #  ----------------
        # Check   Child
        # Thus we have to add a specific spacing between the child and the
        # check. By default we will use the given StyleInformation value.
        width += rect_check.width + StyleInformation.get ("CHECK_SPACING")
        if height < rect_check.height:
            # Do not forget to add the padding!
            height = rect_check.height + 2 * button.padding

        # Guarantee size.
        width, height = button.check_sizes (width, height)

        # The surface on which both components will be placed.
        surface = self.draw_rect (width, height, button.state, cls,
                                  button.style)
        rect_surface = surface.get_rect ()

        # Draw the check on the surface.
        rect_check.centery = rect_surface.centery
        self.draw_check (surface, rect_check, button.active, button.state, cls,
                         button.style)

        # Draw a dashed border around the label, if the button has
        # focus.
        if button.focus:
            r = None
            if button.child:
                r = button.child.rect
                r.x -= border
                r.y -= border
                r.width += 2 * border
                r.height += 2 * border
            else:
                r = rect_surface
                r.topleft = (border, border)
                r.width -= 2 * border
                r.height -= 2 * border

            self.draw_border (surface, button.state, cls, button.style, active,
                              r, StyleInformation.get ("ACTIVE_BORDER_SPACE"))

        return surface

    def draw_entry (self, entry):
        """D.draw_entry (...) -> Surface

        Creates the surface for the passed Entry widget.
        """
        cls = entry.__class__
        border = self.style.get_border_size (cls, entry.style, entry.border)

        # Peek the style so we can calculate the font.
        st = entry.style or self.style.get_style (cls)
        fn = self.style.get_style_entry (cls, st, "font", "name")
        sz = self.style.get_style_entry (cls, st, "font", "size")
        fs = self.style.get_style_entry (cls, st, "font", "style")

        font = String.create_font (fn, sz, fs)
        height = font.get_height () + 2 * (entry.padding + border)

        width, height = entry.check_sizes (0, height)

        # Main surface.
        surface = self.draw_rect (width, height, entry.state, cls, entry.style)
        self.draw_border (surface, entry.state, cls, entry.style, entry.border)

        return surface

    def draw_imagebutton (self, button):
        """D.draw_imagebutton (button) -> Surface

        Creates the surface for the passed ImageButton widget.
        """
        cls = button.__class__
        border = self.style.get_border_size (cls, button.style, button.border)
        active = StyleInformation.get ("ACTIVE_BORDER")
        border_active = self.style.get_border_size (cls, button.style, active)
        spacing = StyleInformation.get ("IMAGEBUTTON_SPACING")

        width = 2 * (button.padding + border + border_active)
        height = 2 * (button.padding + border + border_active)

        rect_child = None
        if button.child:
            rect_child = button.child.rect
            width += button.child.width
            height += button.child.height

        rect_img = None
        if button.picture:
            rect_img = button.picture.get_rect ()
            width += rect_img.width
            if button.child:
                 width += spacing
            needed_he = rect_img.height + \
                        2 * (button.padding + border + border_active)
            if height < needed_he:
                height = needed_he

        # Guarantee size.
        width, height = button.check_sizes (width, height)
        
        surface = self.draw_rect (width, height, button.state, cls,
                                  button.style)
        rect = surface.get_rect ()
        
        self.draw_border (surface, button.state, cls, button.style,
                          button.border)

        # Dashed border.
        if button.focus:
            r = None
            if rect_img and rect_child:
                rect_img.center = rect.center
                rect_img.right -= button.child.rect.width / 2 + spacing
                rect_child.center = rect.center
                rect_child.left = rect_img.right + spacing
                r = rect_img.union (rect_child)
            elif rect_img:
                rect_img.center = rect.center
                r = rect_img
            elif rect_child:
                rect_child.center = rect.center
                r = rect_child

            if r:
                r.x -= border_active
                r.y -= border_active
                r.width += 2 * border_active
                r.height += 2 * border_active
            else:
                adj = border + 2 * border_active
                r = rect
                r.topleft = (adj, adj)
                r.width -= 2 * adj
                r.height -= 2 * adj

            self.draw_border (surface, button.state, cls, button.style, active,
                              r, StyleInformation.get ("ACTIVE_BORDER_SPACE"))
        return surface

    def draw_radiobutton (self, button):
        """D.draw_radiobutton (button) -> Surface

        Creates the surface for the passed RadioButton widget.
        """
        cls = button.__class__
        active = StyleInformation.get ("ACTIVE_BORDER")
        border = self.style.get_border_size (cls, button.style, active)
        radiosize = StyleInformation.get ("RADIO_SIZE")
        
        # Create the absolute sizes of the surface, including the
        # padding and.
        width = 2 * (button.padding + border)
        height = 2 * (button.padding + border)
        if button.child:
            width += button.child.width
            height += button.child.height

        # Create radio box.
        rect_radio = pygame.Rect (button.padding, button.padding, radiosize,
                                  radiosize)

        # The layout looks like:
        #  ----------------
        #  | X | child    |
        #  ----------------
        # Check   Child
        # Thus we have to add a specific spacing between the child and the
        # check. By default we will use the given StyleInformation value.
        width += rect_radio.width + StyleInformation.get ("RADIO_SPACING")
        if height < rect_radio.height:
            # Do not forget to add the padding!
            height = rect_radio.height + 2 * button.padding

        # Guarantee size.
        width, height = button.check_sizes (width, height)

        # The surface on which both components will be placed.
        surface = self.draw_rect (width, height, button.state, cls,
                                  button.style)
        rect_surface = surface.get_rect ()

        rect_radio.centery = rect_surface.centery
        self.draw_radio (surface, rect_radio, button.active, button.state, cls,
                         button.style)

        # Draw a dashed border around the label, if the button has
        # focus.
        if button.focus:
            r = None
            if button.child:
                r = button.child.rect
                r.x -= border
                r.y -= border
                r.width += 2 * border
                r.height += 2 * border
            else:
                r = rect_surface
                r.topleft = (border, border)
                r.width -= 2 * border
                r.height -= 2 * border

            self.draw_border (surface, button.state, cls, button.style, active,
                              r, StyleInformation.get ("ACTIVE_BORDER_SPACE"))

        return surface

    def draw_progressbar (self, bar):
        """D.draw.progressbar (...) -> Surface

        Creates the surface for the passed ProgressBar widget.
        """
        cls = bar.__class__
        border_type = StyleInformation.get ("PROGRESSBAR_BORDER")
        border = self.style.get_border_size (cls, bar.style, border_type)
        st = bar.style or self.style.get_style (cls)

        # Guarantee size.
        width, height = bar.check_sizes (0, 0)
        
        surface = self.draw_rect (width, height, bar.state, cls, st)

        # Status area.
        width -= 2 * border
        height -= 2 * border
        width = int (width * bar.value / 100)

        # Draw the progress.
        sf_progress = Draw.draw_rect (width, height,
                                      StyleInformation.get ("PROGRESS_COLOR"))
        surface.blit (sf_progress, (border, border))

        self.draw_border (surface, bar.state, cls, st, border_type)
        return surface

    def draw_frame (self, frame):
        """D.draw_frame (...) -> Surface

        Creates the surface for the passed Frame widget.
        """
        cls = frame.__class__
        # Guarantee size.
        width, height = frame.calculate_size ()
        width, height = frame.check_sizes (width, height)

        surface = self.draw_rect (width, height, frame.state, cls, frame.style)

        rect = surface.get_rect ()
        if frame.widget:
            rect.y = frame.widget.height / 2
            rect.height -= frame.widget.height / 2
        self.draw_border (surface, frame.state, cls, frame.style, frame.border,
                          rect)
        return surface

    def draw_table (self, table):
        """D.draw_table (...) -> Surface

        Creates the surface for the passed Table widget.
        """
        cls = table.__class__
        width, height = table.calculate_size ()
        width, height = table.check_sizes (width, height)
        return self.draw_rect (width, height, table.state, cls, table.style)

    def draw_scale (self, scale, orientation):
        """D.draw_scale (...) -> Surface

        Creates the surface for the passed Scale widget.

        If the passed orientation argument is ORIENTATION_VERTICAL, the
        vertical slider information (VSCALE_SLIDER_SIZE) is used,
        otherwise the horizontal (HSCALE_SLIDER_SIZE).
        """
        cls = scale.__class__

        # Use a default value for the slider, if not set in the style.
        slider = None
        if orientation == ORIENTATION_VERTICAL:
            slider = StyleInformation.get ("VSCALE_SLIDER_SIZE")
        else:
            slider = StyleInformation.get ("HSCALE_SLIDER_SIZE")

        width, height = scale.check_sizes (0, 0)
        if width < slider[0]:
            width = slider[0]
        if height < slider[1]:
            height = slider[1]

        # The slider line in the middle will be a third of the complete
        # width/height. To center it correctly, we need an odd value.
        if (orientation == ORIENTATION_VERTICAL) and (height % 2 == 0):
            width += 1
        elif width % 2 == 0:
            height += 1

        # Main surface to draw on. We do not want to have any resizing,
        # thus we are doing this in two steps.
        surface = self.draw_rect (width, height, scale.state, cls, scale.style)
        rect = None
        if orientation == ORIENTATION_VERTICAL:
            r = pygame.Rect (width / 3, 0, width / 3, height)
            r.centery = height / 2
        else:
            r = pygame.Rect (0, height / 3, width, height /3)
            r.centerx = width / 2
        
        self.draw_border (surface, scale.state, cls, scale.style,
                          StyleInformation.get ("SCALE_BORDER"), r)

        return surface

    def draw_scrollbar (self, scrollbar, orientation):
        """D.draw_scrollbar (...) -> Surface

        Creates the surface for the passed ScrollBar widget.

        If the passed orientation argument is ORIENTATION_VERTICAL, the
        vertical slider information (VSCALE_SLIDER_SIZE) is used,
        otherwise the horizontal (HSCALE_SLIDER_SIZE).
        """
        cls = scrollbar.__class__
        border_type = StyleInformation.get ("SCROLLBAR_BORDER")
        border = self.style.get_border_size (cls, scrollbar.style, border_type)

        # We use a temporary state here, so that just the buttons will
        # have the typical sunken effect.
        tmp_state = scrollbar.state
        if scrollbar.state == STATE_ACTIVE:
            tmp_state = STATE_NORMAL

        # Guarantee size.
        width, height = scrollbar.check_sizes (0, 0)
        size_button = (0, 0)
        if orientation == ORIENTATION_VERTICAL:
            size_button = StyleInformation.get ("VSCROLLBAR_BUTTON_SIZE")
            if width < (size_button[0] + 2 * border):
                width = size_button[0] + 2 * border
            if height < 2 * (size_button[1] + border):
                height = 2 * (size_button[1] + 2 * border)
        else:
            size_button = StyleInformation.get ("HSCROLLBAR_BUTTON_SIZE")
            if width < 2 * (size_button[0] + border):
                width = 2 * (size_button[0] + border)
            if height < (size_button[1] + 2 * border):
                height = size_button[1] + 2 * border

        surface = self.draw_rect (width, height, tmp_state, cls,
                                  scrollbar.style)
        self.draw_border (surface, tmp_state, cls, scrollbar.style,
                          border_type)
        return surface

    def draw_scrolledwindow (self, window):
        """D.draw_scrolledwindow (...) -> Surface

        Creates the Surface for the passed ScrolledWindow widget.
        """
        cls = window.__class__
        width, height = window.check_sizes (0, 0)
        surface = self.draw_rect (width, height, window.state, cls,
                                  window.style)
        return surface

    def draw_viewport (self, viewport):
        """D.draw_viewport (...) -> Surface

        Creates the Surface for the passed ViewPort widget.
        """
        cls = viewport.__class__
        width, height = viewport.check_sizes (0, 0)
        surface = self.draw_rect (width, height, viewport.state, cls,
                                  viewport.style)
        self.draw_border (surface, viewport.state, cls, viewport.style,
                          StyleInformation.get ("VIEWPORT_BORDER"))
        return surface

    def draw_statusbar (self, statusbar):
        """D.draw_statusbar (...) -> Surface
        
        Creates the Surface for the passed StatusBar widget.
        """
        cls = statusbar.__class__
        border_type = StyleInformation.get ("STATUSBAR_BORDER")

        # Guarantee size.
        width, height = statusbar.calculate_size ()
        width, height = statusbar.check_sizes (width, height)

        # Create the main surface
        surface = self.draw_rect (width, height, statusbar.state, cls,
                                  statusbar.style)
        self.draw_border (surface, statusbar.state, cls, statusbar.style,
                          border_type)
        return surface

    def draw_imagemap (self, imagemap):
        """D.draw_imagemap (...) -> Surface

        Creates the Surface for the passed ImageMap widget.
        """
        cls = imagemap.__class__
        border_type = StyleInformation.get ("IMAGEMAP_BORDER")
        border = self.style.get_border_size (cls, imagemap.style, border_type)

        rect_image = imagemap.picture.get_rect ()
        width = rect_image.width + 2 * border
        height = rect_image.height + 2 * border

        # Guarantee size.
        width, height = imagemap.check_sizes (width, height)
        
        surface = self.draw_rect (width, height, imagemap.state, cls,
                                  imagemap.style)
        self.draw_border (surface, imagemap.state, cls, imagemap.style,
                          border_type)
        return surface

    def draw_textlistitem (self, viewport, item):
        """D.draw_textlistitem (...) -> Surface

        Creates the Surface for the passed TextListItem.
        """
        text = item.text or ""
        return self.draw_string (text, viewport.state, item.__class__,
                                 item.style)
    
    def draw_filelistitem (self, viewport, item):
        """D.draw_filelistitem (...) -> Surface

        Creates the Surface for the passed FileListItem.
        """
        style = viewport.style or self.style.get_style (viewport.__class__)
        color = StyleInformation.get ("SELECTION_COLOR")
        
        style = item.style
        if not style:
            style = self.style.get_style (item.__class__)
        
        rect_icon = None
        if item.icon:
            rect_icon = item.icon.get_rect ()
        else:
            rect_icon = pygame.Rect (0, 0, 0, 0)
        
        sf_text =  self.draw_textlistitem (viewport, item)
        rect_text = sf_text.get_rect ()

        width = rect_icon.width + 2 + rect_text.width
        height = rect_icon.height
        if height < rect_text.height:
            height = rect_text.height

        surface = None
        if item.selected:
            surface = Draw.draw_rect (width, height, color)
        else:
            surface = self.draw_rect (width, height, viewport.state,
                                      item.__class__, item.style)
        rect = surface.get_rect ()

        if item.icon:
            rect_icon.centery = rect.centery
            surface.blit (item.icon, rect_icon)

        rect_text.centery = rect.centery
        surface.blit (sf_text, (rect_icon.width + 2, rect_text.y))
        return surface

    def draw_window (self, window):
        """D.draw_window (...) -> Surface

        Creates the Surface for the passed Window.
        """
        cls = window.__class__
        style = window.style or self.style.get_style (cls)
        border_type = StyleInformation.get ("WINDOW_BORDER")
        border = self.style.get_border_size (cls, style, border_type)

        dropshadow = self.style.get_style_entry (cls, style, "shadow")
        # Added +4 by stas for better display with pango fonts
        width = 2 * (window.padding + border) + dropshadow +8
        height = 2 * (window.padding + border) + dropshadow+8

        if window.child:
            width += window.child.width
            height += window.child.height
       
        width, height = window.check_sizes (width, height)

        # Calculate the height of the caption bar.
        fn = self.style.get_style_entry (cls, style, "font", "name")
        sz = self.style.get_style_entry (cls, style, "font", "size")
        fs = self.style.get_style_entry (cls, style, "font", "style")
        font = String.create_font (fn, sz, fs)
        height_caption = font.get_height () + 2 * self.style.get_border_size \
                         (cls, style, StyleInformation.get ("CAPTION_BORDER"))
        height += height_caption

        # Create the surface.
        surface = self.draw_rect (width, height, window.state, cls, style)
        self.draw_border (surface, window.state, cls, style, border_type,
                          pygame.Rect (0, 0, width - dropshadow,
                                       height - dropshadow))
        if dropshadow > 0:
            self.draw_dropshadow (surface, cls, style)

        return surface

    def draw_graph2d (self, graph):
        """D.draw_graph2d (...) -> Surface

        Creates the Surface for the passed Graph2D
        """
        cls = graph.__class__

        width, height = graph.check_sizes (0, 0)
        surface = self.draw_rect (width, height, graph.state, cls, graph.style)

        # Draw dashed border, if focused.
        if graph.focus:
            self.draw_border (surface, graph.state, cls, graph.style,
                              StyleInformation.get ("ACTIVE_BORDER"),
                              space = \
                              StyleInformation.get ("ACTIVE_BORDER_SPACE"))
        return surface

    def draw_imagelabel (self, label):
        """D.draw_imagelabel (...) -> Surface

        Creates the surface for the passed ImageLabel widget.
        """
        cls = label.__class__
        border = self.style.get_border_size (cls, label.style, label.border)

        width = 2 * (border + label.padding)
        height = 2 * (border + label.padding)

        rect_img = label.picture.get_rect ()
        width += rect_img.width
        height += rect_img.height

        # Guarantee size.
        width, height = label.check_sizes (width, height)
        
        surface = self.draw_rect (width, height, label.state, cls, label.style)
        self.draw_border (surface, label.state, cls, label.style, label.border)

        return surface

    def draw_tooltipwindow (self, window):
        """D.draw_tooltipwindow (...) -> Surface
        
        Creates the surface for the passed TooltipWindow widget.
        """
        cls = window.__class__
        style = window.style or self.style.get_style (cls)
        border_type = StyleInformation.get ("TOOLTIPWINDOW_BORDER")
        border = self.style.get_border_size (cls, style, border_type)
        color = StyleInformation.get ("TOOLTIPWINDOW_COLOR")

        width = 2 * (window.padding + border)
        height = 2 * (window.padding + border)
        
        rtext = self.draw_string (window.text, window.state, cls, style)
        rect  = rtext.get_rect ()
        width += rect.width
        height += rect.height

        # Guarantee size.
        width, height = window.check_sizes (width, height)
        surface =  Draw.draw_rect (width, height, color)
        surface.blit (rtext, (window.padding, window.padding))
        self.draw_border (surface, window.state, cls, style, border_type)
        return surface

    def draw_box (self, box):
        """D.draw_box (...) -> Surface

        Creates the surface for the passed Box widget.
        """
        cls = box.__class__
        # Guarantee size.
        width, height = box.check_sizes (0, 0)
        return self.draw_rect (width, height, box.state, cls, box.style)

    def draw_alignment (self, alignment):
        """D.draw_alignment (...) -> Surface

        Creates the surface for the passed Alignment widget.
        """
        # Guarantee size.
        width, height = 0, 0
        if alignment.child:
            width += alignment.child.width
            height += alignment.child.height
        width, height = alignment.check_sizes (width, height)
        return self.draw_rect (width, height, alignment.state,
                               alignment.__class__, alignment.style)

