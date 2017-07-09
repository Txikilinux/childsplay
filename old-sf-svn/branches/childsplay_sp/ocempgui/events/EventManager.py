# $Id: EventManager.py,v 1.22.2.1 2006/08/18 08:35:03 marcusva Exp $
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

"""Event management system for any type of events and objects."""

from Signals import Event
from INotifyable import INotifyable

class EventManager (object):
    """EventManager () -> EventManager

    An event distribution system.

    The EventManager enables objects to receive events. Each object can
    register several signal types, on which occurance the EventManager
    will call the object's 'notify' method with that event.

    Events also can be distributed by invoking the 'emit()' method of
    the EventManager.

    Attributes:
    queues        - A dict with signal-list associations of registered objects.
    event_grabber - The event grabbing object, which will receive all events.
    """
    def __init__ (self):
        self.queues = {}
        self._grabber = None

    def __len__ (self):
        """E.__len__ () -> len (E)

        Returns the amount of objects within the EventManager
        """
        length = 0
        evlist = self.queues.keys ()
        for signal in evlist:
            length += len (self.queues[signal])
        return length

    def add_object (self, obj, *signals):
        """E.add_object (...) -> None

        Adds an object to the EventManger.

        Adds an object as listener for one or more events to the
        EventManager. Each event type in the *signals argument will
        cause the object to be added to a respective queue, on which
        events with the same type will be emitted.

        Raises an AttributeError, if the passed 'obj' argument does
        not have a callable notify attribute.
        """
        if not isinstance (obj, INotifyable):
            print "Warning: object should inherit from INotifyable"
            if not hasattr (obj, "notify") or not callable (obj.notify):
                raise AttributeError ("notify() method not found in object %s"
                                      % obj)
        for key in signals:
            self.queues.setdefault (key, []).append (obj)

    def add_high_priority_object (self, obj, *signals):
        """E.add_high_priority_object (...) -> None

        Adds a high priority object to the EventManager.

        High priority objects do not differ from normal objects. Instead
        they are added in the first place to the signal queues instead
        of being appended to them like add_object() does. This results
        in notifying those objects in the first place.

        Raises an AttributeError, if the passed 'obj' argument does
        not have a callable notify attribute.
        """
        if not isinstance (obj, INotifyable):
            print "*** Warning: object should inherit from INotifyable"
            if not hasattr (obj, "notify") or not callable (obj.notify):
                raise AttributeError ("notify() method not found in object %s"
                                      % obj)
        for key in signals:
            self.queues.setdefault (key, []).insert (0, obj)

    def remove_object (self, obj, *signals):
        """E.remove_object (...) -> None

        Removes an object from the EventManager.

        Removes the object from the queues passed as the 'signals'
        arguments. If 'signals' is None, the object will be removed
        from all queues of the EventManager.
        """
        if signals:
            evlist = signals
        else:
            evlist = self.queues.keys ()

        for signal in evlist:
            if obj in self.queues[signal]:
                self.queues[signal].remove (obj)

    def clear (self):
        """E.clear () -> None

        Removes all objects and signals from all event queues.
        """
        self.event_grabber = None
        self.queues = {}

    def grab_events (self, obj):
        """E.grab_events (...) -> None

        Sets an event grabber object for the EventManager.

        Causes the EventManager to send _all_ its events only to this
        object instead of the objects in its queues. It is up to the
        event grabbing object to filter the events, it received.
        """
        if (obj != None) and not isinstance (obj, INotifyable):
            print "*** Warning: object should inherit from INotifyable"
            if not hasattr (obj, "notify") or not callable (obj.notify):
                raise AttributeError ("notify() method not found in object %s"
                                      % obj)
        self._grabber = obj

    def emit (self, signal, data):
        """E.emit (...) -> None

        Emits an event, which will be sent to the objects.

        Emits an event on a specific queue of the EventManager, which
        will be sent to the objects in that queue. If one of the
        receiving objects sets the 'handled' attribute of the event to
        True, the emission will stop immediately so that following
        objects will not receive the event.
        """
        self.emit_event (Event (signal, data))

    def emit_event (self, event):
        """E.emit_event (...) -> None

        Emits an event, which will be sent to the objects.

        Emits an event on a specific queue of the EventManager, which
        will be sent to the objects in that queue. If one of the
        receiving objects sets the 'handled' attribute of the event to
        True, the emission will stop immediately so that following
        objects will not receive the event.
        """
        if self.event_grabber:
            self.event_grabber.notify (event)
            return

        evlist = self.queues.get (event.signal, [])
        for obj in evlist:
            obj.notify (event)
            if event.handled:
                break

    event_grabber = property (lambda self: self._grabber,
                              lambda self, var: self.grab_events (var),
                              doc = "Sets the event grabber object.")
