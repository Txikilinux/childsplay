# $Id: base.py,v 1.12.2.2 2006/09/14 23:32:01 marcusva Exp $
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

"""Globally used variables and objects by the widgets."""

from pygame import init as pygameinit, key
from Style import Style
from StyleInformation import StyleInformation

# Globally used style object for the widgets.
GlobalStyle = None

# Timer rate in ms to adjust the double-click speed.
DoubleClickRate = 0

def init ():
    """base.init () -> None

    Initializes the globally used variables and objects.

    Initializes the globally used variables and objects for the widgets
    package such as a global style and the pygame engine
    """
    global GlobalStyle
    global DoubleClickRate
    
    GlobalStyle = Style ()
    DoubleClickRate = 250

    pygameinit ()
    key.set_repeat (500, 30)

def set_doubleclick_rate (rate):
    """base.set_doubleclick_rate (...) -> None

    Sets the maximum time to elaps between two clicks for a double-click.

    Sets the maximum time in milliseconds to elaps between two click events
    (SIG_MOUSEDOWN, SIGMOUSEUP) identify them as a double-click.
    The default are 250 ms.

    Raises a TypeError, if the passed argument is not an integer greater
    than 0.
    """
    if (type (rate) != int) or (rate < 1):
        raise TypeError ("rate must be a positive integer greater than 0")
    global DoubleClickRate
    DoubleClickRate = rate
