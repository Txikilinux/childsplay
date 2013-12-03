#!/usr/bin/python
# Copyright (c) 2010 stas zytkiewicz stas.zytkiewicz@gmail.com
#
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


import sys, os
import glob
import shutil
import logging

from Tkinter import *                        # widget classes
from TKmixin import *        # mix-in methods
from TKguimaker import *        # frame, plus menu/toolbar builder
from ImageTk import PhotoImage, Image
from tkSimpleDialog import askstring

try:
    from xml.etree.ElementTree import ElementTree
except ImportError:
    # try the python2.4 way 
    from elementtree.ElementTree import ElementTree

XML_HEAD = \
"""<?xml version="1.0" encoding="utf-8"?>
<album name='%(albumname)s' nofPicture='%(numpics)s'>
"""
XML_END = \
"""</album>
"""
XML_NODE = \
"""     <photo name='%(name)s' >
        <title>%(title)s</title>
        <text>%(text)s</text>
    </photo>
"""

SUPPORTED_FILES = ['.png', '.jpg', '.jpeg', '.tiff']

class ScrolledList(Frame):
    def __init__(self, options, observer, parent=None):
        self.observer = observer
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)                  # make me expandable
        self.makeWidgets(options)
        
    def handleList(self, event):
        index = self.listbox.curselection( )              # on list double-click
        label = self.listbox.get(index)                   # fetch selection text
        self.runCommand(label)                            # and call action here
    
    def makeWidgets(self, options):                       # or get(ACTIVE)
        sbar = Scrollbar(self)
        self.listbox = Listbox(self, relief=SUNKEN)
        sbar.config(command=self.listbox.yview)                   # xlink sbar and list
        self.listbox.config(yscrollcommand=sbar.set)              # move one moves other
        sbar.pack(side=RIGHT, fill=Y)                     # pack first=clip last
        self.listbox.pack(side=LEFT, expand=YES, fill=BOTH)       # list clipped first
        self.set_content(options)
        
    def set_content(self, options):
        self.listbox.delete(0, END)
        pos = 0
        for label in options:                             # add to listbox
            self.listbox.insert(pos, label)                       # or insert(END,label)
            pos += 1
        self.listbox.config(selectmode=SINGLE, setgrid=1)         # select,resize modes
        self.listbox.bind('<Double-1>', self.handleList)          # set event handler
    
    def runCommand(self, selection):                      # redefine me lower
        self.observer(selection)

