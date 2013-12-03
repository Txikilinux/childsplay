# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
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

import __builtin__
import imp
import sys
from SPConstants import *
from NormalDistTable import normal_distribution_table
import gettext
import glob
import fnmatch
import locale
import logging
import os
if not NoGtk:
    import pangofont
import pygame
import shutil
import time
import datetime
import types
import ConfigParser
import math
from collections import MutableMapping
from pygame.constants import *
from pygame import surfarray
import textwrap
#from facedetect.facedetect import CAMFOUND
CAMFOUND = None
if CAMFOUND:
    import opencv.adaptors as adaptors
module_logger = logging.getLogger("childsplay.utils")

if NoGtk:
    module_logger.warning("NoGtk is set, not using GTK pango font rendering some non-latin characters might be missing.")


UT_DEBUG = 0

class StopGameException(Exception):
    # Raise this to quit outside the eventloop
    pass

class MyError(Exception):
    def __init__(self, str='', line=''):
        self.line = line
        self.str = str
    def __str__(self): return "%s" % self.str

class SPError(Exception):
    pass
class NoSuchTable(SPError):
    pass
class ReporterError(SPError):
    pass
class XMLParseError(SPError):
    pass
class StopmeException(Exception):
    pass
class RestartMeException(Exception):
    pass
class TextRectException(Exception):
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

###### For debugging memoryleaks #####################
#def memory_profile(h):
#    f = open('heap_profile.txt', 'a')
#    f.write('heap: \n%s' % h.heap())
#    f.write('\n\n')
#    hh = h.heap()
#    #f.write('heap byvia: \n%s' % hh.byvia)
#    f.write('Traversing Heap: \n%s' % hh.get_rp())
#    f.write('\n\n')
#    f.close()
#####################################################

def calcdist(v1, v2):
    """Calculate the distance between two vectors where a vector is a tuple (x,y)"""
    dx = v2[0] - v1[0]
    dy = v2[1] - v1[1]
    return math.sqrt(dx*dx + dy*dy)

def set_locale(lang=None):
    """Used by the core to set the locale.
    """
    module_logger.debug("set_locale called with %s" % lang)
    global LOCALE_RTL, LANG # These come from SPConstants
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
                    lang, enc = locale.getdefaultlocale()
                    lang = "%s.%s" % (lang, enc.lower())
            except ValueError, info:
                module_logger.error(info)
                lang = 'en'
        languages = [lang]
        if os.environ.has_key('LANGUAGE'):
            languages += os.environ['LANGUAGE'].split(':')
        module_logger.info("Setting seniorplay locale to '%s' modir: %s" % (lang, LOCALEDIR))
        lang_trans = gettext.translation('seniorplay', \
            localedir=LOCALEDIR, \
            languages=languages)
        __builtin__.__dict__['_'] = lang_trans.ugettext
    except Exception, info:
        txt = ""
        if lang and lang.split('@')[0].split('.')[0].split('_')[0] != 'en':
            txt = "Cannot set language to '%s' \n switching to English" % lang
            module_logger.info("%s %s" % (info, txt))
        __builtin__.__dict__['_'] = lambda x:x
        lang = 'en_US.utf8'
    else:
        lang = lang.split('@')[0]#.split('.')[0].split('_')[0]
    # This is to signal that we running under a RTL locale like Hebrew or Arabic
    # Only Hebrew and Arabic is supported until now
    if lang[:2] in ['he', 'ar']:
        LOCALE_RTL = True
    LANG = lang
    module_logger.debug("Locale set to %s, RTL set to %s" % (LANG, LOCALE_RTL))
    return (lang, LOCALE_RTL)

def get_locale_local():
    """Returns the locale set by set_locale.
    This can differ from systems locale."""
    return (LANG, LOCALE_RTL)

