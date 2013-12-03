# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           quizengine.py
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

# Provides Super classes for the quiz activities.

#create logger, logger was setup in SPLogging
import logging
# In your Activity class -> 
# self.logger =  logging.getLogger("childsplay.quiz_text.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.quizengine")

import os, sys
import random
import glob
import pygame
from pygame.constants import *
import types
import datetime
from SPConstants import *

from utils import load_image, char2surf, get_locale_local, MyError, load_music
from utils import current_time, read_rcfile, sleep
from SPSpriteUtils import SPSprite, SPInit
from SPWidgets import TransPrevNextButton, TransImgButton
from SPSoundServer import SoundServer
from SPORMs import type2table

class ParserError(Exception):
    pass


# special gamethemes for regional and personal quizzes which aren't part of the server_content table
REGIONAL_GAME_THEME = -2
PERSONAL_GAME_THEME = -1

class ContentFeeder:
    """Extracts content from the SQL tables."""
    def __init__(self, dbase, difficulty, tp, rchash, spgoodies):
        """Class that interacts with the xml parser to get content from the disk,
        check for completeness and return it to the caller.
        dbase - path to the dbase
        difficulty - which difficulty level we want questions from.
        tp - string  which type of questions we want.
        possible types are: history,math,picture,royal,sayings,text,melody
        """
        self.logger = logging.getLogger("childsplay.quizengine.ContentFeeder")
        self.logger.debug("start ContentFeeder with %s" % dbase)
        self.tp = tp
        self.SPG = spgoodies
        self.rchash = rchash
        self.difficulty = difficulty
        self.served_dict = {}
        self.served = []
        self.wrongexercises = []
        self._not_serve_all_content = False
        self.current_user_id = self.SPG.get_current_user_id()
        self.served_content_orm, self.served_content_session = self.SPG.get_served_content_orm()
        self.rowlist = []
        self.current_question_id = -1
        self.type2table = type2table
        self.year = None
        self.questions_order = {}
        # we make one query for the language code and use that for all queries
        lang = get_locale_local()[0].split('_')[0] # we filter on language, not country
        orm, session = self.SPG.get_orm('game_languages', 'content')
        query = session.query(orm).filter_by(lang = lang)
        self.lang = [l.ID for l in query.all()]
        session.flush()
        session.close()
        # and a query to get the template strings for additional content files like audio and images.
        orm, session = self.SPG.get_orm('game_filenames', 'content')
        query = session.query(orm)
        self.filename_template = {}
        for row in query.all():
            self.filename_template[row.tableName[5:]] = row.fileNameFormat
        session.flush()
        session.close()
        if tp == 'regional':
            self.whatarewe = 'regional'
        elif tp == 'personal':
            self.whatarewe = 'personal'
        else:
            self.whatarewe = 'regular'
    
    def _get_kind(self):
        return self.whatarewe
    
    def __del__(self):
        try:
            self.served_content_session.close()
        except:
            pass

    def serve_all_content(self, value):
        """When set to True we serve all content, False will serve only content which
        has audio"""
        self._not_serve_all_content = value
        self.rowlist = []# will force get_exercise to get new rows
        
    def _get_rows(self, tp, difficulty, year=None):
        self.logger.debug("_get_rows types:%s, difficulty:%s year:%s" % (tp, difficulty, year))
        lang = self.lang
        if tp == 'math':
            lang = [1] # math is the same for all languages.
        orm, session = self.SPG.get_orm('game_released_content', 'content')
        query = session.query(orm)
        if tp == 'picture':
            query = query.filter_by(module = 'quiz_pic')
            query = query.filter(orm.language.in_(lang))
            gt_list = [gt.game_theme for gt in query.all()]
        elif tp == 'regional':
            gt_list = [REGIONAL_GAME_THEME]
        elif tp == 'personal':
            gt_list= [PERSONAL_GAME_THEME]
        else:
            query = query.filter_by(module = 'quiz_'+tp)
            query = query.filter(orm.language.in_(lang))
            gt_list = [gt.game_theme for gt in query.all()]
        
        session.close()
        if year or self.year:
            if self.year:# needed when the questions list is empty and get_exercise queries for ids
                year = self.year
            orm, session = self.SPG.get_orm(type2table[tp], 'content')
            query = session.query(orm)
            query = query.filter(orm.language.in_(lang))
            query = query.filter(orm.year > year).filter(orm.year < year + 10)
            query = query.filter(orm.content_checked > 0)
            rows = [result for result in query.all()]
            all_ids = [row.CID for row in rows]
            if not all_ids or len(all_ids) < 10:
                self.logger.info("Too little questions found, serving all years")
                query = query.filter_by(difficulty = difficulty)
                rows = [result for result in query.all()]
                all_ids = [row.CID for row in rows]
            random.shuffle(rows)
            self.num_questions = len(rows)
            l = self.SPG.check_served_content(rows, \
                            int(self.rchash[self.rchash['theme']]['questions']), \
                            gt_list, all_ids)
            self.year = year
            #print "list of rows",len(rows),l
            session.close()
        else:
            # and now we get the contents from game_quiz* with game_theme(s),
            # difficulty and language.
            orm, session = self.SPG.get_orm(type2table[tp], 'content')
            query = session.query(orm)
            query = query.filter(orm.language.in_(lang))
            query = query.filter(orm.game_theme.in_(gt_list))
            query = query.filter(orm.difficulty == difficulty)
            query = query.filter(orm.content_checked > 0)
            if tp == 'melody' or self._not_serve_all_content:
                self.logger.debug("Serving only questions with audio")
                query = query.filter(orm.audiofiles == 5)
            else:
                self.logger.debug("Serving all questions")
            if tp == 'personal':
                query = query.filter(orm.user_id == self.current_user_id)
            rows_with_audio = [result for result in query.all()]
            self.logger.debug("found %s exercises with audio" % len(rows_with_audio))
            if len(rows_with_audio) < 10:
                orm, session = self.SPG.get_orm(type2table[tp], 'content')
                query = session.query(orm)
                query = query.filter(orm.language.in_(lang))
                query = query.filter(orm.game_theme.in_(gt_list))
                query = query.filter(orm.difficulty == difficulty)
                query = query.filter(orm.content_checked > 0)
                if tp == 'personal':
                    query = query.filter(orm.user_id == self.current_user_id)
                rows_without_audio = [result for result in query.all()]
                rows = rows_without_audio
            else:
                rows = rows_with_audio
            
            session.close()
            all_ids = [row.CID for row in rows]
            random.shuffle(rows)
            self.num_questions = len(rows)
            self.logger.debug("total rows: %s" % len(rows))
            l = self.SPG.check_served_content(rows, \
                            int(self.rchash[self.rchash['theme']]['questions']), \
                            gt_list, all_ids)
            #print ">>>>>>>>>>", len(l)
            
        return l
    
    def set_difficulty(self, difficulty, AreWeDT, year=None):
        self.logger.debug("set_difficulty: %s, year: %s" % (difficulty, year))
        self.AreWeDT = AreWeDT
        self.rowlist = []
        if self.difficulty != difficulty:
            self.logger.debug("difficulty change, remove wrong exercises")
            self.wrongexercises = []
        else:
            self.wrongexercises = self.have_wrong_exercise()
        if not self.rowlist or len(self.rowlist) < int(self.rchash[self.rchash['theme']]['questions']):
            self.rowlist = self._get_rows(self.tp, difficulty, year)
        self.WehaveWrong = False
        if self.wrongexercises:
            self.UseWrongExercises = True
        else:
            self.UseWrongExercises = False
        self.difficulty = difficulty
        self.logger.debug("UseWrongExercises set to %s" % self.UseWrongExercises)

    def get_exercise(self):
        """Returns a dict with the keys set to the question, correct answer
        and possible answers.
        """
        if not self.AreWeDT and self.UseWrongExercises and random.choice([1, 2, 3]) == 1:
            if self.wrongexercises:
                d, self.current_question_id = self.wrongexercises.pop()
                self.logger.debug("serving wrong question: %s" % self.current_question_id)
                self.logger.debug("question contents %s" % d)
                return d
            else:
                self.WehaveWrong = False  
        
        if not self.rowlist:
            self.logger.warning("no more questions, getting them again from the dbase")
            self.rowlist = self._get_rows(self.tp, self.difficulty)
            self.served = []
        row = self.rowlist.pop()
        ##### for debugging only ##########################
