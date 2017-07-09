# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           utils.py
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

import logging
module_logger = logging.getLogger("schoolsplay.utils")

import os,sys,fnmatch,traceback,imp,glob,locale,\
        gettext,__builtin__,shutil,types,string,datetime,time
import gtk

##import pygame
##from pygame.constants import *

from SPConstants import *

UT_DEBUG = 0

class MyError(Exception):
    def __init__(self,str,line=''): 
        self.line = line
        self.str = str
    def __str__(self): return "%s: %s" % (self.line,self.str)

class SPError(Exception):
    pass
class NoSuchTable(SPError):
    pass
class ReporterError(SPError):
    pass
class XMLParseError(SPError):
    pass
    
def trace_error():
    """returns a stack trace"""
    return traceback.format_exc()
    
def set_locale(lang=None):
    # pyfribidi comes from SPConstants
    global LOCALE_RTL,pyfribidi
    module_logger.debug("set_locale called with %s" % lang)
    txt = ""
    try:
        if not lang or lang == 'system':
            try:
                # FIX locale.py LANGUAGE parsing bug, the fix was added on the
                # upstream CVS on the 1.28.4.2 revision of 'locale.py', It
                # should be included on Python 2.4.2.
                if os.environ.has_key('LANGUAGE'):
                    lang = os.environ['LANGUAGE'].split(':')[0]
                else:
                    lang = locale.getdefaultlocale()[0]
            except ValueError, info:
                module_logger.error(info)
                lang = 'en'
        languages = [ lang ]
        if os.environ.has_key('LANGUAGE'):
          languages += os.environ['LANGUAGE'].split(':')
        module_logger.info("Setting childsplay locale to '%s'" % (lang))
        lang_trans = gettext.translation('schoolsplay',\
                                     localedir=LOCALEDIR,\
                                     languages=languages)
        __builtin__.__dict__['_'] = lang_trans.ugettext
    except Exception, info:
        txt=""
        if lang and lang.split('@')[0].split('.')[0].split('_')[0] != 'en':
            txt = "Cannot set language to '%s' \n switching to English" % lang
            module_logger.info("%s %s" % (info,txt))
        __builtin__.__dict__['_'] = lambda x:x
        lang = 'en'
    else:
        lang = lang.split('@')[0].split('.')[0].split('_')[0]
    # This is to signal that we running under a RTL locale like Hebrew or Arabic
    # Only Hebrew and Arabic is supported until now
    if lang in ['he','ar']:
        if pyfribidi:
            LOCALE_RTL = True
        else:
            text = "Your locale needs RTL support, but I can't find pyfribidi.\n"+\
                    "Your locale needs RTL support, but I can't find pyfribidi.\n"+\
                    "See http://hspell-gui.sourceforge.net/pyfribidi.html.\n"+\
                    "Cannot set language to '%s' \n switching to English" % lang
            module_logger.error(text)
            lang = 'en'
    return (lang,LOCALE_RTL)
    
def get_locale():
    """Get the systems locale.
    This can be different from the locale used by childsplay.(see set_locale())"""
    try:
        lang = ''
        # FIX locale.py LANGUAGE parsing bug, the fix was added on the
        # upstream CVS on the 1.28.4.2 revision of 'locale.py', It
        # should be included on Python 2.4.2.
        if os.environ.has_key('LANGUAGE'):
            lang = os.environ['LANGUAGE'].split(':')[0]
        # This makes sure that we never return a value of None.
        # This is a fix for systems that set LANGUAGE to ''.
        if lang == '':
            lang = locale.getdefaultlocale()[0]
    except Exception,info:
        module_logger.error("%s, %s" % info,"Switching to English")
        lang = 'en'
    if lang == 'C' or lang.lower() == 'posix':
        # Default to English
        lang = 'en'
    return lang
    