def get_locale():
    """Get the systems locale.
    This can be different from the locale used by childsplay.(see set_locale())"""
    global LOCALE_RTL
    try:
        lang = ''
        # FIX locale.py LANGUAGE parsing bug, the fix was added on the
        # upstream CVS on the 1.28.4.2 revision of 'locale.py', It
        # should be included on Python 2.4.2.
        if os.environ.has_key('LANGUAGE'):
            lang = os.environ['LANGUAGE'].split(':')[0].split('_')[0]
        # This makes sure that we never return a value of None.
        # This is a fix for systems that set LANGUAGE to ''.
        if lang == '':
            lang = locale.getdefaultlocale()[0].split('_')[0]
    except Exception, info:
        module_logger.error("%s, %s" % (info, "Switching to English"))
        lang = 'en'
    if lang == 'C' or lang.lower() == 'posix':
        # Default to English
        lang = 'en'
    # This is to signal that we running under a RTL locale like Hebrew or Arabic
    # Only Hebrew and Arabic is supported until now
    elif lang in ['he', 'ar']:
        LOCALE_RTL = True
    return (lang, LOCALE_RTL)

def read_rcfile(path):
    """Reads a config file and returns all the entries in a hash.
    Use this for the activity rc files.
    The core libs have their own specialized rc readers.
    """
    config = ConfigParser.ConfigParser()
    if not os.path.exists(path):
        module_logger.info("No rc file found at: %s" % path)
        return {}
    try:
        config.read(path)
    except Exception, info:
        module_logger.error("Failed to parse rc file: %s" % info)
        return {}
    hash = {}
    for section in config.sections():
        hash[section] = dict(config.items(section))
    return hash

def read_unicode_file(path, lines=1):
    import codecs
    file = []
    try:
        f = codecs.open(path, 'r', encoding='utf-8')
        if lines:
            file = f.readlines()
        else:
            file = f.read()
    except Exception:
        module_logger.exception("Error reading: %s" % path)
        return None
    return file

def hex2ascii(hc):
    """Converts a hex string representing an char 0-9/a-z into a unicode string.
    Use this only for converting the alphabet soundfile names.
    'U0031' -> '1'""" 
    if hc[1] == 'U':
        name = hc[1:]
    else:
        name = hc
    i = int(hex(name), 16)
    text = unichr(i)
    return text

def ascii2hex(sc):
    """Converts a ascii string representing an char 0-9/a-z into a unicode hex string.
    Use this only for converting the alphabet soundfile names.
    u'1' -> 'U0031'"""
    if type(sc) is types.UnicodeType:
        sc = str(sc)
    hs = 'U%s' % (hex(ord(unicode(sc, 'utf8')))[2:].zfill(4))
    return hs

def map_keys(key_map, key):
    """map_keys --> mapped key when a map is specified else the key is returnt
    unchanged.
    @key_map is the keymap to use or None when no mapping is needed.
    @key is the key to map.
    Used to provide a keymapping for Hebrew, Arabic and Russian."""
    if not key_map:
        return key
    try:
        km = getattr(KeyMaps, key_map)
    except AttributeError:
        module_logger.error("No keymap: %s found" % key_map)
        return key
    else:
        if km.has_key(key):
            return km[key]
        else:
            module_logger.error("No key: %s found" % key)
            return key

class NoneSound:
    """Used by the load_sound and load_music functions to provide
     a bogus sound object.
     You can also test if your object is a NoneSound object or not.
     if sndobject == 'NoneSound' or if sndobject != 'NoneSound'."""
    def play(self, loop=None):
        pass
    def stop(self):
        pass
    def queue(self):
        pass
    def get_volume(self):
        return None
    def set_volume(self, sound_value):
        pass
    def __eq__(self, other):
        if other == 'NoneSound': return True
        else: return False
    def __ne__(self, other):
        if other != 'NoneSound': return True
        else: return False

class MusicObject:
    """This is a wrapper around pygame.music"""
    def __init__(self, filename):
        self.s = filename
    def __eq__(self, other):
        if other == 'MusicObject': return True
        else: return False
    def __ne__(self, other):
        if other != 'MusicObject': return True
        else: return False
    def play(self, loop=0):
        """loop defaults to 0. values > 0 to loop a number of times.
            -1 means loop forever."""
        pygame.mixer.music.load(self.s)
        pygame.mixer.music.play(loop)
    def stop(self):
        pygame.mixer.music.stop()
    def queue(self):
        pygame.mixer.music.queue(self.s)

