# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPSpriteUtils.py
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

"""
SPSpriteUtils - Module which provides some high level extensions to the 
basic pygame.sprite classes.

class SPSprite - A class which extends the standard pygame Sprite class.

class SPGroup - A class which extends the standard pygame RenderUpdate group class.

You should let your classes inherit from these classes.
For a detailed explanation you should check the pygame docs as we just extends
that class.
Also look at the docstrings in these classes for more info.
"""

import math
import sys
import os
import logging
import pygame
import types
from pygame.constants import *
from types import StringType

from utils import MyError, char2surf, load_image
from SPConstants import ACTIVITYDATADIR

module_logger = logging.getLogger("schoolsplay.SPSpriteUtils")

def SPInit(scr, back, group=pygame.sprite.Group(), theme='default'):
    """ Init(back,scr,group=pygame.sprite.Group()) -> SPGroup instance
        
         This MUST be called BEFORE the SpriteUtils classes are used, and is needed
         for some of the magic.
         It's very straight forward and can probably used for all plugins.
         It must be called with references to the background surface and display surface.
         back = background surface.
         scr = display surface.
         
         group = pygame.sprite group used as the group which holds all the sprites.
         You probably don't want to change this group.
         
         theme  = The them used. Optional only needed for the GUI stuff from SPSpriteGui.
         The group instance returnt is a extended pygame.sprite group, which you should
         use to put your sprites in and then call the refresh method to update all the
         sprites. Be sure to check the reference before using this high level classes.
         It also possible to call this function multiple times to get multiple classes, but be aware
         that they all share the same screen and background surfaces. 
         """
    
    logger = logging.getLogger("schoolsplay.SPSpriteUtils.SPInint")
    
    SPSprite.group = pygame.sprite.Group()# base class to hold sprites
    # All the objects which derives from SPSprite belongs to this group.
    # store a reference, needed for removal and erasing of sprites
    SPSprite.backgr = back
    SPSprite.screen = scr
    
    # SPGroup needs screen and backgr to erase and draw the sprites
    # belonging to this group
    g = SPGroup(scr, back)# special CP group
    return g

