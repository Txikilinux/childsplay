# $Id: Renderer.py,v 1.61.2.25 2007/03/23 06:02:21 marcusva Exp $
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

"""A specialized event manager and render group class for widgets."""

from pygame import display, Surface, event, QUIT, VIDEORESIZE, KMOD_SHIFT
from pygame import K_TAB, KMOD_LALT, KMOD_RALT, KMOD_ALT, KMOD_CTRL, KMOD_RCTRL
from pygame import KMOD_LCTRL, KMOD_RSHIFT, KMOD_LSHIFT, KEYUP, KEYDOWN, mouse
from pygame import error as PygameError, time as PygameTime, Rect
from childsplay_sp.ocempgui.events import EventManager, Event
from childsplay_sp.ocempgui.access import IIndexable
from childsplay_sp.ocempgui.draw import Complex, String
from BaseWidget import BaseWidget
from Constants import *
import base

class _LayerEventManager (EventManager):
    """_LayerEventManager (renderer) -> _LayerEventManager

    An event manager, that supports the layer system of the Renderer.
    """
    def __init__ (self, renderer, layer):
        EventManager.__init__ (self)

        if not isinstance (renderer, Renderer):
            raise TypeError ("renderer must inherit from Renderer")
        self._renderer = renderer

        if type (layer) != int:
            raise TypeError ("layer must be an integer")
        self._layer = layer
    
    def emit_event (self, event):
        """L.emit_event (...) -> None

        Emits an event, which will be sent to the objects.

        Emits an event on a specific queue of the _LayerEventManager,
        which will be sent to the objects in that queue. If one of the
        receiving objects sets the 'handled' attribute of the event to
        True, the emission will stop immediately so that following
        objects will not receive the event.  The method also will send
        specific events such as the SIG_FOCUSED event to _all_ event
        managers attched to the renderer.
        """
        if event.signal == SIG_FOCUSED:
            re = self._renderer
            if isinstance (event.data, BaseWidget) and event.data.focus:
                re.active_layer = re._layers[event.data.depth]
                re._index_widget = event.data

            layers = re._layers.keys ()
            for layer in layers:
                manager = re._layers.get (layer, (None, None, None))[2]
                if manager:
                    if manager.event_grabber:
                        manager.event_grabber.notify (event)
                        return
                    evlist = manager.queues.get (event.signal, [])
                    for obj in evlist:
                        obj.notify (event)
                        if event.handled:
                            break
        
        elif event.signal == SIG_DESTROYED:
            self._renderer.remove_widget (event.data)
        else:
            if self.event_grabber:
                self.event_grabber.notify (event)
                return
            evlist = self.queues.get (event.signal, [])
            for obj in evlist:
                obj.notify (event)
                if event.handled:
                    break

    def emit_all (self, event):
        """L.emit_all (...) -> None

        Emits the passed event on all objects.
        """
        evlist = self.queues.get (event.signal, [])
        for obj in evlist:
            obj.notify (event)
    
    def remove_object (self, obj, *signals):
        """L.remove_object (...) -> None

        Removes an object from the LayerEventManager.

        Removes the object from the queues passed as the 'signals'
        arguments. If 'signals' is None, the object will be removed
        from all queues of the EventManager.
        """
        EventManager.remove_object (self, obj, *signals)
        if len (self) == 0:
            self._renderer._destroy_layer (self._layer)

    def grab_events (self, obj):
        """L.grab_events (...) -> None

        Sets an event grabber object for the LayerEventManager.

        Overrides the EventManager.grab_events() method and causes the
        Renderer, this manager is set for to send all events to distribute
        only to this instance.
        """
        EventManager.grab_events (self, obj)
        if self.event_grabber:
            self._renderer._set_grab (self)
        else:
            self._renderer._set_grab (None)

    layer = property (lambda self: self._layer,
                      doc = "The layer id, the event manager operates on.")