def load_alphabetsound(char, loc='en'):
    """Loads an alphabet sound file for the @loc locale.
    If @loc is a 'complete' locale like nl_BE then first the nl_BE alphabetsound directory
    is look for. When that fails the 'nl' directory is queried and when that also
    fails the fallback 'en' is used.
    """
    name = ascii2hex(char)
    module_logger.debug("load_alphabetsound got locale %s" % loc)
    if not os.path.exists(os.path.join(ALPHABETDIR, loc)):
        module_logger.debug("load_alphabetsound cannot find %s" % os.path.join(ALPHABETDIR, loc))
        if '_' in loc:
            module_logger.debug("load_alphabetsound trying to use short name for locale")
            if os.path.exists(os.path.join(ALPHABETDIR, loc.split('_')[0])):
                loc = loc.split('_')[0]
            else:
                loc = 'en'
        else:
            loc = 'en'
    path = os.path.join(ALPHABETDIR, loc, name + '.ogg')
    module_logger.debug("load_alphabetsound trying to load %s" % path)
    if not os.path.exists(path):
        module_logger.debug("load_alphabetsound trying to use sound file name in upper case")
        path = os.path.join(ALPHABETDIR, loc, name.upper() + '.ogg')
    snd = load_sound(path)
    return snd
    
def speak_letter(letter, loc='en'):
    """Plays the alphabet soundfile for @letter.
    @loc is the locale.
    Return True on succes and False on failure"""
    try:
        load_alphabetsound(letter.lower(), loc).play()
    except Exception, info:
        module_logger.error("error while trying to play alphabet sounds: %s" % info)
        return False
    else:
        return True
            
def load_sound(name):
    """Loads a sound -> pygame sound object.
      If no file can be loaded return a dummy class"""
                
    if not pygame.mixer or not pygame.mixer.get_init():
        module_logger.info('Cannot load sound: %s, no mixer initialized' % name)
        module_logger.info('Using Nonesound')
        return NoneSound()
    if not os.path.exists(name):
        module_logger.info("Soundpath %s doesn't exists" % name)
        return NoneSound()
    try:
        sound = pygame.mixer.Sound(name)
    except pygame.error:
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
    
def aspect_scale(img,(bx,by)):
    """ Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio """
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    return pygame.transform.scale(img, (int(sx),int(sy)))

def grayscale_image(surf):
    width, height = surf.get_size()
    for x in range(width):
        for y in range(height):
            red, green, blue, alpha = surf.get_at((x, y))
            L = 0.3 * red + 0.59 * green + 0.11 * blue
            gs_color = (L, L, L, alpha)
            surf.set_at((x, y), gs_color)
    return surf
    
def load_image(file, transparent=0, theme='childsplay'):
    """loads an image and convert it.
    When a theme is set it will try to load the image from the theme directory
    otherwise it will load the default image.
    Set transparent to 1 if you want to add transparenty to your non-alpha image.
    The color of the pixel located at 0,0 in your image will be taken as the trans layer.
    If you have a image with an alpha channel set transparent to 0 nd alpha to 1.
    ATTENTION, if you planning to rotate your image DON'T use alpha, it will crash pygame."""
    
    if theme and theme != 'childsplay':
        path, name = os.path.split(file)
        path = os.path.join(path, theme, name)
        try:
            surface = pygame.image.load(path)
        except pygame.error:
            module_logger.info('Failed to load theme image: %s' % path)
            module_logger.info('%s' % pygame.get_error())
            module_logger.info('Trying default images')
            theme = None
    if not theme or theme == 'childsplay':
        try:
            surface = pygame.image.load(file)
        except pygame.error:
            module_logger.exception('Could not load image "%s"\n %s' % (file, pygame.get_error()))
            MyError.line = 'Utils.py -> load_image()'
            raise MyError('Could not load image "%s"\n %s' % (file, pygame.get_error()))
    if transparent:
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
    if surface.get_alpha():
        #if the image loaded has alpha, the overall alpha set here
        #(128) will be overriden. Do it anyway for forcing RLEACCEL
        surface.set_alpha(127, RLEACCEL)
        # if the display is in a lower mode, then surface.convert would
        # convert the surface in an alpha-less surface.
        return surface
    return surface.convert()

