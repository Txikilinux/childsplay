# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           SPDebugDialog.py
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

import pygame
from pygame.constants import *
import utils
from SPConstants import *
import logging 
import SPWidgets
import Mail
import os
import subprocess
import glob

GITBRANCH = 'master'

class Debugscreen:
    def __init__(self, actname, milestone, screen):
        self.logger = logging.getLogger("childsplay.SPDebugDialog.Debugscreen")
        self.orgscreen = pygame.display.get_surface()
        self.act_name = actname
        self.currentmilestone = milestone
        self.screen = screen
        self.screenshotpath = self._make_screenshot()
        
        id_pos = (60, 0)
        txt_0_pos = (60, 450)
        short_descr_pos = (60, 80)
        long_descr_pos = (60, 120)
        milestone_pos = (60, 360)
        component_pos = (60, 400)
        prio_pos = (550, 360)
        assigned_pos = (270, 360)
        name_pos = (270, 400)
        txt_1_pos = (60, 40)
        but_pos = (40, 500)
        fsize12 = 11
        fsize14 = 14
        
        self.labels = []
        self.buttons = []
        self.entries = []
        
        self.buthash = utils.OrderedDict()
        self.buthash = {"Cancel":self.on_quit_clicked, \
                        "Mail log":self.on_mail_logfile_clicked,\
                         "Mail scrshot":self.on_mail_scrshot_clicked, \
                         "Mail log+scrshot":self.on_mail_all_clicked,\
                         "Update from GIT":self.on_git_pull_clicked}

        # labels
        self.txt0_lbl = SPWidgets.Label("Your IP, Mac address and the date will be included in the mail.", \
                                txt_0_pos, fsize12, transparent=True)
        self.labels.append(self.txt0_lbl)
        self.txt1_lbl = SPWidgets.Label("Entries marked with a '*' are required fields without it your mail will not be send.", \
                                txt_1_pos, fsize14, bgcol=ORANGERED1)
        self.labels.append(self.txt1_lbl)
        short_descr_lbl = SPWidgets.Label("* Give a short description of the problem (Min 10 chars):", \
                                short_descr_pos, fsize12, transparent=True)
        self.labels.append(short_descr_lbl)
        long_descr_lbl = SPWidgets.Label("* Give a proper description of the issue and steps to reproduce it (Min 50 chars):", \
                               long_descr_pos, fsize12, transparent=True)
        self.labels.append(long_descr_lbl)
        milestone_lbl = SPWidgets.Label("Milestone:", milestone_pos, fsize12, transparent=True)
        self.labels.append(milestone_lbl)
        component_lbl = SPWidgets.Label("Component:", component_pos, fsize12, transparent=True)
        self.labels.append(component_lbl)
        prio_lbl = SPWidgets.Label("Priority:", prio_pos, fsize12, transparent=True)
        self.labels.append(prio_lbl)
        assigned_lbl =SPWidgets.Label("Assigned to:", assigned_pos, fsize12, transparent=True)
        self.labels.append(assigned_lbl)
        name_lbl = SPWidgets.Label("* Your name (Min 2 chars):", name_pos, fsize12, transparent=True)
        self.labels.append(name_lbl)
        # entries
        self.short_descr_te = SPWidgets.TextEntry((short_descr_pos[0] + short_descr_lbl.get_sprite_width()+12, short_descr_pos[1]), \
                                    length=300, fsize=fsize12, border=1)
        self.entries.append(self.short_descr_te)
        self.long_descr_te = SPWidgets.TextEntryBox((long_descr_pos[0]+12, long_descr_pos[1]+24),\
                                    height=10, length=600, fsize=fsize12)
        self.entries += self.long_descr_te.get_actives()
        self.labels.append(self.long_descr_te)
        self.milestone_te = SPWidgets.TextEntry((milestone_pos[0] + milestone_lbl.get_sprite_width()+12, milestone_pos[1]), \
                                    length=100, message=self.currentmilestone, fsize=fsize12, border=1)
        self.entries.append(self.milestone_te)
        self.component_te = SPWidgets.TextEntry((component_pos[0] + component_lbl.get_sprite_width()+12, component_pos[1]), \
                                    length=100, fsize=fsize12, border=1)
        self.entries.append(self.component_te)
        self.prio_te = SPWidgets.TextEntry((prio_pos[0] + prio_lbl.get_sprite_width()+12, prio_pos[1]), \
                                    length=100, message='3', fsize=fsize12, border=1)
        self.entries.append(self.prio_te)
        self.assigned_te = SPWidgets.TextEntry((assigned_pos[0] + assigned_lbl.get_sprite_width()+12, assigned_pos[1]), \
                                    length=150, message='Rene', fsize=fsize12, border=1)
        self.entries.append(self.assigned_te)
        self.name_te = SPWidgets.TextEntry((name_pos[0] + name_lbl.get_sprite_width()+12, name_pos[1]), \
                                    length=150, fsize=fsize12, border=1)
        self.entries.append(self.name_te)
        # buttons
        for label, func in self.buthash.items():
            b = SPWidgets.Button(label, but_pos, fsize=16, padding=8, name=label)
            b.connect_callback(func, MOUSEBUTTONDOWN, label)
            self.buttons.append(b)
            but_pos = (but_pos[0] + b.get_sprite_width()+12, but_pos[1])
        
        self._build_screen()

    def _build_screen(self):
        self.scrclip = self.screen.get_clip()
        self.screen.set_clip((0, 0, 800, 600))
        self.dim = utils.Dimmer()
        self.dim.dim(darken_factor=160, color_filter=CORNFLOWERBLUE)
    
        self.surf = pygame.Surface((750, 550))
        self.surf.fill(GREY92)
        self.screen.blit(self.surf, (25, 25))
        pygame.display.update()
        for s in self.labels + self.buttons + self.entries:
            s.display_sprite()
            
    def get_actives(self):
        return self.buttons + self.entries
    
    def on_quit_clicked(self, *args):
        self.logger.debug("quit called")
        for s in self.labels + self.buttons + self.entries:
            s.erase_sprite()
        self.screen.blit(self.orgscreen, (0, 0))
        self.dim.undim()
        self.screen.set_clip(self.scrclip)
        pygame.display.update()
        return -2
        
    def on_mail_logfile_clicked(self, *args):
        self.logger.debug("mail_logfile called")
        return self._mail_logfile(logpath=os.path.expanduser(os.path.join('~', '.schoolsplay.rc', 'schoolsplay.log')))

    def on_mail_scrshot_clicked(self, *args):
        self.logger.debug("mail_scrshot called")
        
        return self._mail_logfile(imgpath=self.screenshotpath)
        
    def on_mail_all_clicked(self, *args):
        self.logger.debug("mail_all")
        return self._mail_logfile(logpath=os.path.expanduser(os.path.join('~', '.schoolsplay.rc', 'schoolsplay.log')), \
                            imgpath=self.screenshotpath)
        
    def on_git_pull_clicked(self, *args):
        self.logger.debug("git_pull called")
        self.screen.blit(self.surf, (25, 25))
        # If we have network troubles, the smtp client timesout in 10 seconds.
        line = _("Git is updating your code, please wait.....")
        s = utils.char2surf(line, fsize=24, fcol=DARKGREEN,bold=True)
        self.screen.blit(s, (50, 300))
        pygame.display.update()
        process = subprocess.Popen(['git checkout %s & git pull' % GITBRANCH], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        txt = list(process.communicate())
        # we run a script which could contain stuff needed after a git update.
        self.logger.debug("Run scripts from post_pull directory, if any.")
        pp_txt = self._run_post_pull()
        self.logger.debug(pp_txt)
        txt += pp_txt
        result = -3
        txt.append("\nThe system will be restarted with the current commandline options.")
        txtlist = [s for s in txt if s]
        if len(txtlist) > 13:
            txtlist = txtlist[:-40]
        txt = '\n'.join(txtlist)
        dlg = SPWidgets.Dialog(txt, dialogwidth=500, buttons=["OK"], title='Information',fsize=8)
        dlg.run()
        self.on_quit_clicked()
        return result

    def _run_post_pull(self):
        try:
            import db_conf as dbrc
            rckind = 'db_conf'
        except ImportError:
            import db_dev as dbrc
            rckind = 'db_dev'
        rc_hash = dbrc.rc
        if rc_hash['default']['production']:
            kind = 'production'
        else:
            kind = 'develop'
        rc_hash['kind'] = kind
        
        cmd_list = []
        print rc_hash
        for k in rc_hash.keys():
            for c, v in rc_hash[k].items():
                cmd_list.append('--%s=%s' % (c,v))
        
        ppp = os.path.expanduser(os.path.join('~', '.schoolsplay.rc', 'post_pull'))
        if os.path.exists(ppp):
            f = open(ppp, 'r')
            scripts_done = [l[:-1] for l in f.readlines()]
            f.close()
        else:
            scripts_done = []
        scripts = glob.glob(os.path.join('.','post_pull', '*.sh'))
        scripts.sort()
        scripts_todo = []
        for s in scripts:
            if s not in scripts_done:
                scripts_todo.append(s)
        out = ['Running any new post_pull scripts:']
        scripts_todo.sort()
        f = open(ppp, 'a')
        for s in scripts_todo:
            self.logger.debug("Running post_pull script %s" % s)
            cmd = ' '.join(['sh %s' %s] + cmd_list)
            self.logger.debug("using cmdline options %s" % cmd)          
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            txt = []
            for l in process.communicate():
                if l:
                    l = l.replace('\n',' ')
                    txt.append(l)
            out += txt
            # TODO check exit code
            f.write("%s\n" % s)
        f.close()
        return out

    def _make_screenshot(self):
        try:
            scr = pygame.display.get_surface()
            path = os.path.join(HOMEDIR, self.act_name + '.jpeg')
            pygame.image.save(scr, path)
            self.logger.info("Screenshot %s taken" % path)
        except Exception, info:
            self.logger.error("Failed to make screenshot %s" % info)
            text = _("Failed to make screenshot %s") % info
            dlg = SPWidgets.Dialog(text, title="ERROR !")
            dlg.run()
            raise utils.MyError, "failed to make a screenshot"
        return path

    def _get_entrydata(self):
        data = {}
        data['short'] = self.short_descr_te.get_text()
        data['long'] = '\n'.join(self.long_descr_te.get_text())
        data['milestone'] = self.milestone_te.get_text()
        data['component'] = self.component_te.get_text()
        data['prio'] = self.prio_te.get_text()
        data['assigned'] = self.assigned_te.get_text()
        data['name'] = self.name_te.get_text()
        return data
            

    def _validate_data(self, data):
        entries = []
        if len(data['short']) < 10:
            entries.append('Short description')
        if len(data['long']) < 50:
            entries.append('Long description')
        if len(data['name']) < 2:
            entries.append('Name')
        return ','.join(entries)

    def _mail_logfile(self, logpath='', imgpath=''):
        self.logger.debug("_mail_logfile called")
        data = self._get_entrydata()
        result = self._validate_data(data)
        if result:
            dlg = SPWidgets.Dialog("The following entries are empty or have to little text:\n%s" % result,dialogwidth=500,  \
                    buttons=["OK"], title='Error !')
            dlg.run()
            return
        
        self.screen.blit(self.surf, (25, 25))
        # If we have network troubles, the smtp client timesout in 10 seconds.
        line = _("Your email will be send, please wait.....")
        s = utils.char2surf(line, fsize=24, fcol=DARKGREEN,bold=True)
        self.screen.blit(s, (50, 300))
        pygame.display.update()
        
        try:
            Mail.mail(subject=data['short'], description=data['long'], \
                      component=data['component'], prio=data['prio'], \
                      assigned=data['assigned'], milestone=data['milestone'], \
                      name=data['name'], \
                      logpath=logpath, imgpath=imgpath)
        except Mail.SendmailError,err:
            self.activity_info_dialog(_("Failed to send the email. Error: %s") % err)
        return self.on_quit_clicked()

if __name__ == '__main__':
    
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
    
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
        
    import pygame
    from pygame.constants import *
    pygame.init()
    
    from SPSpriteUtils import SPInit
    from SPWidgets import Init
    def cbf(sprite, event, data):
        print 'cb called with sprite %s, event %s and data %s' % (sprite, event, data)
        print 'sprite name: %s' % sprite.get_name()
        print 'data is %s' % data
    
    scr = pygame.display.set_mode((800, 600))
    scr.fill(LIGHTSKYBLUE1)
    pygame.display.flip()
    back = scr.convert()
    actives = SPInit(scr, back)
    
    Init('braintrainer')

    db = Debugscreen('none_act', 'BT2.1', scr)
    actives.add(db.get_actives())
    runloop = 1 
    while runloop:
        pygame.time.wait(100)
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            if event.type is KEYDOWN:
                if event.key == K_ESCAPE:
                    runloop = 0
                elif event.key == K_F1:
                    print "F1"
                
            result = actives.update(event)
            if result and result[0][1] == -2:
                runloop = False
                    
                    
                    
