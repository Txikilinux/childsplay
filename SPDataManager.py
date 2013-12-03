# -*- coding: utf-8 -*-

# Copyright (c) 2007-2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           SPDataManager.py
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

# TODO: what do we do when a error in dbase stuff occurs?

#create logger, logger was configured in SPLogging
import logging
module_logger = logging.getLogger("childsplay.SPDataManager")

import atexit, os, sys, datetime

# Don't do from 'sqlalchemy import *' as SQA has also 'logging' and 'types'
# modules. This is very bad coding practice but they claim to have good reasons
# for it. Those reasons suck of course but I don't have the time to discuss it
# with them. So I will just use practices *I* think are right and which I should
# have used to begin with and that's '*never* do from foo import *'.
# The braindead part of it all is that SQA use 'from sqlalchemy import *' in their
# docs and tutorials :-(
# None the less, SQA is a very good lib.
from SPConstants import ACTIVITYDATADIR
import SPHelpText
from utils import MyError, StopmeException
try:
    import sqlalchemy as sqla
    import sqlalchemy.orm as sqlorm
except ImportError:
    module_logger.exception("No sqlalchemy package found")
    raise MyError
try:
    import sqlalchemy.exceptions as sqlae
except ImportError:
    from sqlalchemy import exc as sqlae
# attempt to prevent sqlalchemy trhowing recursion limit error
sys.setrecursionlimit(2000) # 1000 is the default

from utils import set_locale

#import SPgdm

from SPDataManagerCreateDbase import DbaseMaker
DEBUG = False

DEMO_DT = [{'fortune': 0, 'target': 'demo', 'level': 2, 'group': 'Lange termijn', 'cycles': 1,'act_name': 'quiz_picture', 'order': 0}, \
           {'fortune': 0, 'target': 'demo', 'level': 2, 'group': 'Puzzels', 'cycles': 1,'act_name': 'electro_sp', 'order': 1}, \
           {'fortune': 0, 'target': 'demo', 'level': 2, 'group': 'Lange termijn', 'cycles': 1,'act_name': 'quiz_melody', 'order': 2},\
           ]
DEFAULT_DT = [{'fortune': 0, 'target': 'default', 'level': 2, 'group': 'Lange termijn', 'cycles': 1,'act_name': 'quiz_picture', 'order': 0},\
           {'fortune': 0, 'target': 'default', 'level': 2, 'group': 'Puzzels', 'cycles': 2,'act_name': 'electro_sp', 'order': 1}, \
           {'fortune': 0, 'target': 'default', 'level': 2, 'group': 'Lange termijn', 'cycles': 1,'act_name': 'quiz_math', 'order': 2},\
           {'fortune': 0, 'target': 'default', 'level': 2, 'group': 'Puzzels', 'cycles': 2,'act_name': 'numbers_sp', 'order': 3},\
           {'fortune': 0, 'target': 'default', 'level': 2, 'group': 'Lange termijn', 'cycles': 1,'act_name': 'quiz_sayings', 'order': 4},\
           {'fortune': 0, 'target': 'default', 'level': 2, 'group': 'Korte termijn', 'cycles': 2,'act_name': 'memory_sp', 'order': 5},\
           {'fortune': 0, 'target': 'default', 'level': 2, 'group': 'Lange termijn', 'cycles': 1,'act_name': 'quiz_picture', 'order': 6}, \
           {'fortune': 0, 'target': 'default', 'level': 2, 'group': 'Puzzels', 'cycles': 2,'act_name': 'findit_sp', 'order': 7}, \
           {'fortune': 0, 'target': 'default', 'level': 2, 'group': 'Lange termijn', 'cycles': 1,'act_name': 'quiz_melody', 'order': 8}
              ]