def char2surf(char, fsize, fcol=None, ttf='arial', bold=False, antialias=True, split=0):
    """Renders a character and returns the surface.
    char must be a string. Returns the surface.
    This now uses pango to render the fonts.
    @ttf must be a fontname installed on the system
    When you supply a name ending on '.ttf' a truetype font path is assumed and
    the pygame font renderer is used. 
    @split indicates the length of the strings. When it's set to 0, the default,
    it will not split the string and the surface will be returnt.
    When split > 0 a list with surfaces is returnt.
    """
    if NoGtk:
        ttf = TTF
    items = []
    if split:
        txt = txtfmt([char], split)
    else:
        txt = [char]
    if not fcol:
        fcol = (0, 0, 0)
    if ttf and os.path.splitext(ttf)[1] == '.ttf':
        #module_logger.debug('ttf=%s, using standard pygame font' % ttf)
        font = pygame.font.Font(ttf, fsize)
        for line in txt:
            if not txt: continue
            s = font.render(line, True, fcol)
            items.append(s)
    else:
        font = pangofont.PangoFont(family=ttf, size=fsize, bold=bold)
        font.set_bold(bold)
        for line in txt:
            s = font.render(line, True, fcol, None)
            items.append(s)
    if split:
        return items
    else:
        return items[0]
    
def text2surf(word, fsize, fcol=None, ttf=None, sizel=None, bold=False, antialias=True):
    """Renders a text in a surface and returns a surface,size list of the items
    sizelist is a list like this [(7,17),(10,17)] tuples are x,y size of the character."""
    if NoGtk:
        ttf = TTF
    if not fcol:
        fcol = (0, 0, 0)
    if ttf and os.path.splitext(ttf)[1] == '.ttf':
        module_logger.debug('ttf=%s, using standard pygame font' % ttf)
        font = pygame.font.Font(ttf, fsize)
        s = font.render(word, True, fcol)
    else:
        try:
            font = pangofont.PangoFont(family=ttf, size=fsize)
            font.set_bold(bold)
        except Exception, info:
            module_logger.error('%s. Using standard pygame font' % info)
            font = pygame.font.Font(None, fsize)
            s = font.render(word, True, fcol)
        else:
            try:
                s = font.render(word, True, fcol, None)# none means trasparent
            except Exception, info:
                module_logger.exception("Failed to render SDL font: %s" % info)
                return
    if sizel:
        sizelist = font.size(word)
    else:
        sizelist = map(font.size, word)
    return s, sizelist

def Ipl2NumPy(img):
    """ Converts an openCV cvArray to a pygame surface.
     Parameters:   IplImage img - image"""
    array = adaptors.Ipl2NumPy(img)
    surf = pygame.surfarray.make_surface(array)
    surf = pygame.transform.rotate(surf, -90)
    surf = pygame.transform.flip(surf, 1, 0)
    return surf

def NumPy2Ipl(surf):
    """Converts a pygame surface to an openCV cvArray.
    Parameters:   pygame.Surface surf - pygame Surface
    """
    py_image = surfarray.pixels3d(surf)
    cv_image = adaptors.NumPy2Ipl(py_image.transpose(1,0,2))
    return cv_image

def find_files(directory, patternlist):
    """Generator function to search files that match a certain pattern.
    patternlist must be a list of patterns.
    Usage: for file in find_files('topdir','*.foo'):
                print 'found:',file 
    """
    for root, dirs, files in os.walk(directory):
        for pattern in patternlist:
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename

class Dimmer:
    """
Dimmer class

Tobias Thelen (tthelen@uni-osnabrueck.de)
6 September 2001

PUBLIC DOMAIN
Use it in any way you want...

tested with: Pyton 2.0/pygame-1.1, Windows 98

A class for 'dimming' (i.e. darkening) the entire screen, useful for:
- indicating a 'paused' state
- drawing user's attention away from background to e.g. a Quit/Don't Quit
  dialog or a highscore list or...

Usage:

dim=Dimmer(keepalive=1)
  Creates a new Dimmer object,
  if keepalive is true, the object uses the same surface over and over again,
  blocking some memory, but that makes multiple undim() calls possible - 
  Dimmer can be 'abused' as a memory for screen contents this way..

dim.dim(darken_factor=64, color_filter=(0,0,0))
  Saves the current screen for later restorage and lays a filter over it -
  the default color_filter value (black) darkens the screen by blitting a 
  black surface with alpha=darken_factor over it.
  By using a different color, special effects are possible,
  darken_factor=0 just stores the screen and leaves it unchanged

dim.undim()
  restores the screen as it was visible before the last dim() call.
  If the object has been initialised with keepalive=0, this only works once.

"""
    def __init__(self, keepalive=0):
        self.keepalive = keepalive
        if self.keepalive:
            self.buffer = pygame.Surface(pygame.display.get_surface().get_size())
        else:
            self.buffer = None
        
    def dim(self, darken_factor=64, color_filter=(0, 0, 0)):
        if not self.keepalive:
            self.buffer = pygame.Surface(pygame.display.get_surface().get_size())
        self.buffer.blit(pygame.display.get_surface(), (0, 0))
        if darken_factor > 0:
            darken = pygame.Surface(pygame.display.get_surface().get_size())
            darken.fill(color_filter)
            darken.set_alpha(darken_factor)
            # safe old clipping rectangle...
            old_clip = pygame.display.get_surface().get_clip()
            # ..blit over entire screen...
            pygame.display.get_surface().blit(darken, (0, 0))
            pygame.display.update()
            # ... and restore clipping
            pygame.display.get_surface().set_clip(old_clip)

    def undim(self):
        if self.buffer:
            pygame.display.get_surface().blit(self.buffer, (0, 0))
            pygame.display.update()
            if not self.keepalive:
                self.buffer = None
    