## Work in progress, to be used in conjuction with a RTL language
def _check_LocaleIsRTL(seq):
    """This will check if we should use different stuff for the locale.
    Returns -> tuple: ttf font to use, reversed seq.
    """
    rtl_ttf,rtl_seq = None,seq
    # Hebrew and Arabic is supported
    try:
        loc =  get_locale()[:2].split('@')[0].split('.')[0].split('_')[0]
        if loc not in ['he','ar']:
            return (None,seq)
    except Exception,info:
        module_logger.error("%s, %s" % (info,"Error checking locale setting\nMake sure your locale is configured properly"))
        return (None,seq)
    if type(seq) is types.ListType:
        rtl_seq = []
        for line in seq:
            if UT_DEBUG:
                print "from gettext",line.encode('utf-8')
                print "from pyfribidi",pyfribidi.log2vis(line.encode('utf-8'))
            rtl_seq.append(unicode(pyfribidi.log2vis(line.encode('utf-8')),'utf-8'))
    else:
        if UT_DEBUG:
            print "from gettext",seq.encode('utf-8')
            print "from pyfribidi",pyfribidi.log2vis(seq.encode('utf-8'))
        rtl_seq = unicode(pyfribidi.log2vis(seq.encode('utf-8')),'utf-8')
    if loc == 'he':
        if os.path.exists('/usr/share/fonts/truetype/freefont/FreeSans.ttf'):
            rtl_ttf = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
        elif os.path.exists('/usr/local/share/fonts/truetype/freefont/FreeSans.ttf'):
            rtl_ttf = '/usr/local/share/fonts/truetype/freefont/FreeSans.ttf'
        elif os.path.exists(os.path.join(DATADIR,'he.ttf')):
            rtl_ttf = os.path.join(DATADIR,'he.ttf')
        else:
            module_logger.info("No suitable fonset found for your locale")
            rtl_ttf = None
    elif loc == 'ar':
        if os.path.exists('usr/share/fonts/truetype/ttf-arabeyes/ae_AlMohanad.ttf'):
            rtl_ttf = 'usr/share/fonts/truetype/ttf-arabeyes/ae_AlMohanad.ttf'
        elif os.path.exists('usr/share/fonts/truetype/ttf-arabeyes/ae_AlMohanad.ttf'):
            rtl_ttf = 'usr/share/fonts/truetype/ttf-arabeyes/ae_AlMohanad.ttf'
        elif os.path.exists(os.path.join(DATADIR,'ae_AlMohanad.ttf')):
            rtl_ttf = os.path.join(DATADIR,'ae_AlMohanad.ttf')
        else:
            module_logger.info("No suitable fonset found for your locale")
            rtl_ttf = None
    if UT_DEBUG: print "using fontset %s \nfor RTL locale" % rtl_ttf
    return (rtl_ttf,rtl_seq)

def read_unicode_file(path,lines=1):
    import codecs
    file = []
    try:
        f = codecs.open(path, 'r',encoding='utf-8')
        if lines:
            file = f.readlines()
        else:
            file = f.read()
    except Exception,info:
        module_logger.exception("Error reading: %s" % path)
        return None
    return file

def hex2ascii(hc):
    """Converts a hex string representing an char 0-9/a-z into a unicode string.
    Use this only for converting the alphabet soundfile names.
    'U0031' -> '1'""" 
    name = hc.replace('U','0x')
    i = int(hex(eval(name)),16)
    text = unichr(eval(hex(i)))
    return text

def ascii2hex(sc):
    """Converts a ascii string representing an char 0-9/a-z into a unicode hex string.
    Use this only for converting the alphabet soundfile names.
    u'1' -> 'U0031'"""
    hs = 'U%s' % (hex(ord(unicode(sc,'utf8')))[2:].zfill(4))
    return hs

def map_keys(key_map,key):
    """map_keys --> mapped key when a map is specified else the key is returnt
    unchanged.
    @key_map is the keymap to use or None when no mapping is needed.
    @key is the key to map.
    Used to provide a keymapping for Hebrew, Arabic and Russian."""
    if not key_map:
        return key
    if key in dict.keys(key_map):
        return key_map[key]
    return key

def replace_rcfile():
    """This is only used when we want to replace an existing configfile."""
    #pass #enable this and comment out the rest when not replacing
    src = os.path.join(RCDIR,CHILDSPLAYRC)
    dst = os.path.join(HOMEDIR,'ConfigData',CHILDSPLAYRC) 
    if os.path.exists(src) and os.path.exists(dst):
        shutil.move(dst,dst+'.old')
        module_logger.info("Backup made from your old config file called %s." % dst+'.old')
        module_logger.info("Replace childsplayrc file:\n %s\n->%s" % (src,dst))
        shutil.copyfile(src,dst)