class SPSprite(pygame.sprite.Sprite):
    """ Class to inherited from by regular sprite classes.
     When you extend this class you must call the constructor *before* you alter
     the 'rect' member. 
     
     This class calls the pygame.sprite.Sprite constructor and adds itself
     to the RenderUpdates group.
     There's also the possibility to connect a callback method to a pygame event
     much like the GTK/libglade way of callbacks.
     
     Be aware that this class derives from the pygame Sprite class, so
     there are two mandatory attributes: 'image' and 'rect'.
     See the pygame.sprite.Sprite reference for more information.
     
     You MUST call the init function BEFORE you use anything in this module.
    """
    
    def __init__(self, image=None, name=None):
        """Turn an image into a sprite object.
        image - pygame.Surface. If set to None you must set the image and rect
                attributes before using it. Only set it to None if you know
                why you want it too be None.
        name - a string so that one can do: if sprite_obj == 'foobar':"""
        pygame.sprite.Sprite.__init__(self)# This must be set before using this class
        self.logger = logging.getLogger("schoolsplay.SPSpriteUtils.SPSprite")
        self.DEBUG = 0
        # make sure we have a correct background
        #self.backgr = self.backgr.convert()
        #self.backgr.blit(self.screen, (0, 0))
        self.image = image
        if self.image:
            self.rect = image.get_rect()
        
        self.hover_active = False
        self._args = [self] # default value to pass to update functions
        self._event_type = None # default in case there's no callback while there's a mouseevent
        self._callback = None # same as with self.event_type
        # defaults for movement of the object
        self._start = (0, 0)
        self._end = (0, 0)
        self._vector = (0, 0)
        self.__name = name
        self.name = name
        self._moveit_iter = None
        # needed for rotation
        self.__dir = 0
        self.__OrgImage = self.image #comes from the derived class
        # a group that owns by this sprite, used to address common properties
        # of sprites within the group
        self.group_owner = None
        self.UseCurrentScreenAsBackground = False
        self.erasesurf = None
    
    def get_name(self):
        return self.__name

    def set_group_owner(self, group):
        """Set group that owns by this sprite"""
        self.group_owner = group        
    
    def set_use_current_background(self, bool=False):
        self.UseCurrentScreenAsBackground = bool
    
    def __eq__(self, x):
        return x == self.__name
    def __ne__(self, x):
        return x != self.__name
    
    def mouse_hover_enter(self):
        """Called by the update method when a MOUSEMOTION event occurs and the 
        mouse is inside our rect.
        Derived gui widget classes should override this method."""
        self.hover_active = True
        
    def mouse_hover_leave(self):
        """Called by the update method when a MOUSEMOTION event occurs and the 
        mouse is outside our rect.
        Derived gui widget classes should override this method."""
        self.hover_active = False

    def connect_callback(self, callback=None, event_type=None,  * args):
        """ Connect a callback function to a pygame event type with a optional arguments, the *args tuple.
         
         The event_type can be set to a pygame.event, this becomes the event
         to 'trigger' the callback. (see update method)"""
        self._callback = callback
        self._event_type = event_type
        self._args = args
        if self.DEBUG == 1: print "connect_callback", callback, event_type, self._args

    def disconnect_callback(self):
        """Disconnects the callback from the sprite.
        When you want to reconnect the callback you must reset it again with connect_callback"""
        c, e, a = self._callback, self._event_type, self._args
        self._args = [self]
        self._event_type = None 
        self._callback = None
        return (c, e, a)

    def update(self, event=None):
        """ When there's a callback function set it will run the function, then the
        on_update method is called when it exist. 
        
         It is best to loop the event queue and look for a event, then call the group
         refresh method with the event, which updates  all the sprites as well as it 
         calls this method.
         It returns the return values of resp. on_update and the callback, or None 
        """ 
        cb, ou = None, None
        if event:
            if self._callback and event.type is self._event_type:
                # self.rect is the rect from the sub class
                if self._event_type == MOUSEBUTTONDOWN and \
                    self.rect.contains((pygame.mouse.get_pos() + (0, 0))) or\
                        self._event_type == KEYDOWN:
                    # we check if we should call all possible matches
                    if not (self.group_owner and self.group_owner.get_onematch()):
                        try:
                            #print "--------call cbf-----------"
                            cb = apply(self._callback, (self, event, self._args))
                        except StandardError, info:
                            self.logger.exception("Callback function %s failed" % self._callback)
                            self.logger.error(info)
                            return
                    else:
                        # we do not need to check existence of self.group_owner because we get
                        # here only if it exists.
                        if not self.group_owner.get_havematch():
                            self.group_owner.set_havematch(True)
                            try:
                                cb = apply(self._callback, (self, event, self._args))
                            except StandardError, info:
                                self.logger.exception("Callback function %s failed" % self._callback)
                                self.logger.error(info)
            elif event.type is MOUSEMOTION:
                collide = self.rect.collidepoint(pygame.mouse.get_pos())
                if collide and not self.hover_active:
                    self.mouse_hover_enter()
                elif self.hover_active and not collide:
                    self.mouse_hover_leave()
        if hasattr(self, "on_update"):
            if cb:
                apply(self.on_update, self._args)
            else:
                ou = apply(self.on_update, self._args)
        return cb or ou
    
    def on_update(self,  * args):
        """ Always called by the group 'update' and 'refresh' methods and will
        move the sprite when a movement is set, you can override this to set
        your own 'update' stuff.
        
        This method just calls the 'next' method on the iterator returnt by
        the 'set_movement' method if it is set. Nothing more.
        When you override this method you must call 'next' yourself on the
        iterator returnt by 'set_movement'. But be aware that if you don't
        override this method you shouldn't call 'next' on the iterator as it
        would be called in here also."""
        if self._moveit_iter:
            try:
                self._moveit_iter.next()
            except StopIteration:
                self._moveit_iter = None
                self.stop_movement(now=1)
            except:
                self.logger.exception("Error while calling on_update. Killing sprite.")
                self.dokill = 1
                self.stop_movement(now=1)
    
    def set_movement(self, start=(0, 0), end=(0, 0), step=1, retval=0, loop=1, dokill=0):
        """ Define the movement of the object, it returns a generator.
        
         start = tuple x,y
         end = tuple x,y
         vector = tuple offset x, offset y
         retval = can be anything and is used as return value when the end of the 
         movement is reached.
         loop = times to loop before we signal retval, -1 means forever.
         dokill = kill the sprite by calling the kill() method when the movement is done.
        """
        self._stop_moveit = 0# flag used to stop a movement
        self._start, self._end, self._step, self._retval, self._loop = \
            start, end, step, retval, loop
        self.rect.topleft = self._start# place it in the start position
        #print "sprite moved to",self._start
        self.dokill = dokill 
        # also a class attribute so that on_update can call it.
        self._moveit_iter = self._moveit()
        return self._moveit_iter
        
    def _moveit(self):
        """ Move this object according to the values in movement.
        
         The set_movement method should be called before this one.
         Returns -1 when the movement continues, and the given return value when
         it stops. (the retval argument from set_movement)."""
        if self._stop_moveit:#test if the flag is set, see def stop_moveit
            yield self._retval
        
        x0, y0 = self._start
        x1, y1 = self._end
        
        dx = x1 - x0
        dy = y1 - y0
        dist = math.sqrt((dx * dx) + (dy * dy))
        nhops = int(dist)
        for i in range(1, 1 + nhops, self._step):
            if self._stop_moveit:#test if the flag is set, see def stop_moveit
                yield self._retval
            x, y = x0 + dx * i / nhops, y0 + dy * i / nhops
            # Remember that self.rect is a mandatory member of any SPSprite class
            self.rect.topleft = (x, y)
            #print x,y,self.rect
            yield -1
        if self._loop == -1: # we loop forever
            self._moveit() # recursive call 
        # when we are here, we loop a finite amount of times
        self._loop -= 1
        if self._loop > 0:
            self._moveit()
        # when we are here the motion is ended.
        self.stop_movement(1)
        yield self._retval
        
    def stop_movement(self, now=None):
        """This stops any running movement, when 'now' is set it will terminate
        
        the movement by changing the return value from 'moveit', else we change the
        loop attribute. This way the movement stops when the current run is done."""
        if now:
            self._stop_moveit = 1
            self._loop = 0# to be sure
        else:
            self._loop = 0
        if self.dokill:
            self.erase_sprite()
            self.kill()
            
    def moveto(self, pos, hide=True):
        """ Move the sprite to a new position.
        
        This will erase the sprite on it's old position and redraw it on the new
        position.
        When @hide is True the sprite is only moved but not shown"""
        if hide:
            self.rect.topleft = pos
        else:
            self.erase_sprite()
            self.display_sprite(pos)
    
    def display_sprite(self, pos=None):
        """ Display a sprite without the need to call group methods.
        
        Usefull for just displaying this sprite, nothing more.
        It takes an optional argument 'pos' which will place the sprite to
        that location."""
        if self.UseCurrentScreenAsBackground:
            #self.backgr = pygame.display.get_surface()
            self.erasesurf = pygame.Surface(self.image.get_size())
            self.erasesurf.blit(pygame.display.get_surface(), (0, 0), self.rect)
        if pos:
            self.rect.topleft = pos
        r = self.screen.blit(self.image, self.rect)
        pygame.display.update(r)

    def erase_sprite(self):
        """ Erase a sprite without the need to call group methods.
        
        Usefull for just erasing this sprite, nothing more."""
        #print "self",self,"erase rect",self.rect
        #r = self.screen.blit(self.backgr, self.rect.inflate(6, 4), self.rect.inflate(6, 4))
        #r = self.screen.blit(self.backgr, self.rect, self.rect)
        if self.erasesurf:
            r = self.screen.blit(self.erasesurf, self.rect)
        else:
            r = self.screen.blit(self.backgr, self.rect, self.rect)
        pygame.display.update(r)
    
    def remove_sprite(self):
        """ Remove this sprite object from all the groups it belongs.
        
          as well as remove it from the screen. This calls pygame.display.update
          The sprite is returnt so that you can keep a reference.
        """
        #self.screen and self.backgr are set by _Sprite_setup
        self.kill()# removes this object from any group it belongs
        self.erase_sprite()
        return self
    
    def rotate_sprite(self, amount):
        """ Rotate the sprite by the amount given. The image should be loaded
        without setting aplha channel otherwise pygame will crash!!
        See utils.load_image for arguments to unset alphachannel.
        
        Positive degrees rotates counterclockwise.
        Negative degrees rotates clockwise"""
        oldCenter = self.rect.center
        self.__dir += amount
        if self.__dir >= 360:
            self.__dir = 0
            self.image = self.__OrgImage
        self.erase_sprite()
        self.image = pygame.transform.rotate(self.__OrgImage, self.__dir)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter
        self.display_sprite()
    
    def get_sprite_height(self):
        """ Returns the height of the surface used in this sprite"""
        return self.image.get_height()
    def get_sprite_width(self):
        """ Returns the width of the surface used in this sprite"""
        return self.image.get_width()
    def get_sprite_rect(self):
        """ Returns the rect of the sprite"""
        return self.rect
    def get_sprite_pos(self):
        """ Returns the position of the sprite"""
        return self.rect.topleft

