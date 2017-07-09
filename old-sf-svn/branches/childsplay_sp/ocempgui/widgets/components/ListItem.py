# $Id: ListItem.py,v 1.18 2006/06/24 11:21:28 marcusva Exp $
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

"""Objects suitable for the usage in a list."""
from childsplay_sp.ocempgui.widgets.base import GlobalStyle

class ListItem (object):
    """ListItem () -> ListItem

    Creates a new ListItem suitable for the usage in list or tree widgets.

    The ListItem class is an abstract class for list implementations.
    It is not able to react upon events nor has the flexibility and
    capabilities a widget inheriting from the BaseWidget class has, but
    provides a minimalistic set of methods to make it suitable for lists
    of nearly any type.

    ListItems support a 'style' attribute and get_style() method, which
    enable them to use different look than default one. The 'style'
    attribute of a ListItem usually defaults to a None value and can be
    set using the get_style() method. This causes the ListItem internals
    to setup the specific style for it and can be accessed through the
    'style' attribute later on. A detailled documentation of the style
    can be found in the Style class.

    if not listitem.style:
        listitem.get_style () # Setup the style internals first.
    listitem.style['font']['size'] = 18
    listitem.get_style ()['font']['name'] = Arial

    The ListItem supports a selection state using the 'selected'
    attribute. This indicates, whether the ListItem was selected or not.

    listitem.selected = False
    listitem.selected = True

    ListItems can be set in a dirty state, which indicates, that they
    need to be updated. The 'dirty' attribute and set_dirty() method
    take care of this and automatically invoke the bound has_changed()
    method of the ListItem. In user code, 'dirty' usually does not need
    to be modified manually.

    listitem.dirty = True
    listitem.set_dirty (True)

    The ListItem can be bound to or unbounds from a ListItemCollection
    using the 'collection' attribute or set_collection() method. This
    usually invokes the append() or remove() method of the collection,
    so that it can invoke its list_changed() method.

    listitem.collection = my_collection
    listitem.set_collection (None)
    
    Attributes:
    style      - The style to use for drawing the ListItem.
    selected   - Indicates, whether the ListItem is currently selected.
    collection - The ListItemCollection, the ListItem is attached to.
    dirty      - Indicates, that the ListItem needs to be updated.    
    """
    def __init__ (self):
        # Used for drawing.
        self._style = None

        self._selected = False
        self._collection = None # TODO: implement list checks.
        self._dirty = True
    
    def has_changed (self):
        """L.has_changed () -> None

        Called, when the item has been changed and needs to be refreshed.

        This method will invoke the item_changed() notifier slot of the
        attached collection.
        """
        if (self.collection != None) and self.collection.item_changed:
            self.collection.item_changed (self)
    
    def _select (self, selected=True):
        """L._select (...) -> None

        Internal select handler, which causes the parent to update.
        """
        if self._selected != selected:
            self._selected = selected
            self.dirty = True

    def set_collection (self, collection):
        """L.set_collection (...) -> None

        Sets the collection the ListItem is attached to.

        Sets the 'collection' attribute of the ListItem to the passed
        argument and appends it to the collection if not already done.

        Raises an Exception, if the argument is already attached to a
        collection.
        """
        if collection:
            # TODO: make it type safe!
            if self._collection != None:
                raise Exception ("ListItem already attached to a collection")
            self._collection = collection
            # Add the item if it is not already in the collection.
            if self not in collection:
                collection.append (self)
        else:
            # Remove the item.
            if self._collection != None:
                collection = self._collection
                self._collection = None
                if self in collection:
                    collection.remove (self)
    
    def get_style (self):
        """L.get_style () -> Style
        
        Gets the style for the ListItem.

        Gets the style associated with the ListItem. If the ListItem had
        no style before, a new one will be created for it. More
        information about how a style looks like can be found in the
        Style class documentation.
        """
        if not self._style:
            # Create a new style from the base style class.
            self._style = GlobalStyle.copy_style (self.__class__)
        return self._style

    def set_dirty (self, dirty):
        """L.set_dirty (...) -> None

        Marks the ListItem as dirty.

        Marks the ListItem as dirty.
        """
        self._dirty = dirty
        if dirty:
            self.has_changed ()
        
    collection = property (lambda self: self._collection,
                           lambda self, var: self.set_collection (var),
                           doc = "The collection the ListItem is attached to.")
    selected = property (lambda self: self._selected,
                         lambda self, var: self._select (var),
                         doc = "The selection state of the ListItem.")
    style = property (lambda self: self._style,
                      doc = "The style of the ListItem.")
    dirty = property (lambda self: self._dirty,
                      lambda self, var: self.set_dirty (var),
                      doc = """Indicates, whether the ListItem needs to be
                      redrawn.""")
    
class TextListItem (ListItem):
    """TextListItem (text=None) -> TextListItem

    Creates a new TextListItem, which can display a portion of text.

    The TextListItem is able to display a short amount of text.

    The text to display on the TextListItem can be set through the
    'text' attribute or set_text() method. The TextListItem does not
    support any mnemonic keybindings.

    textlistitem.text = 'Item Text'
    textlistitem.set_text ('Another Text')

    Attributes:
    text - The text to display on the TextListItem.
    """
    def __init__ (self, text=None):
        ListItem.__init__ (self)
        self._text = None
        self.set_text (text)

    def set_text (self, text):
        """T.set_text (...) -> None
        
        Sets the text of the TextListItem to the passed argument.

        Sets the text to display on the TextListItem to the passed
        argument.

        Raises a TypeError, if the passed argument is not a string or
        unicode.
        """
        if text and type (text) not in (str, unicode):
            raise TypeError ("text must be a string or unicode")
        self._text = text
        self.dirty = True
    
    text = property (lambda self: self._text,
                     lambda self, var: self.set_text (var),
                     doc = "The text to display on the TextListItem.")
