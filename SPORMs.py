# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
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
type2table = {'history':'game_quizhistory', 'picture':'game_quizpic', \
            'text':'game_quiztext', 'math':'game_quiztext', \
            'royal':'game_quiztext', 'sayings':'game_quiztext', \
            'melody':'game_quiztext', 'regional':'game_quizregional',\
            'personal':'game_quizpersonal'}

# ORMs for the btp_content dbase
# These MUST start with 'game_'
class game_quiztext(object): pass
class game_quizhistory(object): pass
class game_released_content(object): pass
class game_quizpic(object): pass
class game_puzzle(object): pass
class game_languages(object):
    def __init__(self, language='', lang='', rapcms_lang='', comment=''):
        self.language = language
        self.lang = lang
        self.rapcms_lang = rapcms_lang
        self.comment = comment
class game_findit(object): pass
class game_filenames(object): pass
class game_available_content(object): pass
class game_quotes(object): pass


# ORMs for the sp_users dbase
# Which attributes must be set depends if you want the ORM to be used to write
# to the table, for every column you want to write too you must set attributes.
class users(object):
    def __init__(self, login_name='', title='', first_name='', last_name='',\
                  birthdate=datetime.datetime(1900,1,1), \
                    group='', profile='', passwrd='', activities='', audio=50, dt_target='default',\
                    levelup_dlg='true'):
        self.login_name = login_name
        self.title = title
        self.first_name = first_name
        self.last_name = last_name
        self.birthdate = birthdate
        self.group = group
        self.profile = profile
        self.passwrd = passwrd
        self.activities = activities
        self.audio = audio
        self.st_target = dt_target
        self.levelup_dlg = levelup_dlg
        
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

class group_names(object):
    def __init__(self, group_id='', group_name=''):
        self.group_id = group_id
        self.group_name = group_name

class spconf(object):
    def __init__(self, activity_name='', key='', value='', theme='', comment=''):
        self.activity_name = activity_name
        self.key = key
        self.value = value
        self.comment = comment
        self.theme = theme

class activity_options(object): 
    def __init__(self, activity, mu=None, sigma=None):
        self.activity = activity
        self.mu = mu
        self.sigma = sigma

class users_faces(object):
    def __init__(self, face_id='', user_id='', shape_diff = '', temp_diff = '', pic_name='', datetime=''):
        self.face_id = face_id
        self.user_id = user_id
        self.shape_diff = shape_diff
        self.temp_diff = temp_diff
        self.pic_name = pic_name
        self.datetime = datetime

class change_pass(object):
    def __init__(self, user='', passwrd=''):
        self.user = user
        self.passwrd = passwrd
    
class zorgenquete(object):
    def __init__(self, item='', state='', network=''):
        self.item = item
        self.state = state
        self.network = network
        
class dt_sequence(object):
    def __init__(self, fortune=0, act_name='', group='', level='', cycles='', target='', order=0):
        self.fortune = fortune
        self.act_name = act_name
        self.group = group
        self.level= level
        self.cycles = cycles
        self.target = target
        self.order = order
    
    def get_values(self):
        return {'fortune':self.fortune, 'act_name':self.act_name, 'group':self.group,\
                'level':self.level,'cycles':self.cycles,'target':self.target,'order':self.order}
    
class dt_sequence_manual(object):
    def __init__(self, user_id='', target=''):
        self.user_id = user_id
        self.target = target

class stats(object):
    def __init__(self, datetime='', activity_name='', message='', game_start_called=False, \
                 game_nextlevel_called=False, game_end_called=False, is_cop=False, \
                 user_id='', final_score='', session=''):
        self.datetime = datetime
        self.activity_name = activity_name
        self.message = message
        self.game_start_called = game_start_called
        self.game_end_called = game_end_called
        self.game_nextlevel_called = game_nextlevel_called
        self.is_cop = is_cop
        self.user_id =user_id
        self.final_score = final_score
        self.session = session
        
class stats_session(object):
    def __init__(self, datetime=''):
        self.datetime =datetime
               
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
        
class quiz_melody(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.total_wrongs = total_wrongs
        self.total_questions = total_questions

class quiz_math(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.total_wrongs = total_wrongs
        self.total_questions = total_questions
        
class quiz_picture(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.total_wrongs = total_wrongs
        self.total_questions = total_questions
        
class quiz_history(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.total_wrongs = total_wrongs
        self.total_questions = total_questions
        
class quiz_royal(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.total_wrongs = total_wrongs
        self.total_questions = total_questions
        
class quiz_sayings(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, total_questions=None, total_wrongs=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.total_wrongs = total_wrongs
        self.total_questions = total_questions
        
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
        
class numbers_sp(act_parent):
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

class list_game(act_parent):
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
        
class dictionary(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        
class wipe(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)

class fourrow(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None, stonesplayed=0):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)
        self.stonesplayed = stonesplayed


class test_act(act_parent):
    def __init__(self, user_id=None, timespend=None, start_time=None, end_time=None,\
                  level=None, score=None):
        act_parent.__init__(self, user_id, timespend, start_time, end_time, level, score)