EASY_DT = [{'fortune': 0, 'target': 'Easy', 'level': 2, 'group': 'Lange termijn', 'cycles': 1, 'act_name': 'quiz_picture', 'order': 0},\
           {'fortune': 0, 'target': 'Easy', 'level': 2, 'group': 'Puzzels', 'cycles': 3, 'act_name': 'electro_sp', 'order': 1},\
           {'fortune': 0, 'target': 'Easy', 'level': 2, 'group': 'Lange termijn', 'cycles': 1, 'act_name': 'quiz_sayings', 'order': 2},\
           {'fortune': 0, 'target': 'Easy', 'level': 2, 'group': 'Puzzels', 'cycles': 3, 'act_name': 'puzzle', 'order': 3},\
           {'fortune': 0, 'target': 'Easy', 'level': 2, 'group': 'Lange termijn', 'cycles': 1, 'act_name': 'quiz_math', 'order': 4},\
           {'fortune': 0, 'target': 'Easy', 'level': 2, 'group': 'Lange termijn', 'cycles': 1, 'act_name': 'quiz_melody', 'order': 5},\
           ]

HARD_DT = [{'fortune': 0, 'target': 'Hard', 'level': 2, 'group': 'Lange termijn', 'cycles': 1, 'act_name': 'quiz_picture', 'order': 0},\
         {'fortune': 0, 'target': 'Hard', 'level': 3, 'group': 'Puzzels', 'cycles': 3, 'act_name': 'electro_sp', 'order': 1},\
         {'fortune': 0, 'target': 'Hard', 'level': 2, 'group': 'Lange termijn', 'cycles': 1, 'act_name': 'quiz_sayings', 'order': 2},\
         {'fortune': 0, 'target': 'Hard', 'level': 3, 'group': 'Korte termijn', 'cycles': 3,'act_name': 'memory_sp', 'order': 3}, \
         {'fortune': 0, 'target': 'Hard', 'level': 2, 'group': 'Lange termijn', 'cycles': 1,'act_name': 'quiz_history', 'order': 4}, \
         {'fortune': 0, 'target': 'Hard', 'level': 2, 'group': 'Korte termijn', 'cycles': 3, 'act_name': 'soundmemory', 'order': 5},\
         {'fortune': 0, 'target': 'Hard', 'level': 2, 'group': 'Lange termijn', 'cycles': 1, 'act_name': 'quiz_math', 'order': 6},\
         {'fortune': 0, 'target': 'Hard', 'level': 2, 'group': 'Puzzels', 'cycles': 3, 'act_name': 'numbers_sp', 'order': 7},\
         {'fortune': 0, 'target': 'Hard', 'level': 3, 'group': 'Lange termijn', 'cycles': 1, 'act_name': 'quiz_math', 'order': 8},\
         {'fortune': 0, 'target': 'Hard', 'level': 2, 'group': 'Puzzels', 'cycles': 3, 'act_name': 'fourrow', 'order': 9},\
         {'fortune': 0, 'target': 'Hard', 'level': 2, 'group': 'Lange termijn', 'cycles': 1, 'act_name': 'quiz_melody', 'order': 10}\
         ]