class Renderer (IIndexable):
    """Renderer () -> Renderer

    A render engine, which can deal with events and sprites.

    The Renderer class incorporates an event management system based on
    the EventManager class from the ocempgui.events module and can
    render widgets based on the BaseWidget class. It contains several
    attributes and methods to create and manipulate a pygame window as
    well as interfaces to support a higher range of accessibility
    features such as keyboard navigation by implementing the IIndexable
    interfaces.

    The Renderer class can be used as standalone render engine and event
    loop for a pygame application or be integrated in an existing loop
    easily (which is exaplained below).

    The 'title' attribute and set_title() method will set the caption
    title of the pygame window. This works independant of if the
    Renderer works in a standalon or integrated mode.

    renderer.title = 'My title'
    renderer.set_title ('Another title')

    The 'screen' attribute and set_screen() method allow you to set up
    the background surface the Renderer shall use for blitting
    operations. This can be especially useful, if only portions of the
    complete visible screen contain elements, which should be handled by
    the Renderer and/or if the Renderer is not used as standalone render
    engine. If you instead want to use the Renderer as standalone, the
    create_screen() method should be used to create the pygame window
    with the desired size.

    # Screen already exists:
    renderer.screen = mainscreen
    renderer.set_screen (own_screen_portion)

    # Renderer will be used as standalone render engine with a pygame
    # window of 800x600 size.
    renderer.create_screen (800, 600)

    When using only a part of the screen it is important to adjust the
    Renderer's position, too, so that events, which require positional
    arguments (such as mouse movements, etc), can be translated
    correctly. This means, that when the Renderer's screen is blit a
    certain offset (x, y), its topleft position should be set to (x, y)
    as well:

    mainsurface.blit (renderer.screen, (10, 10))
    renderer.topleft = 10, 10

    As the Renderer exposes the attributes of its bound 'rect' attribute
    you can use the following attributes directly to modify its position:

        top, left, bottom, right,
        topleft, bottomleft, topright, bottomright,
        midtop, midleft, midbottom, midright,
        center, centerx, centery,
        size, width, height

    This however will NOT move the bound screen of the Renderer around.
    
    If the create_creen() method is used, resizing events will be
    recognized and resize the display accordingly. The 'support_resize'
    attribute and set_support_resize() method can influence this
    behaviour. It will be necessary to create the screen with the
    pygame.RESIZEABLE flag enabled in order to retrieve resizing events.
    'support_resize' will be automatically enabled anyways, if
    create_screen() is used.

    # Create a resizeable window - no need to set support_resize.
    renderer.create_screen (200, 200, pygame.RESIZEABLE)

    # Enable resizing support, if the screen is assigned manually.
    renderer.support_resize = True
    renderer.set_support_resize (True)
    
    It is possible to set the background color of the set screen by
    adjusting the 'color' attribute or set_color() method. By default it
    uses a clear white color with the RBG value (255, 255, 255). It is
    possible to change that value by any time. It will be applied
    instantly.

    renderer.color = (255, 0, 0)
    renderer.set_color (100, 220, 100)

    The Renderer supports an update timer value (~ FPS setting), which
    defaults to 40. That means, that the timer will cause the default
    event system to poll events 40 times a second, which is a good value
    for most cases. On demand it can be adjusted using the 'timer'
    attribute or set_timer() method. Be careful with it. Higher values
    will cause higher CPU load.

    renderer.timer = 20
    renderer.set_timer (100)

    It also supports different polling modes for events. The first
    polling mode relies on the timer value while the second uses an
    event based polling system. This means, that the second mode will
    completely ignore the timer value and instead wait for events to
    occur on the event queue. While the first mode is suitable for most
    FPS based applications and games, the latter one suits perfectly for
    event based ones.

    Note however, that the events to occur _MUST_ occur on the pygame
    event queue, not on those of the different EventManagers!

    The mode can be chosen by passing the Renderer.start() method an
    optional boolean argument, that determins, which mode should be
    used. True indicates the event based loop, False (the default)
    indicates the timer based loop.

    renderer.start ()      # Use the timer based polling.
    renderer.start (False) # Use the timer based polling.
    renderer.start (True)  # Use the event based polling.

    The Renderer supports temporary locking the update routines by using
    the lock() and unlock() methods. Each lock() call however has to
    be followed by a call to unlock(). You can check whether the Renderer
    is currently locked by using its 'locked' attribute.

    renderer.lock () # Note that an unlock() has to follow.
    if renderer.locked:
        print 'The Renderer is currently locked'
    renderer.unlock ()

    To speed up the mouse interaction behaviour, you can adjust the
    amount of mouse motion events to drop on each update the Renderer
    performs. This usually increases the overall speed while decreasing
    the exactness of mouse position related actions. You can adjust the
    amount of mouse motion events to drop using the 'drops' attribute and
    set_drops() method.

    renderer.drops = 10 # Drop each 10th mouse motion event on updates.
    renderer.set_drops (5)

    Keyboard navigation
    -------------------
    The Renderer class implements keyboard navigation through the
    ocempgui.access.IIndexable interface class. It uses the TAB key for
    switching between attached objects of the currently active layer.
    Objects can be attached and removed using the add_index() and
    remove_index() method and will be automatically put into the
    correct layer (Note: objects inheriting from the BaseWidget class
    will do that automatically by default). Switching is done via
    the switch_index() method, which will be activated automatically by
    sending a KEYDOWN event with the TAB key as value.

    Objects which should be added to the navigation indexing, need to
    have a 'index' and 'sensitive' attribute and a set_focus() method,
    which receives a bool value as argument and returns True on
    successfully setting the focus or False otherwise. In case that
    False will be returned the method will try to set the focus on the
    next object.

    The index is needed for the order the objects shall be navigated
    through. Objects with a lower index will be focused earlier than
    objects with a higher index. If multiple objects with the same index
    are added, it cannot be guaranteed in which order they are
    activated.

    The active layer can be switched using the switch_layer() method,
    which will be activated automatically by sending a KEYDOWN event
    with the TAB key as value and CTRL as modifier. More information
    about the layer system can be found in the 'Layer system' section
    beneath.

    The Renderer supports automatic cycling through the objects and
    layers, which means, that if the end of the index list or layer list
    is reached it will start from the beginning of the respective list.

    Mnemonic support
    ----------------
    The Renderer supports mnemonic keys (also known as hotkeys) for
    object activation through the <ALT><Key> combination. If it receives
    a KEYDOWN event, in which the ALT modifier is set, it will not
    escalate the event to its children, but instead loop over its
    indexing list in order to activate a matching child.

    As stated in 'Keyboard Navigation' the objects need to have a
    'sensitive' attribute. Additionally they must have an
    activate_mnemonic() method, which receives a unicode as argument and
    returns True on successful mnemonic activation or False
    otherwise. If the widget's 'sensitive' attribute does not evaluate
    to True, the Renderer will not try to invoke the activate_mnemonic()
    method of the widget.

    Layer system
    ------------
    The Renderer contains full z-axis support by using different layers,
    in which widgets will be kept and drawn. A higher layer index will
    cause widgets to be drawn on top of others with a lower index.
    The layer, in which a widget will be put, can be adjusted using the
    'depth' attribute or set_depth() method of the BaseWidget class.
    
    Each layer stored in the Renderer is a tuple consisting of three
    values,
    
    * an index list, which keeps a list of indexable objects for that
      layer (see the section 'Keyboard navigation' above for more),
    * a widget list, which contains all the widgets and
    * a specialized EventManager subclass, that will deal with the
      events sent to the specific layer.
    
    The Renderer forwards received events to each layer starting
    with the currently active layer and then in order from the highest
    layer index (topmost layer) to the one with the lowest index
    (=lowest depth).
    The only exception from this behaviour is mouse input, which
    alaways will be sent in order from the highest layer index to the
    one with the lowest index.
    if the sent event is handled by any object within that particular
    layer and its 'handled' attribute is set to True, the event manager
    and Renderer will stop passing the event around, so that neither
    following widgets in that layer nor following layers will receive
    the event.

    Using the Renderer as standalone engine
    ---------------------------------------
    Using the Renderer as standalone engine is very simple. You usually
    have to type the following code to get it to work:

    renderer = Renderer ()
    renderer.create_screen (width, height, optional_flags)
    renderer.title = 'Window caption title'
    renderer.color = (100, 200, 100)
    ...
    re.start ()
    
    The first line will create a new Renderer object. The second creates
    a new pygame window with the passed width and height. The third and
    fourth line are not necessary, but useful and will set the window
    caption of the pygame window and the background color to use for the
    window.
    
    After those few steps you can add objects to the Renderer via the
    add_widget() method, use the inherited Group.add() method of the
    pygame.sprite system or the add_object() method from the inherited
    ocempgui.events.EventManager class.

    When you are done with that, an invocation of the start() method
    will run the event loop of the Renderer.

    Integrating the Renderer in an existing environment
    ---------------------------------------------------
    If an event loop and window already exists or an own event loop is
    necessary, the Renderer can be integrated into it with only a few
    lines of code. First you will need to set the screen, on which the
    Renderer should blit its objects:

    renderer = Renderer ()
    renderer.screen = your_main_screen_or_surface

    Note, that if the assigned scren is a surface, which will be blit at
    a certain position x, y (e.g. mainscreen.blit (renderer.screen, (10, 10)),
    the Renderer's screen offset values have to be adjusted, too:

    Renderer.topleft = 10, 10 # Set both, x and y offset.
    Renderer.x = 10           # Only x offset.
    Renderer.y = 10           # Only y offset.

    See above for the necessity of it.

    Then you can send the events processed in your event loop to the
    Renderer and its objects via the distribute_events() method:

    def your_loop ():
        ...
        renderer.distribute_events (received_events)
    
    Attributes:
    title           - The title caption to display on the pygame window.
    screen          - The surface to draw on.
    timer           - Speed of the event and update loop. Default is 40 fps.
    color           - The background color of the screen. Default is
                      (255, 255, 255).
    managers        - The EventManager objects of the different layers.
    active_layer    - The currently activated layer.
    show_layer_info - Indicates, whether the layer information should be
                      shown on the screen when the layer is switched.
    support_resize  - Indicates, whether resize events should be supported.
                      Default is False and automatically set to True,
                      if create_screen() is used.
    locked          - Indicates, whether the Renderer is locked.
    drops           - The mouse motion events to drop on each update.
    rect            - The area occupied by the Renderer.
    x, y, ...       - The Renderer allows to reposition itself through the
    width, ...        various attributes offered by its rect attribute.
    size       
    """
    def __init__ (self):
        IIndexable.__init__ (self)

        self._title = None
        self._screen = None
        self._color = None
        self._background = None

        # _layers is a dictionary consisting of keys, that mark the
        # depth of a widget and a tuple value, that consists an index
        # list as first and a widget list (for the updating routines) as
        # second entry.
        #
        # layers = self._layers[0] # Get the entries for depth 0.
        # indices = layers[0]
        # widgets = layers[1]
        #
        # The _active_layer variable marks the currently active layer
        self._layers = { 0 : ([], [], _LayerEventManager (self, 0)) }
        self._activelayer = self._layers[0]

        self.__layerinfo = None
        self._showlayerinfo = False

        # Grabbed event manager for modal dialog locks.
        self._grabber = None

        # The currently indexed widget, that has the input focus. This is
        # layer independant to guarantee, that multiple widgets cannot
        # receive the input focus at the same time.
        self._indexwidget = None

        # Timer value for the event system. 40 frames per second should
        # be enough as default.
        self._timer = 40

        # Tuple for double-click information. The tuple usually consists of:
        # self._mouseinfo[0] -> x coordinate of the mouse event pos.
        # self._mouseinfo[1] -> y coordinate of the mouse event pos.
        # self._mouseinfo[2] -> button id of the mouse event.
        # self._mouseinfo[3] -> tick amount since start.
        # See def _check_doubleclick () for details.
        self._mouseinfo = (0, 0, 0, 0)

        self.__updateevent = event.Event (SIG_UPDATED, data=self)

        # Indicates, the VIDEORESIZE events should be recognized.
        self._supportresize = False

        # Internal flags field for create_screen() calls, if
        # _supportresize is enabled.
        self.__flags = 0

        # Screen offsets for partial screen assignments (Renderer is bound
        # to a surface instead to the whole pygame window.
        self._rect = Rect (0, 0, 0, 0)

        # Locking system.
        self._lock = 0

        # The mouse motion events to drop on each update.
        self._drops = 0

    def _get_rect (self):
        """W._get_rect () -> pygame.Rect

        Gets a copy of the widget's rect.
        """
        return Rect (self._rect)

    def _get_rect_attr (self, attr):
        """R._get_rect_attr (...) -> var

        Gets the wanted attribute value from the underlying rect.
        """
        return getattr (self._rect, attr)

    def _set_rect_attr (self, attr, value):
        """R._set_rect_attr (...) -> None

        Sets a specific attribute value on the underlying rect.

        Raises an AttributeError if the attr argument is the width,
        height or size.
        """
        if attr in ("width", "height", "size"):
            # The width and height are protected!
            raise AttributeError ("%s attribute is read-only" % attr)
        setattr (self._rect, attr, value)

    def initclass (cls):
        """R.initclass () -> None

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

    def set_title (self, title):
        """R.set_title (...) -> None

        Sets the title to display on the pygame window.

        Raises a TypeError, if the passed argument is not a string or
        unicode.
        """
        if type (title) not in (str, unicode):
            raise TypeError ("title must be a string or unicode")
        self._title = title
        display.set_caption (self._title)
        
    def set_screen (self, screen, x=0, y=0):
        """R.set_screen (...) -> None

        Sets the screen to use for the Renderer and its widgets.

        Sets the screen surface, the renderer will draw the widgets on
        (usually, you want this to be the entire screen). The optional
        x and y arguments specify, where the screen will be blit on the
        pygame display (this is important for event handling).

        Raises a TypeError, if the passed argument does not inherit
        from pygame.Surface.
        """
        if screen and not isinstance (screen, Surface):
            raise TypeError ("screen must inherit from Surface")
        self._rect = screen.get_rect ()
        self.topleft = x, y
        self._screen = screen
        self._create_bg ()

        layers = filter (None, self._layers.values ())
        for layer in layers:
            layer[2].emit_all (Event (SIG_SCREENCHANGED, screen))
        self.refresh ()

    def set_timer (self, timer=40):
        """R.set_timer (...) -> None

        Sets the speed of the event and update loop for the Renderer.

        Sets the speed for the internal event and update loop of the
        renderer. The higher the value, the faster the loop will go,
        which can cause a higher CPU usage. As a rough rule of thumb the
        timer value can be seen as the frames per second (FPS) value. A
        good value (also the default) is around 40 (~40 FPS) for modern
        computers.

        Raises a TypeError, if the passed argument is not a positive
        integer.
        """
        if (type (timer) != int) or (timer <= 0):
            raise TypeError ("timer must be a positive integer > 0")
        self._timer = timer

    def set_show_layer_info (self, show):
        """R.set_show_layer_info (...) -> None

        Sets, whether the layer information should be shown or not.

        If set to true, the layer, which gets activated, will be shortly
        shown on the screen.
        """
        self._showlayerinfo = show
    
    def set_color (self, color):
        """R.set_color (...) -> None

        Sets the background color of the attached screen.
        """
        self._color = color
        if self.screen:
            self._create_bg ()
            self.refresh ()

    def set_support_resize (self, support):
        """R.set_support_resize (...) -> None

        Sets, whether resize event (VIDEORESIZE) should be supported.
        """
        self._supportresize = support

    def _create_bg (self):
        """R._create_bg () -> None

        Creates the background for refreshing the window.
        """
        if self.color != None:
            self.screen.fill (self.color)
        self._background = self.screen.copy ()
        
    def create_screen (self, width, height, flags=0, depth=0):
        """R.create_screen (...) -> None

        Creates a new pygame window for the renderer.

        Creates a new pygame window with the given width and height and
        associates its entire surface with the 'screen' attribute to
        draw on. The optional flags argument can contain additional
        flags as specified by pygame.display.set_mode().

        Raises a TypeError, if the passed arguments are not positive
        integers.
        Raises a ValueError, if the passed arguments are not positive
        integers greater than 0.
        """
        if (type (width) != int) or (type (height) != int):
            raise TypeError ("width and height must be positive integers > 0")
        if (width <= 0) or (height <= 0):
            raise ValueError ("width and height must be positive integers > 0")

        self.support_resize = False # Suspend VIDEORESIZE events.
        self.screen = display.set_mode ((width, height), flags, depth)
        self.support_resize = True # Enable VIDEORESIZE events.
        self.__flags = flags
        self.refresh ()
    
    def set_active_layer (self, layer):
        """R.set_active_layer (...) -> None

        Sets the currently active layer.

        Raises a TypeError, if the passed argument is not a valid
        layer index or key.
        """
        if type (layer) == int:
            lay = self._layers.get (layer)
            if lay:
                show = self._activelayer != layer
                self._activelayer = lay
                if show:
                    if self._showlayerinfo:
                        self._create_layer (layer)
                    self.switch_index ()
                return

        elif type (layer) == tuple:
            layers = self._layers.values ()
            if layer in layers:
                show = self._activelayer != layer
                self._activelayer = layer
                if show:
                    if self._showlayerinfo:
                        self._create_layer (layers.index (layer))
                    self.switch_index ()
                return

        # Cause an exception, if the layer does not exist
        raise TypeError ("layer must be a valid key or value")

    def set_drops (self, drops):
        """R.set_drops (...) -> None

        Sets the amount of mouse motion events to drop on each update.

        Raises a TypeError, if the passed argument is not a positive
        integer.
        Raises a ValueError, if the passed argument is not a positive
        integer greater than or equal to 0.
        """
        if type (drops) != int:
            raise TypeError ("drops must be a positive integer")
        if drops < 0:
           raise ValueError ("drops must be a positive integer")
        self._drops = drops

    def _set_grab (self, manager):
        """R._set_grab (manager) -> None

        Sets the event manager, which acts as grabber of all events.
        """
        self._grabber = manager

    def lock (self):
        """R.lock () -> None

        Acquires a lock on the Renderer to suspend its updating methods.
        """
        self._lock += 1
    
    def unlock (self):
        """R.unlock () -> None

        Releases a previously set lock on the Renderer and updates it
        instantly.
        """
        if self._lock > 0:
            self._lock -= 1
        if self._lock == 0:
            self.refresh ()

    def _add (self, widget):
        """R._add (...) -> None

        Adds a widget to the internal lists.
        """
        layers = self._layers.get (widget.depth)
        if not layers:
            manager = _LayerEventManager (self, widget.depth)
            layers = ([], [], manager)
            self._layers[widget.depth] = layers

        # The first list is an indexing list used in add_index, the
        # second the widget list for updates, the third an event manager
        # for that layer.
        
        if widget in layers[1]:
            raise ValueError ("Widget %s already added" % widget)
        layers[1].append (widget)
        widget.manager = layers[2]

    def clear (self):
        """R.clear () -> None

        Removes and destroys all widgets and objects of the Renderer queues.
        """
        keys = self._layers.keys ()
        layers = self._layers
        rm_index = self.remove_index
        for key in keys:
            layer = layers[key]

            # Remove all widgets.
            widgets = layer[1][:]
            for w in widgets:
                w.destroy ()

            if layers.has_key (key):
                # Remove all event capable objects.
                layer[2].clear ()
                
                # Remove all indexed objects.
                rm_index (*layer[0])

    def add_widget (self, *widgets):
        """R.add_widget (...) -> None

        Adds one or more widgets to the Renderer.

        Adds one or more widgets to the event system and the RenderGroup
        provided by the Renderer class. The widgets will be added to the
        internal indexing system for keyboard navigation, too.

        Raises a TypeError, if one of the passed arguments does not
        inherit from the BaseWidget class.
        """
        for widget in widgets:
            if not isinstance (widget, BaseWidget):
                raise TypeError ("Widget %s must inherit from BaseWidget"
                                 % widget)
            self._add (widget)
            self.add_index (widget)
            widget.parent = self
            widget.update ()

    def remove_widget (self, *widgets):
        """R.remove_widget (...) -> None

        Removes one or more widgets from the Renderer.

        Removes one or more widgets from the event and indexing systen of the
        Renderer class.

        Raises a TypeError, if one of the passed arguments does not
        inherit from the BaseWidget class.
        """
        cleanup = False
        blit = self.screen.blit
        rects = []
        for widget in widgets:
            layer = self._layers[widget.depth]
            if not isinstance (widget, BaseWidget):
                raise TypeError ("Widget %s must inherit from BaseWidget"
                                 % widget)

            if widget.parent == self:
                widget.parent = None
            
            if widget in layer[1]:
                # Not any widget is added to the widget queue (only the
                # topmost one), thus check, if the widget can be removed at
                # all.
                cleanup = True
                layer[1].remove (widget)
                blit (self._background, widget.rect, widget.rect)
                rects.append (widget.rect)

            self.remove_index (widget)
            widget.manager = None

        # Clean up.
        if cleanup:
            self._redraw_widgets (True, *rects)

    def add_index (self, *objects):
        """R.add_index (...) -> None

        Adds one or more widgets to the indexing system.

        The indexing system of the Renderer provides easy keyboard
        navigation using the TAB key. Widgets will by activated using
        their index, if they are added to to the indexing system.

        Raises a TypeError, if one of the passed arguments does not
        inherit from the BaseWidget class.
        """
        for widget in objects:
            if not isinstance (widget, BaseWidget):
                raise TypeError ("Widget %s must inherit from BaseWidget"
                                 % widget)

            if widget.indexable not in (self, None):
                raise ValueError ("Widget already attched to an IIndexable")
            widget.indexable = self
            
            layers = self._layers.get (widget.depth)
            if not layers:
                manager = _LayerEventManager (self, widget.depth)
                layers = ([], [], manager)
                self._layers[widget.depth] = layers

            if widget not in layers[0]:
                layers[0].append (widget)
            # Sort the widget list, so we can access the index keys more
            # quickly.
            layers[0].sort (lambda x, y: cmp (x.index, y.index))

    def remove_index (self, *objects):
        """R.remove_index (...) -> None

        Removes a widget from the indexing system.

        Removes a wigdget from the indexing system of the Renderer.
        """
        index = None
        for widget in objects:
            index = self._layers[widget.depth][0]
            if widget in index:
                index.remove (widget)
                widget.indexable = None
            if widget == self._indexwidget:
                self._indexwidget = None
        
        if index and (len (index) == 0):
            self._destroy_layer (widget.depth)

    def _destroy_layer (self, index):
        """R._remove_layer (...) -> None

        Removes a layer from the Renderer, if it does not hold any objects.

        Removes a layer from the Renderer, if it does not hold any
        objects in each of its lists anymore. An exception is the layer
        with index 0, in which case this method will do nothing.
        """
        if index == 0:
            return

        layer = self._layers.get (index)

        # Destroy Layer, if no object is contained in that list anymore.
        if (layer != None) and (len (layer[0]) == 0) and \
               (len (layer[1]) == 0) and (len (layer[2]) == 0):
            if layer == self.active_layer:
                self.active_layer = self._layers[0]
            del self._layers[index]

    def update_index (self, *objects):
        """R.update_index (...) -> None

        Updates the indices for one or more widgets.
        """
        layers = self._layers
        for w in objects:
            layers[w.depth][0].sort (lambda x, y: cmp (x.index, y.index))

    def update_layer (self, oldlayer, widget):
        """R.update_layer (...) -> None

        Updates the layer for one or more widgets.
        """
        old = self._layers[oldlayer]
        old[0].remove (widget)
        old[0].sort (lambda x, y: cmp (x.index, y.index))
        old[1].remove (widget)
        old[2].remove (widget)

        new = self._layers[widget.depth]
        new[0].append (widget)
        new[0].sort (lambda x, y: cmp (x.index, y.index))
        new[1].append (widget)
        new[2].add_object (widget)

    def _redraw_widgets (self, post=True, *rects):
        """R._redraw_widgets (...) -> None

        Redraws all widgets, that intersect with the rectangle list.

        Redraws all widgets, that intersect with the passed rectangles
        and raises the SIG_UPDATED event on demand.
        """

        unique = []
        append = unique.append

        # Clean doubled entries.
        for rect in rects:
            if rect not in unique:
                append (rect)

        bg = self._background
        blit = self.screen.blit
        layers = self._layers
        keys = self._layers.keys ()
        keys.sort ()

        redraw = []
        append = redraw.append
        for index in keys:
            widgets = layers[index][1]
            for w in widgets:
                clip = w.rect.clip
                for rect in unique:
                    intersect = clip (rect)
                    if intersect.size != (0, 0):
                        append ((w, intersect))

        # We have the intersection list, blit it.
        redraw.sort (lambda x, y: cmp (x[0].depth, y[0].depth))

        # Clean up.
        for w, i in redraw:
            blit (bg, i, i)
        # Blit changes.
        for w, i in redraw:
            blit (w.image, i.topleft,
                  ((i.left - w.left, i.top - w.top), i.size))
        display.update (unique)

    def update (self, **kwargs):
        """R.update (...) -> None

        Forces the Renderer to update its screen.
        """
        if self.locked:
            return        
        if not self.screen:
            return
        
        children = kwargs.get ("children", {})

        dirty = []
        dirty_append = dirty.append
        blit = self.screen.blit
        bg = self._background

        # Clear.
        for rect in children.values ():
            blit (bg, rect, rect)

        # Update dirty widgets.
        rect_widget = None
        items = children.items ()
        for widget, rect in items:
            blit (bg, rect, rect)
            rect_widget = widget.rect
            blit (widget.image, rect_widget)
            if rect.colliderect (rect_widget):
                dirty_append (rect.union (rect_widget))
            else:
                dirty_append (rect)
                dirty_append (rect_widget)

        # Update intersections.
        self._redraw_widgets (True, *dirty)

        # Post update.
        event.clear (SIG_TICK)
        if self.drops > 0:
            motions = event.get (MOUSEMOTION)[::self.drops]
            for m in motions:
                event.post (m)
        if not event.peek (SIG_UPDATED):
            event.post (self.__updateevent)

    def refresh (self):
        """R.refresh () -> None

        Causes the Renderer to do a complete screen refresh.

        In contrast to the update() method this method updates the whole
        screen area occupied by the Renderer and all its widgets. This
        is especially useful, if the size of the pygame window changes
        or the fullscreen mode is toggled.
        """
        # If widgets have been added already, show them.
        layers = self._layers.values ()
        for layer in layers:
            for widget in layer[1]:
                widget.update ()

        if self.screen:
            display.flip ()

    def start (self, wait=False):
        """R.start (...) -> None

        Starts the main loop of the Renderer.

        Start the main loop of the Renderer. Currently two different
        modes are supported:
        * Timer based event polling and distribution.
          This does not care about whether there are events or not, but
          suspends the loop for the set timer value on each run (known
          as FPS scaling).
        * Event based polling and distribution.
          This loop will only continue, if an event occurs on the queue
          and wait otherwise.
        """
        if wait:
            self._synced_loop ()
        else:
            self._loop ()

    def switch_index (self, reverse=False):
        """R.switch_index (reverse=False) -> None

        Passes the input focus to the next or previous widget.

        Passes the input focus to the widget, which is the next or
        previous focusable after the one with the current focus.  The
        default passing is to focus widget with the next higher or equal
        index set. If the reverse argument is set to True, the previous
        widget with a lower index is focused.
        """
        indices = None
        if self._activelayer:
            indices = self._activelayer[0]
        else:
            indices = self._layers[0][0]

        if len (indices) == 0:
            return

        # Check, if at least one widget can be activated.
        widgets = [wid for wid in indices if wid.sensitive]
        if len (widgets) == 0:
            # None active here
            return
        
        # Get the widget with focus.
        try:
            self._indexwidget = [w for w in widgets if w.focus][0]
        except IndexError:
            # None is focused in that layer
            pass
            
        if self._indexwidget in widgets:
            pos = widgets.index (self._indexwidget)
        else:
            # index widget is not in the current layer. or not set
            pos = -1
            
        # Reslice the list and traverse it.
        if not reverse:
            widgets = widgets[pos + 1:] + widgets[:pos + 1]
        else:
            widgets = widgets[pos:] + widgets[:pos]
            widgets.reverse ()
            
        for wid in widgets:
            if (wid != self._indexwidget) and wid.set_focus (True):
                # Found a widget, which allows to be focused, exit.
                self._indexwidget = wid
                return

    def switch_layer (self):
        """R.switch_layer () -> None
        
        Passes the keyboard focus to the next layer.
        """
        layers = self._layers.values ()
        if len (layers) == 1:
            return

        index = 0
        if self._activelayer:
            index = layers.index (self._activelayer)
        # Deactivate the current focus, if any.
        indices = self._activelayer[0]
        for w in indices:
            w.set_focus (False)

        if self._grabber:
            self._activelayer = layers[self._grabber.layer]
        else:
            # Reslice the list and traverse it.
            layers = layers[index + 1:] + layers[:index + 1]
            if (layers[0] != self._activelayer):
                self._activelayer = layers[0]

        # Focus the first index widget of that layer.
        self._indexwidget = None
        self.switch_index ()
        if self._showlayerinfo:
            self._create_layer (layers.index (self._activelayer))

    def _create_layer (self, index):
        """R._create_layer (...) -> None

        Creates a layer information surface.
        """
        text = String.draw_string ("Layer: %d" % index,
                                   "sans", 18, True, (0, 0, 0))
        r = text.get_rect ()
        r.center = self.screen.get_rect ().center
        self.__layerinfo = Complex.FaderSurface (r.width, r.height)
        self.__layerinfo.blit (self.screen, (0, 0), r)
        self.__layerinfo.blit (text, (0, 0))
        self.__layerinfo.step = -10

    def _show_layer_info (self):
        """R._show_layer_info () -> None

        Shows the layer information on the main screen.
        """
        rect = self.__layerinfo.get_rect ()
        rect.center = self.screen.get_rect ().center
        if self.__layerinfo.alpha > 0:
            # Clean.
            self.screen.blit (self._background, rect, rect)
            self._redraw_widgets (False, (rect,))
            # Redraw.
            self.__layerinfo.update ()
            self.screen.blit (self.__layerinfo, rect)
            display.update (rect)
        else:
            # Clean up.
            self.__layerinfo = None
            self.screen.blit (self._background, rect, rect)
            self._redraw_widgets (False, (rect))

    def _is_mod (self, mod):
        """R._is_mod (...) -> bool

        Determines, if the passed key value is a key modificator.
        
        Returns True if the pass key value is a key modificator
        (KMOD_ALT, KMOD_CTRL, etc.), False otherwise.
        """
        return (mod & KMOD_ALT == KMOD_ALT) or \
               (mod & KMOD_LALT == KMOD_LALT) or \
               (mod & KMOD_RALT == KMOD_RALT) or \
               (mod & KMOD_SHIFT == KMOD_SHIFT) or \
               (mod & KMOD_LSHIFT == KMOD_LSHIFT) or \
               (mod & KMOD_RSHIFT == KMOD_RSHIFT) or \
               (mod & KMOD_RCTRL == KMOD_RCTRL) or \
               (mod & KMOD_LCTRL == KMOD_LCTRL) or \
               (mod & KMOD_CTRL)

    def _activate_mnemonic (self, event):
        """R._activate_mnemonic (...) -> None

        Activates the mnemonic key method of a widget.

        This method iterates over the widgets of the indexing system and
        tries to activate the mnemonic key method (activate_mnemonic())
        of them. It breaks right after the first widget's method
        returned True.
        """
        indices = self._activelayer[0]
        for wid in indices:
            if wid.sensitive and wid.activate_mnemonic (event.unicode):
                return

    def get_managers (self):
        """R.get_managers () -> dict

        Gets the event managers of the layers.

        Gets the event managers of the different layers as dictionary
        using the layer depth as key.
        """
        keys = self._layers.keys ()
        managers = {}
        for k in keys:
            managers[k] = self._layers[k][2]
        return managers

    def _get_layers (self, signal):
        """R._get_layers (signal) -> list

        Gets an ordered list of the layers.
        """
        if signal not in SIGNALS_MOUSE:
            if self._activelayer:
                return [self._activelayer]

        # Get the key ids in reverse order
        keys = self._layers.keys ()
        keys.sort ()
        keys.reverse ()

        self_layers = self._layers
        layers = []
        for k in keys:
            layers.append (self_layers[k])
        return layers

    def _check_doubleclick (self, event):
        """R._check_doubleclick (...) -> None

        Checks if the received event matches the criteria for a double-click.

        Checks if the received event matches the criteria for a
        double-click and emits a SIG_DOUBLICKED event, if it does.
        """
        x, y = event.pos
        button = event.button
        ticks = PygameTime.get_ticks ()
        elaps = ticks - self._mouseinfo[3]

        # Ignore button 4 and 5 for scroll wheels.
        if (button < 4) and (self._mouseinfo[2] == button):
            if elaps <= base.DoubleClickRate:
                if (x == self._mouseinfo[0]) and (y == self._mouseinfo[1]):
                    ev = Event (SIG_DOUBLECLICKED, event)
                    if not self._grabber:
                        layers = self._get_layers (ev.signal)
                        for layer in layers:
                            if not ev.handled:
                                layer[2].emit_event (ev)
                    else:
                        self._grabber.emit_event (ev)
        
        self._mouseinfo = (x, y, button, ticks)

    def distribute_events (self, *events):
        """R.distribute_events (...) -> bool

        Distributes one ore more events to the widgets of the Renderer.

        The method distributes the received events to the attached
        objects. If the events contain KEYDOWN events, the IIndexable
        interface method for keyboard navigation will be invoked before
        the Renderer tries to send them to its objects.

        The method returns False, as soon as it receives a QUIT event.
        If all received events passed it successfully, True will be
        returned.
        """
        resize = self.support_resize
        ismod = self._is_mod
        pos = None
        
        for event in events:
            ev = None
            pos = None
            etype = event.type
            if etype == QUIT:
                return False

            elif (etype == VIDEORESIZE) and resize:
                self.create_screen (event.w, event.h, self.__flags)
            
            elif etype == MOUSEMOTION:
                pos = event.pos
                # Check, whether the mouse is located within the assigned
                # area.
                if (pos[0] < self.left) or (pos[0] > self.right) or \
                   (pos[1] < self.top) or (pos[1] > self.bottom):
                    continue
                event.dict["pos"] = event.pos[0] - self.x, \
                                    event.pos[1] - self.y
                ev = Event (SIG_MOUSEMOVE, event)

            elif etype == MOUSEBUTTONDOWN:
                pos = event.pos
                # Check, whether the mouse is located within the assigned
                # area.
                if (pos[0] < self.left) or (pos[0] > self.right) or \
                   (pos[1] < self.top) or (pos[1] > self.bottom):
                    continue
                event.dict["pos"] = event.pos[0] - self.x, \
                                    event.pos[1] - self.y
                ev = Event (SIG_MOUSEDOWN, event)

            elif etype == MOUSEBUTTONUP:
                pos = event.pos
                # Check, whether the mouse is located within the assigned
                # area.
                if (pos[0] < self.left) or (pos[0] > self.right) or \
                   (pos[1] < self.top) or (pos[1] > self.bottom):
                    continue
                event.dict["pos"] = event.pos[0] - self.x, \
                                    event.pos[1] - self.y
                self._check_doubleclick (event)
                ev = Event (SIG_MOUSEUP, event)

            elif etype == KEYDOWN:
                # Check, if it is the TAB key and call the indexing
                # methods on demand.
                if event.key == K_TAB:
                    if not ismod (event.mod):
                        # Cycle through the widgets of the current layer.
                        self.switch_index ()
                    elif event.mod & KMOD_SHIFT:
                        self.switch_index (True)
                    elif event.mod & KMOD_CTRL:
                        # Cycle through the layers.
                        self.switch_layer ()

                elif event.mod & KMOD_LALT == KMOD_LALT:
                    self._activate_mnemonic (event)

                else:
                    ev = Event (SIG_KEYDOWN, event)

            elif etype == KEYUP:
                ev = Event (SIG_KEYUP, event)

            else:
                # We also will distribute any other event.
                ev = Event (etype, event)

            if ev:
                if ev.signal in (SIG_TICK, SIG_SCREENCHANGED):
                    layers = filter (None, self._layers.values ())
                    for layer in layers:
                        layer[2].emit_all (ev)
                
                elif not self._grabber:
                    layers = filter (None, self._get_layers (ev.signal))
                    for layer in layers:
                        if not ev.handled:
                            layer[2].emit_event (ev)
                else:
                    self._grabber.emit_event (ev)

            # Restore the original position.
            if pos != None:
                event.dict["pos"] = pos
        return True

    def _loop (self):
        """R._loop () -> None
        
        A main event loop, which uses a timer based polling.

        Main event loop of the Renderer. This loop hooks up on the event
        loop of pygame and distributes all its events to the attached
        objects. It uses a timer based polling mechanism instead of
        waiting for events.
        """
        # Emit the tick event every 10 ms.
        PygameTime.set_timer (SIG_TICK, 10)
        delay = PygameTime.delay
        event_get = event.get
        pump = event.pump

        while True:
            pump ()
            # Get events and distribute them.
            events = event_get ()

            if not self.distribute_events (*events):
                return # QUIT event
            if self.timer > 0:
                delay (1000 / self.timer)
            if self.__layerinfo:
                self._show_layer_info ()

    def _synced_loop (self):
        """R._synced_loop () -> None

        A main event loop, which uses an event based polling.

        Main event loop of the Renderer. This loop hooks up on the event
        loop of pygame and distributes all its events to the attached
        objects. It waits for an event to occur on the queues before it
        does further processing. It ignores the Renderer.timer setting.
        """
        # Emit the tick event every 10 ms.
        PygameTime.set_timer (SIG_TICK, 10)
        event_wait = event.wait
        pump = event.pump

        while True:
            pump ()
            # Get an event and distribute it.
            if not self.distribute_events (event_wait ()):
                return # QUIT event
            if self.__layerinfo:
                self._show_layer_info ()
        
    locked = property (lambda self: self._lock > 0,
                       doc = "Indicates, whether the Renderer is locked.")
    title = property (lambda self: self._title,
                      lambda self, var: self.set_title (var),
                      doc = "The title of the pygame window.")
    screen = property (lambda self: self._screen,
                       lambda self, var: self.set_screen (var),
                       doc = "The screen to draw on.")
    timer = property (lambda self: self._timer,
                      lambda self, var: self.set_timer (var),
                      doc = "The speed of the event and update loop.")
    color = property (lambda self: self._color,
                      lambda self, var: self.set_color (var),
                      doc = "The background color of the pygame window.")
    active_layer = property (lambda self: self._activelayer,
                             lambda self, var: self.set_active_layer (var),
                             doc = "The active layer on the pygame window.")
    show_layer_info = property (lambda self: self._showlayerinfo,
                           lambda self, var: self.set_show_layer_info (var),
                           doc = "Indicates, whether the layer info should "\
                           "be shown when changing the layer.")
    support_resize = property (lambda self: self._supportresize,
                               lambda self, var: self.set_support_resize (var),
                               doc = "Indicates, whether resize events "\
                               "should be supported.")
    managers = property (lambda self: self.get_managers (),
                         doc = "Tuple containing the available " \
                         "EventManagers for the different layers.")
    rect = property (lambda self: self._get_rect (),
                     doc = "The area occupied by the Renderer.")
    drops = property (lambda self: self._drops,
                      lambda self, var: self.set_drops (var),
                      doc = "The mouse motion events to drop on each update.")

