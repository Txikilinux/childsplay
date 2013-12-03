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

import os, locale, gettext
import __builtin__
import logging, logging.handlers
# set loglevel, possible values:
# logging.DEBUG
# logging.INFO
# logging.WARNING
# logging.ERROR
# logging.CRITICAL
LEVEL = logging.DEBUG

LOGPATH = os.path.join(os.getcwd(), "schoolsplay.log")

# remove old log
if os.path.exists(LOGPATH):
    try:
        os.remove(LOGPATH)
    except Exception, info:
        print "Failed to remove old log"
        print info
    else:
        print "removed old logpath"

#create logger
logger = logging.getLogger("schoolsplay")
logger.setLevel(LEVEL)
sqla_logger = logging.getLogger("sqlalchemy")
#create console handler and set level
ch = logging.StreamHandler()
ch.setLevel(LEVEL)
#create file handler and set level
fh = logging.FileHandler(LOGPATH)
fh.setLevel(LEVEL)
#create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#add formatter to ch and fh
ch.setFormatter(formatter)
fh.setFormatter(formatter)
#add ch and fh to logger
logger.addHandler(ch)
logger.addHandler(fh)
sqla_logger.addHandler(fh)
logger.info("File logger created: %s" % LOGPATH)
# test
module_logger = logging.getLogger("schoolsplay.text2photo")
module_logger.debug("logger created, start logging")

lang = 'system'

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
LANG = lang
module_logger.debug("Locale set to %s" % LANG)

import TKgui
module_logger.debug("text2photo starts.")
TKgui.Main().mainloop()
module_logger.debug("text2photo quits, bye")