class MazeGen:
    """  Perfect maze generator, based on the Mazeworks algorithm.(adapted for Packid)
  Constuctor takes two uneven integers eg rows,cols. If the rows/cols are even
  then they will be decreased by one.
  Usage: m = MazeGen(17,17)
         maze = m.get_maze()
  maze is a tuple with tuples representing a grid where a 0 stands for a wall,
  and 1 for a room. The outer walls are also zeros.
  """
              
    def __init__(self, rows, cols):
        rows = rows-(rows % 2 == 0)
        cols = cols-(cols % 2 == 0)
        self.matrix = []
        for r in range(rows):
            self.matrix.append(([0] * cols))
        self._make_maze()
    
    def _make_maze(self):
        import random
        cellstack = []
        maxrow = len(self.matrix)
        row = random.choice(range(1, maxrow, 2))
        maxcol = len(self.matrix[0])
        col = random.choice(range(1, maxcol, 2))
        #print 'start row,col',row,col
        maxcol -= 3
        maxrow -= 3
        
        self.matrix[row][col] = 1
        
        nextcell = []
        while 1:
            nextcell = []
            #check neighbors
            if col < maxcol and self.matrix[row][col + 2] == 0:
                nextcell.append(((row, col + 1), (row, col + 2)))
            if col > 2 and self.matrix[row][col-2] == 0:
                nextcell.append(((row, col-1), (row, col-2)))
            if row < maxrow and self.matrix[row + 2][col] == 0:
                nextcell.append(((row + 1, col), (row + 2, col)))
            if row > 2 and self.matrix[row-2][col] == 0:
                nextcell.append(((row-1, col), (row-2, col)))
            
            if nextcell:
                next = random.choice(nextcell)
                # knock down the wall
                self.matrix[next[0][0]][next[0][1]] = 1
                self.matrix[next[1][0]][next[1][1]] = 1
                cellstack.append(((row, col)))# stack old cell
                row, col = next[1][0], next[1][1]
                
            else:# Backtrack our steps
                try:
                    row, col = cellstack.pop()
                except IndexError:
                    #print 'break'
                    break
        self.matrix[-2][-2] = 2
        self.matrix[-1][-2:] = [1, 1]
        
    def get_maze(self):
        grid = tuple(map(tuple, self.matrix))
        return grid

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
        fp, pathname, description = imp.find_module(name, [path])
        return imp.load_module(name, fp, pathname, description)
        if fp: fp.close()
    except (StandardError, MyError), info:
        module_logger.exception("Import of %s failed" % filename)
        raise MyError, info
        if fp: fp.close()
    
def txtfmt(text, split):
    """ Formats a list of strings in a list of strings of 'split' length.
       returns a new list of strings.
       text = list of strings
       split = integer
       """
    return textwrap.wrap('\n'.join(text), split)

def txtfmtlines(text, split):
    """Formats a list of strings of 'split' length.
    Returns a list of strings with single linebreaks preserved.
    This differs from txtfmt which removed single line linebreaks
    """
    wrapper = textwrap.TextWrapper()
    wrapper.width = split
    wrapper.drop_whitespace = False
    lines = []
    for line in text:
        if not line.split('\n'):
            lines += line
        else:
            lines += wrapper.wrap(line)
    return lines