class DataManager:
    """Class that handles all users data related stuff except the collecting that
    should be done by the activity."""
    def __init__(self, spgoodies, dbm):
        self.logger = logging.getLogger("childsplay.SPDataManager.DataManager")
        self.logger.debug("Starting")
        self.SPG = spgoodies
        self.cmd_options = self.SPG._cmd_options
        self.current_user = self.cmd_options.user
        self.current_user_id = None
        self.COPxml = None# controlpanel stuff
        atexit.register(self._cleanup)

        self.content_engine, self.user_engine = dbm.get_engines()
        self.metadata_contentdb, self.metadata_usersdb = dbm.get_metadatas()
        self.all_orms = dbm.get_all_orms()
        self.orms_content_db, self.orms_userdb = dbm.get_orms()
        self.UserSession = sqlorm.sessionmaker(bind=self.user_engine)
        self.ContentSession = sqlorm.sessionmaker(bind=self.content_engine)
        # query which language we should use.
        orm, session = self.get_orm('spconf', 'user')
        row = session.query(orm).filter_by(activity_name = 'language_select')\
                                    .filter_by(key = 'locale').first()
        if not row:
            language = self.cmd_options.lang
            if not language:
                language = self.cmd_options.default_language
            row = orm(activity_name='language_select', key='locale', value=language, comment='locale used by the core')
            session.add(row)
            row = orm(activity_name='language_select', key='lang', value=language[:2], comment='language code used by the core')
            session.add(row)
            session.commit()
            session.close()
            language = set_locale(language)
        elif not self.cmd_options.lang:
            language = set_locale(row.value)
        else:
            language = self.cmd_options.lang
            if not language:
                language = self.cmd_options.default_language
            language = set_locale(language)    
        self.language = language
        self.SPG.localesetting = language
        self._check_tables_uptodate()
        # query to get all availabe cids, used to check served_content
        orm, session = self.get_orm('game_available_content', 'content')
        query = session.query(orm)
        self.all_ids = [result.CID for result in query.all()]
        session.close()
        
        if self.cmd_options.no_login:
            self.current_user = 'SPUser'
            self._start_gdm_greeter()
        elif self.cmd_options.user:
            self.current_user = self.cmd_options.user
            self._start_gdm_greeter()
        elif self.SPG.get_theme() == 'braintrainer':
            self.WeAreBTP = True
            self._start_btp_screen()
        else:
            self.WeAreBTP = False
            # we don't have a working login screen yet
            self.current_user='SPUser'
            self._start_gdm_greeter()
    
    def reset(self):
        self.UserSession.close_all()
        self.ContentSession.close_all()
        try:
            self.user_engine.dispose()
            self.content_engine.dispose()
        except:
            pass
    
    def _get_language(self):
        return self.language
    
    def _check_tables_uptodate(self):
        self.logger.debug("_check_tables_uptodate")
        reload(SPHelpText)
        modules = [x for x in os.listdir(ACTIVITYDATADIR) if '.py' in x and not '.pyc' in x]
        # check that all the activities are present in the activity_options table
        orm, session = self.get_orm('activity_options', 'user')
        if orm == None:
            self.logger.error("No activity_options ORM found, dbase corrupt")
            raise MyError, "No activity_options ORM found, dbase corrupt"
        for m in modules:
            m = m[:-3]
            query = session.query(orm)
            query = query.filter_by(activity = m)
            result = query.first()
            if not result:
                # Not found activity name, set activity name with default values
                session.add(orm(m))
        session.commit()
        session.close()
                                        
        orm, session = self.get_orm('group_names', 'user')
        
        # make user demo    
        orm, session = self.get_orm('users', 'user')
        result = session.query(orm).filter_by(login_name = 'Demo').first()
        if not result:
            session.query(orm).filter_by(user_id = 1).delete()
            neworm = orm()
            neworm.user_id = 1
            neworm.first_name = 'Demo'
            neworm.last_name = ''
            neworm.login_name = 'Demo'
            neworm.audio = 50
            neworm.usersgroup = 0
            neworm.dt_target = 'demo'
            session.add(neworm)
        session.commit()
        session.close()
        # check for mandatory DT sequences
        orm, session = self.get_orm('dt_sequence', 'user')
        query = session.query(orm).filter_by(target = 'demo').all()
        if len(query) != len(DEMO_DT):
            self.logger.info("demo dt target differs from hardcoded sequence, replacing it")
            session.query(orm).filter(orm.target == 'demo').delete()
            session.commit()
            for row in DEMO_DT:
                session.add(orm(**row))
        query = session.query(orm).filter_by(target = 'default').all()
        if not query:
            self.logger.info("default dt target missing, adding a hardcoded sequence.")
            session.query(orm).filter(orm.target == 'default').delete()
            session.commit()
            for row in DEFAULT_DT:
                session.add(orm(**row))
        session.commit()
        session.close()
        val = self._get_rcrow('SPDatamanager', 'set_extra_dt_sequences')
        if not val or val != 'yes':
            # we also set two DT sequences once, user can remove them
            orm, session = self.get_orm('dt_sequence', 'user')
            query = session.query(orm).filter_by(target = 'Easy').all()
            if not query:
                self.logger.info("First time Easy dt target missing, adding a hardcoded sequence.")
                session.query(orm).filter(orm.target == 'Easy').delete()
                session.commit()
                for row in EASY_DT:
                    session.add(orm(**row))
            query = session.query(orm).filter_by(target = 'Hard').all()
            if not query:
                self.logger.info("First time Hard dt target missing, adding a hardcoded sequence.")
                session.query(orm).filter(orm.target == 'Hard').delete()
                session.commit()
                for row in HARD_DT:
                    session.add(orm(**row))
            session.commit()
            session.close()
            self._set_rcrow('SPDatamanager', 'set_extra_dt_sequences', 'yes', 'flag to check if we already have set the extra dt sequences')
        
    def _cleanup(self):
        """atexit function"""
        # Nothing to see here, please move on.
        self.reset()
    
    def _start_btp_screen(self):
        """Starts a login screen for the braintrainer plus.
        Beaware that this only works on a BTP system as the login and
        control panel is a proprietary piece of code and it's not included
        in the free versions."""
        sys.path.insert(0, './controlpanel_lgpl')
        import Start_screen as Ss #@UnresolvedImport
        self.SPG.dm = self
        ss = Ss.Controller(self.SPG, fullscr=self.cmd_options.fullscreen)
        result = ss.get_result()
        if result[0] == 'user':
            self.current_user = result[1]
            self._start_gdm_greeter()
        elif result[0] == 'quit':
            raise StopmeException, 0
        elif result[0] == 'controlpanel':
            self.COPxml = result[1]
            
    def are_we_cop(self):
        return self.COPxml
        
    def _start_gdm_greeter(self):
        """Will start login screen and stores the login name in the db"""
        self.current_user = 'Demo'
        if not self.current_user:
            g = SPgdm.SPGreeter(self.cmd_options, \
                theme=self.cmd_options.theme, \
                vtkb=self.SPG.get_virtual_keyboard(), \
                fullscr=self.cmd_options.fullscreen)# returns when user hits login button
            username = g.get_loginname()
        else:
            self.logger.debug("Username %s passed as cmdline option, no login screen" % self.current_user)
            username = self.current_user
        self.logger.debug("Got login: %s" % username)
        if not username:
            # we always must run under a user name so we use default
            username = self.cmd_options.user
            self.logger.debug("No login, setting username to default: %s" % username)
        
        # Now that we have a name we first check if it already exists
        # get the users table
        orm, session = self.get_orm('users', 'user')
        query = session.query(orm)
        query = query.filter_by(login_name = username)
        result = query.first()
        if result:
            self.logger.debug("found existing username: %s" % result.login_name)
        else:
            # insert just user_name, NULL for others, the user_id will be generated
            session.add(orm(login_name=username, first_name=username, usersgroup='SPusers'))
            self.logger.debug("inserted %s" % username)
            session.commit()
            query = session.query(orm)
            query = query.filter_by(login_name = username)
            result = query.first()
            session.close()
            # we must also check if the SPusers group exists.
            orm, session = self.get_orm('group_names', 'user')
            rows = [row for row in session.query(orm).order_by(orm.group_name).all()]
            if not rows:
                # we set a first group
                neworm = orm()
                neworm.group_name = 'SP Group'
                session.add(neworm)
                session.commit()
            session.close()
        self.logger.debug("%s has user id %s" % (username, result.user_id))
        self.current_user_id = result.user_id
        self.current_user = username

    def get_username(self):
        """Returns the current user or None if in anonymousmode"""
        self.logger.debug("get_username returns:%s" % self.current_user)
        if not self.current_user:
            return ''
        return self.current_user
        
    def get_user_id(self):
        return self.current_user_id
        
    def get_user_id_by_loginname(self, username):
        """Returns the user_id.
        @username must be the users login name"""
        orm, session = self.get_orm('users', 'user')
        query = session.query(orm)
        query = query.filter_by(login_name = username)
        result = query.first()
        if not result:
            self.logger.warning("No user %s found, expect more trouble :-(" % username)
        else:
            return result.user_id
            
    def get_user_dbrow_by_loginname(self, username):
        """Returns the user_id.
        @username must be the users login name"""
        orm, session = self.get_orm('users', 'user')
        query = session.query(orm)
        query = query.filter_by(login_name = username)
        result = query.first()
        if not result:
            self.logger.warning("No user %s found, expect more trouble :-(" % username)
            return 
        else:
            return result
    
    def get_table_names(self):
        """Returns a list with the names (strings) of the SQL tables currently in use."""
        tl = self.metadata_usersdb.tables.keys()
        return tl
    
    def get_orm(self, tablename, dbase):
        try:
            t = self.all_orms[tablename]
        except KeyError:
            self.logger.warning("get_orm No such table: %s" % tablename)
            return None,None
        else:
            if dbase == 'user':
                self.user_engine.dispose()
                return (t, self.UserSession())
            elif dbase == 'content':
                self.content_engine.dispose()
                return (t, self.ContentSession())
            else:
                self.logger.warning("no such dbase: %s" % t)
                return None, None
            
    def get_served_content_orm(self):
        return self.get_orm('served_content', 'user')

    def get_table_data_userdb(self, table):
        orm, session = self.get_orm(table, 'user')
        query = session.query(orm)
        return query.all()
    
    def get_mu_sigma(self, name):
        orm, session = self.get_orm('activity_options', 'user')
        query = session.query(orm)
        query = query.filter_by(activity = name)
        result = query.first()
        if not result:
            self.logger.warning("Not found mu and sigma for %s, expect more trouble :-(" % name)
            return 
        return (result.mu, result.sigma)    

    def get_served_content_mapper(self):
        orm, session = self.get_orm('served_content', 'user')
        mclass = ServedMapper(orm, session, self.current_user_id, self.current_user)
        return mclass
        
    def get_mapper(self, activity, dbase='user'):
        self.logger.debug("get_mapper called with activity:%s" % activity)
        #self.metadata_usersdb.bind.echo = True
        if not activity:
            self.logger.debug("anonymous or no activity, returning bogus")
            return BogusMapper()
        try:
            orm, session = self.get_orm(activity, dbase)
            mclass = RowMapper(orm, session, self.current_user_id, self.current_user)
        except (KeyError, TypeError):
            self.logger.warning("Failed to get mapper or activity doesn't have a dbase table : %s, returning bogus mapper" % activity)
            return BogusMapper()
        else:
            return mclass

    # Used by multiple acts through spgoodies
    def _check_already_served(self, rows, game_theme, minimum=10, all_ids=None):
        """Returns the rows with the ones that are served removed.
        When not enough 'free' rows are left it resets all the count_served fields
        and return the complete rows list.
        all_ids is a list with with possible ids to check against served ids."""
        self.logger.debug("_check_already_served called: %s rows offered" % len(rows))
        if not all_ids:
            all_ids = self.all_ids
        orm, session = self.get_served_content_orm()
        query = session.query(orm)
        query = query.filter_by(user_id = self.current_user_id)
        query = query.filter(orm.game_theme_id.in_(game_theme))
        query = query.filter(orm.count_served > 0)
        allrows = []
        served_ids = []
        for row in query.all():
            allrows.append(row)
            served_ids.append(row.CID)
        self.logger.debug("already served rows: %s" % len(served_ids))
        notserved = set(all_ids).difference(served_ids)
        self.logger.debug("found %s not served cids" % len(notserved))
        if len(notserved) < minimum:
            # Not enough unserved rows
            # first we set all the count_served back to 0
            query = session.query(orm).filter_by(user_id = self.current_user_id)
            query = query.filter(orm.game_theme_id.in_(game_theme))
            query.update({orm.count_served: 0}, synchronize_session=False)
            session.commit()
            session.close()
            # we now return all rows as there are now considered not yet served.
            self.logger.debug("Resetting served count and returning %s original rows" % len(rows))
            return rows
        else:
            # We must filter the rows by removing nonfree ones
            session.close()
            rows = [row for row in rows if row.CID in notserved]
            self.logger.debug("returning %s rows" % len(rows))
            return rows

    def _set_rcrow(self, actname, key, value, comment):
        orm, session = self.get_orm('spconf', 'user')
        query = session.query(orm).filter_by(activity_name = actname).filter_by(key = key).all()
        for row in query:
            session.delete(row)
        row = orm(activity_name=actname, key=key, value=value, comment=comment)
        session.add(row)
        session.commit()
        session.close()

    def _get_rcrow(self, actname, key):
        val = None
        orm, session = self.get_orm('spconf', 'user')
        query = session.query(orm).filter_by(activity_name = actname).filter_by(key = key).first()
        if query:
            val = query.value
        session.commit()
        session.close()
        return val
     
    def _update_rcrow(self, actname, key, val):
        orm, session = self.get_orm('spconf', 'user')
        query = session.query(orm).filter_by(activity_name = actname).filter_by(key = key).first()
        if query:
            comm = query.comment
        session.commit()
        session.close()
        self._set_rcrow(actname, key, val, comm)
        
