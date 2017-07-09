# $Id: Constants.py,v 1.32.2.5 2007/01/28 11:24:30 marcusva Exp $
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

"""Constants used by the ocempgui widgets module.

General constants
-----------------
General constants denote values, which are used for multiple purposes
and usually not limited to specific widget class parts.

DEFAULTDATADIR
Path to the directory where theme files and additional resources were
installed. This path is especially important for the Style class and
user code, which relies upon the drawing engines or other resources.


State constants
---------------
The state constants denote the state of a widget and influence its
behaviour and appeareance. They usually can be read from the widget
through its 'state' attribute and are usually prefixed with 'STATE_'.

The state constants are grouped in the STATE_TYPES tuple.

STATE_NORMAL
The usual state ('default') of a widget. This is the basic state, the
widget has, if it is created and no interaction happened with it.

STATE_ENTERED
The widget area was entered by a pointing device. This usually slightly
changes the visual appearance of the widget, so it is easier to
distinguish between the entered and other widgets.

STATE_ACTIVE
The widget is activated. This usually will cause a widget to change its
visual appearance, so the user can see the interaction. A Button widget
for example will be drawn in a sunken state, while an Entry widget will
show a blinking caret.

STATE_INSENSITIVE
Usually set through the 'sensitive' attribute of a widget. This will
change the visual appearance of the widget, so that it is easier to
distinguish between widgets, with which an interaction is possible and
insensitive widgets, with which it is not.

Scrolling constants
-------------------
The scrolling constants only apply to widgets, which support scrolling
such as the ScrolledList or ScrolledWindow classes. They influence the
visibility and behaviour of the attached scrollbars for those widgets.

The scrolling constants are grouped in the SCROLL_TYPES tuple.

SCROLL_NEVER
Scrollbars will never be shown, independant of if they are necessary or
not.

SCROLL_AUTO
Scrollbars will be shown and hidden on demand.

SCROLL_ALWAYS
Scrollbars will always be shown, independant of if they are necessary or
not.

Selection constants
-------------------
Selection constants influence the selection behaviour in the list and
tree like widgets such as the ScrolledList class.

The selection constants are grouped in the SELECTION_TYPES tuple.

SELECTION_NONE
No selection is possible. Elements cannot be selected and existing
selections can not be changed.

SELECTION_SINGLE
Only one element can be selected per time.

SELECTION_MULTIPLE
Multiple elements can be selected.

Border constants
----------------
The border constants influence the appearance of a widget
border. Several widgets support this constants to fit in their
environment.

The border constants are grouped in the BORDER_TYPES tuple.

BORDER_NONE
The widget will have no visible border.

BORDER_FLAT
The widget will have a flat border around it.

BORDER_SUNKEN
The widget will have a sunken border effect.

BORDER_RAISED
The widget will have a raised border effect.

BORDER_ETCHED_IN
The widget will have a etched in border effect.

BORDER_ETCHED_OUT
The widget will have a etched out border effect.

Arrow constants
---------------
The arrow constants are used by the ScrollBar widgets and determine the
direction of the arrows on the scrollbar buttons.

The arrow constants are grouped in the ARROW_TYPES tuple.

ARROW_UP
The arrow points upwards.

ARROW_DOWN
The arrown points downwards

ARROW_LEFT
The arrow points to the left.

ARROW_RIGHT
The arrow points to the right.

Alignment flags
---------------
The alignment flags are used by most Container and Bin widget classes
and influence the drawing positions of the attached children. The flags
can be combined bitwise, although not every combination makes sense
(like ALIGN_TOP | ALIGN_BOTTOM).

The alignment flags are grouped in the ALIGN_TYPES tuple.

ALIGN_NONE
No special alignment, use the defaults of the widget.

ALIGN_TOP
Align the child(ren) at the top.

ALIGN_BOTTOM
Align the child(ren) at the bottom.

ALIGN_LEFT
Align the child(ren) at the left side.

ALIGN_RIGHT
Align the child(ren) at the right side.

Orientation types
-----------------
The orientation types are used by widgets, which are able to draw
themselves in a vertical or horizontal alignment, such as Diagram or
Scale widgets. A single axis chart for example can have either a
vertical or horizontal axis orientation.

The orientation constance are grouped in the ORIENTATION_TYPES tuple.

ORIENTATION_VERTICAL
The widget parts are aligned and drawn vertically.

ORIENTATION_HORIZONTAL
The widget parts are align and drawn horizontally.

Dialog result values
--------------------
Dialog result values are used and sent by dialog windows, which inherit
from the GenericDialog, only. They usually represent the button of the
dialog, that got pressed and allow to react upon the user input
action.

The dialog result constants are grouped in the DLGRESULT_TYPES tuple.

The descriptions of the results below are meant as usability
guidelines. The average user mostly will have the described intention,
when he presses a button with that result value.

DLGRESULT_OK
Indicates, that the user agrees to or accepts the information shown on
the dialog or successfully finished her input.

DLGRESULT_CANCEL
Indicates, that the user wants to abort from the current action or input
without making any changes to the current state.

DLGRESULT_ABORT
Same as above, but mostly used in a different context such as a hard
program or process abort.

DLGRESULT_CLOSE
Used in dialogs, in which usually no special agreement of the user is
needed. Mostly used for dialogs, that show information only and do not
influence the application behaviour in any way.

DLGRESULT_USER
Freely choosable.

Signal constants
----------------
The signal constants denote various event identfies, which are emitted
on and by widgets and to which widgets can listen. Usually there is a
distinction between native signal (those which are emitted by the pygame
library) and widget signals (those which are emitted by widgets). The
native signals are usually just aliases for pygame constants to fit in
the OcempGUI namespace.
 
Signal callbacks for native signals usually will receive the pygame
event data as first argument. This means, that a callback would look
like the following:

widget.connect_signal (SIG_MOUSEDOWN, mousedown_callback, owndata)

def mousedown_callback (eventdata, userdata1, ...):
    if eventdata.pos == ...:
        ...
    if userdata1 == owndata:
        ...

The passed pygame event data matches the sent pygame.event.Event data
for the specific signal as described in the pygame documentation.

SIG_KEYDOWN
Alias for pygame.locals.KEYDOWN. Emitted, if a key on the keyboard will
be pressed down. OcempGUI uses a repeatedly emittance of that event by
the pygame.key.set_repeat() function.
Note: Signal callbacks will receive the pygame event data as first
argument.

SIG_KEYUP
Alias for pygame.locals.KEYUP. Emitted, if a key on the keyboard is
released.
Note: Signal callbacks will receive the pygame event data as first
argument.

SIG_MOUSEDOWN
Alias for pygame.locals.MOUSEBUTTONDOWN. Emitted, if a mouse button gets
pressed (or the mouse wheel is used).
Note: Signal callbacks will receive the pygame event data as first
argument.

SIG_MOUSEUP
Alias for pygame.locals.MOUSEBUTTONUP, Emitted, if a mouse button is
released.
Note: Signal callbacks will receive the pygame event data as first
argument.

SIG_MOUSEMOVE
Alias for pygame.locals.MOUSEMOTION. Emitted, if the mouse cursor
position changes (the mouse is moved).
Note: Signal callbacks will receive the pygame event data as first
argument.

SIG_TICK
Alias for pygame.locals.USEREVENT + 1. This is a timer event for
widgets, which need timed event emits such as the Entry widget class
(blinking cursor) or the StatusBar (date update). Usually this event is
emitted every 500ms by the Renderer class.

SIG_TWISTED
Alias for pygame.locals.USEREVENT + 2. This signal type is used only by
the TwistedRenderer at the moment and will be sent whenever the
interleave() method of its attached reactor is called.

SIG_UPDATED
Alias for pygame.locals.USEREVENT + 3. This signal is used by the
Renderer class to notify listeners about an update of the screen area.

SIG_SCREENCHANGED
Alias for pygame.locals.USEREVENT + 4. This signal type is used by the
Renderer class to notify listeners about changes of the attached
screen area.

SIG_CLICKED
Raised by supporting widgets, if the following event sequence happens on
the widget:
1) Left mouse button pressed down (SIG_MOUSEDOWN).
2) Left mouse button released (SIG_MOUSEUP)
3) Click event will be raised by the widget (SIG_CLICKED).

SIG_FOCUSED
Raised by supporting widgets, if a widget is focused by the mouse or
another input device (such as the keyboard). This usually will pass the
input focus to that widget.

SIG_INPUT
Raised by widgets, which support data input and indicates, that an made
input was successfully finished. An example would be the Editable widget
class, which raises SIG_INPUT upon pressing Enter/Return after typing text.

SIG_TOGGLED
Raised by widgets, which support and/or indicate True/False value states
such as the Check- or ToggleButton. This will be raised _after_ the
value has been changed.

SIG_VALCHANGED
Raised, if the main value of a supporting widget changed (usually
numeric), such as the value of a Scale or ProgressBar.

SIG_SELECTCHANGED
Raised, if a certain selection changed.

SIG_LISTCHANGED
Raised if the attached item list of a ScrolledList changed.

SIG_DIALOGRESPONSE
Raised, when a button attached to a GenericDialog object gets pressed.
Note: Signal callbacks will receive the result value bound to the button
as first argument.

SIG_DESTROYED
Raised by a widget, when it is about to be destroyed.
Note: Signal callbacks will receive the destroyed widget as first argument.

SIG_ENTER
Raised by a widget, when the mouse cursor enters it.

SIG_LEAVE
Raised by a widget, when the mouse cursor leaves it.
"""
from childsplay_sp.SPConstants import OCWBASEDIR
import os
from pygame import KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP
from pygame import USEREVENT