class SPGroup(pygame.sprite.RenderUpdates):
    """ Group  wich extends the standard RenderUpdates group.
    
    This is meant to use together with the SPSprite class.
    You MUST call the init function BEFORE you use anything in this module.
    
    Look at the examples that came with this module for possible usage.
    If you want to grok this magic, look at the pygame docs (sprite classes).
    The best you can do is just use the magic from the example ;-)
     """
    def __init__(self, scr, bck):
        """__init__(scr,bck)
           scr = reference to the display screen.
           bck = reference to a background screen."""
        self.logger = logging.getLogger("schoolsplay.SPSpriteUtils.SPGroup")
        self.DEBUG = 0
        pygame.sprite.RenderUpdates.__init__(self)
        self.scr = scr
        self.bck = bck
        self.__onematch = False
        self.__havematch = False 
        
    def refresh(self,  * args):
        """ Clear the sprites, calls the update method on the sprites,
        redraw the sprites and update the display.
        It returns the return values of any on_update or callback function.
        Look at the update method for a example of the stuff returnt."""
        self.clear(self.scr, self.bck)
        if args:
            v = self.update(args[0])
        else:
            v = self.update()
        if self.DEBUG: print >> sys.stderr, self.__class__, "returnt from self.update", v
        rects = self.draw(self.scr)    
        pygame.display.update(rects)
        return v
        
    def redraw(self):
        """ Clear the sprites, redraw the sprites.
        """
        for s in self.sprites():
            s.erase_sprite()
            s.display_sprite()
        

    def get_stack_ids(self):
        return self.sprites()

    def get_sprites(self):
        """ get_sprites, returns a list of the sprites currently in the group.
        It's almost the same as group.sprites but this will always return a list,
        group.sprites can return in the future an iterator.
        Anyway, use this if you want a real list of your sprites."""
        return [x for x in self.sprites()]

    def add(self, *sprites):
        """add a sprite to group

        add(...) reuses pygame.sprite.RenderUpdates.add to add a sprite or
        sequence of sprites to a group.
        Before actual adding the sprite to the group, the linkage between the
        sprite and the group is set"""
        for sp in sprites:
            if isinstance(sp, SPSprite):
                sp.set_group_owner(self)
        pygame.sprite.RenderUpdates.add(self, *sprites)
    
    def set_onematch(self, onematch=False):
        """Manipulate the behaviour of the sprites to an event.
        
        When @onematch is true then the calling of callbacks stops after one
        matching event. For example when you have multiple sprites on top of each other
        and the user clicks on the top sprite, all the sprites below the top one 
        reacts to the event as if they were also clicked.
        By setting one_match only one sprite reacts and the rest is ignored."""
        #self.logger.debug("onematch is set to %s", onematch)
        self.__onematch = onematch

    def get_onematch(self):
        #self.logger.debug("onematch is %s", self.__onematch)
        return self.__onematch

    def set_havematch(self, havematch=False):
        """Manipulates the flag which reflects whether the group of the sprites
        has already handles an event
        
        If __onematch attribute of the group is set to true and a sprite within
        the group triggers an event, it sets __havematch in true as so other
        sprites in the group will not handle this event
        The flag is used to re-set to false as soon as all sprites within the
        group are updated with the event"""
        #self.logger.debug("havematch is set to %s", havematch)
        self.__havematch = havematch

    def get_havematch(self):
        #self.logger.debug("havematch is %s", self.__havematch)
        return self.__havematch

    def update(self, *args):
        """update(...), this overrides the pygame.sprite.group.update
           call update for all member sprites

           calls the update method for all sprites in the group.
           Passes all arguments on to the Sprite update and callback function.
           It returns all the return values of these functions in a list.
           
           Example: [(sprite name,return val),(sprite name,return val)]
           sprite name is sprite.__class__, so you can change it to make the sprite name unique.
           return val is the val returnt by the SPSprite.update method and it's the value from the callback
           function if it exist otherwise it's from the on_update."""
        l = []
        l_append = l.append
        if args:
            a = apply
            for s in self.spritedict.keys():
                v = a(s.update, args)
                #v = s.update(args)
                if self.DEBUG: print >> sys.stderr, self.__class__, "returnt from SPGroup update", v
                if v:
                    l_append((s, v))
        else:
            for s in self.spritedict.keys():
                s.update()
        # reset any match 
        # do not use set_havematch here due to overhead - update() is invoked too often
        self.__havematch = False
        return l
        
