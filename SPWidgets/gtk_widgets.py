#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2011 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           gtk_widgets.py
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation.  A copy of this license should
# be included in the file GPL-3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import os
import subprocess
import gtk


# All widgets MUST have a 'win' attribute pointing to the gtk main window

def get_image_text_box(stock_id, label_text):
    box = gtk.HBox(False, 0)
    box.set_border_width(2)

    image = gtk.Image()
    image.set_from_stock(stock_id, gtk.ICON_SIZE_BUTTON)

    label = gtk.Label(label_text)
    
    box.pack_start(image, False, False, 3)
    box.pack_start(label, False, False, 3)
    
    image.show()
    label.show()
    return box

class Base:
    """Derive from this class to get some handy stuff.
    It assumes the child has set an attribute 'win' pointing to the GTK mainwindow"""
    
    def run(self):
        gtk.main()
    
    def keypress_escape(self, widget, event) :
        if event.keyval == gtk.keysyms.Escape :
            self.quit()

    def quit(self):
        self.win.hide()
        self.win.destroy()
        gtk.main_quit()
    
    def quit_dialog(self, text):
        dlg = gtk.MessageDialog(self.win, gtk.DIALOG_DESTROY_WITH_PARENT,\
                                    gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,\
                                     text)
        response = dlg.run()
        if response == gtk.RESPONSE_YES:
            self.quit()
        else:
            dlg.destroy()
            return True

class _Editor:
    """Internally used object.
    Wraps a textview widget and adds a few abstraction methods.
    It adds itself to the parent"""
    def __init__(self,parent,title=''):
        self.parent = parent
        
        self.frame = gtk.Frame()
        
        self.txttagtable = gtk.TextTagTable()
        self.txtbuffer = gtk.TextBuffer(table=self.txttagtable)
        
        self.tag_h = self.txtbuffer.create_tag(background='lightblue')
        
        self.txtview = gtk.TextView(buffer=self.txtbuffer)
        self.txtview.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 20)                
        self.txtview.connect("expose_event", self.line_numbers_expose)
        
        self.parent.add(self.txtview)
        self.parent.show_all()
        
        self.old_start_iter = None

    def get_all_text(self):
        """Return all text from the widget"""
        startiter = self.txtbuffer.get_start_iter()
        enditer = self.txtbuffer.get_end_iter()
        txt = self.txtbuffer.get_text(startiter,enditer)
        if not txt:
            return []
        if '\n' in txt:
            txt = txt.split('\n')
        else:# assuming one line without a end of line
            txt = [txt]
        return txt
        
    def set_text(self,txt):
        """Load a text in the widget"""
        try:
            txt = ''.join(txt)
            utxt = unicode(txt)
        except Exception,info:
            print "Failed to set text in source buffer"
            print info
            return
        self.txtbuffer.set_text(utxt.rstrip('\n'))
        
    def set_highlight(self,line):
        """Highlight the line in the editor"""
        if self.old_start_iter:
            self.txtbuffer.remove_tag(self.tag_h,self.old_start_iter,self.old_end_iter)
        end_iter = self.txtbuffer.get_iter_at_line(line)
        end_iter.forward_to_line_end()  
        start_iter = self.txtbuffer.get_iter_at_line(line)
        self.txtbuffer.apply_tag(self.tag_h,start_iter,end_iter)
        self.old_start_iter,self.old_end_iter = start_iter,end_iter
    
    def reset_highlight(self):
        self.set_highlight(1)
    
    def line_numbers_expose(self, widget, event, user_data=None):
        text_view = widget
  
        # See if this expose is on the line numbers window
        left_win = text_view.get_window(gtk.TEXT_WINDOW_LEFT)
        
        if event.window == left_win:
            type = gtk.TEXT_WINDOW_LEFT
            target = left_win
        else:
            return False
        
        first_y = event.area.y
        last_y = first_y + event.area.height

        x, first_y = text_view.window_to_buffer_coords(type, 0, first_y)
        x, last_y = text_view.window_to_buffer_coords(type, 0, last_y)

        numbers = []
        pixels = []
        count = self.get_lines(first_y, last_y, pixels, numbers)
        # Draw fully internationalized numbers!
        layout = widget.create_pango_layout("")
  
        for i in range(count):
            x, pos = text_view.buffer_to_window_coords(type, 0, pixels[i])
            numbers[i] = numbers[i] + 1
            str = "%d" % numbers[i] 
            layout.set_text(str)
            widget.style.paint_layout(target, widget.state, False,
                                      None, widget, None, 2, pos + 2, layout)

        # don't stop emission, need to draw children
        return False
        
    def get_lines(self, first_y, last_y, buffer_coords, numbers):
        text_view = self.txtview
        # Get iter at first y
        iter, top = text_view.get_line_at_y(first_y)

        # For each iter, get its location and add it to the arrays.
        # Stop when we pass last_y
        count = 0
        size = 0

        while not iter.is_end():
            y, height = text_view.get_line_yrange(iter)
            buffer_coords.append(y)
            line_num = iter.get_line()
            numbers.append(line_num)
            count += 1
            if (y + height) >= last_y:
                break
            iter.forward_line()

        return count

