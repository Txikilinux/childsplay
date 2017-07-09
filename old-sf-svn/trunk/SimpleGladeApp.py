"""
 SimpleGladeApp.py
 Module that provides an object oriented abstraction to pygtk and gtk.builder.
 Copyright (C) 2004 Sandino Flores Moreno
 Copyright (C) 2008 Stas Zytkiewicz
"""
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation.  A copy of this license should
# be included in the file GPL-3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.

import os
import sys
import re
import tokenize
import weakref
#import inspect
import logging
SG_module_logger = logging.getLogger('schoolsplay.SimpleGladeApp')
import pygtk
pygtk.require('2.0')
import gtk

def bindtextdomain(app_name, locale_dir=None):
    #TODO: do we still need this function ???
    """
    This function is only used when the installed GTK version <= 2.14. 
    Bind the domain represented by app_name to the locale directory locale_dir.
    It has the effect of loading translations, enabling applications for different
    languages.
    
    app_name:
            a domain to look for translations, tipically the name of an application.
    
    locale_dir:
            a directory with locales like locale_dir/lang_isocode/LC_MESSAGES/app_name.mo
            If omitted or None, then the current binding for app_name is used.
    """     
    try:
            import locale
            import gettext
            locale.setlocale(locale.LC_ALL, "")
            gtk.glade.bindtextdomain(app_name, locale_dir)
            #gettext.install(app_name, locale_dir, unicode=1)
    except (IOError,locale.Error), e:
            print "Warning", app_name, e
            __builtins__.__dict__["_"] = lambda x : x

class SimpleGladeApp:
        def __init__(self, path, root=None, domain=None, **kwargs):
                """
                Load a glade file specified by glade_filename, using root as
                root widget and domain as the domain for translations.
                
                If it receives extra named arguments (argname=value), then they are used
                as attributes of the instance.
                
                path:
                        path to a glade filename.
                        If glade_filename cannot be found, then it will be searched in the
                        same directory of the program (sys.argv[0])
                
                root:
                        the name of the widget that is the root of the user interface,
                        usually a window or dialog (a top level widget).
                        If None or ommited, the full user interface is loaded.
                
                domain:
                        A domain to use for loading translations.
                        If None or ommited, no translation is loaded.
                
                **kwargs:
                a dictionary representing the named extra arguments.
                It is useful to set attributes of new instances, for example:
                        glade_app = SimpleGladeApp("ui.glade", foo="some value", bar="another value")
                sets two attributes (foo and bar) to glade_app.
                """
                if os.path.isfile(path):
                    self.glade_path = path
                elif os.path.isfile(os.path.join(glade_dir,'pixmaps', path)):
                    glade_dir = os.path.dirname( sys.argv[0] )
                    self.glade_path = os.path.join(glade_dir,'pixmaps', path)
                else:
                    SG_module_logger.error('*** Not found glade file: % ***' % path)
                for key, value in kwargs.items():
                    try:
                        setattr(self, key, weakref.proxy(value) )
                    except TypeError:
                        setattr(self, key, value)
                self.glade = None
                self.main_widget = None
                self.builder = gtk.Builder()
                self.builder.add_from_file(self.glade_path)
                if root:
                    self.main_widget = self.builder.get_object(root)
                self.normalize_names()
                self.add_callbacks(self)
                self.new()
                
        def __repr__(self):
                class_name = self.__class__.__name__
                if self.main_widget:
                        root = self.main_widget.get_name()
                        repr = '%s(path="%s", root="%s")' % (class_name, self.glade_path, root)
                else:
                        repr = '%s(path="%s")' % (class_name, self.glade_path)
                return repr

        def new(self):
                """
                Method called when the user interface is loaded and ready to be used.
                At this moment, the widgets are loaded and can be refered as self.widget_name
                """
                pass
    
        def add_callbacks(self, callbacks_proxy):
                """
                It uses the methods of callbacks_proxy as callbacks.
                The callbacks are specified by using:
                        Properties window -> Signals tab
                        in glade-2 (or any other gui designer like gazpacho).

                Methods of classes inheriting from SimpleGladeApp are used as
                callbacks automatically.
                
                callbacks_proxy:
                        an instance with methods as code of callbacks.
                        It means it has methods like on_button1_clicked, on_entry1_activate, etc.
                """  
                self.builder.connect_signals(callbacks_proxy)
                

        def normalize_names(self):
                """
                It is internally used to normalize the name of the widgets.
                It means a widget named foo:vbox-dialog in glade
                is refered self.vbox_dialog in the code.
                
                It also sets a data "prefixes" with the list of
                prefixes a widget has for each widget.
                """
                widgets = self.builder.get_objects()
                for widget in widgets:
                        widget_name = widget.get_name()
                        prefixes_name_l = widget_name.split(":")
                        prefixes = prefixes_name_l[ : -1]
                        widget_api_name = prefixes_name_l[-1]
                        widget_api_name = "_".join( re.findall(tokenize.Name, widget_api_name) )
                        widget.set_name(widget_api_name)
                        if hasattr(self, widget_api_name):
                                raise AttributeError("instance %s already has an attribute named %s" % (self,widget_api_name))
                        else:
                                setattr(self, widget_api_name, widget)
                                if prefixes:
                                        widget.set_data("prefixes", prefixes)
                        
        def gtk_widget_show(self, widget, *args):
                """
                Predefined callback.
                The widget is showed.
                Equivalent to widget.show()
                """
                widget.show()

        def gtk_widget_hide(self, widget, *args):
                """
                Predefined callback.
                The widget is hidden.
                Equivalent to widget.hide()
                """
                widget.hide()

        def gtk_widget_grab_focus(self, widget, *args):
                """
                Predefined callback.
                The widget grabs the focus.
                Equivalent to widget.grab_focus()
                """
                widget.grab_focus()

        def gtk_widget_destroy(self, widget, *args):
                """
                Predefined callback.
                The widget is destroyed.
                Equivalent to widget.destroy()
                """
                widget.destroy()

        def gtk_window_activate_default(self, window, *args):
                """
                Predefined callback.
                The default widget of the window is activated.
                Equivalent to window.activate_default()
                """
                widget.activate_default()

        def gtk_true(self, *args):
                """
                Predefined callback.
                Equivalent to return True in a callback.
                Useful for stopping propagation of signals.
                """
                return True

        def gtk_false(self, *args):
                """
                Predefined callback.
                Equivalent to return False in a callback.
                """
                return False

        def gtk_main_quit(self, *args):
                """
                Predefined callback.
                Equivalent to gtk.main_quit()
                """
                gtk.main_quit()

        def main(self):
                """
                Starts the main loop of processing events.
                The default implementation calls gtk.main()
                
                Useful for applications that needs a non gtk main loop.
                For example, applications based on gstreamer needs to override
                this method with gst.main()
                
                Do not directly call this method in your programs.
                Use the method run() instead.
                """
                gtk.main()

        def quit(self):
                """
                Quit processing events.
                The default implementation calls gtk.main_quit()
                
                Useful for applications that needs a non gtk main loop.
                For example, applications based on gstreamer needs to override
                this method with gst.main_quit()
                """
                gtk.main_quit()

        def run(self):
                """
                Starts the main loop of processing events checking for Control-C.
                
                The default implementation checks wheter a Control-C is pressed,
                then calls on_keyboard_interrupt().
                
                Use this method for starting programs.
                """
                try:
                        self.main()
                except KeyboardInterrupt:
                        self.on_keyboard_interrupt()

        def on_keyboard_interrupt(self):
                """
                This method is called by the default implementation of run()
                after a program is finished by pressing Control-C.
                """
                pass
