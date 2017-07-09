# $Id: Style.py,v 1.66.2.10 2007/05/08 14:52:37 marcusva Exp $
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

"""Style class for widgets."""

import os.path, copy
from UserDict import IterableUserDict
from Constants import *
from StyleInformation import StyleInformation

# Import the default theme engine path.
import sys
sys.path.append (DEFAULTDATADIR)
from themes import default

class WidgetStyle (IterableUserDict):
    """WidgetStyle (dict=None) -> WidgetStyle

    A style dictionary that tracks changes of its items.

    The WidgetStyle dictionary class allows one to let a bound method be
    executed, whenever a value of the dictionary changed. Additionally,
    the WidgetStyle class supports recursive changes, so that a
    WidgetStyle object within this WidgetStyle can escalate the value
    change and so on.

    To set up the value change handler you can bind it using the
    set_value_changed() method of the WidgetStyle class:

    style.set_value_changed (callback_method)

    This will cause it and all values of it, which are WidgetStyle
    objects to invoke the callback_method on changes.

    To get the actually set value change handler, the
    get_value_changed() method can be used:

    callback = style.get_value_changed ()
    """
    def __init__ (self, dict=None):
        # Notifier slot.
        self._valuechanged = None
        IterableUserDict.__init__ (self, dict)

    def __copy__ (self):
        """W.__copy__ () -> WidgetStyle

        Creates a shallow copy of the WidgetStyle dictionary.
        """
        newdict = WidgetStyle ()
        keys = self.keys ()
        for k in keys:
            newdict[k] = self[k]
            newdict.set_value_changed (self._valuechanged)
        return newdict
        
    def __deepcopy__(self, memo={}):
        """W.__deepcopy__ (...) -> WidgetStyle.

        Creates a deep copy of the WidgetStyle dictionary.
        """
        newdict = WidgetStyle ()
        keys = self.keys ()
        for k in keys:
            newdict[copy.deepcopy (k, memo)] = copy.deepcopy (self[k], memo)
            newdict.set_value_changed (self._valuechanged)
        memo [id (self)] = newdict
        return newdict
    
    def __setitem__ (self, i, y):
        """W.__setitem__ (i, y) <==> w[i] = y
        """
        IterableUserDict.__setitem__ (self, i, y)
        if isinstance (y, WidgetStyle):
            y.set_value_changed (self._valuechanged)
        if self._valuechanged:
            self._valuechanged ()

    def __delitem__ (self, y):
        """W.__delitem__ (i, y) <==> del w[y]
        """
        IterableUserDict.__delitem__ (self, y)
        if self._valuechanged:
            self._valuechanged ()

    def __repr__ (self):
        """W.__repr__ () <==> repr (W)
        """
        return "WidgetStyle %s" % IterableUserDict.__repr__ (self)
    
    def clear (self, y):
        """W.clear () -> None

        Remove all items from the WidgetStyle dictionary.
        """
        changed = self._valuechanged
        self.set_value_changed (None)
        IterableUserDict.clear (self)
        self.set_value_changed (changed)
        if changed:
            changed ()

    def pop (self, k, d=None):
        """W.pop (k, d=None) -> object

        Remove specified key and return the corresponding value.

        If key is not found, d is returned if given, otherwise KeyError
        is raised.
        """
        changed = IterableUserDict.has_key (self, k)
        v = IterableUserDict.pop (self, k, d)
        if changed and self._valuechanged:
            self._valuechanged ()
        return v

    def popitem (self):
        """W.popitem () -> (k, v)

        Remove and return some (key, value) pair as a 2-tuple

        Raises a KeyError if D is empty.
        """
        v = IterableUserDict.popitem (self)
        if self._valuechanged:
            self._valuechanged ()
        return v

    def setdefault (self, k, d=None):
        """W.setdefault (k,d=None) -> W.get (k, d), also set W[k] = d if k not in W
        """
        changed = not IterableUserDict.has_key (self, k)
        v = IterableUserDict.setdefault (self, k, d)
        if changed and self._valuechanged:
            self._valuechanged ()
        return v

    def update (self, E, **F):
        """W.update (E, **F) -> None

        Update W from E and F.

        for k in E: W[k] = E[k] (if E has keys else: for (k, v) in E:
        W[k] = v) then: for k in F: W[k] = F[k]
        """
        amount = len (self)
        IterableUserDict.update (self, E, **F)
        if self._valuechanged and (len (self) != amount):
            self._valuechanged ()

    def get_value_changed (self):
        """W.get_value_changed (...) -> callable

        Gets the set callback method for the dictionary changes.
        """
        return self._valuechanged
    
    def set_value_changed (self, method):
        """W.set_value_changed (...) -> None

        Connects a method to invoke, when an item of the dict changes.

        Raises a TypeError, if the passed argument is not callable.
        """
        if method and not callable (method):
            raise TypeError ("method must be callable")

        values = self.values ()
        for val in values:
            if isinstance (val, WidgetStyle):
                val.set_value_changed (method)
        self._valuechanged = method

