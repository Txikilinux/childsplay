# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           Timer.py
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

import time

import atexit
import logging
import threading
from SPSpriteUtils import MySprite, SPSprite
from utils import char2surf

module_logger = logging.getLogger("childsplay.Timer")

# In the Timer related classes the logger is disabled because it can flood the
# logfile. (especially with find_char_sound)
class Worker(threading.Thread):
    """Thread object internally used and called by Timer.
    Don't use this directly, use Timer.""" 
    
    def __init__(self, delay=None, func=None, fargs=None, loop=1, lock=None, cb_func=None, now=False):
        self.logger = logging.getLogger("childsplay.Timer.Worker")
        threading.Thread.__init__(self)
        self.__delay = delay
        self.__func = func
        self.__fargs = fargs
        self.__loop = loop
        self.__do = 1
        self.__die = False
        self.__lock = lock
        self.__cb_func = cb_func
        self.__now = now
        atexit.register(self._stop)
        
    def __sleep(self, secs):
        """Sleep fuction that checks every tenth of a second to see if we should die"""
        while secs > 0:
            if not self.__do:
                break
            if self.__lock and self.__lock.locked():
                #print "locked continue to sleep"
                time.sleep(0.1)
                continue
            time.sleep(0.1)
            secs -= 0.1
    
    def run(self, now=False):
        """This overrides the threading.Thread.run method."""
        #self.logger.info("Timer started")
        if self.__now:
            apply(self.__func, self.__fargs)
        while self.__do:
            if self.__die:
                break
#            if self.__lock and self.__lock.locked():
#                print "locked and sleeping 100 msec"
#                time.sleep(0.1)
            self.__sleep(self.__delay)
#            if self.__lock and self.__lock.locked():
#                print "locked and again sleeping 100 msec"
#                time.sleep(0.1)
            try:
                if not self.__do:
                    # this is done because when we call _stop when we in time.sleep
                    # the __func will set it back and the thread will never die.
                    break
                self.__do = apply(self.__func, self.__fargs)
            except Exception:
                self.logger.exception("Timer stopped due to an exception in %s" % self.__func)
                self.__do = 0
            self.__loop -= 1
            if not self.__loop: self.__do = 0
        #self.logger.info("Timer thread stopped")
        if self.__cb_func:
            apply(self.__cb_func)
            
    def _stop(self):
        """Used to stop the thread.
        DON'T call this directly, use Timer.stop()."""
        self.__do = 0
        self.__die = True
            
class Timer:
    def __init__(self, delay=1, func=None, fargs=(), loop=-1, lock=None, cb_func=None, startnow=False):
        """Timer, a timer object which runs in a seperate thread and calls the
        function 'func' with the arguments 'fargs' after 'delay' seconds for 
        'loop' times.
        'fargs' defaults to (), and 'loop' defaults to -1 which means
        loop forever.
        lock is a threading.lock object
        cb_func is a function that is called when the timer stops. 
        The timer checks the return value of the called function and will stop
        when the return value is false.
        So you should make sure you return true when you want to continue and false
        on error or when it should stop.        
            
        After construction you must call the start method to actual start 
        the timer.
        The timer register a function in the atexit module to cleanup any threads
        still running when the main application exits.
        Be aware that if your application doesn't exit in a 'normal' way the 
        atexit function might not work. (not normal ways are exceptions that are
        not cached by your app and terminate the program.)        
        """
        self.logger = logging.getLogger("childsplay.Timer.Timer")
        #self.logger.debug("Timer created")
        self.worker = Worker(delay, func, fargs, loop, lock, cb_func, now=startnow)
    
    def start(self):
        """Start the timer object."""
        #self.logger.info("Starting timer...")
        self.worker.start()
                    
    def stop(self):
        """Stop the timer."""
        #self.logger.info("Stopping timer...")
        self.worker._stop()

