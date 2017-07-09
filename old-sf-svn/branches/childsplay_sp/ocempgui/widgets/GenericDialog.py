# $Id: GenericDialog.py,v 1.4 2006/07/02 13:08:53 marcusva Exp $
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

"""An universal dialog window class with additional buttons."""

from DialogWindow import DialogWindow
from Frame import VFrame, HFrame
from Button import Button
from Constants import *

class GenericDialog (DialogWindow):
    """GenericDialog (title, buttons, results) -> GenericDialog

    A generic dialog window, which supports result values.

    The GenericDialog widget class is suitable to create dialog windows
    which need to check for certain dialog results in an easy
    way. Specific result values can be bound to the buttons of the
    dialog and will be emitted upon clicking the buttons.

    The creation of the GenericDialog is a bit different from other
    widgets. Besides the title, it receives two lists for the buttons to
    display and the results they have to send. Both lists need to have
    the same length.

    dialog = GenericDialog ('Test', [Button ('OK'), Button ('Cancel')],
                            [DLGRESULT_OK, DLGRESULT_CANCEL])

    The index of the result values need to match the index of the
    button, that should emit them. Of course the buttons can be changed
    at runtime programmatically with the set_buttons() method, which is
    similar to the constructor.

    dialog.set_buttons ([Button ('Close'), Button ('ClickMe')],
                        [DLGRESULT_CLOSE, DLGRESULT_USER])

    The result values to set must match a valid value from the
    DLGRESULT_TYPES tuple.

    Given the above set_buttons() example, a callback for the
    SIG_DIALOGRESPONSE signal will receive either the DLGRESULT_CLOSE or
    DLGRESULT_USER value upon which certain actions can take place.

    def dialog_callback (result, dialog):
        if result == DLGRESULT_CLOSE:
            dialog.destroy ()
        elif result == DLGRESULT_USER:
            ...

    mydialog.connect_signal (SIG_DIALOGRESPONSE, dialog_callback, mydialog)
    
    The GenericDialog is separated in several frames, to which user
    content can be added. The main frame, which holds anything else, can
    be accessed through the 'main' attribute. While it is possible to
    change most of its attributes without unwanted side effects, its
    children should not be modifed or deleted to prevent misbehaviour of
    the dialog.

    dialog.main.spacing = 10
    
    The second frame, which is usually the most interesting is the
    content frame, packed into the main frame. It can be accessed
    through the 'content' attribute and should (only) be used to add own
    widgets. Those can be deleted and modified, too.

    label = Label ('Label on the dialog')
    dialog.content.add_child (label)
    dialog.content.add_child (Button ('Button after label'))
    dialog.content.remove_child (label)

    Default action (invoked by activate()):
    See the DialogWindow class.
    
    Mnemonic action (invoked by activate_mnemonic()):
    See the DialogWindow class.

    Signals:
    SIG_DIALOGRESPONSE - Invoked, when an attached button is pressed.
    """
    def __init__ (self, title, buttons, results):
        DialogWindow.__init__ (self, title)
        
        # The main frame holds the whole content for the window.
        # The basic design idea of the dialog looks like:
        # +----------------------+
        # | Title caption        |
        # +----------------------+
        # | main frame           |
        # | ++++++++++++++++++++ |
        # | +                  + |
        # | +    with          + |
        # | +                  + |
        # | +   user content   + |
        # | +                  + |
        # | +------------------+ |
        # | +  Action frame    + 
        # | ++++++++++++++++++++ |
        # +----------------------+
        self.padding = 5
        
        self._mainframe = VFrame ()
        self._mainframe.border = BORDER_NONE
        self._mainframe.spacing = 5
        self._mainframe.padding = 0

        self._contentframe = VFrame ()
        self._contentframe.border = BORDER_NONE
        self._contentframe.spacing = 0
        self._contentframe.padding = 0
        self._mainframe.add_child (self._contentframe)

        # Buttons will be placed in the action frame.
        self._actionframe = HFrame ()
        self._actionframe.border = BORDER_NONE
        self._actionframe.padding = 0
        self._mainframe.add_child (self._actionframe)

        self.set_buttons (buttons, results)

        self._signals[SIG_DIALOGRESPONSE] = []
        self.set_child (self._mainframe)

    def set_buttons (self, buttons, results):
        """G.set_buttons (buttons. results) -> None

        Sets the buttons for the dialog and their wanted result values.
        """
        for widget in self._actionframe.children:
            widget.destroy ()
        
        for i in xrange (len (buttons)):
            if not isinstance (buttons[i], Button):
                raise TypeError ("All elements in buttons must inherit "
                                 "from Button")
            if results[i] not in DLGRESULT_TYPES:
                raise TypeError ("All elements in results must be values "
                                 "of DLGRESULT_TYPES")
            buttons[i].connect_signal (SIG_CLICKED, self._button_clicked,
                                       results[i])
            self._actionframe.add_child (buttons[i])
        self.dirty = True

    def _button_clicked (self, result):
        """G._button_clicked (...) -> None

        Callback for the buttons in the action frame.

        The _button_clicked method will run the SIG_DIALOGRESPONSE
        signal handlers with the passed result. 
        """
        self.run_signal_handlers (SIG_DIALOGRESPONSE, result)

    content = property (lambda self: self._contentframe,
                        doc = "The content frame to add widgets to.")
    main = property (lambda self: self._mainframe,
                     doc = "The main frame of the dialog.")
