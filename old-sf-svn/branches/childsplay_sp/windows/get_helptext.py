#! /usr/bin/env python

# Script to extract the help text from the activities, must be placed in
# the CP base sourcetree.
# It will import all the activities in ./lib and parse the helptext in
# all supported languages.
# It writes all the translations to files called get_helptext_#language".txt
# Output is formatted in the Wikidot syntax and can be copied directly in the online editor

# These languages are currently supported and will be used to translate
# the helptext. Extend when new langauges are added.
SUPPORTED = ['en', 'it','ar','nl','es','ca','de','fr','el','nb', 'pl', 'ro']

import os,sys,imp
import pygame,logging
from pygame.constants import KEYDOWN, K_ESCAPE
pygame.init()
scr = pygame.display.set_mode((500,40))
scr.fill((255,255,255))

import utils
s = utils.char2surf("Proccessing activity modules, please wait",18)
scr.blit(s,(8,8))
pygame.display.update()

import gettext

import childsplay_sp.SPLogging as SPLogging
SPLogging.set_level('debug')
SPLogging.start()
import SPConstants

class SPG:
    """Fake SPGoodies class, needed to get an Activity class instance"""
    def __init__(self):
        self.logger = logging.getLogger("fake_goodies")
        self.screen = pygame.Surface((1,1))
        self.background = self.screen
        self.screenclip = (0,0,0,0)
        self.virtkb = None
        self.level_end = None
        self.game_end = None
        self.localesetting = ''
        self.lock = None
        self.info_dialog = None
        self.display_execounter = None
        self.set_framerate = None
    def tellcore_level_end(self,store_db=None):
        pass
    def tellcore_game_end(self,store_db=None):
        pass
    def tellcore_info_dialog(self,text):
        pass
    def tellcore_display_execounter(self,total,text=''):
        pass
    def tellcore_set_framerate(self,rate):
        pass
    # these methods provide stuff needed by the activity.
    def get_screen(self):
        return self.screen
    def get_background(self):
        return self.screen
    def get_virtual_keyboard(self):
        pass
    def get_localesetting(self):
        return ("","")
    def get_screenclip(self):
        return self.screenclip
    def get_thread_lock(self):
        return self.lock
    def get_theme(self):
        pass
    # paths related to the place where SP is currently installed
    def get_libdir_path(self):
        """path to the 'lib' directory were activities store there stuff"""
        return SPConstants.ACTIVITYDATADIR
    def get_absdir_path(self):
        """path to the 'alphabetsounds directory"""
        return SPConstants.ALPHABETDIR 
   
   
def import_module(filename, globals=None, locals=None, fromlist=None):
    """ Import any module without changes to sys.path.
      Taken from the library reference.(Never invent the wheel twice)"""
    # Fast path: see if the module has already been imported.
    try:
        return sys.modules[filename]
    except KeyError:
        pass
    path, name = os.path.split(filename)
    name, ext = os.path.splitext(name)
    fp = None    
    try:
        fp, pathname, description = imp.find_module(name,[path])
        return imp.load_module(name, fp, pathname, description)
        print "import succeeded: %s, %s, %s" % fp, pathname, description
        if fp: fp.close()
    except Exception,info:
        print "Import of %s failed" % filename
        print info
        if fp: fp.close()

modules = filter(lambda x: '.py' in x,os.listdir('./lib'))
print "found: %s" % modules

for module in modules:
    if module == '__init__.py' or module[-3:] == 'pyc':
        continue
    for lang in SUPPORTED:
        events = pygame.event.get()
        for event in events:
            if event.type is KEYDOWN and event.key is K_ESCAPE:
                sys.exit(0)
        print "set language to %s" % lang
        utils.set_locale(lang)
        M = os.path.join('.','lib',module)
        print "trying to import",M
        print "importing %s" % M
        m = import_module(M[:-3])
        a = m.Activity(SPG())
        l = []
                
        l.append('\n-------------------------------------------------------------')
        text = u"++ "
        l.append(text + (_('Short description\n')))
        l.append(a.get_helptitle())
        text = u"\n++ "
        l.append(text + (_('Screenshot\n')))
        l.append('[[table style="margin: 0 10px;"]]')
        l.append('[[row]]')
        l.append('[[cell style="padding: 10px; border: 0px; width: 100%;"]]')
        l.append('[[div  class="p-shadow" style="background-color:#EEE;border:0px solid #000;width:510px;"]]')
        text = u' [[image /childsplay-%s/CP_%s.gif size="medium"]]' % (module[:-3], module[:-3])
        l.append(text + (_('Click image to enlarge')))
        l.append('[[/div]]') 
        l.append('[[/cell]][[/row]][[/table]]')
        text = u'\n++ '
        l.append(text + (_('Goal of the activity')))
        for line in a.get_help():
            l.append(line)
        text = u'\n++ '
        l.append(text + (_('Tips')))
        for line in a.get_helptip():
            l.append(line)
        text = u'\n++ '
        l.append(text + (_('Type of activity')))
        l.append(a.get_helptype())
        text = u'\n++ '
        l.append(text + (_('Information')))
        l.append('* %s' % a.get_helplevels())
        text = u'* '
        l.append(text + (_('filename: %s') % module))
        f = open('get_helptext_out_%s.txt' % lang,'a')
        f.write('\n'.join(l).encode('utf-8'))
        f.close()
