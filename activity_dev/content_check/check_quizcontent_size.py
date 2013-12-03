# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@gmail.com
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

# This script assumes to be run in a directory with the following stuff available
# SPOrms.py
# box2.png
# box4.png
# vraagbox.png
# arial.ttf

import sys, os

print "=" * 80
print """This is a tool to check if all the quiz text content will fit into
the quiz question and answer images."""
print """It will query the btp_content game_available_content table for all the CIDS."""
print "=" * 80

import pygame
from pygame.constants import *

import sqlalchemy as sqla
import sqlalchemy.exceptions as sqlae
import sqlalchemy.orm as sqlorm
import SPORMs as ORMS
import pangofont
# Set this to True to show sqla SQL statements
debug_sql = False

# get our pygame stuff
picture_button_width = 380

pygame.init()

scr = pygame.display.set_mode((1, 1))

question_surf_long = pygame.image.load('vraagbox.png')
question_surf_short = pygame.transform.smoothscale(question_surf_long,\
                                                (picture_button_width,\
                                                question_surf_long.get_rect().h ))
question_long_rect =  question_surf_long.get_rect()
question_short_rect =  question_surf_short.get_rect()

answer2_surf_long = pygame.image.load('box2.png')
answer2_surf_short = pygame.transform.smoothscale(answer2_surf_long,\
                                                (picture_button_width,\
                                                answer2_surf_long.get_rect().h ))
answer2_long_rect = answer2_surf_long.get_rect()
answer2_short_rect = answer2_surf_short.get_rect()                                          
                                                
answer4_surf_long = pygame.image.load('box4.png')
answer4_surf_short = pygame.transform.smoothscale(answer4_surf_long,\
                                                (picture_button_width,\
                                                answer4_surf_long.get_rect().h ))
answer4_long_rect = answer4_surf_long.get_rect()
answer4_short_rect = answer4_surf_short.get_rect() 

# values taken from quizengine.py
fsize = 34
fnt = os.path.join(os.getcwd(),'arial.ttf')
font = pygame.font.Font(fnt, fsize)


def __string_split(line, split):
    """ Split a string at the first space left from split index
      in two pieces of 'split' length -> two strings,
      where the first is of length 'split'.
      The second string is the the rest or None
      line = string
      split = integer
      """
    if len(line) < split:
        return line, ''
    while line[split] != " " or split == 0:
        split -= 1
    line1 = line[:split]
    line2 = line[split + 1:]#loose the space
    
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
        if len(line) >= split:
            newtxt.append((line))
            continue
        while len(line) > split:
            left, right = __string_split(line, split)
            newtxt.append((left.strip(' ')))
            line = right
        newtxt.append((line))
    txt = filter(None, newtxt)
    return txt

# dabe stuff
engine = sqla.create_engine('mysql://btp_user@localhost/btp_content')
Session = sqlorm.sessionmaker(bind=engine)
metadata = sqla.MetaData(engine)
metadata.bind.echo = debug_sql

orms_content_db = {}
# get our orms
for name in [k for k in ORMS.__dict__.keys() if k.startswith('game_')]:
    t = sqla.Table(name, metadata, autoload=True)
    orm = getattr(ORMS, name)
    orm._name = name
    sqlorm.mapper(orm, t)
    orms_content_db[name] = orm

# get all CIDS from all quiz tables, all languages, all difficulties
session = Session()
allrows = {}
print "Start to query the dbase quiz tables. (excluding math questions)"
print "Rows found:"
for tn in ['game_quiztext','game_quizpic', 'game_quizhistory']:
    orm = orms_content_db[tn]
    query = session.query(orm).filter(orm.game_theme != 49)
    allrows[tn] = [result for result in query.all()]
    print "%s rows in %s" % (len(allrows[tn]), tn)
print "=" * 80
# Now we start the hard work of blitting all the cids
# values taken from quizengine.py
text_blit_x = 50
x=10
y=10
wrongs = {}
print "Starting to check content text sizes."
for name, rows in allrows.items():
    print "Checking text from table %s" % name
    if name == 'game_quizpic':
        split = 21
        ans_split = 21
        question_rect = question_short_rect
        answer2_rect = answer2_short_rect
        answer4_rect = answer4_short_rect
    else:
        split = 48
        ans_split = 44
        question_rect = question_long_rect
        answer2_rect = answer2_long_rect
        answer4_rect = answer4_long_rect
    # we blit the text at an offset of 10
    answer4_rect = answer4_rect.inflate((-10, -10))
    answer4_rect.topleft = (0, 0)
    answer2_rect = answer4_rect.inflate((-10, -10))
    answer2_rect.topleft = (0, 0)
    
    for row in rows:
        # we start with the question text
        longest = 0
        items = []
        txt = row.question
        txtlines = txtfmt([txt], split)
        for line in txtlines:
            s = font.render(line, True, (0, 0, 0))
            items.append(s)
            if s.get_width() > longest:
                longest = s.get_width()
        surf = pygame.Surface((longest, s.get_height() * len(items)))    
        target_rect = question_rect
        text_rect = surf.get_rect()
        # Finally we can check the sizes
        if not target_rect.contains(text_rect):
            print "%s to large: %s target: %s text: %s" % (row.CID, txt,  target_rect, text_rect)
            if not wrongs.has_key(name):
                wrongs[name] = []
            wrongs[name].append((row.CID, "question:" + row.question))
        # now we check the answers
        for col in ['answer', 'wrong1', 'wrong2', 'wrong3']:
            longest = 0
            items = []
            txt = getattr(row, col)
            txtlines = txtfmt([txt], split)
            for line in txtlines:
                s = font.render(line, True, (0, 0, 0))
                items.append(s)
                if s.get_width() > longest:
                    longest = s.get_width()
            surf = pygame.Surface((longest, s.get_height() * len(items)))    
            target_rect = answer4_rect
            text_rect = surf.get_rect()
            # Finally we can check the sizes
            if not target_rect.contains(text_rect):
                print "%s to large: %s target: %s text: %s" % (row.CID, txt, target_rect, text_rect) 
                if not wrongs.has_key(name):
                    wrongs[name] = []
                wrongs[name].append((row.CID, "%s: len:%s text:%s" % (col, len(txt), txt)))
      
        
        
if wrongs:
    print "=" * 80
    print "Found %s content items that doesn't fit the image." % len(wrongs.keys())
    print "=" * 80
    for k, v in wrongs.items():
        print "=" * 80
        print k
        for l in v:
            print l

print "=" * 37, "Done", "="*37

