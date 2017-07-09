# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@gmail.com
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.# Provieded

# Provides Super classes for the quiz activities.

#create logger, logger was setup in SPLogging
import logging
# In your Activity class -> 
# self.logger =  logging.getLogger("schoolsplay.quiz_text.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.quizengine")

# standard modules you probably need
import os
import random
import glob
import pygame
from pygame.constants import *
import types

from SPConstants import *
if NoGtk:
    try:
        from pysqlite2 import dbapi2 as sqlite3
    except ImportError:
        import sqlite3
else:
    import sqlite3
        
from utils import load_image, char2surf
from SPSpriteUtils import SPSprite, SPInit
from SPWidgets import TransPrevNextButton, TransImgButton
from SPSoundServer import SoundServer

class ParserError(Exception):
    pass

class ContentFeeder:
    """Extracts content from the SQL tables."""
    # TODO: when we start 2.2 we must rewrite this once more to use persistant storage.
    # I have now made the wrong questions stuff like this: (taken from ticket)
    
    def __init__(self, dbase, difficulty, tplist, rchash):
        """Class that interacts with the xml parser to get content from the disk,
        check for completeness and return it to the caller.
        dbase - path to the dbase
        difficulty - which difficulty level we want questions from.
        tplist - list of which types of questions we want.
        possible types are: history,math,picture,royal,sayings,text,audio
        """
        self.logger = logging.getLogger("schoolsplay.quizengine.ContentFeeder")
        self.logger.debug("start ContentFeeder with %s" % dbase)
        self.tplist = tplist
        
        self.questions_order_org = []
        if len(self.tplist) > 1 and rchash:
            # we are general quiz
            self.questions_order_org = []
            for item in [s.strip(' ') for s in rchash[rchash['theme']]['questions_order_%s' % rchash['lang']].split(',')]:
                i, t = item.split('_')
                t += '_%s' % rchash['lang']
                self.questions_order_org += int(i) * [t]
            self.questions_order = self.questions_order_org[:]
            random.shuffle(self.questions_order)
        self.difficulty = difficulty
        self.served_dict = {}
        self.served = []
        self.wrongexercises = []
        con = sqlite3.connect(dbase)
        self.cursor = con.cursor()
        self.idlist = self._get_ids(tplist, difficulty)
        self.current_question_id = -1
            
    def _get_ids(self, tp, difficulty, year=None):
        self.logger.debug("_get_ids types:%s, difficulty:%s year:%s" % (tp, difficulty, year))
        if len(tp) == 1:
            if year:
                self.cursor.execute(
                        '''SELECT content_id, year FROM %s WHERE difficulty=? AND year=?''' % tp[0],\
                        (difficulty, year))
                l = [(i[0], ) for i in self.cursor.fetchall()]
            else:
                self.cursor.execute('''SELECT content_id FROM %s WHERE difficulty=?''' % tp[0],\
                        (str(difficulty), ))
                l = [i for i in self.cursor.fetchall()]
            random.shuffle(l)
            self.num_questions = len(l)
        else:
            # we are textquiz
            self.num_questions = 0
            l = {}
            for t in tp:
                if t.split('_')[0] == 'math' and difficulty > 4:
                    self.cursor.execute(
                        '''SELECT content_id FROM %s WHERE difficulty=?''' % t,\
                        (4, ))
                else:
                    self.cursor.execute(
                        '''SELECT content_id FROM %s WHERE difficulty=?''' % t,\
                        (str(difficulty), ))
                l[t] = self.cursor.fetchall()
                random.shuffle(l[t])
            for i in l.values():
                self.num_questions += len(i)
        return l
                        
    def set_difficulty(self, difficulty, AreWeDT):
        self.logger.debug("set_difficulty: %s" % difficulty)
        self.AreWeDT = AreWeDT
        if self.difficulty != difficulty:
            self.logger.debug("difficulty change, remove wrong exercises")
            self.wrongexercises = []
        else:
            self.wrongexercises = self.have_wrong_exercise()
        self.idlist = self._get_ids(self.tplist, difficulty)
        self.WehaveWrong = False
        if self.wrongexercises:
            self.UseWrongExercises = True
        else:
            self.UseWrongExercises = False

    def get_exercise(self, tp=None):
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
##### Just as a reminder of the table layout ########################
#        ( id INTEGER PRIMARY KEY, content_id TEXT, content_type TEXT,
#                    difficulty TEXT, question_text TEXT,
#                    question_audio TEXT, answer TEXT, answer_audio TEXT,
#                    wrong_answer1 TEXT, wrong_answer1_audio TEXT,
#                    wrong_answer2 TEXT, wrong_answer2_audio TEXT,
#                    wrong_answer3 TEXT, wrong_answer3_audio TEXT,
#                    data TEXT, year TEXT, _group TEXT) 
#######################################################################        
        if hasattr(self, 'idlist') and type(self.idlist) == types.DictType:
            if not self.questions_order:
                self.questions_order = self.questions_order_org[:]
                random.shuffle(self.questions_order)
            k = self.questions_order.pop()
            l = self.idlist[k]
            if not l:
                self.logger.warning("no more questions, getting them again from the dbase")
                self.idlist = self._get_ids(self.tplist, self.difficulty)
                k = random.choice(self.idlist.keys())
                l = self.idlist[k]
                self.served = []
            id = l.pop()
            tb = k
        else:
            if not self.idlist:
                self.logger.warning("no more questions, getting them again from the dbase")
                self.idlist = self._get_ids(self.tplist, self.difficulty)
                self.served = []
            id = self.idlist.pop()
            tb = self.tplist[0]
        if id[0] in self.served:
            self.logger.debug("id %s already served, trying to find a new one." % id)
            if self.idlist:
                id = self.idlist.pop()
                while id[0] in self.served and self.idlist:
                    id = self.idlist.pop()
            else:
                self.logger.warning("no more questions, getting them again from the dbase")
                self.idlist = self._get_ids(self.tplist, self.difficulty)
                id = self.idlist.pop()
                tb = self.tplist[0]
                self.served = []
        self.cursor.execute('''SELECT * FROM %s WHERE content_id=?''' % tb, id)
        row = self.cursor.fetchone()
        i = row[1]
        q = (row[4], row[5])
        a = (row[6], row[7])
        p = [(row[8], row[9]), (row[10], row[11]), (row[12], row[13])] 
        dt = row[14]
        d = {'question':q, 'answer':a, 'possibles':p, 'data':dt}
        self.logger.debug("get_exercise serves question id: %s" % i)
        self.served_dict[i] = (d, 0)
        self.served.append(i)
        self.current_question_id = i
        return d

    def set_exercise_result(self, id, result):
        if self.served_dict.has_key(id):
            self.served_dict[id] = (self.served_dict[id][0], result)
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
    
    def use_wrong_exercise(self):
        self.UseWrongExercises = True
    
    def filter_history_questions(self, year):
        self.idlist = self._get_ids(self.tplist, self.difficulty, year)

    def get_num_questions(self):
        return self.num_questions
    def get_current_id(self):
        return self.current_question_id

