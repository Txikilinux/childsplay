# $Id: ListItemCollection.py,v 1.9.2.1 2006/08/09 09:07:12 marcusva Exp $
#
# Copyright (c) 2004-2005, Marcus von Appen
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

"""List item collection."""

from UserList import UserList
from ListItem import ListItem

class ListItemCollection (UserList):
    """ListItemCollection (items=None) -> ListItemCollection

    An collection class for ListItem objects.

    The ListItemCollection wraps a list object and limits it to the
    abstract ListItem class type, so that it is guaranteed, that the
    collection only contains a specific object type.

    It adds a notification slot 'list_changed', to which a method or
    function can be connected either by assigning the attribute directly
    or using the set_list_changed() method. The slot'ed callback will be
    invoked, whenever the list contents change. The signature of the
    function or method to connect has to get one argument, which will be
    the ListItemCollection.
    
    class Example:
        ...

        def list_callback (self, collection):
            ...

    collection.list_changed = object_example.list_callback
    collection.set_list_changed (object_example.list_callback)

    The ListItemCollection also adds a notification slot 'item_changed',
    to which a method or function can be connected using (again) the
    attribute directly or the set_item_changed() method. The callback
    will be invoked, whenever a ListItem of the collection changes and
    calls the callback. The signature of the function or method to
    connect has to get one argument, which will be the ListItem, which
    invoked it.

    class Example:
        ...

        def item_callback (self, item):
            ...

    collection.item_changed = object_example.item_callback
    collection.set_item_changed (object_example.item_callback)
    
    The ListItemCollection does support the usual list operations such as
    appending, insertion and removal using indices, slicing,the count()
    and len() methods and the list iterator.

    Attributes:
    length       - Amount of the items attached to the ListItemCollection.
    list_changed - Slot to connect a method to, which will be called whenever
                   the contents of the ListItemCollection change.
    item_changed - Slot to connect a method to, which will be called whenever
                   an item of the ListItemCollection changes.
    """
    def __init__ (self, items=None):
        if items != None:
            invalid = filter (lambda x: not isinstance (x, ListItem), items)
            if len (invalid) != 0:
                raise ValueError ("items must contain only ListItem objects")

        UserList.__init__ (self, items)
        
        self._length = 0
        # Notifier slots.
        self._listchanged = None
        self._itemchanged = None

    def append (self, item):
        """L.append (...) -> None

        Appends a ListItem to the end of the ListItemCollection

        Raises a TypeError, if the passed argument does not inherit
        from the ListItem class.
        """
        if not isinstance (item, ListItem):
            raise TypeError ("item must inherit from ListItem")
        UserList.append (self, item)
        self._length += 1
        if item.collection != self:
            item.collection = self
        if self.list_changed:
            self.list_changed (self)

    def count (self, item):
        """L.count (...) -> int

        Returns the number of occurences of the ListItem.

        Raises a TypeError, if the passed argument does not inherit
        from the ListItem class.
        """
        if not isinstance (item, ListItem):
            raise TypeError ("item must inherit from ListItem")
        UserList.count (self, item)

    def insert (self, index, item):
        """L.insert (...) -> None

        Inserts the ListItem before index.

        Raises a TypeError, if the passed item argument does not
        inherit from the ListItem class.
        """
        if not isinstance (item, ListItem):
            raise TypeError ("item must inherit from ListItem")
        UserList.insert (self, index, item)
        self._length += 1
        if item.collection != self:
            item.collection = self
        if self.list_changed:
            self.list_changed (self)

    def remove (self, item):
        """L.remove (...) -> None

        Removes the first occurance of item from the ListItemCollection.
        """
        UserList.remove (self, item)
        item.collection = None
        self._length -= 1
        if self.list_changed:
            self.list_changed (self)

    def sort (self, cmp=None, key=None, reverse=False):
        """L.sort (...) -> None

        Stable in place sort for the ListItemCollection.
        """
        UserList.sort (self, cmp, key, reverse)
        if self.list_changed:
            self.list_changed (self)

    def set_list_changed (self, method):
        """L.set_list_changed (...) -> None

        Connects a method to invoke, when the collection changes.

        Raises a TypeError, if the passed argument is not callable.
        """
        if method and not callable (method):
            raise TypeError ("method must be callable")
        self._listchanged = method
    
    def set_item_changed (self, method):
        """L.set_item_changed (...) -> None

        Connects a method to invoke, when an item of the collection changes.

        Raises a TypeError, if the passed argument is not callable.
        """
        if method and not callable (method):
            raise TypeError ("method must be callable")
        self._itemchanged = method

    def __setitem__ (self, index, item):
        """L.__setitem__ (index, item) -> L[index] = item

        Raises a TypeError, if the passed item argument does not inherit
        from the ListItem class.
        """
        if not isinstance (item, ListItem):
            raise TypeError ("item must inherit from ListItem")

        old = UserList.__getitem__ (self, index)

        # Remove the old ListItem.
        old.collection = None
        del old

        # Set the new one.
        UserList.__getitem__ (self, index, item)
        if item.collection != self:
            item.collection = self
        if self.list_changed:
            self.list_changed (self)

    def __len__ (self):
        """L.__len__ () -> len (L)
        """
        return self._length

    def __setslice__ (self, i, j, collection):
        """L.__setslice__ (i, j, collection) -> L[i:j] = collection

        Raises a TypeError, if the passed collection argument does not
        inherit from the ListItemCollection class.
        """
        if not isinstance (collection, ListItemCollection):
            raise TypeError ("collection must inherit from ListItemCollection")

        old = UserList.__getslice__ (self, i, j)
        UserList.__setslice__ (self, i, j, collection[:])
        new = UserList.__getslice__ (self, i, j)
        
        # Clean up the old ones.
        for item in old:
            item.collection = None
            self._length -= 1
            del item

        # Set the relations for the new ones.
        for item in new:
            item.collection = self
            self._length += 1
        if self.list_changed:
            self.list_changed (self)

    length = property (lambda self: self._length,
                       doc = "Amount of the attached items.")
    list_changed = property (lambda self: self._listchanged,
                             lambda self, var: self.set_list_changed (var),
                             doc = "Notifier slot for collection changes.")
    item_changed = property (lambda self: self._itemchanged,
                             lambda self, var: self.set_item_changed (var),
                             doc = "Notifier slot for item changes.")
