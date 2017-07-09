# $Id: IObserver.py,v 1.1.2.3 2006/08/20 08:35:53 marcusva Exp $
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

"""Observer interface class."""

class IObserver (object):
    """IObserver () -> IObserver

    A class matching a observer interface of the observer pattern.

    The IObserver class is an interface, that should be implemented by
    classes, that should be able to register themselves on concrete
    Subject implementations. It declares a single method, update(),
    which receives the state change details of the Subject.

    A short example for reacting upon state changes of Subject:
    
    class MyObserver (IObserver):
        ...
        def update (self, subject, attribute, oldval, newval):
            # Look for the certain subject.
            if subject == 'UniqueSubjectName':
                # Which state changed?
                if attribute == 'value':
                    self.do_some_action (oldval, newval)
            ...

    """
    def update (self, subject, prop, oldval, newval):
        """I.update (...) -> None

        Notifies the IObserver about a state change of a certain Subject.

        This method has to be implemented by inherited classes. Its
        signature matches the basic requirements of the Subject class.
        """
        raise NotImplementedError