class AudioPlayer:
    def __init__(self, audio, ad_audio, ss):
        self.logger = logging.getLogger("schoolsplay.quizengine.AudioPlayer")
        self.logger.debug("setup audio stream: %s" % audio)
        self.ss = ss
        if not os.path.splitext(audio['question'])[1]:
            self.logger.info("We don't have audio, set play to False")
            self.wehaveaudio = False
            return
        else:
            self.wehaveaudio = True
        keys = audio.keys()
        self.audiolist = [audio['silence_1000']]
        self.audiolist.append(audio['question'])
        keys.sort()
        for k in keys[:-3]:
            self.audiolist.append(audio['silence_1000'])
            ad_k = k.split('_')[1]
            self.audiolist.append(ad_audio[ad_k][0])
            self.audiolist.append(audio['silence_500'])
            self.audiolist.append(audio[k])
    
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
        self.logger = logging.getLogger("schoolsplay.quizengine.Answer")
        self.connect_callback(self._cbf, MOUSEBUTTONDOWN, state)
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
        self.logger = logging.getLogger("schoolsplay.quizengine.Question")
        self.moveto(pos, hide=True)
        
class Engine:
    """Class that handles the sprites for the quizzes.
    All the quiz elements are sprites, the answers and prev/next are Button objects.
    The class uses the observer pattern to communicate with the caller
    """
    def __init__(self, quiz, spgoodies, observers, rchash=None):
        """Engine which controls the quiz sprites.
        quiz - String indicating which kind of quiz do we run.
               possible values: text,picture,math,melody,history, mixed.(more in the future)
        actives - SPGroup instance which is used by the caller in the eventloop
        observers - list with observer objects
        """
        self.logger = logging.getLogger("schoolsplay.quizengine.Engine")
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
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.content_imgpath = os.path.join(self.SPG.get_libdir_path(),'CPData','Quizcontent', self.lang, 'images')
        self.content_sndpath = os.path.join(self.SPG.get_libdir_path(),'CPData','Quizcontent', self.lang, 'sounds')
        self.ttfpath = TTF
        
        dbpath = os.path.join(HOMEDIR, self.theme, 'quizcontent.db')
        if len(quiz) > 1:
            quizlist = []
            for item in quiz:
                quizlist.append('%s_%s' % (item, self.lang))
            self.quiz = 'general'
        else:
            quizlist = ['%s_%s' % (quiz[0], self.lang)]
            self.quiz = quiz[0]
        self.CF = ContentFeeder(dbpath, 1, quizlist, rchash)
        if self.CF.get_num_questions() < 10:
            self.logger.error("To little questions found in %s, found %s questions should be at least 10" % (self.quiz, self.CF.get_num_questions()))
            raise ParserError, _("To little questions found in %s, found %s questions should be at least 10"% (self.quiz, self.CF.get_num_questions()))
        
        self.retry = 2# default values
        self.totalretry = 1
        self.answers_list = []
        self.currentscreen = None
        self.previous_list = []
        self.correct_answer = None
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
        self.question_pos = (15, 10 + y)
        self.answer2_pos = [((15, 200 + y),iconA, 'a'), ((15, 365 + y), iconB, 'b')]
        self.answer4_pos = [((15, 190 + y), iconA, 'a'), ((15, 270 + y), iconB, 'b'),\
                             ((15, 350 + y), iconC, 'c'), ((15, 430 + y), iconD, 'd')]
        self.logo_pos = (615, 200 + y)
        self.snd_pos = (700, 410 + y)
        self.prev_pos = (615, 410 + y)
        self.data_display_center = (600, 200 + y)
        if self.quiz == 'picture':
            y = 0
        self.good_image.moveto((229, 280 + y))
        self.good_image.set_use_current_background(True)

        picture_button_width = 380
        
        self.question_surf_long = load_image(os.path.join(self.my_datadir,'vraagbox.png'))
        self.question_surf_short = pygame.transform.smoothscale(self.question_surf_long,\
                                                (picture_button_width,\
                                                self.question_surf_long.get_rect().h ))
        
        self.answer2_surf_long = load_image(os.path.join(self.my_datadir,'box2.png'))
        self.answer2_surf_short = pygame.transform.smoothscale(self.answer2_surf_long,\
                                                (picture_button_width,\
                                                self.answer2_surf_long.get_rect().h ))
      
        self.answer2GR_surf_long = load_image(os.path.join(self.my_datadir,'box2_green.png'))
        self.answer2GR_surf_short = pygame.transform.smoothscale(self.answer2GR_surf_long,\
                                                (picture_button_width,\
                                                self.answer2GR_surf_long.get_rect().h ))

        self.answer2R_surf_long = load_image(os.path.join(self.my_datadir,'box2_red.png'))
        self.answer2R_surf_short = pygame.transform.smoothscale(self.answer2R_surf_long,\
                                                (picture_button_width,\
                                                self.answer2R_surf_long.get_rect().h ))

        self.answer4_surf_long = load_image(os.path.join(self.my_datadir,'box4.png'))
        self.answer4_surf_short = pygame.transform.smoothscale(self.answer4_surf_long,\
                                                (picture_button_width,\
                                                self.answer4_surf_long.get_rect().h ))
        
        self.answer4GR_surf_long = load_image(os.path.join(self.my_datadir,'box4_green.png'))
        self.answer4GR_surf_short = pygame.transform.smoothscale(self.answer4GR_surf_long,\
                                                (picture_button_width,\
                                                self.answer4GR_surf_long.get_rect().h ))
        
        self.answer4R_surf_long = load_image(os.path.join(self.my_datadir,'box4_red.png'))
        self.answer4R_surf_short = pygame.transform.smoothscale(self.answer4R_surf_long,\
                                                (picture_button_width,\
                                                self.answer4GR_surf_long.get_rect().h ))
        
        self.good4_surf = load_image(os.path.join(self.my_datadir,'box4_good.png'))
        self.wrong4_surf = load_image(os.path.join(self.my_datadir,'box4_wrong.png'))
        
        # Setup some of the static objects
        self.prevnext_button = TransPrevNextButton(self.prev_pos, \
                                              self._cbf_prevnext_button, \
                                              'core_prev_button.png', \
                                              'core_prev_button_ro.png', \
                                              'core_next_button.png', \
                                              'core_next_button_ro.png')
        
        self.snd_button = TransImgButton(os.path.join(self.my_datadir, 'speaker.png'), \
                                         None, self.snd_pos)
        self.snd_button.connect_callback(self._cbf_snd_button, MOUSEBUTTONDOWN)
                    
        self.good_sound=os.path.join(self.CPdatadir,'good.ogg')
        self.wrong_sound=os.path.join(self.CPdatadir,'wrong.ogg')
        
        if self.lang == 'en':
            p = os.path.join(self.SPG.get_libdir_path(),'SPData', 'themes',\
                                        self.theme,'menuicons', \
                                    'quiz_%s.icon.png' % self.quiz)
        else:
            p = os.path.join(self.SPG.get_libdir_path(),'SPData', 'themes',\
                                        self.theme,'menuicons', self.lang, \
                                    'quiz_%s.icon.png' % self.quiz)
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
        if data[0] == 'prev': self._cbf_prev_button(data)
        else: self._cbf_next_button(data)

    def _cbf_next_button(self, data):
        self.SS.clear_queue()
        self.logger.debug("_cbf_next_button: %s" % data)
        if not self.previous_list:
            return
        self._clear_screen()
        self.actives.add(self.answers_list)
        for s in self.answers_list:
            s.display_sprite()
        self.prevnext_button.toggle()
        if self.wehaveaudio:
            #self.snd_button.enable(True)
            self.snd_button.display_sprite()
        try:
            self.current_question_id = self.CF.served[-1]
        except IndexError:
            # this shouldn't happen
            self.current_question_id = -1
          
    def _cbf_prev_button(self, data):
        self.SS.clear_queue()
        self.logger.debug("_cbf_prev_button: %s" % data)
        self.actives.remove(self.answers_list)
        self._clear_screen()
        if self.logo_sprite:
            self.logo_sprite.erase_sprite()
        self.prevnext_button.toggle()
        for s in self.previous_list:
            s.display_sprite()
        if self.wehaveaudio:
            #self.snd_button.enable(False)
            self.snd_button.erase_sprite()
        try:
            self.current_question_id = self.CF.served[-2]
        except IndexError:
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
                pygame.time.wait(QUIZPAUSE)
                self.good_image.erase_sprite()
            else:
                self.maxresult = 0
                pygame.time.wait(QUIZPAUSE)
            self._notify_obs(self.maxresult)
            return
        if self.retry and result == 0:# correct answer for 4 answers
            self.good_image.display_sprite()
            pygame.time.wait(QUIZPAUSE)
            self.good_image.erase_sprite()
            self._notify_obs(self.maxresult)
            return
        self.maxresult -= result
        self.retry -= 1
        if self.retry == 0 and result:
            # whatever, your time has come to quit this pathetic attempt
            self.maxresult = 0
            self.correct_answer._display()
            self._notify_obs(self.maxresult)
            pygame.time.wait(QUIZPAUSE)
            return
        r = sprite.rect.move(100,0)
        self.tryagain_image.moveto((r[0], r[1]))
        self.tryagain_image.set_use_current_background(True)
        self.tryagain_image.display_sprite()
        self.erase_tryagain = True
        pygame.time.wait(QUIZPAUSE)
        #self.tryagain_image.erase_sprite()
        
    def _notify_obs(self, result):
        """Notify the callers observers and restart the next question
        """
        self.logger.debug("_notify_obs called, result = %s" % result)
        # keep sprites for the 'previous screen'
        self.previous_list = self.answers_list[:]
        if self.CF.WehaveWrong and result > 1:
            self.scoredisplay.increase_score(result*5)
            self.parent_observers(result/2.0)
        else:
            self.scoredisplay.increase_score(result*10)
            self.parent_observers(result)
        if result > -1:
            if result > 0:
                self.CF.set_exercise_result(self.current_question_id, 1)
            self.next_question()
        
    def _blit_on_me(self, surf, ls, x=10, y=10):
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

    def init_exercises(self,answers, maxtimes, difficulty, AreWeDT, year=None):
        """Setup some defaults for the contentfeeder.
        answers - Integer indicating how many answers we should display.
        maxtimes - the number of questions we show, 0 means until we ran out of questions
        difficulty - level of difficulty.
        """
        self.logger.debug("init_exercises: answers %s, maxtimes %s, difficulty %s, DT %s year %s" % \
                          (answers, maxtimes, difficulty, AreWeDT, year))
        # The first time were called by the caller quiz, then _next_question is called.
        # After that next_question is called in the _notify_obs method which is in turn called by the answer object.
        self.difficulty = difficulty
        self.CF.set_difficulty(difficulty, AreWeDT)
        self.answers = answers
        if not maxtimes:
            self.maxtimes = self.CF.get_num_questions()
        else:
            self.maxtimes = maxtimes
        self.numOfQuestions = 0
        p = os.path.join(self.SPG.get_libdir_path(), 'CPData', 'Quizcontent', '*.ogg')
        self.ad_audiohash = {'a':[], 'b':[], 'c':[], 'd':[]}
        for f in glob.glob(p):
            p, fp = os.path.split(f)
            if fp[0] in ('a', 'b', 'c', 'd'):
                self.ad_audiohash[fp[0]].append(f)
        if year:
            self.CF.filter_history_questions(year)
        #self.prevnext_button.enable(False)
            
    def next_question(self):
        self.logger.debug("next_question called")