class CPStackGroup:
    """ Group which mimics the pygame.sprite groups, but keeps the sprites
    it contains on a stack so that you have control over the way the sprites are handled.
    
    Besides typical stack like stuff like pop and push this group keeps a reference
    to each sprite that gets added, which is also returned when the sprite is added.
    Use this group when you want to manage the way and moment each sprite is updated.
    The way the sprites are cleared is by getting a run-time background rect of the area
    of the sprite just before it gets drawn.
    The stack makes also possible to raise or lower sprites.
    See the actual methods on usages.
    Be aware that this group sprite updating methods involves a lot of overhead, so use
    it only if you need some of the features it provides.
    
    You MUST call the init function BEFORE you use anything in this module.
    """
    _spritegroup = 1 #dummy val to identify groups
    
    def __init__(self, scr, bck):
        """__init__(scr,bck)
           scr = reference to the display screen.
           bck = reference to a background screen.
        """
        self.DEBUG = 1
        self.stack = []# becomes [(ID,sprite),(ID,sprite),...]
        self.ID = 0 # becomes self.ID += 1 : str(self.ID)
        self.scr = scr
        self.bck = bck

    def add(self, sprite):
        """add(sprite)
           add sprite to the group and push it/them on the stack."""
        try: 
            len(sprite) #see if its a sequence
        except (TypeError, AttributeError):
            id = self.push(sprite)
            sprite.add_internal(self)
            return id
        else:
            t = ()
            for s in sprite:
                t = t + self.push(s)
                s.add_internal(self)
            return t

    def get_sprite(self, id):
        """get(id)
           Get a sprite from the stack.
           
           This returns a sprite but does NOT remove it.
           """
        found = self._find_in_stack(id)
        if found != -1:
            s = self.stack[found][1]
            return s
            
    
    def push(self, sprite):
        """push(sprite)
           Push a sprite on the stack."""
        self.ID += 1
        id = str(self.ID)
        self.stack.append((id, sprite))
        return id
    
    def pop(self, index=-1):
        """pop(index=-1)
           Pop a sprite from the stack, remove and return the last one added.
           
           Optional you can give a index which item to pop.
           It defaults to -1, the last item."""
        try:
            s = self.stack.pop(index)[1]
        except IndexError:
            return None
        else:
            r = self.scr.blit(self.bck, s.rect, s.rect)
            #print "pop clear",s.rect,"rect",r
            pygame.display.update(r)
        return s
        
                     
    def _find_in_stack(self, sprite):
        # search the stack for a sprite, sprite can be a sprite object or a ID string
        index = 0
        for item in self.stack:
            if sprite in item:
                return index
            else:
                index += 1
        return -1# not found      
        
    def add_internal(self, sprite):
        self.push(sprite)


    def remove(self, sprite):
        """remove(sprite)
           remove sprite from the stack and group

           Remove a sprite or sequence of sprites from the stack and group."""
        try:
            len(sprite) #see if its a sequence
        except (TypeError, AttributeError):
            found = self._find_in_stack(sprite)#returns a index
            if self.DEBUG == 1: print "found", found
            if found != -1:
                self.remove_internal(found)
                sprite.remove_internal(self)
        else:
            for s in sprite:
                found = self._find_in_stack(s)
                if found != -1:
                    self.remove_internal(found)
                    sprite.remove_internal(self)
                    
    def remove_internal(self, index):
        found = self._find_in_stack(index)
        if found != -1:
            self.pop(found)
            

    def draw(self,  * args):
        """draw(surface)
           draw all sprites onto the surface

           Draws all the sprites onto the given surface. It
           creates a list of rectangles, which which are passed
           to pygame.display.update()
           Sprites are first erased and then drawn "FILD",
           First In Last Drawn."""
        bck = self.bck
        scr_blit = self.scr.blit
        
        stack = self.stack[:]
        rects = []
        rects_append = rects.append
        for id, sprite in stack:
            # first we erase the sprite by blitting the old backgr
            rects_append(scr_blit(bck, sprite.rect, sprite.rect))
            if sprite.update( * args):# callback function returns true/false
                break# then we considered to stop 
            # now we draw them 
            rects_append(scr_blit(sprite.image, sprite.rect))
        pygame.display.update(rects)
        
            
    def refresh(self, event):
        """ refresh(*args)
             Calls the update and draw methods on all the sprites belonging to this group.
        """
        #self.update(*args)
        self.draw(event)
        #print "Stack",self.stack

    def update(self, * args):
        """update(...)
           call update for all member sprites

           calls the update method for all sprites in the group.
           passes all arguments are to the Sprite update function."""
        if args:
            a = apply
            stack = self.stack
            for i, s in stack:
                a(s.update, args)
        else:
            for i, s in stack:
                s.update()

    def get_stack_ids(self):
        """ get_stack_ids()
            Get a list with the current IDs from the stack.
            
            Use this to get a overview of the contents of the stack but use pop, push etc
            to handle the stack.
            """
        ids = []
        ids_append = ids.append
        for i in self.stack:
            ids_append(i[0])
        return ids
    
    def up(self, id):
        """ up(ID)
            Raise the sprite to the top of the stack.
            """
        index = self._find_in_stack(id)
        if index != -1:
            self.stack.append(self.stack.pop(index))
                
    def down(self):
        """ down() 
            Get the sprite on top of the stack and put it on the bottom of the stack.
            """
        self.stack.insert(0, self.stack.pop())

