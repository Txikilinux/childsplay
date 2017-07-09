# $Id: Constants.py,v 1.1.2.2 2006/08/15 23:52:45 marcusva Exp $
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

"""Constants used by the ocempgui.draw module.

Font style constants
--------------------
Font style flsgs influence the rendering of the font and add, dependant
on the set flags, a bold, italic or underlined layout (or an combination
of those three).

The font flags are grouped in the FONT_STYLE_TYPES tuple.

FONT_STYLE_NORMAL
Default font style with no additional rendering.

FONT_STYLE_BOLD
Bold font rendering.

FONT_STYLE_ITALIC
Italic font rendering.

FONT_STYLE_UNDERLINE
Underlined font rendering.
"""

FONT_STYLE_NORMAL =    0
FONT_STYLE_BOLD =      1
FONT_STYLE_ITALIC =    2
FONT_STYLE_UNDERLINE = 4
FONT_STYLE_TYPES = (FONT_STYLE_NORMAL, FONT_STYLE_BOLD, FONT_STYLE_ITALIC,
                    FONT_STYLE_UNDERLINE)

def constants_is_font_style (style):
    """C.constants_is_font_style (style) -> bool

    Checks whether the passed value evaluates to a font style value.
    """
    if type (style) != int:
        raise TypeError ("style must be an integer.")
    
    return (style & FONT_STYLE_BOLD == FONT_STYLE_BOLD) or \
           (style & FONT_STYLE_ITALIC == FONT_STYLE_ITALIC) or \
           (style & FONT_STYLE_UNDERLINE == FONT_STYLE_UNDERLINE)
