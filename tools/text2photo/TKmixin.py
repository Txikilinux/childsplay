# Taken from the book Programming Python
# No license.
##############################################################################
# a "mixin" class for other frames: common methods for canned dialogs,
# spawning programs, simple text viewers, etc; this class must be mixed
# with a Frame (or a subclass derived from Frame) for its quit method
##############################################################################

import os
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import scrolledtext
#from PP3E.launchmodes import PortableLauncher, System

class GuiMixin:
    def infobox(self, title, text, *args):              # use standard dialogs
        return messagebox.showinfo(title, text)                    # *args for bkwd compat
    def errorbox(self, text):
        messagebox.showerror('Error!', text)
    def question(self, title, text, *args):
        return filedialog.askyesno(title, text)

    def notdone(self):
        filedialog.showerror('Not implemented', 'Option not available')
    def quit(self):
        ans = self.question('Verify quit', 'Are you sure you want to quit?')
        if ans == 1:
            Frame.quit(self)                            # quit not recursive!
    def help(self):
        self.infobox('RTFM', 'See figure 1...')         # override this better

    def selectOpenFile(self, file="", dir="."):         # use standard dialogs
        return filedialog.askopenfilename(initialdir=dir, initialfile=file)
    def selectSaveFile(self, file="", dir="."):
        return filedialog.asksaveasfilename(initialfile=file, initialdir=dir)

    def clone(self):
        new = Toplevel( )                   # make a new version of me
        myclass = self.__class__            # instance's (lowest) class object
        myclass(new)                       # attach/run instance to new window

    def spawn(self, pycmdline, wait=0):
        if not wait:
            os.PortableLauncher(pycmdline, pycmdline)( )     # run Python progam
        else:
            os.System(pycmdline, pycmdline)( )               # wait for it to exit

    def browser(self, filename):
        new  = Toplevel( )                                # make new window
        text = filedialog.ScrolledText(new, height=30, width=90)      # Text with scrollbar
        text.config(font=('courier', 10, 'normal'))        # use fixed-width font
        text.pack( )
        new.title("Text Viewer")                          # set window mgr attrs
        new.iconname("browser")
        text.insert('0.0', open(filename, 'r').read( ) )  # insert file's text

if __name__ == '__main__':
    class TestMixin(GuiMixin, Frame):      # standalone test
        def __init__(self, parent=None):
            Frame.__init__(self, parent)
            self.pack( )
            Button(self, text='quit',  command=self.quit).pack(fill=X)
            Button(self, text='help',  command=self.help).pack(fill=X)
            Button(self, text='clone', command=self.clone).pack(fill=X)
    TestMixin().mainloop( )