class MySprite(SPSprite):
    """Container to turn a surface into a SPSprite object"""
    def __init__(self, value, name=None):
        """Turn an image into a schoolsplay sprite.
        @value can be a SDL surface or a string.
        Only use this if you need a simple sprite.
        For anything else let your sprite derive from SPSprite. 
        See the SPSprite api documentation for info about this class.
        value must be an pygame surface or a path to a supported image file.
        name is optional and can be used to identify this sprite.
        See also the SPSprite class."""
        self.logger = logging.getLogger("schoolsplay.SPSpriteUtils.MySprite")
        if type(value) is pygame.Surface:
            self.image = value
        elif type(value) in (types.StringType, types.UnicodeType):
            try:
                self.image = load_image(value)
            except Exception, info:
                self.logger.error("failled to load image: %s" % value)
                raise MyError, info
        self.rect = self.image.get_rect()
        SPSprite.__init__(self, self.image, name=name)
        
class SPButton(SPSprite):
    """ Turn an image into a button like object which reacts to mouseclicks.
    It will connect the 'MOUSEBUTTONDOWN' event to the callback function named
    'callback'.
    This callback function returns the data given in the class constructor when
    called from the eventloop.
    DEPRECATED; Use Button
    """
    def __init__(self, img, pos, data):
        """@img is an SDL image object.
        @pos is a tuple with a x,y grid numbers.
        @data is returnt by the callback function when the MOUSEBUTTONDOWN occurs
        """
        self.image = img
        self.rect  = self.image.get_rect()
        SPSprite.__init__(self, self.image)
        self.rect.move_ip(pos)
        self.data = data
        self.connect_callback(self.callback, event_type=MOUSEBUTTONDOWN)
    
    def callback(self,  * args):
        return self.data   



