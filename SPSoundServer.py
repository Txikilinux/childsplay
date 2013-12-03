# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           SPSoundServer.py
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

# Simple threaded soundserver with minimal features to make it as bullutproof
# as possible. We must never leave a stale soundserver thread running after
# a crash or whatever. It's nearly impossible for BT users to kill threads.

import os,sys,time
import utils
import logging
from threading import Thread,enumerate
import atexit
import pygame

class SoundServer:
    """ Threaded soundserver which plays the files placed on the queue.
    It checks for the existence of the file and when it doesn't exists it will
    be removed from the queue and a error message will be placed in the logs.
     """         
    server_allready_running = False
    def __init__(self, sleep=0.2):
        """ This will start the server, the sleep value is the time the server
        will sleep between polling the message queue"""
        self.logger = logging.getLogger("childsplay.SPSoundServer")
        if self.server_allready_running:
            self.logger.debug("Soundserver allready running. You should first stop the server before you start a new one.")
            return
        # These are the attributes which shared between the threads
        self.sleep = sleep
        self.queue = []
        self.workingserver = True
        self.serverstatus = True
        self.serverping = False
        self.stopplaying = False
        self.start_server()
                        
    def __del__(self):
        try:
            self.stop_server(0)
        except:
            pass

    def start_server(self):
        if not self.server_allready_running:
            self.queue = []
            self.workingserver = True
            self.logger.debug("(re)starting soundserver")
            try:
                self.thread = Thread(target=self._start_server)
                self.thread.start()
                time.sleep(0.1)
            except Exception,info:
                self.logger.exception("SoundServer startup problem")
                self.serverstatus = False
                self.server_allready_running = False
            else:
                self.logger.debug("SoundServer running: %s" % self.thread)
                self.server_allready_running = True

    def stop_server(self,s=1):
        """ Stops a running server, after one second(default). 
        The delay is for stuff to finish, you can use stop_server(0) to stop now."""
        if not hasattr(self,"thread") or self.workingserver == 0:
            return
        self.logger.debug("stop_server called with delay: %s" % s)
        time.sleep(s)
        self.workingserver = False
        time.sleep(0.2)# give the thread the chance to terminate itself
        # Or in case it's playing something we just kill it :-/
        pygame.mixer.music.stop()
        self.logger.debug("result of stop_server (remaining threads):%s" % enumerate())
        self.server_allready_running = False
        self.serverstatus = False

    def play(self, file):
        """Creates a SDL music object from the file and places the file
        on the stack for the server to play.
        It returns True when the server isn't running or the file doesn't exists.
        """
        self.stopplaying = False
        if not self.server_allready_running:
            self.logger.error("sound server not running")
            return True
        if file != "PING" and not os.path.exists(file):
            self.logger.error("SoundServer: %s doesn't exists" % file)
            self.stop()
            return True
        #self.logger.debug("placed %s on the queue" % file)
        self.queue.insert(0, file)# The server checks the stack for messages
        return
    
    def clear_queue(self):
        """Clears the queue, useful when you want to interrupt the playing and
        play a new file."""
        self.queue = []
    
    def stop(self):
        """Stops the music but leaves the server running."""
        pygame.mixer.music.stop()
        self.stopplaying = True
        #self.queue = []
    
    def ping_server(self):
        """ Use this to test if the server is running.
        This actually sends a message to the server and the server signals
        back, this is done to check the message queue aswell.
        Be aware that this call pauses for half a second the current thread.
        It return True when the server is running and False when it's not."""
        self.serverping = False
        self.queue.insert(0,("PING", utils.NoneSound))
        time.sleep(0.5)
        self.logger.debug("result of ping_server:%s" % self.serverping)
        if self.serverping: 
            return True
        else: 
            return False

    def _start_server(self):
        """ This runs in a seperate thread and plays the sound object from the queue
        in a seperate thread also. Don't call this method, it is called from the class 
        constructor."""
        while self.workingserver:
            try:
                msg = ''
                try:
                    if self.queue:
                        msg = self.queue.pop()
                        #self.logger.debug("message from stack: %s" % msg)
                except IndexError:
                    pass
                else:
                    if msg:
                        if msg == "PING":
                            self.logger.debug("server pinged: running")
                            self.serverping = True                    
                        else:
                            while pygame.mixer.music.get_busy():
                                if self.stopplaying:
                                    self.logger.debug("server stopplaying set to True, stop playing %s" % msg)
                                    #self.queue = []
                                    self.stopplaying = False
                                    pygame.mixer.music.stop()
                                    break
                                pygame.time.wait(200)# prevent cpu hogging
                            else:
                                #self.logger.debug("playing: %s" % msg)
                                pygame.mixer.music.load(msg)
                                pygame.mixer.music.play()
                        
                time.sleep(self.sleep)
            except:
                self.logger.exception("Troubles in server thread, stopping server.")
                pygame.mixer.music.stop()
                self.stop_server(0)
        try:
            pygame.mixer.music.stop()
        except:
            pass
        self.logger.debug("Server stopped")
                

if __name__ == '__main__':
    
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
    
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
        
    import pygame
    from pygame.constants import *
    pygame.init()    
    scr = pygame.display.set_mode((100, 100))
    
    ss = SoundServer()
    ss.play("test.ogg")
    ss.ping_server()
    ss.play("test.ogg")
    
    runloop = 1 
    while runloop:
        pygame.time.wait(500)
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            if event.type is KEYDOWN:
                if event.key == K_ESCAPE:
                    print "escape hit, stopping main"
                    runloop = 0
        print "main doing stuff"
    
    ss.stop_server(0)
    raw_input("hit any key to quit")