class Clock(SPSprite):
    """"""
    def __init__(self, start='00:00', counting=1, end='10:00',
        clocksize=32, clockpos=(0, 0), clockcolor=(0, 0, 0),
        text='', textsize=18, textcolor=(0, 0, 0), textpos=1,
        alarm=None, lock=None):
        """Timer clock. This clock depends on SpriteUtils object which is part
        of the childsplay project (http://childsplay.sf.net).
        @start is the start value of the clock in a string and must contains 
        a colon as a seperation between minutes and seconds.
        @counting must be an integer 1 or -1 and is used to tell the clock to
        count up (1) or down (-1). You should make sure the @start has a suitable
        format to count up or down otherwise you could have negative values.
        @end is the end time in a string, format is the same as @start.
        @text is a string to be displayed together with the clock.
        @textpos can be 1 to 4 to set the position of the text related to the
        clock. 1 is on top, 2 right, 3 bottom, 4 left.
        @alarm is called when the end time is reached, should be a callable function.
        It defaults to None.
        The rest will be obvious.
        
        This class implements the Timer.Timer object so you should make sure
        you don't leave threads running in case of a exception."""
        self.logger = logging.getLogger("childsplay.Timer.Clock")
        self.__csurf = char2surf(start, clocksize, clockcolor)
        SPSprite.__init__(self, self.__csurf)
        
        self.__tsprite = MySprite(char2surf(text, textsize, textcolor))
        
        # convert textpos into a xy coordinate
        if textpos == 1:
            x = clockpos[0]
            y = clockpos[1] - textsize
        elif textpos == 3:
            x = clockpos[0]
            y = clockpos + clocksize
        elif textpos == 2:
            x = clockpos[0] + self.__csurf.get_width()
            y = clockpos[1] + \
                ((self.__csurf.get_height() / 2) - (self.__tsprite.get_sprite_height() / 2))
        elif textpos == 4:
            x = clockpos[0] - self.__tsprite.get_sprite_width() 
            y = clockpos[1] + \
                ((self.__csurf.get_height() / 2) - (self.__tsprite.get_sprite_height() / 2))
        self.__tpos = (x, y)
        m, s = start.split(':')
        self.__startminutes, self.__startseconds = int(m), int(s)
        self.__start = start
        m, s = end.split(':')
        self.__endminutes, self.__endseconds = int(m), int(s)
        self.__minutes = self.__startminutes
        self.__seconds = self.__startseconds
        self.__end = end
        self.__count = counting
        self.__csize = clocksize
        self.__cpos = clockpos
        self.__ccol = clockcolor
        self.__text = text
        self.__tsize = textsize
        self.__tcol = textcolor
        self.__alarm = alarm
        self.__clock_stopped = 0
        self.__clock = Timer(1, self.__update, loop=-1, lock=lock)
    
    def start_clock(self):
        self.display_sprite(pos=self.__cpos)
        self.__tsprite.display_sprite(pos=self.__tpos)
        self.__clock.start()
        
    def stop_clock(self):
        self.__clock.stop()
    def get_display(self):
        return (self.rect, self.image)
    def get_time(self):
        return "%02d:%02d" % (self.__minutes, self.__seconds)
        
    def __update(self):
        if self.__clock_stopped:
            return
        if self.__minutes == self.__endminutes and \
            self.__seconds == self.__endseconds:
            if self.__alarm:
                try:
                    apply(self.__alarm)
                except Exception:
                    self.logger.exception("Exception in %s" % self.__class__)
                self.__clock.stop()
                self.__clock_stopped = 1
                return
        if self.__count == 1:# forwards
            if self.__seconds == 59:
                self.__seconds = 0
                self.__minutes += self.__count
            else:
                self.__seconds += self.__count
        else:# backwards
            if self.__seconds == 0:
                self.__seconds = 59
                self.__minutes += self.__count
            else:
                self.__seconds += self.__count
        time = "%02d:%02d" % (self.__minutes, self.__seconds)
        self.__tsprite.erase_sprite()
        self.erase_sprite()
        self.image = char2surf(time, self.__csize, self.__ccol)
        self.display_sprite()
        self.__tsprite.display_sprite()
        return 1

if __name__ == '__main__':
    i = 0
    def test( *args):
        global i
        i += 1
        print i, "message from test"
        if args: 
            print "args from test", args
        return 1
        
    t = Timer(1, test, ('these are the args', ), loop=60)
    print "Start timer (60 times)"
    t.start()
    while i < 60:
        pass
    print "wait 2 seconds"
    time.sleep(2)
    print "and do some stuff in main"
    print "wait another 2 secs"
    time.sleep(2)
    print "and now stop the timer"
    t.stop()
    