class RowMapper:
    """DB object used by the core and activity to store data in the dbase
    table and row beloging to the current activity.
    Don't use this class directly, use the DataManagers get_mapper method."""
    def __init__(self, orm, session, user_id=None, current_user=''):
        self.logger = logging.getLogger("childsplay.SPDataManager.RowMapper")
        self.currentuser = current_user
        self.user_id = user_id
        self.orm = orm
        self.session = session
        self.coldata = {}
            
    def insert(self, col, data):
        """collects all the data which should go into a row.
        You must call 'commit' to actually store it into the dbase."""
        self.logger.debug("insert in %s: %s" % (col, data))
        self.coldata[col] = data
            
    def update(self, rowdata):
        """insert a row in to the current table.
        @rowdata must be a dictionary with column keys and data values.
        You must call 'commit' to actually store it into the dbase."""
        self.coldata.update(rowdata)
    
    def commit(self):
        """Flush dbase data to disk.
        Returns None on success and True on faillure."""
        self.logger.debug("orm %s commit data to dbase" % self.orm._name)
        if hasattr(self.orm, 'user_id'):
            self.insert('user_id', self.user_id)
        self.logger.debug("raw row data:%s" % self.coldata)
        self.session.add(self.orm(**self.coldata))
        if not self.session:
            return
        self.session.commit()
        self.session.close()

    def _get_level_data(self, levelnum=1):
        """Used by maincore"""
        query = self.session.query(self.orm)
        query.filter_by(level = levelnum)
        query.filter_by(user_id = self.user_id)
        return query.all()
    
    def _get_start_time(self):
        """Used by the maincore"""
        if self.coldata.has_key('start_time'):
            return self.coldata['start_time']
        
    def _get_end_time(self):
        """Used by the maincore"""
        if self.coldata.has_key('end_time'):
            return self.coldata['end_time']
    
    def get_orm(self):
        return self.orm
    def get_session(self):
        return self.session
    def close(self):
        if not self.session:
            return
        self.session.close()

