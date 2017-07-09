# $Id: IIndexable.py,v 1.1 2006/07/21 08:42:14 marcusva Exp $
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

"""Abstract indexing interface for easy navigation through object lists."""

class IIndexable (object):
    """IIndexable () -> IIndexable

    Abstract class providing methods for easy navigation.

    The IIndexable interface class provides a minimal method set, a
    class should implement to allow easy navigation through objects.

    Objects can be added to the indexing system using the add_index()
    method and be removed by the counterpart remove_index().

    To cycle through the objects, the switch_index() method has to be
    implemented by an inheriting class. This causes - dependant on the
    implementation - another object to get the navigation focus
    (preferably the next object in the logical index list).
    """
    def add_index (self, *objects):
        """I.add_index (...) -> None

        Adds one or more objects to the indexing system.

        This method has to be implemented by inherited classes.
        """
        raise NotImplementedError

    def remove_index (self, *objects):
        """I.remove_index (...) -> None

        Removes one or more objects from the indexing system.

        This method has to be implemented by inherited classes.
        """
        raise NotImplementedError

    def switch_index (self):
        """I.switch_index () -> None

        Passes the input focus to another object from the list.

        This method has to be implemented by inherited classes.
        """
        raise NotImplementedError

    def update_index (self, *objects):
        """I.update_index () -> None

        Updates the index for one or more objects.

        This method has to be implemented by inherited classes.
        """
        raise NotImplementedError
