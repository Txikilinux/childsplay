# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPORMs.py
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

# This module holds all the ORM classes for sqlalchemy.
# The DataManager object handles these classes.
# This module must only contain ORMs classes no other classes or functions
# as the DataManager assumes every object in here to be a ORM

# The classes below are ORMs which will be mapped on dbase tables by sqlalchemy
# and must be new style classes (derived from object).
# IMPORTANT: You must use the dbase table names as names for the ORMs.
import sqlalchemy as sqla
import sqlalchemy.orm as sqlorm
import datetime
# Hash used by the quizengine.ContentFeeder to determine which contentdb table to use
#possible quiz types are: history,math,pic,royal,sayings,text,melody and general
# we don't pass the actual tables as they are requested through the Datamanager
type2table = {'history':'game_quizhistory', 'pic':'game_quizpic', \
            'text':'game_quiztext', 'math':'game_quiztext', \
            'royal':'game_quiztext', 'sayings':'game_quiztext', \
            } # must be added when table is ready 'melody':'game_quizsound'

# ORMs for the btp_content dbase
# These MUST start with 'game_'
class game_quiztext(object): pass
class game_quizhistory(object): pass
class game_released_content(object): pass
class game_quizpic(object): pass
#class game_quizsound(object): pass
class game_puzzle(object): pass
class game_languages(object): pass
class game_findit(object): pass
class game_filenames(object): pass
class game_available_content(object): pass

# ORMs for the sp_users dbase
# Which attributes must be set depends if you want the ORM to be used to write
# to the table, for every column you want to write to you must set attributes.
class users(object):
    def __init__(self, login_name='', first_name='', last_name='', birthdate='', \
                    group='', profile='', passwrd='', activities=''):
        self.login_name = login_name
        self.first_name = first_name
        self.last_name = last_name
        self.birthdate = birthdate
        self.group = group
        self.profile = profile
        self.passwrd = passwrd
        self.activities = activities
        
class served_content(object):
    def __init__(self, user_id='', CID='', game_theme_id='', module='', start_time=None, \
                 count_served='', wrong=''):
        self.user_id = user_id
        self.CID = CID
        self.game_theme_id = game_theme_id
        self.module = module
        self.start_time = start_time
        self.count_served = count_served
        self.wrong = wrong

class activity_options(object): 
    def __init__(self, activity, mu=None, sigma=None):
        self.activity = activity
        self.mu = mu
        self.sigma = sigma

# parent class for regular activities which provide mandatory attributes.
class act_parent(object):
    def __init__(self, user_id, timespend, start_time, end_time, level, score):
        self.user_id = user_id
        self.timespend = timespend
        self.start_time = start_time
        self.end_time = end_time
        self.level = level
        self.score = score

class quiz_general(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.total_wrongs = total_wrongs
        self.total_questions = total_questions

class quiz(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        self.total_wrongs = total_wrongs
        self.total_questions = total_questions
        
class quiz_text(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.total_wrongs = total_wrongs
        self.total_questions = total_questions
        
class quiz_melody(quiz):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        quiz.__init__(self, user_id, timespend, start_time, end_time, level,\
                               score, total_questions=None, total_wrongs=None)
class quiz_math(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.total_wrongs = total_wrongs
        self.total_questions = total_questions
        
class quiz_picture(quiz):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        quiz.__init__(self, user_id, timespend, start_time, end_time, level,\
                               score, total_questions=None, total_wrongs=None)
class quiz_history(quiz):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        quiz.__init__(self, user_id, timespend, start_time, end_time, level,\
                               score, total_questions=None, total_wrongs=None)
        
class quiz_royal(quiz):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        quiz.__init__(self, user_id, timespend, start_time, end_time, level,\
                               score, total_questions=None, total_wrongs=None)
class quiz_sayings(quiz):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        quiz.__init__(self, user_id, timespend, start_time, end_time, level,\
                               score, total_questions=None, total_wrongs=None)
   
class findit_sp(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_diffs=None,  wrongs=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.wrongs = wrongs
        self.total_diffs = total_diffs
        
class electro_sp(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, cards=0, knowncards=0):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.cards = cards
        self.knowncards = knowncards

class memory_sp(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, knowncards=None, cards=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.knowncards = knowncards
        self.cards = cards
        
class simon_sp(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, sounds=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.sounds = sounds
        
class puzzle(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_pieces=None, wrongs=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.wrongs = wrongs
        self.total_pieces = total_pieces
        
class soundmemory(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, sounds=None, knownsounds=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.sounds = sounds
        self.knownsounds = knownsounds
        
class ichanger(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, wrongs=None, extra=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.wrongs = wrongs
        self.extra = extra 
        
class fishtank(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, fish=None, clearfish=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.fish = fish
        self.clearfish = clearfish
        
class photoalbum(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        
class numbers(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        
class video(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, movie=None, answer=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.movie = movie
        self.answer = answer
        
class dltr(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, activity=None, done=None, cycles=None, epoch=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.activity = activity
        self.done = done
        self.cycles = cycles
        self.epoch = epoch
        
class spinbottle(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total=None, wrong=None, correct=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.total = total
        self.wrong = wrong
        self.correct = correct
        
class story(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        
class synonyms(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        
class wipe(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        
class test_act(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