class ServedMapper:
    """DB object for the served_content table in the users db.
    Used by the core and activity to store data in the dbase
    table and row beloging to the current activity.
    Don't use this class directly, use the DataManagers get_mapper method."""
    def __init__(self, orm, session, user_id=None, current_user=''):
        self.logger = logging.getLogger("childsplay.SPDataManager.ServedMapper")
        self.currentuser = current_user
        self.user_id = user_id
        self.orm = orm
        self.session = session
        self.coldata = {}
          
    def insert(self, cid, gtheme):
        """collects all the data which should go into a row.
        You must call 'commit' to actually store it into the dbase."""
        self.logger.debug("insert cid:%s game_theme_id:%s" % (cid, gtheme))
        svc = self.orm(user_id=self.user_id, CID=cid,\
                       game_theme_id=gtheme, \
                       module='', start_time=datetime.datetime.now(), \
                        count_served=1)
        self.session.add(svc)
        
    def commit(self):
        if not self.session:
            return
        self.logger.debug("commiting session")
        self.session.commit()
        self.session.close()
        
    def close(self):
        if not self.session:
            return
        self.session.close()
    
class BogusMapper:
    """Bogus mapper class used when we are in anonymousmode"""
    def __init__(self):
        pass
    def __str__(self):
        return "BogusMapper"
    def __repr__(self):
        return "BogusMapper"
    def insert(self, col, data):
        pass
    def insert_row(self, rowdata):
        pass
    def update(self, rowdata):
        pass
    def commit(self):
        pass
    def close(self):
        pass
    def get_table_column_names(self):
        pass
    def get_table_data(self):
        pass  
    def delete_row(self, row_id):
        pass
    def get_table_selection(self, args):
        pass
    def _get_level_data(self, levelnum=1):
        pass
    def _get_start_time(self):
        return "2000-01-01_00:00:00"
    def _get_end_time(self):
        return "2000-01-01_00:00:00"
    def _get_level_data(self, level=1):
        return None

