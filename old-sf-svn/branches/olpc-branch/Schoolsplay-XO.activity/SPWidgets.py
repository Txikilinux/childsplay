# -*- coding: utf-8 -*-

# Copyright (c) 2007 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPWidgets.py
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
import pygtk
pygtk.require('2.0')
import gtk
import pango

import logging

def xpm_label_box(img_filename, label_text=''):
    """Create a new hbox with an image and a label packed into it
       and return the box.
       Used to construct image buttons.
    """
    # Create box for xpm and label
    box1 = gtk.HBox(False, 0)
    box1.set_border_width(2)

    # Now on to the image stuff
    image = gtk.Image()
    image.set_from_file(img_filename)

    if label_text:
        # Create a label for the button
        label = gtk.Label(label_text)

    # Pack the pixmap and label into the box
    box1.pack_start(image, False, False, 3)
    if label_text:
        box1.pack_start(label, False, False, 3)
        label.show()
        
    image.show()
    return box1

class WarningDialog(gtk.MessageDialog):
    def __init__(self,parent=None,flags=gtk.DIALOG_MODAL,type=gtk.MESSAGE_WARNING,
                    buttons=gtk.BUTTONS_CLOSE,message_format='',txt=''):
        gtk.MessageDialog.__init__(self,parent=parent,
                            flags=flags,
                            type=type,
                            buttons=buttons,
                            message_format=message_format)
        self.connect("response", self.response)
        self.set_markup('%s%s%s' % ('<big>',txt,'</big>'))
        self.show()
    def __call__(self):
        self.show()
        self.run()
    def response(self,*args):
        """destroys itself on a respons, we don't care about the response value"""
        self.destroy()
        
class ErrorDialog(WarningDialog):
    def __init__(self,txt):
        WarningDialog.__init__(self,parent=None,
                            flags=gtk.DIALOG_MODAL,
                            type=gtk.MESSAGE_ERROR,
                            buttons=gtk.BUTTONS_CLOSE,
                            message_format='',
                            txt=txt)
        
class InfoDialog(WarningDialog):
    def __init__(self,txt):
        WarningDialog.__init__(self,parent=None,
                            flags=gtk.DIALOG_MODAL,
                            type=gtk.MESSAGE_INFO,
                            buttons=gtk.BUTTONS_CLOSE,
                            message_format='',
                            txt=txt)
        
class YesNoDialog(gtk.MessageDialog):
    def __init__(self,parent=None,flags=gtk.DIALOG_MODAL,type=gtk.MESSAGE_INFO,
                    buttons=gtk.BUTTONS_YES_NO,message_format='',txt=''):
        gtk.MessageDialog.__init__(self,parent=parent,
                            flags=flags,
                            type=type,
                            buttons=buttons,
                            message_format=message_format)
        #self.connect("response", self.response)
        self.set_markup('%s%s%s' % ('<b>',txt,'</b>'))
            
        
class GraphDialog(gtk.Dialog):
    def __init__(self,parent=None,data=[],norm=None,header=''):
        gtk.Dialog.__init__(self,parent=None,flags=gtk.DIALOG_MODAL)
        self.vbox.pack_start(gtk.Label(header))
        g = Graph(parent=self,data=data,norm=norm)
        img = gtk.Image()
        img.set_from_pixmap(g.get_pixmap(), None)
        img.show()
        self.vbox.pack_start(img)
        lb = g.get_labelbox()
        print lb
        if lb:
            self.vbox.pack_end(lb)
        # close button	#
        close_button = gtk.Button(None, 'gtk-close')
        close_button.connect('clicked', self.response)
        close_button.show()
        self.action_area.pack_start(close_button)
        
        self.connect("response", self.response)
        print "dialog called"
        self.show_all()
        self.run() 
        
    def response(self,*args):
        """destroys itself on a respons, we don't care about the response value"""
        self.destroy()
        

