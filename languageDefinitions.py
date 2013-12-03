# -*- coding: utf-8 -*-

# Copyright (c) 2010 Rene Dohmen <acidjunk@gmail.com> and Peter Govers <petergovers@gmail.com>
# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#           languageDefinitions.py
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

# leave this line intact as it is
_ = lambda x:x

################## Put your translatable words in this list ###################
words = [ _("Good!"), 
         _("Cheat"), 
         _("Start"), 
         _("Try again!"), 
         _("New word"), 
         _("New question"), 
         _("Other category"), 
         _("Did you enjoy this?"), 
         _("Yes"), 
         _("No"), 
         _("Continue movie"), 
         _("Next movie"), 
         _("Memory"), 
         _("New Games"), 
         _("Puzzle"), 
         _("Quiz"), 
         _("Training"),
         _("Short Term"), 
         _("Long Term"), 
         _("Daily Training") 
         ]

############################### End of word definitions #####################

# Don't change stuff below this line.

# text from dailytraing.xml which is used in DT endscreen
a = _("short-term")
b = _("long-term")
c =_("quiz")


if __name__ == '__main__':
    
    import codecs
    import gettext
    from SPConstants import LOCALEDIR 

    lang_nl = gettext.translation('seniorplay', LOCALEDIR, languages=['nl'])
    lang_fr = gettext.translation('seniorplay', LOCALEDIR, languages=['fr'])
    lang_de = gettext.translation('seniorplay', LOCALEDIR, languages=['de'])
    lang_sv = gettext.translation('seniorplay', LOCALEDIR, languages=['sv'])

    lines = ["Words from the languageDefinitions file"]
    sep = "-" * 80
    
    for lang in [lang_nl, lang_de, lang_fr, lang_sv]:
        lines.append(sep)
        s = lang.info()['language-team'].split('_')[0].split('language: ')[0]
        lines.append("Language code: %s" % s)
        lines.append(sep)
        lang.install()
        _ = lang.ugettext
        for word in words:
            lines.append("%s = %s" % (word, _(word)))
    
    f = codecs.open('languageDefinitions_output.txt', 'wt', 'utf-8')
    f.write('\n'.join(lines))
    f.close()