# State constants.
STATE_NORMAL =      0
STATE_ENTERED =     1
STATE_ACTIVE =      2
STATE_INSENSITIVE = 3
STATE_TYPES = (STATE_NORMAL, STATE_ENTERED, STATE_ACTIVE, STATE_INSENSITIVE)

# Srolling behaviour widget widgets, which support it.
SCROLL_NEVER =  0
SCROLL_AUTO =   1
SCROLL_ALWAYS = 2
SCROLL_TYPES = (SCROLL_NEVER, SCROLL_AUTO, SCROLL_ALWAYS)

# Selection modes.
SELECTION_NONE =     0
SELECTION_SINGLE =   1
SELECTION_MULTIPLE = 2
SELECTION_TYPES = (SELECTION_NONE, SELECTION_SINGLE, SELECTION_MULTIPLE)

# Border types.
BORDER_NONE =       0
BORDER_FLAT =       1
BORDER_SUNKEN =     2
BORDER_RAISED =     3
BORDER_ETCHED_IN =  4
BORDER_ETCHED_OUT = 5
BORDER_TYPES = (BORDER_NONE, BORDER_FLAT, BORDER_SUNKEN, BORDER_RAISED,
                BORDER_ETCHED_IN, BORDER_ETCHED_OUT)

# Arrow types.
ARROW_UP =    0
ARROW_DOWN =  1
ARROW_LEFT =  2
ARROW_RIGHT = 3
ARROW_TYPES = (ARROW_UP, ARROW_DOWN, ARROW_LEFT, ARROW_RIGHT)