#        orm, session = self.SPG.get_orm('game_quizpic', 'content')
#        query = session.query(orm)
#        row = query.filter_by(CID = 2752).first()
#        session.close()
        ###################################################
        i = row.CID
        print row
        print row.CID
        bad = ('\t', '\r', '\n')
        rq = ''.join(c for c in row.question if c not in bad).strip()
        ra = ''.join(c for c in row.answer if c not in bad).strip()
        rw1 = ''.join(c for c in row.wrong1 if c not in bad).strip()
        rw2 = ''.join(c for c in row.wrong2 if c not in bad).strip()
        rw3 = ''.join(c for c in row.wrong3 if c not in bad).strip()
        if row.audiofiles == 5:
            templ = self.filename_template['quiztext']
            q = (rq, templ % (i,'question'))
            a = (ra, templ % (i,'answer'))
            p = [(rw1, templ % (i,'wrong 1')), \
                    (rw2, templ % (i,'wrong 2')),\
                    (rw3, templ % (i,'wrong 3'))] 
        else:   
            q = (rq, '')
            a = (ra, '')
            p = [(rw1, ''), (rw2, ''), (rw3, '')] 
        # data is an image or movie.
        if hasattr(row, 'file') and row.file:
            if self.tp == 'picture':
                dt = self.filename_template['quizpic'] % row.ID
            elif self.tp == 'regional':
                dt = self.filename_template['quizregional'] % row.ID
            elif self.tp == 'personal':
                dt = self.filename_template['quizpersonal'] % row.ID
        else:
            dt = ''
        d = {'question':q, 'answer':a, 'possibles':p, 'data':dt, 'speakerID':str(row.speakerID)}
        ############# for debugging only #################################
