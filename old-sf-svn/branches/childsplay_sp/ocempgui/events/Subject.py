# $Id: Subject.py,v 1.1.2.3 2006/08/20 08:35:53 marcusva Exp $
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

"""Simple observer subject class."""

from IObserver import IObserver

class Subject (object):
    """Subject (name) -> Subject

    A class matching the subscriptable Subject of the observer pattern.

    The Subject class allows other classes to be notified whenever its
    state(s) change. It has an unique name which identifies itself upon
    notification of the registered classes.
    
    The unique name of the concrete subject implementation can be
    adjusted using the 'name' attribute and set_name() method.

    subject.name = 'MySubject'
    subject.set_name ('AnotherSubject')

    Observers will be notified about state changes through an update()
    method, they have to implement. The IObserver interface class
    contains details about its signature.

    To notify observers about a state change, the Subject implementation
    must invoke its notify() method with the state, that changed, its
    old state value and the newly set value.

    class MySubject (Subject):
        def __init__ (self):
            Subject.__init__ (self, 'UniqueSubjectName')
            self._value = None
        
        def set_value (self, value):
            # Preserve old value.
            oldval = self._value

            # Set new value.
            self._value = value

            # Notify observers
            self.notify ('value', old, value)

    A listening observer which should react upon changes of that value
    could implement the reaction the following way:

    class MyObserver (IObserver):
        ...
        def update (self, subject, attribute, oldval, newval):
            # Look for the certain subject.
            if subject == 'UniqueSubjectName':
                # Which state changed?
                if attribute == 'value':
                    self.do_some_action (oldval, newval)
            ...
    
    Attributes:
    name      - The name of the Subject.
    listeners - List containing the attached observers.
    """
    def __init__ (self, name):
        self._name = None
        self._listeners = []
        self.set_name (name)

    def set_name (self, name):
        """S.set_name (...) -> None

        Sets the name of the Subject.
        
        Raises a TypeError, if the passed argument is not a string or
        unicode.
        """
        if type (name) not in (str, unicode):
            raise TypeError ("name must be a string or unicode")
        self._name = name
        
    def add (self, *observers):
        """S.add (observers) -> None

        Adds one or more observers to the Subject.

        Raises an AttributeError, if one of the passed 'observers'
        arguments does not have a callable update() attribute.
        Raises a ValueError, if one of the passed 'observers' arguments
        is already registered as listener.
        """
        for obj in observers:
            if not isinstance (obj, IObserver):
                print "Warning: observer should inherit from IObserver"
                if not hasattr (obj, "update") or not callable (obj.update):
                    raise AttributeError ("update() method not found in"
                                          "observer %s" % obj)
            if obj in self._listeners:
                raise ValueError ("observer %s already added" % obj)
            self._listeners.append (obj)

    def remove (self, observer):
        """S.remove (observer) -> None

        Removes an observer from the Subject.
        """
        self._listeners.remove (observer)

    def notify (self, prop=None, oldval=None, newval=None):
        """S.notify (...) -> None

        Notifies all observers about a state change.
        """
        for obj in self._listeners:
            obj.update (self.name, str (prop), oldval, newval)

    name = property (lambda self: self._name,
                     lambda self, var: self.set_name (name),
                     doc = "The name of the Subject.")
    listeners = property (lambda self: self._listeners,
                          doc = "The observers for the Subject.")