class NoneSound:
    """Used by the load_sound and load_music functions to provide
     a bogus sound object.
     You can also test if your object is a NoneSound object or not.
     if sndobject == 'NoneSound' or if sndobject != 'NoneSound'."""
    def play(self,loop=None):
        pass
    def stop(self):
        pass
    def queue(self):
        pass
    def __eq__(self,other):
        if other == 'NoneSound': return True
        else: return False
    def __ne__(self,other):
        if other != 'NoneSound': return True
        else: return False

class MusicObject:
        """This is a wrapper around pygame.music"""
        def __init__(self,filename):
            self.s = filename
        def __eq__(self,other):
            if other == 'MusicObject': return True
            else: return False
        def __ne__(self,other):
            if other != 'MusicObject': return True
            else: return False
        def play(self,loop=0):
            """loop defaults to 0. values > 0 to loop a number of times.
            -1 means loop forever."""
            pygame.mixer.music.load(self.s)
            pygame.mixer.music.play(loop)
        def stop(self):
            pygame.mixer.music.stop()
        def queue(self):
            pygame.mixer.music.queue(self.s)

def load_sound(name):
    """Loads a sound -> pygame sound object.
      If no file can be loaded return a dummy class"""
                
    if not pygame.mixer or not pygame.mixer.get_init():
        module_logger.info('Cannot load sound: %s, no mixer initialized' % name)
        module_logger.info('Using Nonesound')
        return NoneSound()
    try:
        sound = pygame.mixer.Sound(name)
    except pygame.error, message:
        module_logger.info('Cannot load sound: %s ' % name)
        module_logger.info('Using Nonesound')
        return NoneSound()
    return sound

def load_music(file):
    """  Set up music object, if the music can't be loaded a bogus object will be returnt.
     Beware that due to SDL limitations you can only have one music source loaded.
     This means that even when you have multiple pygame instances, there can only be one
     music source. This function returns a filename wrapped in a sound like object with
     a play and stop method.
     For multiple sources use the pygame.Sound and wave combination.
     """    
    if not pygame.mixer or not pygame.mixer.get_init():
        module_logger.info('Cannot load sound: %s, no mixer initialized' % file)
        return NoneSound()
    if not os.path.exists(file):
        module_logger.info('Cannot load sound: %s' % file)
        module_logger.info('Using Nonesound')
        playmusic = NoneSound()
    else:
        playmusic = MusicObject(file)

    return playmusic

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
        if fp: fp.close()
    except (StandardError,MyError),info:
        module_logger.exception("Import of %s failed" % filename)
        raise MyError,info
        if fp: fp.close()
    

def __string_split(line, split):
    """ Split a string at the first space left from split index
      in two pieces of 'split' length -> two strings,
      where the first is of length 'split'.
      The second string is the the rest or None
      line = string
      split = integer
      """
    while line[split] != " " or split == 0:
        split -= 1
    line1 = line[:split]
    line2 = line[split+1:]#loose the space
    
    return line1, line2

def txtfmt(text, split):
    """ Formats a list of strings in a list of strings of 'split' length.
       returns a new list of strings. This depends on utils.__string_split().
       text = list of strings
       split = integer
       """
    newtxt = []
    left, right = "", ""
    for line in text:
        while len(line) > split:
            left, right = __string_split(line,split)
            newtxt.append((left.strip(' ')))
            line = right
        newtxt.append((line))
    txt = filter(None,newtxt)
    return txt

def current_time():
    """Maincore uses this to get the current time to set the 'time_start'
    and 'time_end' values in the dbase table"""
    return time.strftime("%y-%m-%d_%H:%M:%S", time.localtime())
def calculate_time(start,end):
    """The 'end'time is substracted from 'start'time and the result time is
    returned in a format suitable to put into the dbase.
    Times must be in the format as returnt from current_time.
    """
    logger = logging.getLogger("schoolsplay.utils.calculate_time")
    logger.debug("Called with start:%s, end:%s" % (start,end))
    start = start.replace('-',':').replace('_',':')
    end = end.replace('-',':').replace('_',':')
    arg_key0 = [int(s) for s in start.split(':')]
    arg_key1 = [int(s) for s in end.split(':')]
    #t1 = datetime.datetime.now()
    #t2 = datetime.datetime.now()
    #t3 = t2-t1
    #t3.seconds / 60
    #t3.seconds % 60
    dt0 = datetime.datetime(*arg_key0)
    dt1 = datetime.datetime(*arg_key1)
    dt2 = dt1 - dt0
    h, m = dt2.seconds / 60, dt2.seconds % 60
    return "%02d:%02d" % (h,m)
        