class ScaleImages:
    def __init__(self, imgObjects, TargetSize, stdCardObj=None):
        """ ImgObjects = sequence of SDL objects, can also be a dictionairy but in that
                    case you can't use stdCard. If you set it to None you MUST pass a
                    surface to the get_images method.
                    This way you can use it to construct a scaler and each time pass
                   a surface to get_images which will be blitted on the stdCardObj. 
        stdCardObj = None means no blitting on card, just return
                   the scaled images. Else the images are blitted on this object.
        TargetSize = desired scale size (tuple)
        """
        self.logger = logging.getLogger("childsplay.utils.ScaleImages")
        self.TargetSize = pygame.Rect((0, 0) + TargetSize)# convert this tuple in a pygame rect
            # see: def _scale_if_needed
        if stdCardObj:
            # in case of error, we don't use a card back
            # just return scaled images.
            border = 10 # border size of card (memory), 2 * border size
            try: 
                self.stdCard = stdCardObj
                # scale the card also to TargetSize, so we use one card for everything
                self.scaled_card = self._scale_if_needed(self.stdCard)
                self.TargetSize.inflate_ip(-border, -border)# reduce the size of the rect, so the images are smaller
                    # then the card (compensate for border)
            except StandardError, info:
                self.logger.exception("Failed to scale stdCardObj:%s, %s" % (stdCardObj, info))
                self.stdCard = None
        else:
            self.stdCard = None #to use as a test later, if we gonna blit the img on a card or not
                # see get_images
        self.imgObjects = imgObjects
        
    def get_images(self, image=None):
        """ This returns a list with scaled images, blitted on a card if
         it was parsed to the class constructor.
         When image is a surface image is scaled on a card and returnt in list of one
        """
        if type(self.imgObjects) == types.DictType:
            # This won't work in combination with stdCard
            imgs = {}
            for k, v in self.imgObjects.items():
                imgs[k] = self._scale_if_needed(v)
            return imgs
        if image:
            self.imgObjects = (image, )
        imgs = map(self._scale_if_needed, self.imgObjects) #this returns always a surface, scaled or not
        if self.stdCard:# we have a blanc card to blit the images on
            card_imgs = []
            for img in imgs:
                if self.scaled_card.get_alpha():
                    card = self.scaled_card.convert_alpha()
                else:
                    card = self.scaled_card.convert()
                # center the image on the card
                center_pos = img.get_rect()
                center_pos.center = self.TargetSize.center # Wow, magic, see the pygame reference on Rect
                    # a good understanding of the pygame.Rect is a real time saver.
                card.blit(img, center_pos)
                card_imgs.append((card))
            imgs = card_imgs[:]# a real copy, just to be sure :-)
        return imgs   
        
    def _scale_if_needed(self, img):
        """ We only scale down, not up because the result of upscaling sucks"""
            # Remember, TargetSize is a pygame rect (contains is a method of Rect)
        if not self.TargetSize.contains(pygame.Rect((0, 0) + img.get_size())):
            return self._scale_card(img)
        else:
            return img  #not changed!
            
    def _scale_card(self, img):
        """ This does the actual scaling and returns a scaled SDL surface."""
        imgSize = img.get_size()
        
        # we assume TargetSize = x == y, a square
        # TODO XXX what if Target not a square ??
        if (imgSize[0] > imgSize[1]):# which one should we divide to get the longest side within the TargetSize 
            scale_ratio = float(imgSize[0]) / self.TargetSize[2]# TargetSize is a rect -> (x,y,x-size,y-size)
        else:
            scale_ratio = float(imgSize[1]) / self.TargetSize[3]
                           
        scale_x = int(imgSize[0] / scale_ratio)
        scale_y = int(imgSize[1] / scale_ratio)
        
        scaled_img = pygame.transform.scale(img, (scale_x, scale_y))
        return scaled_img