#        d = {'question':('Dit is een lange vraag van 69 characters lang dat is best lang toch ?', ''), \
#        'answer':('Antwoord a is ook erg lang wel 44 characters', ''), \
#        'possibles':[('Antwoord 1 is ook erg lang wel 44 characters', ''), \
#                     ('Antwoord 2 is ook erg lang wel 44 characters',''),  \
#                     ('Scheidsrechtersfluitje', '')],\
#                     'data':dt, 'speakerID':'0'}
        #########################################################################
        self.logger.debug("get_exercise serves question cid: %s" % i)
        self.served_dict[i] = (d, 0)# used for the wrong answered exercises

        self.current_question_id = i
        if not len(self.served) == 2:
            self.served.append(i)
        else:
            self.served[0] = self.served[1]
            self.served[1] = i
        # TODO: how to get the module name ?? XXX
        
        svc = self.served_content_orm(user_id=self.current_user_id, CID=i,\
                       game_theme_id=row.game_theme, \
                       module='', start_time=datetime.datetime.now(), \
                        count_served=1)
        self.served_content_session.add(svc)
        self.served_content_session.commit()
        return d

    def set_exercise_result(self, id, result):
        """Called by Engine._notify_obs"""
        self.logger.debug("set_exercise_result called with id:%s result:%s" % (id, result))
        if self.served_dict.has_key(id):
            self.served_dict[id] = (self.served_dict[id][0], result)
            if result:
                orm, session = self.SPG.get_orm('served_content', 'user')
                query = session.query(orm).filter_by(CID = id)
                query.update({'wrong': orm.wrong + 1})# this query holds one row
                session.commit()
                session.close()
        else:
            self.logger.warning("set_exercise_result: question %s is unkown" % id) 
    
    def have_wrong_exercise(self):
        self.wrongexercises = []
        for k, v in self.served_dict.items():
            if not v[1]:
                self.WehaveWrong = True
                self.wrongexercises.append((v[0], k))
        if self.wrongexercises:
            random.shuffle(self.wrongexercises)
            if len(self.wrongexercises) > 1:
                self.wrongexercises = self.wrongexercises[:len(self.wrongexercises)/2]
        return self.wrongexercises
    
    def get_num_questions(self):
        return self.num_questions
    def get_current_id(self):
        return self.current_question_id
    

class AudioPlayer:
    def __init__(self, audio, ad_audio, ss):
        self.logger = logging.getLogger("childsplay.quizengine.AudioPlayer")
        self.logger.debug("setup audio stream: %s" % audio)
        self.ss = ss
        if not os.path.splitext(audio['question'])[1]:
            self.logger.info("We don't have audio, set play to False")
            self.wehaveaudio = False
            return
        else:
            self.wehaveaudio = True
        keys = audio.keys()
        try:
            self.audiolist = [audio['silence_1000']]
            self.audiolist.append(audio['question'])
            keys.sort()
            for k in keys[:-3]:
                self.audiolist.append(audio['silence_1000'])
                ad_k = k.split('_')[1]
                self.audiolist.append(ad_audio[ad_k][0])
                self.audiolist.append(audio['silence_500'])
                self.audiolist.append(audio[k])
        except (AttributeError, IndexError), info:
            self.logger.warning("%s" % info)
            self.wehaveaudio = False
    
    def play(self):
        if not self.wehaveaudio:
            self._play_noaudio()# perhaps we do something in the future
            return
        self.logger.debug("Playing music stream")
        for item in self.audiolist:
            if self.ss.play(item):
                self.logger.error("The sound server has problems with: %s" % item)
                break
    
    def stop(self):
        try:
            self.ss.stop()
        except AttributeError:
            pass
        else:
            # needed to let the soundserver stop the current music
            pygame.time.wait(500)
            
    def _play_noaudio(self):
        pass

class Answer(SPSprite):
    def __init__(self, image, alt_image, result_img, sound, pos, cbf, state):
        SPSprite.__init__(self, image)
        self.logger = logging.getLogger("childsplay.quizengine.Answer")
        self.connect_callback(self._cbf, MOUSEBUTTONUP, state)
        self.moveto(pos, hide=True)
        self.alt_image = alt_image
        self.alt_image.blit(result_img, (0, 0))
        self.cbf = cbf
        self.sound = sound
        self.ImTouched = False
    
    def _display(self):
        self.logger.debug("_display called")
        self.image = self.alt_image
        self.display_sprite()
        #self.sound.play()

    def _cbf(self, sprite, event, data):
        self.logger.debug("_cbf called: %s" % data)
        if self.ImTouched:
            return 
        self.ImTouched = True
        self.image = self.alt_image
        self.display_sprite()
        #self.sound.play()
        self.cbf(self, data[0])
        return True
        
class Question(SPSprite):
    def __init__(self, image, pos):
        SPSprite.__init__(self, image)
        self.logger = logging.getLogger("childsplay.quizengine.Question")
        self.moveto(pos, hide=True)
        