# Alignment types.
ALIGN_NONE =   0
ALIGN_TOP =    1 << 0
ALIGN_BOTTOM = 1 << 1
ALIGN_LEFT =   1 << 2
ALIGN_RIGHT =  1 << 3
ALIGN_TYPES = (ALIGN_NONE, ALIGN_TOP, ALIGN_BOTTOM, ALIGN_LEFT, ALIGN_RIGHT)

def constants_is_align (align):
    """C.constants_is_align (align) -> bool

    Checks whether the passed value evaluates to an align value.
    """
    if type (align) != int:
        raise TypeError ("align must be an integer.")
    
    return (align & ALIGN_TOP == ALIGN_TOP) or \
           (align & ALIGN_BOTTOM == ALIGN_BOTTOM) or \
           (align & ALIGN_LEFT == ALIGN_LEFT) or \
           (align & ALIGN_RIGHT == ALIGN_RIGHT) or \
           (align & ALIGN_NONE == ALIGN_NONE)

# Orientation types.
ORIENTATION_VERTICAL   = intern ("vertical")
ORIENTATION_HORIZONTAL = intern ("horizontal")
ORIENTATION_TYPES = (ORIENTATION_VERTICAL, ORIENTATION_HORIZONTAL)

# Dialog results.
DLGRESULT_OK =     0
DLGRESULT_CANCEL = 1
DLGRESULT_ABORT =  2
DLGRESULT_CLOSE =  3
DLGRESULT_USER =   99
DLGRESULT_TYPES = (DLGRESULT_OK, DLGRESULT_CANCEL, DLGRESULT_ABORT,
                   DLGRESULT_CLOSE, DLGRESULT_USER)

# Signal constants, native.
SIG_KEYDOWN =       KEYDOWN
SIG_KEYUP =         KEYUP
SIG_MOUSEDOWN =     MOUSEBUTTONDOWN
SIG_MOUSEMOVE =     MOUSEMOTION
SIG_MOUSEUP =       MOUSEBUTTONUP
SIG_TICK =          USEREVENT + 1
SIG_TWISTED =       USEREVENT + 2
SIG_UPDATED =       USEREVENT + 3
SIG_SCREENCHANGED = USEREVENT + 4

# Signal groups for fast tests.
SIGNALS_KEYS = (SIG_KEYDOWN, SIG_KEYUP)
SIGNALS_MOUSE = (SIG_MOUSEDOWN, SIG_MOUSEMOVE, SIG_MOUSEUP)

# Signal constants, raised by the widgets.
SIG_ACTIVATED =      intern ("activated")
SIG_CLICKED =        intern ("clicked")
SIG_FOCUSED =        intern ("focused")
SIG_INPUT =          intern ("input")
SIG_TOGGLED =        intern ("toggled")
SIG_VALCHANGED =     intern ("value-changed")
SIG_SELECTCHANGED =  intern ("selection-changed")
SIG_LISTCHANGED =    intern ("list-changed")
SIG_DOUBLECLICKED =  intern ("double-clicked")
SIG_DIALOGRESPONSE = intern ("dialog-response")
SIG_DESTROYED =      intern ("destroyed")
SIG_ENTER =          intern ("entered")
SIG_LEAVE =          intern ("left")

# The default data directory, where the themes and co. get installed.
# /usr/share/python-ocempgui will be replaced at installation usually.
# Changed by Stas for the inclusion in CP
DEFAULTDATADIR = os.path.join(OCWBASEDIR,'widgets')