# TODO: Do we want to use GfxCursor?
class GfxCursor:
    """
    Replaces the normal pygame cursor with any bitmap cursor.
    This is a nice little GfxCursor class that gives you arbitrary mousecursor
    loadable from all SDL_image supported filetypes. 

    Author: Raiser, Frank aka CrashChaos (crashchaos at gmx.net)
    Author: Shinners, Pete aka ShredWheat
    Version: 2001-12-15

    Usage:
    Instantiate the GfxCursor class. Either pass the correct parameters to
    the constructor or use setCursor, setHotspot and enable lateron.

    The blitting is pretty optimized, the testing code at the bottom of
    this script does a pretty thorough test of all the drawing cases.
    It enables and disables the cursor, as well as uses a changing background.

    In your mainloop, the cursor.show() should be what you draw last
    (unless you want objects on top of the cursor?). Then before drawing
    anything, be sure to call the hide(). You can likely call hide() immediately
    after the display.flip() or display.update().

    The show() method also returns a list of rectangles of what needs to be
    updated. You can also move the cursor with pygame.mouse.set_pos()


    That's it. Have fun with your new funky cursors.
    

    """

    def __init__(self, surface, cursor=None, hotspot=(0, 0)):
        """
        surface = Global surface to draw on
        cursor  = surface of cursor (needs to be specified when enabled!)
        hotspot = the hotspot for your cursor
        """
        self.surface = surface
        self.enabled = 0
        self.cursor  = None
        self.hotspot = hotspot
        self.bg      = None
        self.offset  = 0, 0
        self.old_pos = 0, 0
        
        if cursor:
            self.setCursor(cursor, hotspot)
            self.enable()

    def enable(self):
        """
        Enable the GfxCursor (disable normal pygame cursor)
        """
        if not self.cursor or self.enabled: return
        pygame.mouse.set_visible(0)
        self.enabled = 1

    def disable(self):
        """
        Disable the GfxCursor (enable normal pygame cursor)
        """
        if self.enabled:
            self.hide()
            pygame.mouse.set_visible(1)
            self.enabled = 0

    def setCursor(self, cursor, hotspot=(0, 0)):
        """
        Set a new cursor surface
        """
        if not cursor: return
        self.cursor = cursor
        self.hide()
        self.show()
        self.offset = 0, 0
        self.bg = pygame.Surface(self.cursor.get_size())
        pos = self.old_pos[0]-self.offset[0], self.old_pos[1]-self.offset[1]
        self.bg.blit(self.surface, (0, 0),
            (pos[0], pos[1], self.cursor.get_width(), self.cursor.get_height()))

        self.offset = hotspot

    def setHotspot(self, pos):
        """
        Set a new hotspot for the cursor
        """
        self.hide()
        self.offset = pos

    def hide(self):
        """
        Hide the cursor (useful for redraws)
        """
        if self.bg and self.enabled:
            return self.surface.blit(self.bg,
                (self.old_pos[0]-self.offset[0], self.old_pos[1]-self.offset[1]))

    def show(self):
        """
        Show the cursor again
        """
        if self.bg and self.enabled:
            pos = self.old_pos[0]-self.offset[0], self.old_pos[1]-self.offset[1]
            self.bg.blit(self.surface, (0, 0),
                (pos[0], pos[1], self.cursor.get_width(), self.cursor.get_height()))
            return self.surface.blit(self.cursor, pos)

    def update(self, event):
        """
        Update the cursor with a MOUSEMOTION event
        """
        self.old_pos = event.pos


        
def current_time():
    """Maincore uses this to get the current time to set the 'time_start'
    and 'time_end' values in the dbase table"""
    t = time.strftime("%y-%m-%d_%H:%M:%S", time.localtime())
    module_logger.debug("current_time returns %s" % t)
    return t
def calculate_time(start, end):
    """The 'end'time is substracted from 'start'time and the result time is
    returned in a format suitable to put into the dbase.
    Times must be in the format as returnt from current_time.
    """
    logger = logging.getLogger("childsplay.utils.calculate_time")
    logger.debug("Called with start:%s, end:%s" % (start, end))
    start = start.replace('-', ':').replace('_', ':')
    end = end.replace('-', ':').replace('_', ':')
    arg_key0 = [int(s) for s in start.split(':')]
    arg_key1 = [int(s) for s in end.split(':')]
    #t1 = datetime.datetime.now()
    #t2 = datetime.datetime.now()
    #t3 = t2-t1
    #t3.seconds / 60
    #t3.seconds % 60
    dt0 = datetime.datetime( * arg_key0)
    dt1 = datetime.datetime( * arg_key1)
    dt2 = dt1 - dt0
    h, m = dt2.seconds / 60, dt2.seconds % 60
    return "%02d:%02d" % (h, m)