def set_big_mouse_cursor(file=None, mask=None):
    """This will replace the default cursor with a bigger one"""
    thickarrow_strings = (#sized 24x24
        "XX                      ",
        "XXX                     ",
        "XXXX                    ",
        "XX.XX                   ",
        "XX..XX                  ",
        "XX...XX                 ",
        "XX....XX                ",
        "XX.....XX               ",
        "XX......XX              ",
        "XX.......XX             ",
        "XX........XX            ",
        "XX........XXX           ",
        "XX......XXXXX           ",
        "XX.XXX..XX              ",
        "XXXX XX..XX             ",
        "XX   XX..XX             ",
        "     XX..XX             ",
        "      XX..XX            ",
        "      XX..XX            ",
        "       XXXX             ",
        "       XX               ",
        "                        ",
        "                        ",
        "                        ")
    if file:
        cursordata = pygame.cursors.load_xbm(file, mask)
    else:
        data, mask = pygame.cursors.compile(thickarrow_strings, black='X', white='.', xor='o')
        hot = (0, 0)
        size = (24, 24)
        cursordata = (size, hot, data, mask)
    pygame.mouse.set_cursor( * cursordata)
    
def set_no_mouse_cursor():
    """This will replace the default cursor with one that's empty.
    This is used to hide the cursor"""
    thickarrow_strings = ( #sized 8x8
        "        ",
        "        ",
        "        ",
        "        ",
        "        ",
        "        ",
        "        ",
        "        ")

    cursor = pygame.cursors.compile(thickarrow_strings, black=".", white="X")
    pygame.mouse.set_cursor((8,8), (5,0), *cursor)
    
    