class Engine:
    """Class that handles the sprites for the quizzes.
    All the quiz elements are sprites, the answers and prev/next are Button objects.
    The class uses the observer pattern to communicate with the caller
    """
    def __init__(self, quiz, spgoodies, observers, rchash=None):
        """Engine which controls the quiz sprites.
        quiz - String indicating which kind of quiz do we run.
               possible values: history,math,picture,royal,sayings,text,melody
        actives - SPGroup instance which is used by the caller in the eventloop
        observers - list with observer objects
        """
        self.logger = logging.getLogger("childsplay.quizengine.Engine")
        self.SPG = spgoodies
        self.theme = self.SPG.get_theme()
        self.lang = self.SPG.get_localesetting()[0][:2]
        self.parent_observers = observers
        if rchash:
            rchash['lang'] = self.lang

        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        
        self.actives = SPInit(self.screen,self.backgr)
        self.actives.set_onematch(True)
        
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Quizengine_Data')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        self.my_rcfile = read_rcfile(os.path.join(self.my_datadir,'quizengine.rc'))
        self.quizpause = int(self.my_rcfile[self.theme]['pause'])
        self.quizpause_good = int(self.my_rcfile[self.theme]['pause_good'])
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.content_imgpath = os.path.join(self.SPG.get_libdir_path(),'CPData','DbaseAssets','Images')
        self.content_sndpath = os.path.join(self.SPG.get_libdir_path(),'CPData','DbaseAssets', 'Sounds')
        self.local_content_imgpath = os.path.join(HOMEDIR, self.theme, 'LocalAssets')
        
        # will we have local sound content ??
        #self.local_content_sndpath = os.path.join(self.SPG.get_libdir_path(),'CPData','DbaseAssets', 'Sounds')
        self.ttfpath = TTF
        
        dbpath = os.path.join(HOMEDIR, 'quizcontent.db')
        self.quiz = quiz
        try:
            self.CF = ContentFeeder(dbpath, 1, quiz, rchash, spgoodies)
        except Exception, info:
            self.logger.exception("Failed to start contentfeeder: %s" % info)
            raise MyError
        self.whatarewe = self.CF._get_kind()
        self.retry = 2# default values
        self.totalretry = 1
        self.answers_list = []
        self.currentscreen = None
        self.correct_answer = None
        self.unmute_exer_audio = self.SPG._unmute_quiz_voice
        self.CF.serve_all_content(self.unmute_exer_audio)
        p = os.path.join(self.CPdatadir,'good_%s.png' % self.lang)
        if not os.path.exists(p):
            p = os.path.join(self.CPdatadir,'thumbs.png')
        self.good_image = SPSprite(load_image(p))
        
        self.tryagain_image = SPSprite(load_image(os.path.join(self.my_datadir,'tryagain_%s.png' % self.lang)))
                
        iconA=load_image(os.path.join(self.my_datadir,'a.png'))
        iconB=load_image(os.path.join(self.my_datadir,'b.png'))
        iconC=load_image(os.path.join(self.my_datadir,'c.png'))
        iconD=load_image(os.path.join(self.my_datadir,'d.png'))
                
        y = self.blit_pos[1]
        self.question_pos = (5, 5 + y)
        self.answer2_pos = [((5, 200 + y),iconA, 'a'), ((5, 365 + y), iconB, 'b')]
        self.answer4_pos = [((5, 170 + y), iconA, 'a'), ((5, 255 + y), iconB, 'b'),\
                             ((5, 335 + y), iconC, 'c'), ((5, 415 + y), iconD, 'd')]
        self.logo_pos = (615, 200 + y)
        self.snd_pos = (700, 410 + y)
        self.prev_pos = (580, 410 + y)
        self.previous_screen_path = os.path.join(TEMPDIR, 'previous_screenshot.jpeg')
        self.data_display_center = (600, 200 + y)
        if self.quiz == 'picture':
            y = 0
        self.good_image.moveto((229, 280 + y))
        self.good_image.set_use_current_background(True)

        picture_button_width = 385
        
        self.question_surf_long = load_image(os.path.join(self.my_datadir,'vraagbox.png'))
        self.question_surf_short = load_image(os.path.join(self.my_datadir,'vraagbox_small.png'))
        
        self.answer2_surf_long = load_image(os.path.join(self.my_datadir,'box2.png'))
        self.answer2_surf_short = load_image(os.path.join(self.my_datadir,'box2_small.png'))
      
        self.answer2GR_surf_long = load_image(os.path.join(self.my_datadir,'box2_green.png'))
        self.answer2GR_surf_short = load_image(os.path.join(self.my_datadir,'box2_green_small.png'))

        self.answer2R_surf_long = load_image(os.path.join(self.my_datadir,'box2_red.png'))
        self.answer2R_surf_short = load_image(os.path.join(self.my_datadir,'box2_red_small.png'))
        
        self.answer4_surf_long = load_image(os.path.join(self.my_datadir,'box4.png'))
        self.answer4_surf_short = load_image(os.path.join(self.my_datadir,'box4_small.png'))
        
        self.answer4GR_surf_long = load_image(os.path.join(self.my_datadir,'box4_green.png'))
        self.answer4GR_surf_short = load_image(os.path.join(self.my_datadir,'box4_green_small.png'))
        
        self.answer4R_surf_long = load_image(os.path.join(self.my_datadir,'box4_red.png'))
        self.answer4R_surf_short = load_image(os.path.join(self.my_datadir,'box4_red_small.png'))
        
        self.good4_surf = load_image(os.path.join(self.my_datadir,'box4_good.png'))
        self.wrong4_surf = load_image(os.path.join(self.my_datadir,'box4_wrong.png'))
        
        # Setup some of the static objects
        prev = os.path.join(self.my_datadir,'core_prev_button.png')
        prev_ro = os.path.join(self.my_datadir,'core_prev_button_ro.png')
        next = os.path.join(self.my_datadir,'core_next_button.png')
        next_ro = os.path.join(self.my_datadir,'core_next_button_ro.png')
        self.prevnext_button = TransPrevNextButton(self.prev_pos, \
                                              self._cbf_prevnext_button, \
                                              prev, prev_ro, next, next_ro)
        
        self.snd_button = TransImgButton(os.path.join(self.my_datadir, 'speaker.png'), \
                                         os.path.join(self.my_datadir, 'speaker_ro.png'),\
                                         self.snd_pos)
        self.snd_button.connect_callback(self._cbf_snd_button, MOUSEBUTTONUP)
                            
        self.good_sound=os.path.join(self.CPdatadir,'good.ogg')
        self.wrong_sound=os.path.join(self.CPdatadir,'wrong.ogg')
        if self.quiz == 'picture':
            name = 'picture'
        else:
            name = self.quiz
        if self.lang == 'en':
            p = os.path.join(self.SPG.get_libdir_path(),'SPData', 'themes',\
                                        self.theme,'menuicons', \
                                    'quiz_%s.icon.png' % name)
        else:
            p = os.path.join(self.SPG.get_libdir_path(),'SPData', 'themes',\
                                        self.theme,'menuicons', self.lang, \
                                    'quiz_%s.icon.png' % name)
        self.logger.debug("loading logo %s" % p)
        try:
            self.logo_sprite = SPSprite(load_image(p))
        except Exception, info:
            self.logger.debug("No logo found for %s" % self.quiz)
            self.logo_sprite = None
        if self.quiz == 'picture':
            self.logo_sprite = None
        self.actives.add(self.prevnext_button.get_actives())
        self.current_question_id = -1
        # get a soundserver for the AudioPlayer object
        self.SS = SoundServer()
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.previous_screen = None
    
    def stop_timers(self):
        self.logger.debug("stop_timers called")
        try:
            self.SS.stop_server(0)
        except:
            pass

    def _clear_screen(self):
        for s in self.answers_list:
            s.erase_sprite()
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()
        
        if self.logo_sprite:
            self.logo_sprite.display_sprite(self.logo_pos)
    
    def _cbf_snd_button(self, *args):
        self.SS.clear_queue()
        self.logger.debug('_snd_button_cbf called')
        self.audioplayer.play()
    
    def _cbf_prevnext_button(self, sprite, event, data):
        if data[0] == 'prev': 
            self._cbf_prev_button(data)
        else: 
            self._cbf_next_button(data)

    def _cbf_next_button(self, data):
        self.SS.clear_queue()
        self.logger.debug("_cbf_next_button: %s" % data)
        self._clear_screen()
        self.actives.add(self.answers_list)
        for s in self.answers_list:
            s.display_sprite()
        self.prevnext_button.toggle()
        if self.wehaveaudio:
            #self.snd_button.enable(True)
            self.snd_button.display_sprite()
        try:
            self.current_question_id = self.CF.served[1]
        except IndexError, info:
            self.logger.error(info)
            # this shouldn't happen
            self.current_question_id = -1
          
    def _cbf_prev_button(self, data):
        self.SS.clear_queue()
        self.logger.debug("_cbf_prev_button: %s" % data)
        self.actives.remove(self.answers_list)
        self._clear_screen()
        if self.logo_sprite:
            self.logo_sprite.erase_sprite()
        if os.path.exists(self.previous_screen_path):
            surf = load_image(self.previous_screen_path)
            pygame.display.update(self.screen.blit(surf, (0, self.blit_pos[1])))
        else:
            pygame.display.update(self.screen.blit(self.previous_screen, (0, self.blit_pos[1])))
        self.prevnext_button.toggle()
        if self.wehaveaudio:
            #self.snd_button.enable(False)
            self.snd_button.erase_sprite()
        try:
            self.current_question_id = self.CF.served[0]
        except IndexError, info:
            self.logger.error(info)
            self.current_question_id = -1
    
    def stop_sound(self):
        """Called by the parent if the sound needs to be stopped"""
        self.SS.clear_queue()
            
    def _cbf_answers(self, sprite, result):
        """Callback function for the answers.
        Here we determine the users result by calculating a result."""
        self.audioplayer.stop()
        self.SS.clear_queue()
        self.SS.play(sprite.sound)
        if self.erase_tryagain:
            self.tryagain_image.erase_sprite()
        # result == 0 -> good, result == 1 -> wrong
        self.logger.debug("_cbf_answers called with:%s,%s" % (sprite, result))
        if self.retry == None:# two answers
            if result == 0:
                self.good_image.display_sprite()
                sleep(self.quizpause_good)
                self.good_image.erase_sprite()
            else:
                self.maxresult = 0
                self.totalwrongs += 1
                sleep(self.quizpause)
            self._notify_obs(self.maxresult)
            return
        if self.retry and result == 0:# correct answer for 4 answers
            self.good_image.display_sprite()
            sleep(self.quizpause_good)
            self.good_image.erase_sprite()
            self._notify_obs(self.maxresult)
            return
        self.totalwrongs += 1
        self.maxresult -= result
        self.retry -= 1
        if self.retry == 0 and result:
            # whatever, your time has come to quit this pathetic attempt
            self.maxresult = 0
            self.correct_answer._display()
            sleep(self.quizpause)
            self._notify_obs(self.maxresult)
            return
        r = sprite.rect.move(100,0)
        self.tryagain_image.moveto((r[0], r[1]))
        self.tryagain_image.set_use_current_background(True)
        self.tryagain_image.display_sprite()
        self.erase_tryagain = True
        pygame.event.clear()
        
    def _notify_obs(self, result):
        """Notify the callers observers and restart the next question
        """
        self.logger.debug("_notify_obs called, result = %s" % result)
        # keep sprites for the 'previous screen'
        if self.CF.WehaveWrong and result > 1:
            self.scoredisplay.increase_score(result*5)
            self.parent_observers(result/2.0)
        elif result > 0:
            self.scoredisplay.increase_score(result*10)
            self.parent_observers(result)
        if result > -1:
            if result > 0:
                self.CF.set_exercise_result(self.current_question_id, 1)
            self.previous_screen = pygame.Surface((800, 500))
            surf = pygame.display.get_surface()
            self.previous_screen.blit(surf, (0, 0), (0, self.blit_pos[1], 800, 500))
            # we save it also on disk, this is needed for when we run under the generalknowledge quiz
            # we don't remove it, we let the core decide if it should be removed as
            # the core knows if we run under the general. 
            pygame.image.save(self.previous_screen, self.previous_screen_path)
            self.next_question()
        elif result == -1:
            self.logger.debug("_notify_obs level ended, doing nothing yet")
                
                
    def _blit_on_me(self, surf, ls, x=10, y=5):
        for s in ls:
            surf.blit(s, (x, y))
            y += s.get_height()
        return surf
        
    def set_retry(self, retry):
        """Used by the quiz caller to set the number of times the user 
        may have a retry when an answer is wrong.
        This is only used by 4 answers of course and only values 0-3 are allowed.
        A value of zero means no retry.
        retry - integer."""
        self.logger.debug("retry set to %s" % retry)
        self.retry = retry
        self.totalretry = retry
    
    def _do_data(self, data):
        """Here we decide what to do with the data.
        This is called if we are a picture quiz"""
        self.logger.debug("_do_data called with: %s" % data)
        if self.logo_sprite:
            self.logo_sprite.erase_sprite()
        if os.path.splitext(data)[1] in ('.png', '.jpg', 'gif'):
            if self.whatarewe == 'regular':
                s = load_image(os.path.join(self.content_imgpath, data))
            elif self.whatarewe == 'regional':
                s = load_image(os.path.join(self.local_content_imgpath, 'Regional',data))
            elif self.whatarewe == 'personal':
                s = load_image(os.path.join(self.local_content_imgpath, 'Personal', \
                                            str(self.SPG.get_current_user_id()),data))
            else:
                s = load_image(os.path.join(self.content_imgpath, data))
            pygame.draw.rect(s, ROYALBLUE, s.get_rect(), 4)
            self.picture_sprite = SPSprite(s)
            self.picture_sprite.rect.center = self.data_display_center
            #self.picture_sprite.display_sprite()
            self.answers_list.append(self.picture_sprite)
            return 'short' # indicating we used parts of the screen and left less space for question etc 
        elif os.path.splitext(data)[1] in ('.mpg', '.mpeg'):
            pass
            #TODO: placeholder for movie stuff

    def get_question_id(self):
        """return the id of the question that's currently displayed."""
        return self.current_question_id

    def clear(self):
        """Remove all actives sprites from the actives group and erase them"""
        if not self.answers_list:
            return
        self.logger.debug("Clearing sprites")
        self.actives.remove(self.answers_list)
        self._clear_screen()
        # check to see if the soundserver still running.
        self.SS.start_server()

    def init_exercises(self,answers, maxtimes, difficulty=1, AreWeDT=False, year=None):
        """Setup some defaults for the contentfeeder.
        answers - Integer indicating how many answers we should display.
        maxtimes - the number of questions we show, 0 means until we ran out of questions
        difficulty - level of difficulty.
        """
        self.totalwrongs = 0
        if not difficulty:
            difficulty = 1
        self.logger.debug("init_exercises: answers %s, maxtimes %s, difficulty %s, DT %s year %s" % \
                          (answers, maxtimes, difficulty, AreWeDT, year))
        self.SPG.dm.reset()
        # The first time were called by the caller quiz, then _next_question is called.
        # After that next_question is called in the _notify_obs method which is in turn called by the answer object.
        self.AreWeDT = AreWeDT
        
        self.CF.set_difficulty(difficulty, AreWeDT, year)
        if self.CF.get_num_questions() < 10:
            self.logger.error("To little questions found in %s for locale '%s', found %s questions should be at least 10" % (self.quiz, self.lang, self.CF.get_num_questions()))
            self.SPG.tellcore_info_dialog( _("To little questions found in %s for locale '%s', found %s questions should be at least 10"% (self.quiz, self.lang, self.CF.get_num_questions())))
            raise ParserError,"To little questions found in %s for locale '%s', found %s questions should be at least 10" % (self.quiz, self.lang, self.CF.get_num_questions())
        
        self.answers = answers
        if not maxtimes:
            self.maxtimes = self.CF.get_num_questions()
        else:
            self.maxtimes = maxtimes
        self.numOfQuestions = 0
        self.audiohash = {'0':{'a':[], 'b':[], 'c':[], 'd':[]}}
        for i in os.listdir(os.path.join(self.SPG.get_libdir_path(), \
                                'CPData', 'Quizcontent', 'speakers')):
            p = os.path.join(self.SPG.get_libdir_path(), 'CPData', 'Quizcontent',\
                              'speakers', i, '*.ogg')
            ad_audiohash = {'a':[], 'b':[], 'c':[], 'd':[]}
            for f in glob.glob(p):
                p, fp = os.path.split(f)
                ad_audiohash[fp[0]].append(f)
            self.audiohash[i] = ad_audiohash
        #self.prevnext_button.enable(False)
        
    def get_totalwrongs(self):
        return self.totalwrongs    
                
    def next_question(self):
        self.logger.debug("next_question called")