class Style (object):
    """Style () -> Style

    Style class for drawing objects.

    Style definitions
    -----------------
    Styles are used to change the appearance of the widgets. The drawing
    methods of the Style class will use the specific styles of the
    'styles' attribute to change the fore- and background colors, font
    information and border settings of the specific widgets. The styles
    are set using the lower lettered classname of the widget to draw.
    Additionally the Style class supports cascading styles by falling
    back to the next available class name in the widget its __mro__
    list. If no specific set style could be found for the specific
    widget type, the Style class will use the 'default' style entry of
    its 'styles' dictionary.

    Any object can register its own style definition and request it
    using the correct key. A Button widget for example, could register
    its style definition this way:

    Style.styles['button'] = WidgetStyle ({ .... })

    Any other button widget then will use this style by default, so
    their look is all the same.

    It is also possible to pass an own type dictionary to the drawing
    methods of the attached engine class in order to get a surface,
    which can be shown on the screen then:

    own_style = WidgetStyle ({ ... })
    surface = style.engine.draw_rect (width, height, own_style)

    If the style should be based on an already existing one, the
    copy_style() method can be used to retrieve a copy to work with
    without touching the orignal one:

    own_style = style.copy_style (my_button.__class__)

    The BaseWidget class offers a get_style() method, which will copy
    the style of the widget class to the specific widget instance. Thus
    you can safely modify the instance specific style for the widget
    without touching the style for all widgets of that class.

    The style dictionaries registered within the 'styles' dictionary of
    the Style class need to match some prerequisites to be useful. On
    the one hand they need to incorporate specific key-value pairs,
    which can be evaluated by the various drawing functions, on the
    other they need to have some specific key-value pairs, which are
    evaluated by the Style class.

    The following lists give an overview about the requirements the
    style dictionaries have to match, so that the basic Style class can
    work with them as supposed.

    Style entries
    -------------
    The registered style WidgetStyle dictionaries for the widgets need
    to contain key-value pairs required by the functions of the
    referenced modules. The following key-value pairs are needed to
    create the surfaces:

    bgcolor = WidgetStyle ({ STATE_TYPE : color, ... })

    The background color to use for the widget surface.

    fgcolor = WidgetStyle ({ STATE_TYPE : color, ... })

    The foreground color to use for the widget. This is also the text
    color for widgets, which will display text.

    lightcolor = WidgetStyle ({ STATE_TYPE : color, ... })
    darkcolor = WidgetStyle ({ STATE_TYPE : color, ... })

    Used to create shadow border effects on several widgets. The color
    values usually should be a bit brighter or darker than the bgcolor
    values.

    bordercolor = WidgetStyle ({ STATE_TYPE : color, ... })
    
    Also used to create border effects on several widgets. In contrast
    to the lightcolor and darkcolor entries, this is used, if flat
    borders (BORDER_FLAT) have to drawn.

    shadowcolor = (color1, color2)

    The colors to use for dropshadow effects. The first tuple entry will
    be used as inner shadow (near by the widget), the second as outer
    shadow value.

    image = WidgetStyle ({ STATE_TYPE : string })

    Pixmap files to use instead of the background color. If the file is
    not supplied or cannot be loaded, the respective bgcolor value is
    used.
    
    font = WidgetStyle ({ 'name' : string, 'size' : integer,
                          'alias' : integer, 'style' : integer })

    Widgets, which support the display of text, make use of this
    key-value pair. The 'name' key denotes the font name ('Helvetica')
    or the full path to a font file ('/path/to/Helvetica.ttf').  'size'
    is the font size to use. 'alias' is interpreted as boolean value for
    antialiasing. 'style' is a bit-wise combination of FONT_STYLE_TYPES
    values as defined in ocempgui.draw.Constants and denotes additional
    rendering styles to use.

    shadow = integer

    The size of the 3D border effect for a widget.

    IMPORTANT: It is important to know, that the Style class only
    supports a two-level hierarchy for styles. Especially the
    copy_style() method is not aware of style entries of more than two
    levels. This means, that a dictionary in a style dictionary is
    possible (as done in the 'font' or the various color style entries),
    but more complex style encapsulations are unlikely to work
    correctly.
    Some legal examples for user defined style entries:

    style['ownentry'] = 99                        # One level
    style['ownentry'] = { 'foo' : 1, 'bar' : 2 }  # Two levels: level1[level2]

    This one however is not guaranteed to work correctly and thus should
    be avoided:

    style['ownentry'] = { 'foo' : { 'bar' : 1, 'baz' : 2 }, 'foobar' : { ... }}

    Dicts and WidgetStyle
    ---------------------

    OcempGUI uses a WidgetStyle dictionary class to keep track of
    changes within styles and to update widgets on th fly on changing
    those styles. When you are creating new style files (as explained in
    the next section) you do not need to explicitly use the
    WidgetStyle() dictionary, but can use plain dicts instead. Those
    will be automatically replaced by a WidgetStyle on calling load().

    You should however avoid using plain dicts if you are modifying
    styles of widgets or the Style class at run time and use a
    WidgetStyle instead:

    # generate_new_style() returns a plain dict.
    style = generate_new_style ()
    button.style = WidgetStyle (style)

    Style files
    -----------
    A style file is a key-value pair association of style entries for
    widgets. It can be loaded and used by the Style.load() method to set
    specific themes and styles for the widgets. The style files use the
    python syntax and contain key-value pairs of style information for
    the specific widgets. The general syntax looks like follows:

    widgetclassname = WidgetStyle ({ style_entry : { value } })

    An example style file entry for the Button widget class can look
    like the following:

    button = { 'bgcolor' :{ STATE_NORMAL : (200, 100, 0) },
               'fgcolor' : { STATE_NORMAL : (255, 0, 0) },
               'shadow' : 5 }

    The above example will set the bgcolor[STATE_NORMAL] color style
    entry for the button widget class to (200, 100, 0), the
    fgcolor[STATE_NORMAL] color style entry to (255, 0, 0) and the
    'shadow' value for the border size to 5. Any other value of the
    style will remain untouched.

    Loading a style while running an application does not have any
    effect on widgets

    * with own styles set via the BaseWidget.get_style() method,
    * already drawn widgets using the default style.
    
    The latter ones need to be refreshed via the set_dirty()/update()
    methods explicitly to make use of the new style.
    
    Style files allow user-defined variables, which are prefixed with an
    underscore. A specific color thus can be stored in a variable to allow
    easier access of it.
    
    _red = (255, 0, 0)
    ___myown_font = 'foo/bar/font.ttf'

    Examples
    --------
    The OcempGUI module contains a file named 'default.rc' in the themes
    directory of the installation, which contains several style values
    for the default appearance of the widgets. Additional information
    can be found in the manual of OcempGUI, too.

    Attributes:
    styles - A dictionary with the style definitions of various elements.
    engine - The drawing engine, which takes care of drawing elements.
    """

    __slots__ = ["styles", "_engine"]
    
    def __init__ (self):
        # Initialize the default style.
        self.styles = {
            "default" : WidgetStyle ({
            "bgcolor" : WidgetStyle ({ STATE_NORMAL : (234, 228, 223),
                                       STATE_ENTERED : (239, 236, 231),
                                       STATE_ACTIVE : (205, 200, 194),
                                       STATE_INSENSITIVE : (234, 228, 223) }),
            "fgcolor" : WidgetStyle ({ STATE_NORMAL : (0, 0, 0),
                                       STATE_ENTERED : (0, 0, 0),
                                       STATE_ACTIVE : (0, 0, 0),
                                       STATE_INSENSITIVE : (204, 192, 192) }),
            "lightcolor" : WidgetStyle ({ STATE_NORMAL : (245, 245, 245),
                                          STATE_ENTERED : (245, 245, 245),
                                          STATE_ACTIVE : (30, 30, 30),
                                          STATE_INSENSITIVE : (240, 240, 240)
                                          }),
            "darkcolor" : WidgetStyle ({ STATE_NORMAL : (30, 30, 30),
                                         STATE_ENTERED : (30, 30, 30),
                                         STATE_ACTIVE : (245, 245, 245),
                                         STATE_INSENSITIVE : (204, 192, 192)
                                         }),
            "bordercolor" : WidgetStyle ({ STATE_NORMAL : (0, 0, 0),
                                           STATE_ENTERED : (0, 0, 0),
                                           STATE_ACTIVE : (0, 0, 0),
                                           STATE_INSENSITIVE : (204, 192, 192)
                                           }),
            "shadowcolor" : ((100, 100, 100), (130, 130, 130)),
            "image" : WidgetStyle ({ STATE_NORMAL : None,
                                     STATE_ENTERED : None,
                                     STATE_ACTIVE : None,
                                     STATE_INSENSITIVE : None }),
            "font" : WidgetStyle ({ "name" : None,
                                    "size" : 16,
                                    "alias" : True,
                                    "style" : 0 }),
            "shadow" : 2 })
            }

        # Load the default style and theme engine.
        self.load (os.path.join (DEFAULTDATADIR, "themes", "default",
                                 default.RCFILE))
        self.set_engine (default.DefaultEngine (self))

    def get_style (self, cls):
        """S.get_style (...) -> WidgetStyle
        
        Returns the style for a specific widget class.

        Returns the style for a specific widget class. If no matching
        entry was found, the method searches for the next upper
        entry of the class's __mro__. If it reaches the end of the
        __mro__ list without finding a matching entry, the
        default style will be returned.
        """
        classes = [c.__name__.lower () for c in cls.__mro__]
        for name in classes:
            if name in self.styles:
                return self.styles[name]
        return self.styles.setdefault (cls.__name__.lower (), WidgetStyle ())

    def get_style_entry (self, cls, style, key, subkey=None):
        """S.get_style_entry (...) -> value

        Gets a style entry from the style dictionary.

        Gets a entry from the style dictionary. If the entry could not
        be found, the method searches for the next upper entry of the
        __mro__. If it reaches the end of the __mro__ list without
        finding a matching entry, it will try to return the entry from
        the 'default' style dictionary.
        """
        deeper = subkey != None
        if key in style:
            if deeper:
                if subkey in style[key]:
                    return style[key][subkey]
            else:
                return style[key]

        styles = self.styles
        classes = [c.__name__.lower () for c in cls.__mro__]
        for name in classes:
            if name in styles:
                style = styles[name]
                # Found a higher level class style, check it.
                if key in style:
                    if deeper:
                        if subkey in style[key]:
                            return style[key][subkey]
                    else:
                        return style[key]

        # None found, refer to the default.
        if deeper:
            return styles["default"][key][subkey]
        return styles["default"][key]

    def copy_style (self, cls):
        """S.copy_style (...) -> WidgetStyle

        Creates a plain copy of a specific style.

        Due to the cascading ability of the Style class, an existing
        style will be filled with the entries of the 'default' style
        dictionary which do not exist in it.
        """
        style = copy.deepcopy (self.get_style (cls))
        default = self.styles["default"]
        for key in default:
            if key not in style:
                style[key] = copy.deepcopy (default[key])
            else:
                sub = default[key]
                # No dicts anymore
                for subkey in default[key]:
                    style[key][subkey] = copy.deepcopy (sub[subkey])
        return style
    
    def load (self, file):
        """S.load (...) -> None

        Loads style definitions from a file.

        Loads style definitions from a file and adds them to the
        'styles' attribute. Already set values in this dictionary will
        be overwritten.
        """
        glob_dict = {}
        loc_dict = {}
        execfile (file, glob_dict, loc_dict)
        setdefault = self.styles.setdefault
        for key in loc_dict:
            # Skip the Constants import directive and
            # any user-defined variable.
            if key.startswith ("_") or (key == "Constants"): 
                continue

            # Search the style or create a new one from scratch.
            entry = setdefault (key, WidgetStyle ())

            # Look up all entries of our style keys and add them to the
            # style.
            widget = loc_dict[key]
            for key in widget:
                if type (widget[key]) == dict:
                    if key not in entry:
                        entry[key] = WidgetStyle ()
                    for subkey in widget[key]:
                        entry[key][subkey] = widget[key][subkey]
                else:
                    entry[key] = widget[key]

    def create_style_dict (self):
        """Style.create_style_dict () -> dict

    Creates a new style dictionary.

        Creates a new unfilled style dictionary with the most necessary
        entries needed by the Style class specifications.
        """
        style = WidgetStyle ({
            "bgcolor" : WidgetStyle ({ STATE_NORMAL : (0, 0, 0),
                                       STATE_ENTERED : (0, 0, 0),
                                       STATE_ACTIVE : (0, 0, 0),
                                       STATE_INSENSITIVE : (0, 0, 0) }),
            "fgcolor" : WidgetStyle ({ STATE_NORMAL : (0, 0, 0),
                                       STATE_ENTERED : (0, 0, 0),
                                       STATE_ACTIVE : (0, 0, 0),
                                       STATE_INSENSITIVE : (0, 0, 0) }),
            "lightcolor" : WidgetStyle ({ STATE_NORMAL : (0, 0, 0),
                                          STATE_ENTERED : (0, 0, 0),
                                          STATE_ACTIVE : (0, 0, 0),
                                          STATE_INSENSITIVE : (0, 0, 0) }),
            "darkcolor" : WidgetStyle ({ STATE_NORMAL : (0, 0, 0),
                                         STATE_ENTERED : (0, 0, 0),
                                         STATE_ACTIVE : (0, 0, 0),
                                         STATE_INSENSITIVE : (0, 0, 0) }),
            "bordercolor" : WidgetStyle ({ STATE_NORMAL : (0, 0, 0),
                                           STATE_ENTERED : (0, 0, 0),
                                           STATE_ACTIVE : (0, 0, 0),
                                           STATE_INSENSITIVE : (0, 0, 0) }),
            "shadowcolor": ((0, 0, 0), (0, 0, 0)),
            "image" : WidgetStyle ({ STATE_NORMAL : None,
                                     STATE_ENTERED : None,
                                     STATE_ACTIVE : None,
                                     STATE_INSENSITIVE : None }),
            "font" : WidgetStyle ({ "name" : None,
                                    "size" : 0,
                                    "alias" : False,
                                    "style" : 0 }),
            "shadow" : 0
            })
        return style

    def get_border_size (self, cls=None, style=None, bordertype=BORDER_FLAT):
        """S.get_border_size (...) -> int

        Gets the border size for a specific border type and style.

        Gets the size of a border in pixels for the specific border type
        and style. for BORDER_NONE the value will be 0 by
        default. BORDER_FLAT will always return a size of 1.
        The sizes of other border types depend on the passed style.

        If no style is passed, the method will try to retrieve a style
        using the get_style() method.

        Raises a ValueError, if the passed bordertype argument is
        not a value of the BORDER_TYPES tuple.
        """
        if bordertype not in BORDER_TYPES:
            raise ValueError ("bordertype must be a value from BORDER_TYPES")

        if not style:
            style = self.get_style (cls)

        if bordertype == BORDER_FLAT:
            return 1
        elif bordertype in (BORDER_SUNKEN, BORDER_RAISED):
            return self.get_style_entry (cls, style, "shadow")
        elif bordertype in (BORDER_ETCHED_IN, BORDER_ETCHED_OUT):
            return self.get_style_entry (cls, style, "shadow") * 2
        return 0

    def set_engine (self, engine):
        """S.set_engine (...) -> None

        Sets the drawing engine to use for drawing elements.
        """
        if engine == None:
            raise TypeError ("engine must not be None")
        self._engine = engine

    engine = property (lambda self: self._engine,
                       lambda self, var: self.set_engine (var),
                       doc = "The drawing engine, which draws elements.")