class Main(GuiMixin, GuiMakerWindowMenu):   # or GuiMakerFrameMenu

    def start(self):
        self.logger = logging.getLogger("schoolsplay.text2photo.TKgui.Main")
        self.logger.debug("Start Main")
        self.master.title(_("Add text to your photos."))
        self.master.iconname("text2photo Gui")
        self.menuBar = [                               # a tree: 3 pull downs
          ('File', 0,                                  # (pull-down)
              [ ('Open...', 0, self.fileOpen),\
              ('Save', 0, self.save_xml), \
              ('separator'), \
               ('Quit', 0, self.quit)]              # label,underline,action
          )]
        self.toolBar = [('OK', self.on_okbutton, {'side': RIGHT})]
        self.current_selection = None
        self.current_dir = None

    def makeWidgets(self):
        # left side scrolllist
        fr_0 = Frame(self)
        fr_0.pack()
        name = Label(fr_0, text = _('Picture names'))
        name.pack(expand=NO, fill=None, side=TOP, anchor=N) 
        piclist = ['']
        self.scrlist = ScrolledList(piclist, self._observer_scrolledlist, fr_0)
        self.scrlist.pack(side=LEFT, expand=NO, fill=Y)
        
        fr_0.pack(expand=NO, fill=Y, side=LEFT, anchor=N)
        # frame that holds image and text screens
        fr_1 = Frame(self)
        fr_1.pack(expand=YES, fill=BOTH)
        self.canvaslabel_text = StringVar()
        self.canvaslabel_text.set(_('Picture: %s') % piclist[0])
        name = Label(fr_1, textvariable=self.canvaslabel_text)
        name.pack(expand=NO, fill=None, side=TOP, anchor=N) 
        
        self.canvas_size = (410, 310)
        self.image_canvas = Canvas(fr_1, width=410, height=310)
        txt = _("Use the 'File' menu to open a directory with your pictures.\nDouble click on a image file name to select it.\nAdd a title and text and hit the 'OK' button. \nMake sure you save your work by using the 'File' menu.")
        y = 20
        for line in txt.split('\n'):
            self.image_canvas.create_text(10, y, text=line, anchor=NW)  
            y += 20
        self.image_canvas.pack(side=TOP, expand=YES, fill=BOTH)
        Label(fr_1, text=_("Title: ")).pack(side=LEFT, expand=NO, fill=None, anchor=N)        
        self.texttitle = Entry(fr_1, width=100)
        self.texttitle.pack(side=TOP, expand=YES, fill=X)
        
        #Label(fr_1, text=_("Text:")).pack(side=LEFT, expand=NO, fill=None, anchor=W)
        self.text_entry = Text(fr_1, width=100, height=10)
        self.text_entry.pack(side=LEFT, expand=YES, fill=X)
        
        fr_1.pack(expand=YES, fill=BOTH, side=LEFT, anchor=N)   
           
    def yes_no_dialog(self, title, text):
        return askyesno(title, text)
        
    def info_dialog(self, title, text):
        return showinfo(title, text)

    def quit(self):
        ans = self.question('Verify quit', 'Are you sure you want to quit?')
        if ans == 1:
            if self.current_dir:
                ans = self.question('Verify quit', 'Do you want to save the current album ?')
                if ans == 1:
                    self.save_xml()
            Frame.quit(self)                            # quit not recursive!    

    def fileOpen(self):
        # first we save any xmlnodes that we might have.
        if self.current_dir:
            self.save_xml()
        dlg = Directory(title=_('Select image directory to open'))
        pick = dlg.show()
        if pick:
            self.current_files_hash = {}
            self.current_dir = pick
            self.xml_hash = self.load_xml()
            for file in glob.glob(os.path.join(pick, '*.*')):
                if os.path.splitext(file)[1] not in SUPPORTED_FILES:
                    continue
                k = os.path.split(file)[1]
                self.current_files_hash[k] = file
            self.scrlist.set_content(self.current_files_hash.keys())
            self.albumname =  askstring("Album name", "Give the album name:", \
                                        initialvalue=self.xml_hash['albumname'])
            self.numpics = len(self.current_files_hash.keys())
            
    def _observer_scrolledlist(self, selection):
        self.logger.debug("_observer_scrolledlist called with: %s" % selection)
        p = self.current_files_hash[selection]
        if os.path.splitext(p)[1] in SUPPORTED_FILES:
            img = Image.open(p)
            if img.size[0] > 400:
                img = img.resize((400, 300))
            self.img = PhotoImage(image=img)
            self.image_canvas.delete('all')
            self.image_canvas.create_image(20, 5, image=self.img, anchor=NW)
            self.canvaslabel_text.set(_('Picture: %s' % p))
            self.text_entry.delete(1.0, END)
            self.texttitle.delete(0, END)
            self.current_selection = selection
            if self.xml_hash.has_key(self.current_selection):
                self.texttitle.insert(0, self.xml_hash[self.current_selection]['title'])
                self.text_entry.insert(1.0, self.xml_hash[self.current_selection]['text'])
            
    def on_okbutton(self, *args):
        self.logger.debug("on_okbutton called")
        if not self.current_selection:
            self.info_dialog(_("Warning"), _("No image selected."))
            return
        title = self.texttitle.get().strip()
        if not title:
            self.info_dialog(_("Warning"), _("No title text given."))
            return
        text = [l for l in self.text_entry.get(1.0, END).split('\n') if l.strip()]
        if not text:
            self.info_dialog(_("Warning"), _("No text given."))
            return
        self.xml_hash[self.current_selection] = {'name':self.current_selection, \
                                         'title': title, \
                                         'text':'\n'.join(text)}

    def save_xml(self):
        #TODO:What if the user edits text for an image that already has text ?
        if not self.current_dir:
            self.info_dialog(_("Warning"), _("No directory selected."))
            return
        xmlnodes = []
        xmlpath = os.path.join(self.current_dir, 'text.xml')
        if os.path.exists(xmlpath):
            # backup an existing file
            old_xmlpath = xmlpath + '~'
            shutil.copyfile(xmlpath, old_xmlpath)
            f = open(xmlpath, 'r')
            lines = [l for l in f.readlines()][1:-1]
            xmlnodes += lines
            
        xmlnodes.insert(0, XML_HEAD % {'albumname':self.albumname, \
                                            'numpics':self.numpics})
        for name, hash in self.xml_hash.items():
            if name in ('albumname', 'numpics'):
                continue
            xmlnodes.append(XML_NODE % hash)
        xmlnodes.append(XML_END)
        xml = ''.join(xmlnodes)
        f = open(xmlpath, 'w')
        f.write(xml)
        f.close()
    
    def load_xml(self):
        """Parses the whole xml tree into a hash with lists. Each list contains hashes
        with the elelements from a 'activity' element.
        """  
        p = os.path.join(self.current_dir, 'text.xml')
        self.logger.debug("Starting to parse: %s" % p)
        if not os.path.exists(p):
            return {'albumname': ''}
        tree = ElementTree()
        try:
            tree.parse(p)
        except Exception, info:
            self.logger.error("%s" % info)
            self.info_dialog(_("Warning"), str(info) + '\n' + _("Your text file is moved to text.xml.err"))
            shutil.move(p, p + ".err")
            return {'albumname': ''}
        # here we start the parsing
        albumNode = tree.getroot()
        album_name = albumNode.get('name')
        album_numpics = albumNode.get('nofPicture')
        
        photoNodes = tree.findall('photo')
        self.logger.debug("found %s photo nodes in total" % len(photoNodes))
        albumhash = {'albumname': album_name, 'numpics':album_numpics}
        for node in photoNodes:
            hash = {}
            try:
                hash['name'] = node.get('name')
                hash['title'] = node.find('title').text
                hash['text'] = node.find('text').text
            except AttributeError, info:
                self.logger.error("The %s is badly formed, missing element(s):%s,%s" % (xml, info, e))
                albumhash = {'albumname': ''}
            else:
                albumhash[hash['name']] = hash
        #self.logger.debug("xml hash:%s" % albumhash)
        return albumhash

if __name__ == '__main__':  
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
    
    Main().mainloop( )   # make one, run one