class Graph():
    """Draws a graph on a gdk Pixmap."""
    def __init__(self,parent=None,data=[],norm=None):
        self.logger = logging.getLogger("schoolsplay.SPWidgets.Graph")
        self.logger.debug("Start")
        self.width  = 500 # updated in size-allocate handler
        self.height = 330 # idem
        # This is the drawable we use as our offscreen canvas
        self.pixm = gtk.gdk.Pixmap(None, self.width,self.height, 24)
        # box to hold labels stuff
        self.labelbox = gtk.HBox()
        # setup the pango stuff
        self.pangolayout = parent.create_pango_layout('')
        # create a font description
        font_desc = pango.FontDescription('Sans 10')
        # tell the layout which font description to use
        self.pangolayout.set_font_description(font_desc)
        # Set some colors
        cmap = self.pixm.get_colormap()
        self.WHITE = cmap.alloc_color('white')
        self.BLACK = cmap.alloc_color('black')
        self.RED = cmap.alloc_color('red')
        self.BLUE = cmap.alloc_color('blue')
        self.LBLUE = cmap.alloc_color('lightblue')
        self.gc = gtk.gdk.GC(self.pixm)
        # fill background with white otherwise the screen background is used :-(
        self.gc.set_foreground(self.WHITE)
        self.pixm.draw_rectangle(self.gc, True, 0, 0, self.width,self.height)
        self.gc.set_foreground(self.BLACK)
        # make sure we do have data to display
        if not data:
            font_desc = pango.FontDescription('Serif 16')
            self.pangolayout.set_font_description(font_desc)
            self.pangolayout.set_text('%s' % "No data available for this level")
            self.pixm.draw_layout(self.gc,
                                60, 150,
                                self.pangolayout)
            return
            
        # As there's no easy way to draw vertical text on a canvas we use a 
        # a table with label widgets that have their angle set to 90 degrees
        self.labeltable = gtk.Table(rows=1, columns=len(data), homogeneous=True)
        # set some constants
        step = 30 # by how much do we increase the score values to get grid positions 
        y_offset = 7 # offset y to leave room for the score values 
        self.context = self.pixm.cairo_create()
        # draw mu line and sigma deviation as a lightblue box.
        if norm:
            mu,sigma = norm
            # if mu == 10 then a score of ten would be mu
            # mu is mostly 5, so 5*30 = 150, the middle of the pixmap
            # x has an ofset of 30 to get room for text
            mu_y = mu*step
            
            # deviation box, transparent blue
            # the sigma value is the percentage of the mu value
            top_y = int(mu_y - ((mu_y/100.0) * sigma))
            bottom_y = int(mu_y + ((mu_y/100.0) * sigma) - top_y)
            self.gc.set_foreground(self.LBLUE)
            self.pixm.draw_rectangle(self.gc, True, step,top_y+y_offset, self.width-step,bottom_y)
            # line
            self.gc.set_background(self.WHITE)
            self.gc.set_foreground(self.BLUE)
            self.gc.set_line_attributes(line_width=3,\
                                        line_style=gtk.gdk.LINE_SOLID,\
                                        cap_style=gtk.gdk.CAP_BUTT,\
                                        join_style=gtk.gdk.JOIN_MITER)
            self.pixm.draw_line(self.gc, step,mu_y+y_offset, self.width,mu_y+y_offset)
        # draw y-axes graph lines, initial y offset is 30 pixels to leave room for text
        i = 10
        for y in range(0,330,step):
            self.gc.set_line_attributes(line_width=1,\
                                        line_style=gtk.gdk.LINE_SOLID,\
                                        cap_style=gtk.gdk.CAP_BUTT,\
                                        join_style=gtk.gdk.JOIN_MITER)
            self.pixm.draw_line(self.gc, step,y+y_offset, self.width,y+y_offset)
            self.pangolayout.set_text('%d' % i)
            self.pixm.draw_layout(self.gc,
                                step-20, y,
                                self.pangolayout)
            i -= 1
        # Draw x-axes data
        # determine the size of the x graph steps. This depends on the number of data items.
        # as we fill the x axe. Y step is always the same as the y axe values are always 0-10.
        # The maximum is 470 items, one pixel per data item.
        x_step = 470/len(data)
        dotslist = []
        i = 0 #table row index
        # draw dots and x-axes lines
        for x in range(step,500,x_step):
            self.gc.set_foreground(self.BLUE)
            self.pixm.draw_line(self.gc, x,0, x,self.height)
            try:
                item = data.pop(0)
                #print item
                y = int(self.height-(item[1]+1)*step)+y_offset
                #print "y position",y
                date = item[0]
                #print "date",date
            except IndexError:
                self.logger.exception("Troubles in the datalist, this shouldn't happen")
                break
            else:
                self.gc.set_foreground(self.RED)
                self.pixm.draw_arc(self.gc, True, x-3, y-3, 6, 6, 0, 360*64)  
                dotslist.append((x,y))
                # we use labels that are rotated 90 degrees
                lbl = gtk.Label(date)
                lbl.set_property('angle',90)
                self.labeltable.attach(lbl, left_attach=i, right_attach=i+1,\
                                            top_attach=0, bottom_attach=1,\
                                            xoptions=gtk.EXPAND|gtk.FILL,\
                                            yoptions=gtk.EXPAND|gtk.FILL,\
                                            xpadding=0, ypadding=0)
                i += 1
        # put the table in the box with the same offset as the x-axes so that 
        # the labels lign up. 
        fr = gtk.Frame()
        fr.set_shadow_type(gtk.SHADOW_NONE)
        fr.set_size_request(self.width-step, 100)
        fr.add(self.labeltable)
        self.labelbox.pack_start(gtk.Label(), expand=False, fill=False, padding=step/2)
        self.labelbox.pack_start(fr,expand=True, fill=True, padding=0)
        self.labelbox.pack_end(gtk.Label(), expand=False, fill=False, padding=step/2)
        # connect the dots if there are more then one
        if len(dotslist) > 1:
            self.gc.set_foreground(self.RED)
            for i in range(0,len(dotslist)-1):
                x0,y0 = dotslist[i]
                x1,y1 = dotslist[i+1]
                self.pixm.draw_line(self.gc, x0,y0, x1,y1)
   
    def get_pixmap(self):
        return self.pixm
    def get_labelbox(self):
        return self.labelbox
        
if __name__ == '__main__':
    # test code
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    lbl = gtk.Label("close me last")
    #lbl.set_property('angle',90)
    print lbl.window
    win.add(lbl)
    win.connect('delete_event',gtk.main_quit)
    win.show_all()
    
    #WarningDialog(txt='WarningDialog')
    #ErrorDialog(txt='ErrorDialog')
    #InfoDialog(txt='InfoDialog')    
    
    # YesNoDialog is different as we want a respons value
    #dlg = YesNoDialog(txt='YesNoDialog')
    #respons = dlg.run()
    #print 'respons from YesNoDialog',respons
    
    # dates are like this 07-09-09_10:44:27
    # we ditch the second part
    data = [('07-09-09_10:44',3.899),\
            ('07-09-09_11:44',4.867),\
            ('07-09-09_12:44',5.34),\
            ('07-09-09_13:44',6.36),\
            ('07-09-09_14:44',6.5),\
            ('07-09-09_15:44',7.0),\
            ('07-09-09_16:44',6.5),\
            ('07-09-10_17:44',5.90),\
            ('07-09-10_18:34',4.896),\
            ('07-09-10_19:20',3.20)]
    
    GraphDialog(data=data,norm=(5,50))
    
    gtk.main()