def sleep(ms):
    """Pause the process for the given milliseconds and clears the event queue when
    done."""
    pygame.time.delay(ms)
    pygame.event.clear()

def shadefade(textstring, textsize, amount,bold=False, \
              fcol=(200, 200, 200), shadecol=(255, 255, 255)):
    """Render @textstring onto a surface with a 3d dropshadow-like effect.
    Returns a SDL surface.
    Originally written by Brendan Becker, http://clickass.org/
    """
    if PLATFORM == 'win32':
        textsize -= 16
    
    font = pangofont.PangoFont(None, textsize, bold=bold)
    # determine the size of the text surface so that we can center it later on
    basetext = font.render(unicode(textstring), 1, fcol, None)
    width, height = basetext.get_size()
    displaysurface = pygame.Surface((width, height), SRCALPHA, 32)
    tempsurface = pygame.Surface((width + amount, height+amount), SRCALPHA, 32)
    
    for i in range(amount):
        camt = amount-i
        r = shadecol[0] / camt
        g = shadecol[1] / camt
        b = shadecol[2] / camt
        if r < 0:  r = 0
        if g < 0:  g = 0
        if b < 0:  b = 0
        text = font.render(unicode(textstring), 1, (r, g, b), None)
        tempsurface.blit(text, (camt, camt))
    tempsurface.blit(basetext, (0, 0))
    displaysurface.blit(tempsurface, (0, 0))
    return displaysurface

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
            f = open(LOCKFILE, 'r')
            lines = f.readlines()
            t = float(lines[0][:-1])
        except (IOError, TypeError):
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
        f = open(LOCKFILE, 'w')
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
    
def score2percentile(s_list, mean, sd):
    """Returns the percentile in a list with the coresponding dates
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
    
    Then we find the percentile in a hash table and multiply it by 10 to get a 
    nice value to display.
    """
    module_logger.debug("score2percentile called with:%s,%s,%s" % (s_list, mean, sd))
    # we unpack the score/date list, make the calculation and build
    # a new score/date list
    new_s_list = []
    for date, rs in s_list:
        if not rs:
           continue
        zs = (float(rs) - float(mean)) / float(sd)
        if zs < 0:
            prc = 1.0 - float(normal_distribution_table["%.2f" % abs(zs)])
            prc = str(prc *10)
        else:
            prc = str(float(normal_distribution_table["%.2f" % zs]) * 10)[:4]
        module_logger.debug("rs: %s, mean:%s, sd:%s, zscore:%s, percentile:%s" % (rs, mean, sd, zs, prc))
        new_s_list.append((date, prc))
    return new_s_list
    
class OrderedDict(dict, MutableMapping):
    # Taken from Python 2.7, runs also on python  >= 2.4.
    # Methods with direct access to underlying attributes
    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at 1 argument, got %d', len(args))
        if not hasattr(self, '_keys'):
            self._keys = []
        self.update(*args, **kwds)

    def clear(self):
        del self._keys[:]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            self._keys.append(key)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._keys.remove(key)

    def __iter__(self):
        return iter(self._keys)

    def __reversed__(self):
        return reversed(self._keys)

    def popitem(self):
        if not self:
            raise KeyError
        key = self._keys.pop()
        value = dict.pop(self, key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        inst_dict = vars(self).copy()
        inst_dict.pop('_keys', None)
        return (self.__class__, (items,), inst_dict)

    # Methods with indirect access via the above methods

    setdefault = MutableMapping.setdefault
    update = MutableMapping.update
    pop = MutableMapping.pop
    keys = MutableMapping.keys
    values = MutableMapping.values
    items = MutableMapping.items

    def __repr__(self):
        pairs = ', '.join(map('%r: %r'.__mod__, self.items()))
        return '%s({%s})' % (self.__class__.__name__, pairs)

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

#try:
#    import db_conf as dbrc
#    rckind = 'db_conf'
#except ImportError:
#    import db_dev as dbrc
#    rckind = 'db_dev'
#rc_hash = dbrc.rc
#if rc_hash['default']['production']:
#    kind = 'production'
#else:
#    kind = 'develop'
#rc_hash['kind'] = kind
#try:
#    WEAREPRODUCTION = int(rc_hash['default']['production'])
#except KeyError:
#    WEAREPRODUCTION = '0'
WEAREPRODUCTION = '0'

    