def _set_lock(timeout=10):
    """Set a lock file to prevent starting multiple instances of childsplay_sp.
    It will first look if a lock has been set previously, if so it will check the
    'epoch time' and when it's @timeout seconds in the past it will remove the lock
    and set a new one.
    The timeout is done to prevent stale locks that will prevent restarting childsplay
    in case of a crash.
    The maincore will also register a _remove_lock function at the atexit class."""
    if os.path.exists(LOCKFILE):
        try:
            f = open(LOCKFILE,'r')
            lines = f.readlines()
            t = float(lines[0][:-1])
        except (IOError,TypeError):
            module_logger.exception("failed to read master lockfile")
            _remove_lock()
            return True
        if time.time() - t < timeout:
            module_logger.info("Lock timeout not yet reached")
            return False
        else:
            _remove_lock()
            return True
    module_logger.info("Setting master lock: %s" % LOCKFILE)
    t = str(time.time())
    try:
        f = open(LOCKFILE,'w')
        f.write(t)
        f.close()
    except IOError:
        module_logger.exception("failed to set master lockfile")
        _remove_lock()
        return False
    else:
        module_logger.debug("Lock set to %s" % t)
        f.close()
        return True
    
def _remove_lock():
    """Used to cleanup any locks"""
    module_logger.info("Removing master lock")
    if os.path.exists(LOCKFILE):
        try:
            os.remove(LOCKFILE)
        except IOError:
            module_logger.exception("failed to remove master lockfile")
            module_logger.error("Please remove lock file: % manually" % LOCKFILE)
    
def Zscore(s_list,mean,sd):
    """Returns the zscores in a list with the coresponding dates
    calculated from the given parameters.
    @s_list is a list with tuples: [(date,score),(date,score)....]
    @mean is an float holding the mean from the dbase
    @sd is an float holding the sd from the dbase
    
    The z - Score is simply the number of Standard Deviation units a student's
    raw score is above or below the mean.  It has a one-to-one relationship with
    the standard deviation unit; 
    one z-score unit = one standard deviation unit and a z-score of zero is the mean.
    Further discussion of the standard deviation unit as well as it's use in 
    analyzing student scores is beyond the scope of this document.
    The z - Score is arrived at by taking the raw score for a student,  
    subtracting the mean (average) of all student scores and dividing by 
    the standard deviation of the student raw scores.
    
    zS = (RS - Mean) / SD
    Where:
    zS is the z - Score for the Student
    RS is the student's raw score
    Mean is the mean (average) of the student raw scores
    SD is the Standard Deviation of the student raw scores.
    """
    module_logger.debug("Zscore called with:%s,%s,%s" % (s_list,mean,sd))
    # we unpack the score/date list, make the calculation and build
    # a new score/date list
    new_s_list = []
    for date,rs in s_list:
        zs = (float(rs) - float(mean)) / float(sd)
        module_logger.debug("rs: %s, mean:%s, sd:%s, zscore:%s" % (rs,mean,sd,zs))
        new_s_list.append((date,zs))
    return new_s_list
    
def Percentile(z_list):
    """Returns a list with all the percentile values and dates"""
    pass
    # See http://www.ehow.com/how_2310404_calculate-percentiles.html
    # L/N * 100 == P
    
def validate_entry_cells(e_list):
        """Called by the activity when there's a solution button event
        First we check that all the entries have text.
        Then we check if all the entries integers.
        If not we flag the entry as fault by coloring the background red
        and the solution check failed.
        It returns the number of faulty entries or 0 if all the entries
        have valid text.
        """
        # First we reset all the entry colors as we could have set them to red the 
        # previous time.
        wrongsolutions = 0
        for e in e_list:
            e.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(WHITE))
        correct = True
        for e in e_list:# we just go want to know the values, so we don't use the matrix
            if not e.get_text():
                wrongsolutions += 1
                e.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(RED))
                correct = False
            else:
                try:
                    i = int(e.get_text())
                except ValueError:
                    # not an integer
                    wrongsolutions += 1
                    # reset entry
                    e.set_text('')
                    # color border red
                    e.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(RED))
                    # set a flag
                    correct = False
        if not correct:
            # enties contain non numeric characters or are empty.
            return wrongsolutions
        else:
            return 0
            
