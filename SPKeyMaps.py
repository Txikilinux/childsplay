# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           SPKeyMaps.py
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

# This module holds all the keymap conversion tables used to convert the key event
# into the proper non-latin character.
# Only needed in non-Latin locales.

# TODO: Check the maps. Only arabic and hebrew are probably correct.

class KeyMaps(object):
    supportedmaps = ('he', 'ar', 'el','ru')
    he={
        'Q':'/',
        'W':'\'',
        'E':'ק',
        'R':'ר',
        'T':'א',
        'Y':'ט',
        'U':'ו',
        'I':'ן',
        'O':'ם',
        'P':'פ',
        '[':']',
        ']':'[',
        'A':'ש',
        'S':'ד',
        'D':'ג',
        'F':'כ',
        'G':'ע',
        'H':'י',
        'J':'ח',
        'K':'ל',
        'L':'ך',
        ';':'ף',
        '\'':',',
        'Z':'ז',
        'X':'ס',
        'C':'ב',
        'V':'ה',
        'B':'נ',
        'N':'מ',
        'M':'צ',
        ',':'ת',
        '.':'ץ',
        '/':'.'
        }

    ar={
        'Q':'ض',
        'W':'ص',
        'E':'ث',
        'R':'ق',
        'T':'ف',
        'Y':'غ',
        'U':'ع',
        'I':'ه',
        'O':'خ',
        'P':'ح',
        '[':'ج',
        ']':'د',
        'A':'ش',
        'S':'س',
        'D':'ي',
        'F':'ب',
        'G':'ل',
        'H':'ا',
        'J':'ت',
        'K':'ن',
        'L':'م',
        ';':'ك',
        '\'':'ط',
        'Z':'<',
        'X':'ئ',
        'C':'ء',
        'V':'ؤ',
        'B':'ر',
        'N':'ﻻ',
        'M':'ى',
        ',':'ة',
        '.':'و',
        '/':'ز'
        }
            
    ru={
        'Q':'й',
        'W':'ц',
        'E':'у',
        'R':'к',
        'T':'е',
        'Y':'н',
        'U':'г',
        'I':'ш',
        'O':'щ',
        'P':'з',
        '[':'х',
        ']':'ъ',
        'A':'ф',
        'S':'ы',
        'D':'в',
        'F':'а',
        'G':'п',
        'H':'р',
        'J':'о',
        'K':'л',
        'L':'д',
        ';':'ж',
        '\'':'э',
        'Z':'я',
        'X':'ч',
        'C':'с',
        'V':'м',
        'B':'и',
        'N':'т',
        'M':'ь',
        ',':'б',
        '.':'ю',
        '/':'.'
        }

    el = {
        'E':'Ε',
        'R':'Ρ',
        'T':'Τ',
        'Y':'Υ',
        'U':'Θ',
        'I':'Ι',
        'O':'Ο',
        'P':'Π',
        'A':'Α',
        'S':'Σ',
        'D':'Δ',
        'F':'Φ',
        'G':'Γ',
        'H':'Η',
        'J':'Ξ',
        'K':'Κ',
        'L':'Λ',
        'Z':'Ζ',
        'X':'Χ',
        'C':'Ψ',
        'V':'Ω',
        'B':'Β',
        'N':'Ν',
        'M':'Μ'
        }