#        print self.numOfQuestions,self.maxtimes
        if self.numOfQuestions < self.maxtimes:
            self.numOfQuestions += 1
            self.logger.debug("serve question #%s" % self.numOfQuestions)
            if not self._next_question():
                self.maxresult = -1# notify observer level end
                self._notify_obs(self.maxresult)
#        elif self.CF.have_wrong_exercise():
#            self.CF.use_wrong_exercise()
#            try:
#                if not self._next_question():
#                    self.maxresult = -1# notify observer level end
#                    self._notify_obs(self.maxresult)
#            except Exception:
#                self.logger.exception("Error while serving question, check the contents")
#                self.maxresult = -1# notify observer level end
#                self._notify_obs(self.maxresult)
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
            fsize = 34
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
        else:
            self.question_surf = self.question_surf_long
            self.answer2_surf = self.answer2_surf_long
            self.answer2R_surf = self.answer2R_surf_long
            self.answer2GR_surf = self.answer2GR_surf_long
            self.answer4_surf = self.answer4_surf_long
            self.answer4R_surf = self.answer4R_surf_long
            self.answer4GR_surf = self.answer4GR_surf_long
                
        qs = self.question_surf.convert_alpha()
        if result == 'short':
            split = 22
            ans_split = 21
        else:
            split = 48
            ans_split = 44
        text_blit_x = 50
        txt, audio = exer['question']
        audiohash['question'] = os.path.join(self.content_sndpath, audio)
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
            s_c = self._blit_on_me(s_c, ts, x=50, y=38)
            # and the green one
            s_c_g = self.answer2GR_surf.convert_alpha()
            s_c_g = self._blit_on_me(s_c_g, ts, x=50, y=38)
            
            # blit the wrong anwser
            ts = char2surf(txt_w, fsize, ttf=fnt, bold=False, fcol=ANTIQUEWHITE, split=ans_split)  
            s_w = self.answer2_surf.convert_alpha()
            s_w = self._blit_on_me(s_w, ts, x=50, y=38)
            # and the red one
            s_w_r = self.answer2R_surf.convert_alpha()
            s_w_r = self._blit_on_me(s_w_r, ts, x=50, y=38)
            
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
        
        if self.numOfQuestions > 1:
            self.prevnext_button.enable(True)
            self.prevnext_button.display_sprite()
        else:
            self.prevnext_button.enable(False)
            self.prevnext_button.erase_sprite()
        self.audioplayer = AudioPlayer(audiohash, self.ad_audiohash, self.SS)
        self.audioplayer.play()
        if self.wehaveaudio:
            self.snd_button.display_sprite()
        self.current_question_id = self.CF.get_current_id()
        return True

    def loop(self, events):
        for event in events:
            if event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                result = self.actives.update(event)
        return self.maxresult == -1
    
if __name__ == '__main__':
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
    
    # Test ContentFeeder
    db = os.path.join(HOMEDIR, 'childsplay', 'quizcontent.db') 
    tp = ['math_nl']
    dif = '1'
    cf = ContentFeeder(db, dif, tp)
    cf.get_exercise()
    
    
    
    
