# $Id: BaseWidget.py,v 1.61.2.17 2008/01/09 23:20:38 marcusva Exp $
#
# Copyright (c) 2004-2007, Marcus von Appen
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

"""Basic widget class, used as an abstract definition for widgets."""

# TODO: Add ControlCollection class to the components.

from pygame import sprite, Rect, Surface
from pygame import error as PygameError
from childsplay_sp.ocempgui.object import BaseObject
from childsplay_sp.ocempgui.access import IIndexable
from Style import WidgetStyle
from Constants import *
import base

class BaseWidget (BaseObject, sprite.Sprite):
    """BaseWidget () -> BaseWidget

    A basic widget class for user interface elements.

    The BaseWidget is the most basic widget class, from which any other
    widget class should be inherited. It provides the most basic
    attributes and methods, every widget needs.

    The widget is a visible (or non-vissible) element on the display,
    which allows the user to interact with it (active or passive) in a
    specific way. It has several methods and attributes to allow
    developers to control this interaction and supports accessibility
    through the ocempgui.access module.

    The widget can be placed on the display by accessing the various
    attributes of its 'rect' attribute directly. It exposes the following
    pygame.Rect attributes:
    
        top, left, bottom, right,
        topleft, bottomleft, topright, bottomright,
        midtop, midleft, midbottom, midright,
        center, centerx, centery,
        size, width, height

    Except the last three ones, 'size', 'width' and 'height' any of those
    can be assigned similarily to the pygame.Rect:

    widget.top = 10
    widget.center = (10, 10)
    ...

    Note: This will only work for toplevel widgets as widgets are placed
    relative to their parent. Thus the 'top' attribute value of a
    widget, which is packed into another one, refers to its parents
    coordinates. So if it is placed four pixels to the left on its
    parent, its 'top' value will be 4, while the parent might be placed
    at e.g. 100, 100.
    You can get the absolute coordinates, the widget is placed on the
    display, by using the rect_to_client() method.
    
    To get the actual dimensions of the widget, it provides the
    read-only 'width', 'height' and 'size' attributes.

    if (widget.width > 50) or (widget.height > 50):
        ...
    if widget.size == (50, 50):
        ...

    To force a specific minimum size to occupy by the widget, the
    'minsize' attribute or the respective set_minimum_size() method can
    be used. The occupied area of the widget will not be smaller than
    the size, but can grow bigger.

    widget.minsize = 100, 50
    widget.set_minimum_size (10, 33)

    The counterpart of 'minsize' is the 'maxsize' attribute, which
    defines the maximum size, the widget can grow to. It will never
    exceed that size.

    widget.maxsize = 200, 200
    wdget.set_maximum_size (100, 22)

    The 'image' and 'rect' attributes are used and needed by the
    pygame.sprite system. 'image' refers to the visible surface of the
    widget, which will be blitted on the display. 'rect' is a copy of
    the pygame.Rect object indicating the occupied area of the
    widget. The rect denotes the relative position of the widget on its
    parent (as explained above).

    The 'index' attribute and set_index() method set the navigation
    index position for the widget. It is highly recommended to set this
    value in order to provide a better accessibility (e.g. for keyboard
    navigation). The attribute can be used in ocempgui.access.IIndexable
    implementations for example.

    widget.index = 3
    widget.set_index (0)

    Widgets support a 'style' attribute and create_style() method, which
    enable them to use different look than default one without the need
    to override their draw() method. The 'style' attribute of a widget
    usually defaults to a None value and can be set using the
    create_style() method. This causes the widget internals to setup the
    specific style for the widget and can be accessed through the
    'style' attribute later on. A detailled documentation of the style
    can be found in the Style class.

    if not widget.style:
        widget.create_style () # Setup the style internals first.
    widget.style['font']['size'] = 18
    widget.create_style ()['font']['name'] = Arial

    Widgets can be in different states, which cause the widgets to have
    a certain behaviour and/or look. Dependant on the widget, the
    actions it supports and actions, which have taken place, the state
    of the widget can change. The actual state of the widget can be
    looked up via the 'state' attribute and is one of the STATE_TYPES
    constants.

    if widget.state == STATE_INSENSITIVE:
        print 'The widget is currently insensitive and does not react.'

    Any widget supports layered drawing through the 'depth' attribute.
    The higher the depth is, the higher the layer on the z-axis will be,
    on which the widget will be drawn. Widgets might use the flag to set
    themselves on top or bottom of the display.

    # The widget will be placed upon all widgets with a depth lower than 4.
    widget.depth = 4
    widget.set_depth (4)
    
    Widgets should set the 'dirty' attribute to True, whenever an update
    of the widget surface is necessary, which includes redrawing the
    widget (resp. calling draw_bg() and draw()). In user code, 'dirty'
    usually does not need to be modified manually, but for own widget
    implementations it is necessary (e.g. if a Label text changed).
    If the 'parent' attribute of the widget is set, the parent will be
    notified automatically, that it has to update portions of its
    surface.

    # Force redrawing the widget on the next update cycle of the render
    # group.
    widget.dirty = True

    Widgets support a focus mode, which denotes that the widget has the
    current input and action focus. Setting the focus can be done via
    the 'focus' attribute or the set_focus() method.

    widget.focus = True
    widget.set_focus (True)

    'sensitive' is an attribute, which can block the widget's reaction
    upon events temporarily. It also influences the look of the widget
    by using other style values (see STATE_INSENSITIVE in the Style
    class).

    widget.sensitive = False
    widget.set_sensitive (False)

    Each widget supports transparency, which also includes all children
    which are drawn on it. By setting the 'opacity' attribute you can
    adjust the degree of transparency of the widget. The allowed values
    are ranged between 0 for fully transparent and 255 for fully opaque.

    widget.opacity = 100
    widget.set_opacity (25)

    Widgets allow parent-child relationships via the 'parent' attribute.
    Parental relationships are useful for container classes, which can
    contain widgets and need to be informed, when the widget is
    destroyed, for example. Take a look the Bin and Container classes
    for details about possible implementations.
    Do NOT modify the 'parent' attribute value, if you do not know, what
    might happen.

    Widgets support locking themselves self temporarily using the lock()
    method. This is extremely useful to avoid multiple update/draw
    calls, when certain operations take place on it. To unlock the
    widget, the unlock() method should be called, which causes it to
    update itself instantly.

    widget.lock ()            # Acquire lock.
    widget.focus = False      # Normally update() would be called here.
    widget.sensitive = False  # Normally update() would be called here.
    widget.unlock ()          # Release lock and call update().

    When using the lock() method in your own code, you have to ensure,
    that you unlock() the widget as soon as you do not need the lock
    anymore. The state of the lock on a widget can be queried using the
    'locked' attribute:

    if widget.locked:
        print 'The widget is currently locked'

    Widgets can consist of other widgets. To guarantee that all of them
    will be added to the same event management system, set the same
    state, etc., the 'controls' attribute exists. It is a collection to
    and from which widgets can be attached or detached. Several methods
    make use of this attribute by iterating over the attached widgets
    and invoking their methods to put them into the same state, etc. as
    the main widget.

    widget.controls.append (sub_widget)
    for sub in widget.controls:
        ...

    Default action (invoked by activate()):
    None, will raise an NotImplementedError

    Mnemonic action (invoked by activate_mnemonic()):
    None

    Signals:
    SIG_FOCUSED   - Invoked, when the widget received the focus
                    (widget.focus=True).
    SIG_ENTER     - Invoked, when the input device enters the widget.
    SIG_LEAVE     - Invoked, when the input device leaves the wigdet.
    SIG_DESTROYED - Invoked, when the widget is destroyed.

    Attributes:
    minsize   - Guaranteed size of the widget.
    maxsize   - Counterpart to size and denotes the maximum size the widget.
                is allowed to occupy. Defaults to None usually.
    image     - The visible surface of the widget.
    index     - Navigation index of the widget.
    style     - The style to use for drawing the widget.
    state     - The current state of the widget.
    depth     - The z-axis layer depth of the widget.
    dirty     - Indicates, that the widget needs to be updated.
    focus     - Indicates, that the widget has the current input focus.
    sensitive - Indicates, if the user can interact with the widget.
    parent    - Slot for the creation of parent-child relationships.
    controls  - Collection of attached controls for complex widgets.
    tooltip   - The tool tip text to display for the widget.
    opacity   - The degree of transparency to apply (0-255, 0 for fully
                transparent, 255 for fully opaque).
    indexable - The ocempgui.access.IIndexable implementation to use for
                the 'index' attribute support.
    entered   - Indicates, that an input device is currently over the widget
                (e.g. the mouse cursor).
    locked    - Indicates, whether the widget is locked.
    rect      - The area occupied by the widget.
    x, y, ... - The widget allows to reposition itself through the various
    width, ...  attributes offered by its rect attribute.
    size       
    """
    def __init__ (self):
        BaseObject.__init__ (self)
        sprite.Sprite.__init__ (self)

        # Guaranteed sizes for the widget, see also the minsize/maxsize
        # attributes and set_*_size () methods.
        self._minwidth = 0
        self._minheight = 0
        self._maxwidth = 0
        self._maxheight = 0

        self._indexable = None
        
        self._image = None
        self._rect = Rect (0, 0, 0, 0)
        self._oldrect = Rect (0, 0, 0, 0)

        self._opacity = 255
        self._style = None
        self._index = 0
        self._state = STATE_NORMAL
        self._focus = False
        self._entered = False
        self._sensitive = True

        self._controls = []
        self._depth = 0
        self._dirty = True
        self._lock = 0

        self._bg = None

        self.parent = None
        
        # Accessibility.
        self._tooltip = None
        
        # Signals, the widget listens to by default
        self._signals[SIG_FOCUSED] = []
        self._signals[SIG_ENTER] = []
        self._signals[SIG_LEAVE] = []
        self._signals[SIG_DESTROYED] = []

    def _get_rect_attr (self, attr):
        """W._get_rect_attr (...) -> var

        Gets the wanted attribute value from the underlying rect.
        """
        return getattr (self._rect, attr)

    def _set_rect_attr (self, attr, value):
        """W._set_rect_attr (...) -> None

        Sets a specific attribute value on the underlying rect.

        Raises an AttributeError if the attr argument is the width,
        height or size.
        """
        if attr in ("width", "height", "size"):
            # The width and height are protected!
            raise AttributeError ("%s attribute is read-only" % attr)

        # TODO: This is just a hack around wrong positioning in
        # containers.
        self._oldrect = self.rect
        setattr (self._rect, attr, value)
        if (self.parent != None):
            if not isinstance (self.parent, BaseWidget):
                self.update ()
            else:
                self._oldrect = self.rect

    def initclass (cls):
        """B.initclass () -> None

        Class method to expose the attributes of the own self.rect attribute.

        The method usually is called in the __init__.py script of the
        module.
        """
        attributes = dir (Rect)
        for attr in attributes:
            if not attr.startswith ("__") and \
                   not callable (getattr (Rect, attr)):
                def get_attr (self, attr=attr):
                    return cls._get_rect_attr (self, attr)
                def set_attr (self, value, attr=attr):
                    return cls._set_rect_attr (self, attr, value)
                prop = property (get_attr, set_attr)
                setattr (cls, attr, prop)
    initclass = classmethod (initclass)
    
    def _get_rect (self):
        """W._get_rect () -> pygame.Rect

        Gets a copy of the widget's rect.
        """
        return Rect (self._rect)

    # DEPRECATED
    def set_position (self, x, y):
        """W.set_position (...) -> None

        DEPRECATED - use the 'topleft' attribute instead
        """
        print "*** Warning: set_position() is deprecated, use the topleft"
        print "             attribute instead."
        self._set_rect_attr ("topleft", (x, y))

    def rect_to_client (self, rect=None):
        """W.rect_to_client (...) -> pygame.Rect

        Returns the absolute coordinates a rect is located at.

        In contrast to the widget.rect attribute, which denotes the
        relative position and size of the widget on its parent, this
        method returns the absolute position and occupied size on the
        screen for a passed rect.

        Usually this method will be called by children of the callee and
        the callee itself to detrmine their absolute positions on the
        screen.
        """
        if self.parent and isinstance (self.parent, BaseWidget):
            re = self.rect
            if rect != None:
                re.x += rect.x
                re.y += rect.y
                re.width = rect.width
                re.height = rect.height
            return self.parent.rect_to_client (re)
        
        elif rect != None:
            rect.x = self.x + rect.x
            rect.y = self.y + rect.y
            return rect
        return self.rect
    
    def set_minimum_size (self, width, height):
        """W.set_minimum_size (...) -> None

        Sets the minimum size to occupy for the widget.

        Minimum size means that the widget can exceed the size by any
        time, but its width and height will never be smaller than these
        values.

        Raises a TypeError, if the passed arguments are not integers.
        Raises a ValueError, if the passed arguments are not positive.
        """
        if (type (width) != int) or (type (height) != int):
            raise TypeError ("width and height must be positive integers")
        if (width < 0) or (height < 0):
            raise ValueError ("width and height must be positive integers")
        self._minwidth = width
        self._minheight = height
        self.dirty = True

    # DEPRECATED
    def set_size (self, width, height):
        """W.set_size (...) -> None

        DEPREACATED - use set_minimum_size () instead.
        """
        print "*** Warning: set_size() is deprecated, use set_minimum_size()."
        self.set_minimum_size (width, height)

    def set_maximum_size (self, width, height):
        """W.set_maximum_size (...) -> None

        Sets the maximum size the widget is allowed to occupy.

        This is the counterpart to the set_minimum_size() method.
        """
        if (type (width) != int) or (type (height) != int):
            raise TypeError ("width and height must be positive integers")
        if (width < 0) or (height < 0):
            raise ValueError ("width and height must be positive integers")
        self._maxwidth = width
        self._maxheight = height
        self.dirty = True

    def check_sizes (self, width, height):
        """W.check_sizes (...) -> int, int

        Checks the passed width and height for allowed values.

        Checks, whether the passed width an height match the upper and
        lower size ranges of the widget and returns corrected values, if
        they exceed those. Else the same values are returned.
        """
        minwidth, minheight = self.minsize
        maxwidth, maxheight = self.maxsize
        
        if (minwidth != 0) and (width < minwidth):
            width = minwidth
        elif (maxwidth != 0) and (width > maxwidth):
            width = maxwidth
        
        if (minheight != 0) and (height < minheight):
            height = minheight
        elif (maxheight != 0) and (height > maxheight):
            height = maxheight

        return width, height

    def set_index (self, index):
        """W.set_index (...) -> None
        
        Sets the tab index of the widget.

        Sets the index position of the widget to the given value. It can
        be used by ocempgui.access.IIndexable implementations to allow
        easy navigation access and activation for the widgets.

        Raises a TypeError, if the passed argument is not a positive
        integer.
        """
        if (type (index) != int) or (index < 0):
            raise TypeError ("index must be a positive integer")
        self._index = index

    def set_depth (self, depth):
        """W.set_depth (...) -> None

        Sets the z-axis layer depth for the widget.

        Sets the z-axis layer depth for the widget. This will need a
        renderer, which makes use of layers such as the Renderer
        class. By default, the higher the depth value, the higher the
        drawing layer of the widget is. That means, that a widget with a
        depth of 1 is placed upon widgets with a depth of 0.

        Raises a TypeError, if the passed argument is not an integer.
        """
        if type (depth) != int:
            raise TypeError ("depth must be an integer")

        self.lock ()

        old = self._depth
        self._depth = depth

        if isinstance (self.parent, BaseWidget):
            try:
                self.parent.update_layer (old, self)
            except: pass
        for c in self._controls:
            c.set_depth (depth)
        self.unlock ()

    def set_dirty (self, dirty, update=True):
        """W.set_dirty (...) -> None

        Marks the widget as dirty.

        Marks the widget as dirty, so that it will be updated and
        redrawn.
        """
        self._dirty = dirty
        if dirty and update:
            self.update ()

    def set_event_manager (self, manager):
        """W.set_event_manager (...) -> None

        Sets the event manager of the widget and its controls.

        Adds the widget to an event manager and causes its controls to
        be added to the same, too.
        """
        BaseObject.set_event_manager (self, manager)
        for control in self.controls:
            control.set_event_manager (manager)

    def set_indexable (self, indexable):
        """W.set_indexable (...) -> None

        Sets the IIndexable for the widget.

        The widget will invoke the add_index() method for itself on the
        IIndexable.
        """
        if indexable and not isinstance (indexable, IIndexable):
            raise TypeError ("indexable must inherit from IIndexable")
        if self._indexable == indexable:
            return

        if self._indexable != None:
            self._indexable.remove_index (self)

        self._indexable = indexable
        if indexable != None:
            indexable.add_index (self)

        for ctrl in self.controls:
            ctrl.set_indexable (indexable)

    # DEPRECATED
    def get_style (self):
        """W.get_style () -> WidgetStyle

        DEPRECATED - use the create_style() method instead
        """
        print "*** Warning: get_style() is deprecated, use the create_style()"
        print "             method instead."
        return self.create_style ()
    
    def create_style (self):
        """W.create_style () -> WidgetStyle
        
        Creates the instance-specific style for the widget.

        Gets the style associated with the widget. If the widget had no
        style before, a new one will be created for it, based on the
        class name of the widget. The style will be copied internally
        and associated with the widget, so that modifications on it will
        be instance specific.
        
        More information about how a style looks like and how to modify
        them can be found in the Style class documentation.
        """
        if not self._style:
            # Create a new style from the base style class.
            self._style = base.GlobalStyle.copy_style (self.__class__)
            self._style.set_value_changed (lambda: self.set_dirty (True))
        return self._style

    def set_style (self, style):
        """W.set_style (...) -> None

        Sets the style of the widget.

        Sets the style of the widget to the passed style dictionary.
        This method currently does not perform any checks, whether the
        passed dictionary matches the criteria of the Style class.

        Raises a TypeError, if the passed argument is not a WidgetStyle
        object.
        """
        if not isinstance (style, WidgetStyle):
            raise TypeError ("style must be a WidgetStyle")
        self._style = style
        if not self._style.get_value_changed ():
            self._style.set_value_changed (lambda: self.set_dirty (True))
        self.dirty = True
    
    def set_focus (self, focus=True):
        """W.set_focus (...) -> bool

        Sets the input and action focus of the widget.
        
        Sets the input and action focus of the widget and returns True
        upon success or False, if the focus could not be set.
        """
        if not self.sensitive:
            return False
        if focus:
            if not self._focus:
                self._focus = True
                self.emit (SIG_FOCUSED, self)
                self.dirty = True
                self.run_signal_handlers (SIG_FOCUSED)
        else:
            if self._focus:
                self._focus = False
                self.dirty = True
        return True

    def set_entered (self, entered):
        """W.set_entered (...) -> None

        Sets the widget into an entered mode.
        """
        if entered:
            if not self._entered:
                self._entered = True
                self.state = STATE_ENTERED
                self.emit (SIG_ENTER, self)
                self.run_signal_handlers (SIG_ENTER)
        elif self._entered:
            self._entered = False
            self.state = STATE_NORMAL
            self.run_signal_handlers (SIG_LEAVE)

    def set_sensitive (self, sensitive=True):
        """W.set_sensitive (...) -> None

        Sets the sensitivity of the widget.

        In a sensitive state (the default), widgets can react upon user
        interaction while they will not do so in an insensitive
        state.
        
        To support the visibility of this, the widget style should
        support the STATE_INSENSITIVE flag, while inheriting widgets
        should check for the sensitivity to enable or disable the event
        mechanisms.
        """
        if sensitive != self._sensitive:
            if sensitive:
                self._sensitive = True
                self.state = STATE_NORMAL
            else:
                self._sensitive = False
                self.state = STATE_INSENSITIVE
        for control in self.controls:
            control.set_sensitive (sensitive)

    def set_state (self, state):
        """W.set_state (...) -> None

        Sets the state of the widget.

        Sets the state of the widget. The state of the widget is mainly
        used for the visible or non-visible appearance of the widget,
        so that the user can determine the state of the widget
        easier.
        Usually this method should not be invoked by user code.

        Raises a ValueError, if the passed argument is not a value of
        the STATE_TYPES tuple.
        """
        if state not in STATE_TYPES:
            raise ValueError ("state must be a value from STATE_TYPES")
        if self._state != state:
            self._state = state
            self.dirty = True

    def set_opacity (self, opacity):
        """W.set_opacity (...) -> None

        Sets the opacity of the widget.
        """
        if type (opacity) != int:
            raise TypeError ("opacity must be an integer")
        dirty = self._opacity != opacity
        self._opacity = opacity
        self.update ()
        
    # DEPRECATED
    def set_event_area (self, area):
        """W.set_event_area (...) -> None

        DEPRECATED - this is no longer used.
        """
        print "*** Warning: set_event_area() is no longer used!"

    def lock (self):
        """W.lock () -> None

        Acquires a lock on the Widget to suspend its updating methods.
        """
        self._lock += 1
    
    def unlock (self):
        """W.unlock () -> None

        Releases a previously set lock on the Widget and updates it
        instantly.
        """
        if self._lock > 0:
            self._lock -= 1
        if self._lock == 0:
            self.update ()

    def set_tooltip (self, tooltip):
        """W.set_tooltip (...) -> None

        Sets the tooltip information for the widget.

        Raises a TypeError, if the passed argument is not a string or
        unicode.
        """
        if type (tooltip) not in (str, unicode):
            raise TypeError ("text must be a string or unicode")
        self._tooltip = tooltip
    
    def activate (self):
        """W.activate () -> None

        Activates the widget.

        Activates the widget, which means, that the default action of
        the widget will be invoked.

        This method should be implemented by inherited widgets.
        """
        raise NotImplementedError

    def activate_mnemonic (self, mnemonic):
        """W.activate_mnemonic (...) -> bool

        Activates the widget through the set mnemonic.

        Activates the widget through the set mnemonic for it and returns
        True upon successful activation or False, if the widget was not
        activated.

        The BaseWidget.activate_mnemonic () method always returns False
        by default, so that this method should be implemented by
        inherited widgets, if they need explicit mnemonic support.
        """
        return False

    def draw_bg (self):
        """W.draw_bg () -> Surface

        Draws the widget background surface and returns it.

        Creates the visible background surface of the widget and returns
        it to the caller.
        
        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError

    def draw (self):
        """W.draw () -> None

        Draws the widget surface.

        Creates the visible surface of the widget and updates its
        internals.
        """
        # Original surface.
        self._bg = self.draw_bg ()
        try:
            self._bg = self._bg.convert ()
        except PygameError: pass
        
        rect = self._bg.get_rect ()
        
        # Current surface for blits.
        self._image = Surface ((rect.width, rect.height))
        self._image.blit (self._bg, (0, 0))
        topleft = self._rect.topleft
        self._rect = rect
        self._rect.topleft = topleft
        self._oldrect = self.rect

    def notify (self, event):
        """W.notify (...) -> None

        Notifies the widget about an event.

        Note: Widgets, which are not visible (not shown) or are in a
        specific state (e.g. STATE_INSENSITIVE), usually do not receive
        any events. But dependant on the widget, this behaviour can be
        different, thus checking the visibility depends on the widget
        and implementation.
        """
        if not self.sensitive:
            return
        
        if (event.signal == SIG_FOCUSED) and (event.data != self):
            self.focus = False
        elif (event.signal == SIG_ENTER) and (event.data != self):
            self.entered = False

    def update (self, **kwargs):
        """W.update (...) -> None

        Updates the widget.

        Updates the widget and causes its parent to update itself on
        demand.
        """
        if self.locked:
            return

        oldrect = Rect (self._oldrect)
        resize = kwargs.get ("resize", False)

        if not self.dirty:
            children = kwargs.get ("children", {})
            blit = self.image.blit
            items = children.items ()

            # Clean up the dirty areas on the widget.
            for child, rect in items:
                blit (self._bg, rect, rect)
            # Blit the changes.
            for child, rect in items:
                blit (child.image, child.rect)

            self._image.set_alpha (self.opacity)
            # If a parent's available, reassign the child rects, so that
            # they point to the absolute position on the widget and build
            # one matching them all for an update.
            if self.parent:
                vals = children.values ()
                rect = oldrect
                if len (vals) != 0:
                    rect = vals[0]
                    x = self.x
                    y = self.y
                    for r in vals:
                        r.x += x
                        r.y += y
                    rect.unionall (vals[1:])
                self.parent.update (children={ self : rect }, resize=resize)
            self._lock = max (self._lock - 1, 0)
            return

        # Acquire lock to prevent recursion on drawing.
        self._lock += 1

        # Draw the widget.
        self.draw ()
        self._image.set_alpha (self.opacity)
        if self.parent != None:
            resize = oldrect != self._rect
            self.parent.update (children={ self : oldrect }, resize=resize)

        # Release previously set lock.
        self._lock = max (self._lock - 1, 0)
        self.dirty = False

    def destroy (self):
        """W.destroy () -> None

        Destroys the widget and removes it from its event system.

        Causes the widget to destroy itself as well as its controls and
        removes all from the connected event manager and sprite groups
        using the sprite.kill() method.
        """
        if isinstance (self.parent, BaseWidget):
            raise AttributeError ("widget still has a parent relationship")
        self.run_signal_handlers (SIG_DESTROYED)
        self.emit (SIG_DESTROYED, self)

        # Clear the associated controls.
        _pop = self._controls.pop
        while len (self._controls) > 0:
            control = _pop ()
            control.parent = None
            control.destroy ()
            del control
        del self._controls

        if self._indexable != None:
            index = self._indexable
            self._indexable = None
            index.remove_index (self)
        if self._manager != None:
            self._manager.remove_object (self)
        
        BaseObject.destroy (self) # Clear BaseObject internals.
        self.kill ()              # Clear Sprite
        #del self.parent
        del self._indexable
        del self._bg
        del self._style
        del self._image
        del self._rect
        del self._oldrect
        del self


    # DEPRECATED
    position = property (lambda self: self.topleft,
                         lambda self, (x, y): self.set_position (x, y),
                         doc = "The position of the topleft corner.")
    eventarea = property (lambda self: self.rect_to_client (),
                          lambda self, var: self.set_event_area (var),
                          doc = "The area, which gets the events.")

    minsize = property (lambda self: (self._minwidth, self._minheight),
                     lambda self, (w, h): self.set_minimum_size (w, h),
                     doc = "The guaranteed size of the widget.")
    maxsize = property (lambda self: (self._maxwidth, self._maxheight),
                        lambda self, (w, h): self.set_maximum_size (w, h),
                        doc = "The maximum size to occupy by the widget.")
    image = property (lambda self: self._image,
                      doc = "The visible surface of the widget.")
    rect = property (lambda self: self._get_rect (),
                     doc = "The area occupied by the widget.")
    index = property (lambda self: self._index,
                      lambda self, var: self.set_index (var),
                      doc = "The tab index position of the widget.")
    style = property (lambda self: self._style,
                      lambda self, var: self.set_style (var),
                      doc = "The style of the widget.")
    state = property (lambda self: self._state,
                      lambda self, var: self.set_state (var),
                      doc = "The current state of the widget.")
    focus = property (lambda self: self._focus,
                      lambda self, var: self.set_focus (var),
                      doc = "The focus of the widget.")
    sensitive = property (lambda self: self._sensitive,
                          lambda self, var: self.set_sensitive (var),
                          doc = "The sensitivity of the widget.")
    dirty = property (lambda self: self._dirty,
                      lambda self, var: self.set_dirty (var),
                      doc = """Indicates, whether the widget need to be
                      redrawn.""")
    controls = property (lambda self: self._controls,
                         doc = "Widgets associated with the widget.")
    depth = property (lambda self: self._depth,
                      lambda self, var: self.set_depth (var),
                      doc = "The z-axis layer depth of the widget.")
    tooltip = property (lambda self: self._tooltip,
                        lambda self, var: self.set_tooltip (var),
                        doc = "The tool tip text to display for the widget.")
    locked = property (lambda self: self._lock > 0,
                       doc = "Indicates, whether the widget is locked.")
    indexable = property (lambda self: self._indexable,
                          lambda self, var: self.set_indexable (var),
                          doc = "The IIndexable, the widget is attached to.")
    entered = property (lambda self: self._entered,
                        lambda self, var: self.set_entered (var),
                        doc = "Indicates, whether the widget is entered.")
    opacity = property (lambda self: self._opacity,
                        lambda self, var: self.set_opacity (var),
                        doc = "The opacity of the widget.")