class gtkTextEditor(Base):
    def __init__(self, parent, xmlalbum, photoindex, filelist):
        """Object that packs a GTK window with an text editor and some buttons
        After the GTK loop is left this object is still alive and you can get
        the editors text content with a call to 'get_editor_text'.
        When the user doesn't use the Save button the 'get_editor_text' will
        return an empty list.
        """
        self._editortext = []
        self._title = ''
        self.parent = parent
        self.album = xmlalbum['album']
        self.xmlalbum = xmlalbum
        self.photoindex = photoindex
        self.basepath = xmlalbum['path']
        self.filelist = filelist[:]
        self.photo_id = os.path.basename(self.filelist[self.photoindex])
        
        window = gtk.Window()
        window.set_modal(True)
        window.connect("destroy", lambda w: gtk.main_quit())
        window.connect("key-press-event", self.keypress_escape)
        #window.set_default_size(800, 600)
        window.set_geometry_hints(window, min_width=800, min_height=600, max_width=800, max_height=600)
        window.set_title("GTK window")
        
        vbox = gtk.VBox(False, 4)
        
        _text = _("You can edit the text shown below, if any. Be aware that the album name with a semicolon prepends the title. \nUse the 'Next' button to go to the next photo. \nWhen ready use the 'Close' button to return to the photo album.")
        lbl = gtk.Label()
        lbl.set_use_markup(True)
        lbl.set_markup("<b>%s</b>" % _text)
        vbox.pack_start(lbl, expand=False, padding=4)
        
        frame = gtk.Frame()
        frame.set_size_request(400,308)
        self.image_layout = gtk.Layout(None,None)
        
        frame.add(self.image_layout)
        vbox.pack_start(frame, expand=True, fill=True, padding=0)
        
        hbox = gtk.HBox(False, 2)
        lbl = gtk.Label()
        lbl.set_use_markup(True)
        lbl.set_markup("<b>%s</b>" % _("Title: "))
        hbox.pack_start(lbl, expand=False, fill=False, padding=4)
        self.entry_title = gtk.Entry()
        hbox.pack_start(self.entry_title, expand=True, fill=True, padding=4)
        vbox.pack_start(hbox, expand=True, fill=False, padding=0)
        
        frame = gtk.Frame()
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_size_request(300,150)
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.E = _Editor(scrolledwindow)
        
        frame.add(scrolledwindow)
        vbox.pack_start(frame, expand=True, fill=False)
        
        hbox = gtk.HBox(False, 2)
        but = gtk.Button()
        box = get_image_text_box(gtk.STOCK_STOP, _("Close"))
        but.add(box)
        but.connect("clicked", self.on_cancel_button_clicked)
        hbox.pack_start(but, expand=True, fill=False, padding=16)
        
        box = get_image_text_box(gtk.STOCK_SAVE, _("Next"))
        but = gtk.Button()
        but.add(box)
        but.connect("clicked", self.on_next_button_clicked)
        hbox.pack_start(but, expand=True, fill=False, padding=16)
        vbox.pack_start(hbox, expand=True, fill=True, padding=4)
        
        window.add(vbox)       
        window.show_all()
        
        settings = gtk.settings_get_default()
        settings.props.gtk_button_images = True

        self.win = window
        
        # set first item, the rest is set by next_image
        imgpath = os.path.join(self.basepath, self.photo_id)
        title = self.album[self.photo_id]['title']
        text = self.album[self.photo_id]['text']
        self.set_content(imgpath, title, text)
        self.photoindex += 1
    
    def on_cancel_button_clicked(self, widget):
        self.parent.save_editor(self.entry_title.get_text(), self.E.get_all_text(), self.photo_id)
        return self.quit_dialog(_("Do you want to stop this editor ? \nAll your changes are already saved."))
    
    def on_next_button_clicked(self, widget):
        self.next_image()
            
    def next_image(self):
        if self.photoindex > len(self.filelist) - 1:
            self.photoindex = 0
        self.photo_id = os.path.basename(self.filelist[self.photoindex])
        imgpath = os.path.join(self.basepath, self.photo_id)
        title = self.album[self.photo_id]['title']
        text = self.album[self.photo_id]['text']
        self.set_content(imgpath, title, text)
        self.photoindex += 1
       
        
    def set_content(self, imagepath, title, text):
        img = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(imagepath)
        scaled_buf = pixbuf.scale_simple(400,300,gtk.gdk.INTERP_BILINEAR)
        img.set_from_pixbuf(scaled_buf)
        img.show() 
        self.image_layout.put(img,200,4)
        self.E.set_text(text)
        self.entry_title.set_text(title)
        
    
if __name__ == '__main__':
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
    class parent:
        def save_editor(self, *args):
            print args
    t = gtkTextEditor(parent(), None)
    t.run()
            
        
        
