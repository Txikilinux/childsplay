# $Id: StyleInformation.py,v 1.9.2.2 2006/09/12 19:59:55 marcusva Exp $
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

"""Constant style information used by the drawing routines.

The StyleInformation dictionary contains different additional
information about the widget's style, such as their internally used
border types (e.g. for showing the input focus), size of drawing
components or specific colors.

The following constants are currently defined:

CHECK_SIZE
The default size of a check box to use for Style.draw_check().

CHECK_SPACING
The spacing to place between a check box and the Label of a CheckButton
widget.

RADIO_SIZE
The default size of a check box to use for Style.draw_radio().

RADIO_SPACING
The spacing to place between a check box and the Label of a RadioButton
widget.

IMAGEBUTTON_SPACING
The spacing to place between an image and the Label of an ImageButton
widget.

SCALE_BORDER
The border type to use for the scale rectangle of a Scale widget.

SCALE_COLOR
The fill color for the scale line.

HSCALE_SLIDER_SIZE
VSCALE_SLIDER_SIZE
The default size of the HScale and VScale slider.

SCROLLBAR_BORDER
The border type to use for the Scrollbar borders.

SCROLLBAR_BUTTON_BORDER
The border type to use for the buttons placed on a ScrollBar widget
.
HSCROLLBAR_BUTTON_SIZE
VSCROLLBAR_BUTTON_SIZE
The default size of the HScrollBar and VScrollBar buttons.

PROGRESSBAR_BORDER
The border type of the ProgressBar widget.

IMAGEMAP_BORDER
The border type of the ImageMap widget.

STATUSBAR_BORDER
The border type of the StatusBar widget.

WINDOW_BORDER
The border type of the Window widget.

VIEWPORT_BORDER
The border type of the ViewPort widget.

ACTIVE_BORDER
The default border type to indicate, that a widget has the input focus.

ACTIVE_BORDER_SPACE
The spacin to place between the widget's border and the active border.

CAPTION_BORDER
The border type of a window caption.

CAPTION_ACTIVE_COLOR
CAPTION_INACTIVE_COLOR
The default color information of the window caption.

PROGRESS_COLOR
The default color information for progress indicators.

SELECTION_COLOR
The default color for selections.

TOOLTIPWINDOW_BORDER
The border type of the TooltipWindow widget.

TOOLTIPWINDOW_COLOR
The background color of the TooltipWindow widget.
"""

import Constants

StyleInformation = {
    "CHECK_SIZE" : 14,
    "CHECK_SPACING" : 2,
    "RADIO_SIZE" : 14,
    "RADIO_SPACING" : 2,
    "IMAGEBUTTON_SPACING" : 2,
    "SCALE_BORDER" : Constants.BORDER_FLAT,
    "SCALE_COLOR" : (184, 172, 172),
    "HSCALE_SLIDER_SIZE" : (30, 16),
    "VSCALE_SLIDER_SIZE" : (16, 30),
    "SCROLLBAR_BORDER" : Constants.BORDER_FLAT,
    "SCROLLBAR_BUTTON_BORDER" : Constants.BORDER_RAISED,
    "HSCROLLBAR_BUTTON_SIZE" : (16, 16),
    "VSCROLLBAR_BUTTON_SIZE" : (16, 16),
    "PROGRESSBAR_BORDER" : Constants.BORDER_SUNKEN,
    "IMAGEMAP_BORDER" : Constants.BORDER_FLAT,
    "STATUSBAR_BORDER" : Constants.BORDER_ETCHED_IN,
    "WINDOW_BORDER" : Constants.BORDER_FLAT,
    "VIEWPORT_BORDER" : Constants.BORDER_SUNKEN,
    "ACTIVE_BORDER" : Constants.BORDER_FLAT,
    "ACTIVE_BORDER_SPACE" : 1,
    "CAPTION_BORDER" : Constants.BORDER_FLAT,
    "CAPTION_ACTIVE_COLOR" : (124, 153, 173),
    "CAPTION_INACTIVE_COLOR" : (150, 150, 150),
    "PROGRESS_COLOR" : (124, 153, 173),
    "SELECTION_COLOR" : (124, 153, 173),
    "TOOLTIPWINDOW_BORDER" : Constants.BORDER_FLAT,
    "TOOLTIPWINDOW_COLOR" : (247, 250, 156)
    }