#        print self.numOfQuestions,self.maxtimes
        if self.numOfQuestions < self.maxtimes:
            self.numOfQuestions += 1
            self.logger.debug("serve question #%s" % self.numOfQuestions)
            if not self._next_question():
                self.maxresult = -1# notify observer level end
                self._notify_obs(self.maxresult)
        else:
            self.maxresult = -1# notify observer level end
            self._notify_obs(self.maxresult)
    
    def _next_question(self):
        # This uses pygame font rendering iso pango like the rest of this app.
        # The bigger pango fonts are not so nice.
        # There's a chance that these fonts are not rendered properly in non-western
        # languages.
        if self.quiz == 'math':
            fsize = 40
        else:
            fsize = 32
        fnt = self.ttfpath
        self.erase_tryagain = False
        audiohash = {'silence_1000': os.path.join(self.SPG.get_libdir_path(), \
                        'CPData', 'Quizcontent', 'silence_1000.ogg'), 
                        'silence_500': os.path.join(self.SPG.get_libdir_path(), \
                        'CPData', 'Quizcontent', 'silence_500.ogg')}
        
        self._clear_screen()
        self.actives.remove(self.answers_list)
        self.answers_list = []
        self.retry = self.totalretry
        exer = self.CF.get_exercise()
        if not exer:
            return
        if exer['data']:
            result = self._do_data(exer['data'])
        else:
            result = None
        if result == 'short':
            self.question_surf = self.question_surf_short
            self.answer2_surf = self.answer2_surf_short
            self.answer2R_surf = self.answer2R_surf_short
            self.answer2GR_surf = self.answer2GR_surf_short
            self.answer4_surf = self.answer4_surf_short
            self.answer4R_surf = self.answer4R_surf_short
            self.answer4GR_surf = self.answer4GR_surf_short
            split = 23
            ans_split = 28
            fsize = 30
            if self.answers == 2:
                ans_split = 23
        else:
            self.question_surf = self.question_surf_long
            self.answer2_surf = self.answer2_surf_long
            self.answer2R_surf = self.answer2R_surf_long
            self.answer2GR_surf = self.answer2GR_surf_long
            self.answer4_surf = self.answer4_surf_long
            self.answer4R_surf = self.answer4R_surf_long
            self.answer4GR_surf = self.answer4GR_surf_long
            split = 47
            ans_split = 36
                
        qs = self.question_surf.convert_alpha()
        text_blit_x = 50
        txt, audio = exer['question']
        self.logger.debug("We have audio :%s" % (audio != ''))
        if not self.unmute_exer_audio:
            self.logger.debug("quizvoice is disabled by user")
            if not self.quiz == 'melody':
                audio = ''
        # we will alter the audiohash in case we are melodyquiz AND voice is disabled
        # We will play the question but no answers
        audiohash['question'] = os.path.join(self.content_sndpath, audio)
        speakerID = exer['speakerID']
        if self.audiohash.has_key(speakerID):
            ad_audiohash = self.audiohash[speakerID]
        if audio:
            self.wehaveaudio = True
            self.logger.debug("We have audio, enable soundbutton")
            self.actives.add(self.snd_button)
        else:
            self.logger.debug("We don't have audio, disable soundbutton")
            self.wehaveaudio = False
            self.actives.remove(self.snd_button)
        ts = char2surf(txt, fsize,ttf=fnt, bold=False, fcol=ANTIQUEWHITE, split=split)
        qs = self._blit_on_me(qs, ts)
        qs = Question(qs, self.question_pos)
        qs.display_sprite()
        self.answers_list.append(qs)
        if self.answers == 2:
            self.maxresult = 2# used as a score result
            self.retry = None
            # first we get the correct answer
            txt_c, audio_c = exer['answer']
            # then we pick a random wrong answer
            txt_w, audio_w = random.choice(exer['possibles'])
            
            # blit the correct answer
            s_c = self.answer2_surf.convert_alpha()
            ts = char2surf(txt_c, fsize,ttf=fnt, bold=False,fcol=ANTIQUEWHITE, split=ans_split)
            s_c = self._blit_on_me(s_c, ts, x=50, y=24)
            # and the green one
            s_c_g = self.answer2GR_surf.convert_alpha()
            s_c_g = self._blit_on_me(s_c_g, ts, x=50, y=24)
            
            # blit the wrong anwser
            ts = char2surf(txt_w, fsize, ttf=fnt, bold=False, fcol=ANTIQUEWHITE, split=ans_split)  
            s_w = self.answer2_surf.convert_alpha()
            s_w = self._blit_on_me(s_w, ts, x=50, y=24)
            # and the red one
            s_w_r = self.answer2R_surf.convert_alpha()
            s_w_r = self._blit_on_me(s_w_r, ts, x=50, y=24)
            
            # determine the position (random).
            random.shuffle(self.answer2_pos)
            s_c = self._blit_on_me(s_c, [self.answer2_pos[0][1]])
            s_c_g = self._blit_on_me(s_c_g, [self.answer2_pos[0][1]])
            b = Answer(s_c, s_c_g, self.good4_surf, self.good_sound, \
                       self.answer2_pos[0][0], self._cbf_answers, 0)
            k = 'answer_%s' % self.answer2_pos[0][2]
            audiohash[k] = os.path.join(self.content_sndpath, audio_c)
            self.answers_list.append(b)
            self.correct_answer = b
            
            s_w = self._blit_on_me(s_w, [self.answer2_pos[1][1]])
            s_w_r = self._blit_on_me(s_w_r, [self.answer2_pos[1][1]])
            b = Answer(s_w, s_w_r, self.wrong4_surf, self.wrong_sound, \
                       self.answer2_pos[1][0], self._cbf_answers, 1)
            k = 'answer_%s' % self.answer2_pos[1][2]
            audiohash[k] = os.path.join(self.content_sndpath, audio_w)
            self.answers_list.append(b)

        else: # answer is 4
            self.maxresult = 4# used as a score result
            # first we get the correct answer
            txt_c, audio = exer['answer']
           
            random.shuffle(self.answer4_pos)
            # blit the correct one
            s_c = self.answer4_surf.convert_alpha()
            ts = char2surf(txt_c, fsize-8, ttf=fnt, bold=False,fcol=ANTIQUEWHITE, split=ans_split)
            s_c = self._blit_on_me(s_c, ts,  x=50)
            # and the green one            
            s_c_g = self.answer4GR_surf.convert_alpha()
            s_c_g = self._blit_on_me(s_c_g, ts, x=50)
            s_c = self._blit_on_me(s_c, [self.answer4_pos[0][1]])
            s_c_g = self._blit_on_me(s_c_g, [self.answer4_pos[0][1]])
            b = Answer(s_c, s_c_g, self.good4_surf, self.good_sound, \
                       self.answer4_pos[0][0], self._cbf_answers, 0)
            k = 'answer_%s' % self.answer4_pos[0][2]
            audiohash[k] = os.path.join(self.content_sndpath, audio)
            self.answers_list.append(b)
            self.correct_answer = b
            
            # here we setup the three incorrect answers
            random.shuffle(exer['possibles'])
            for i in range(1, 4):
                txt, audio = exer['possibles'][i-1]
                # placeholder: build audio stream
                # blit the wrong one
                ts = char2surf(txt, fsize-8, ttf=fnt, bold=False, fcol=ANTIQUEWHITE, split=ans_split)  
                s = self.answer4_surf.convert_alpha()
                s = self._blit_on_me(s, ts, x=50)
                s = self._blit_on_me(s, [self.answer4_pos[i][1]])
                k = 'answer_%s' % self.answer4_pos[i][2]
                audiohash[k] = os.path.join(self.content_sndpath, audio) 
                # and the red one
                sr = self.answer4R_surf.convert_alpha()
                sr = self._blit_on_me(sr, ts, x=50)
                sr = self._blit_on_me(sr, [self.answer4_pos[i][1]])
                b = Answer(s, sr, self.wrong4_surf, self.wrong_sound, \
                           self.answer4_pos[i][0], self._cbf_answers, 1)
                self.answers_list.append(b)
        
        # show the stuff       
        for s in self.answers_list:
            s.display_sprite()
        #self.prevnext_button.display_sprite()
        self.actives.add(self.answers_list)
        if self.numOfQuestions > 1 or os.path.exists(self.previous_screen_path):
            self.prevnext_button.enable(True)
            self.prevnext_button.display_sprite()
        else:
            self.prevnext_button.enable(False)
            self.prevnext_button.erase_sprite()
        if self.quiz == 'melody' and not self.unmute_exer_audio:
            # voice disabled but we are melody so  we want to play the question
            self.logger.debug("Altered audiosequence as we are melody and voice is disabled")
            self.audioplayer  = load_music(audiohash['question'])
        else:    
            self.audioplayer = AudioPlayer(audiohash, ad_audiohash, self.SS)
        self.audioplayer.play()
        if self.wehaveaudio:
            self.snd_button.display_sprite()
        self.current_question_id = self.CF.get_current_id()
        return True

    def loop(self, events):
        for event in events:
            if event.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEMOTION):
                result = self.actives.update(event)
        return self.maxresult == -1
    
if __name__ == '__main__':
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
    
    # Test ContentFeeder
    db = os.path.join(HOMEDIR, 'quizcontent.db') 
    tp = 'math_nl'
    dif = '1'
    cf = ContentFeeder(db, dif, tp)
    cf.get_exercise()
    
    
    
    
