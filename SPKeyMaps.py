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
        u'Q':u'/',
        u'W':u'\'',
        u'E':u'ק',
        u'R':u'ר',
        u'T':u'א',
        u'Y':u'ט',
        u'U':u'ו',
        u'I':u'ן',
        u'O':u'ם',
        u'P':u'פ',
        u'[':u']',
        u']':u'[',
        u'A':u'ש',
        u'S':u'ד',
        u'D':u'ג',
        u'F':u'כ',
        u'G':u'ע',
        u'H':u'י',
        u'J':u'ח',
        u'K':u'ל',
        u'L':u'ך',
        u';':u'ף',
        u'\'':u',',
        u'Z':u'ז',
        u'X':u'ס',
        u'C':u'ב',
        u'V':u'ה',
        u'B':u'נ',
        u'N':u'מ',
        u'M':u'צ',
        u',':u'ת',
        u'.':u'ץ',
        u'/':u'.'
        }

    ar={
        u'Q':u'ض',
        u'W':u'ص',
        u'E':u'ث',
        u'R':u'ق',
        u'T':u'ف',
        u'Y':u'غ',
        u'U':u'ع',
        u'I':u'ه',
        u'O':u'خ',
        u'P':u'ح',
        u'[':u'ج',
        u']':u'د',
        u'A':u'ش',
        u'S':u'س',
        u'D':u'ي',
        u'F':u'ب',
        u'G':u'ل',
        u'H':u'ا',
        u'J':u'ت',
        u'K':u'ن',
        u'L':u'م',
        u';':u'ك',
        u'\'':u'ط',
        u'Z':u'<',
        u'X':u'ئ',
        u'C':u'ء',
        u'V':u'ؤ',
        u'B':u'ر',
        u'N':u'ﻻ',
        u'M':u'ى',
        u',':u'ة',
        u'.':u'و',
        u'/':u'ز'
        }
            
    ru={
        u'Q':u'й',
        u'W':u'ц',
        u'E':u'у',
        u'R':u'к',
        u'T':u'е',
        u'Y':u'н',
        u'U':u'г',
        u'I':u'ш',
        u'O':u'щ',
        u'P':u'з',
        u'[':u'х',
        u']':u'ъ',
        u'A':u'ф',
        u'S':u'ы',
        u'D':u'в',
        u'F':u'а',
        u'G':u'п',
        u'H':u'р',
        u'J':u'о',
        u'K':u'л',
        u'L':u'д',
        u';':u'ж',
        u'\'':u'э',
        u'Z':u'я',
        u'X':u'ч',
        u'C':u'с',
        u'V':u'м',
        u'B':u'и',
        u'N':u'т',
        u'M':u'ь',
        u',':u'б',
        u'.':u'ю',
        u'/':u'.'
        }

    el = {
        u'E':u'Ε',
        u'R':u'Ρ',
        u'T':u'Τ',
        u'Y':u'Υ',
        u'U':u'Θ',
        u'I':u'Ι',
        u'O':u'Ο',
        u'P':u'Π',
        u'A':u'Α',
        u'S':u'Σ',
        u'D':u'Δ',
        u'F':u'Φ',
        u'G':u'Γ',
        u'H':u'Η',
        u'J':u'Ξ',
        u'K':u'Κ',
        u'L':u'Λ',
        u'Z':u'Ζ',
        u'X':u'Χ',
        u'C':u'Ψ',
        u'V':u'Ω',
        u'B':u'Β',
        u'N':u'Ν',
        u'M':u'Μ'
        }
