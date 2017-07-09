# -*- coding: utf-8 -*-

# Copyright (c) 2007-2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
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
module_logger = logging.getLogger("schoolsplay.SPDataManager")

import atexit, os, csv, shutil

# Don't do from 'sqlalchemy import *' as SQA has also 'logging' and 'types'
# modules. This is very bad coding practice but they claim to have good reasons
# for it. Those reasons suck of course but I don't have the time to discuss it
# with them. So I will just use practices *I* think are right and which I should
# have used to begin with and that's '*never* do from foo import *'.
# The braindead part of it all is that SQA use 'from sqlalchemy import *' in their
# docs and tutorials :-(
# None the less, SQA is a very good lib.

try:
    import sqlalchemy as sqla
    import sqlalchemy.exceptions as sqlae
    import SQLTables
except ImportError:
    module_logger.exception("No sqlalchemy package found")
    raise Exception
else:
    if sqla.__version__ < '0.4':
        module_logger.error("Found sqlalchemy version %s" % sqla.__version__)
        module_logger.error("Your version of sqlalchemy is to old, please upgrade to version >= 0.4")
    module_logger.debug("using sqlalchemy %s" % sqla.__version__)

from SPConstants import DBASEPATH, ACTIVITYDATADIR

#import SPgdm
import SPHelpText

from utils import MyError

class DataManager:
    """Class that handles all data related stuff except the collecting that
    should be done by the activity."""
    def __init__(self, spgoodies):
        self.logger = logging.getLogger("schoolsplay.SPDataManager.DataManager")
        self.logger.debug("Starting")
        
        self.spg = spgoodies
        self.cmd_options = self.spg._cmd_options
        self.anonymous = self.cmd_options.no_login
        self.current_user = self.cmd_options.user
        self.current_user_id = None
        atexit.register(self._cleanup)
        
        # We could also use a mysql dbase, local or remote
        self.logger.debug("Starting dbase, %s" % DBASEPATH)
        try:
            self.engine = sqla.create_engine('sqlite:///%s' % DBASEPATH)
            self.metadata = sqla.MetaData(self.engine)
            # uncomment this to echo the SQL commands to stdout, usefull for debugging
            #self.engine.echo = True
            sqltb = SQLTables.SqlTables(self.metadata)
            # returns lookup table to get table objects by name and creates tables
            self.tables = sqltb._create_tables(self.metadata, self.engine)
            self._check_tables_uptodate()
        except (AttributeError, sqlae.SQLAlchemyError), info:
            self.logger.exception("Failed to start the DBase, %s" % info)
            raise MyError, info
        if self.anonymous:
            self.logger.debug("Running in anonymousmode, no dbase actions")
            # start gdm greeter
            # It will handle everything itself and will return after the user
            # hits the login button. Then the name is checked and added to the dbase
        else:
            self._start_gdm_greeter(self.cmd_options)# changes self.anonymous when users give no name
        
    def _check_tables_uptodate(self):
        modules = [x for x in os.listdir(ACTIVITYDATADIR) if '.py' in x and not '.pyc' in x]
        
        # check for mu sigma in activity_options table
        t = self.get_table('activity_options')
        if t == None:
            self.logger.error("No activity_options table found")
            raise MyError, "No activity_options table found"
        for m in modules:
            m = m[:-3]
            s = sqla.select([t], t.c.activity==m)
            result = s.execute()
            row = result.fetchone()
            if not row:
                # Not found activity name, set name with default values
                # make sure we don't set the users and options tables.
                t.insert().execute(activity=m, mu=6.5, sigma=1.63)        
    
    def _cleanup(self):
        """atexit function"""
        # Nothing to see here, please move on.
        try:
            pass
        except:
            pass
        
    def _start_gdm_greeter(self, cmd_options):
        """Will start login screen and stores the login name in the db"""
        if not self.current_user:
            g = SPgdm.SPGreeter(cmd_options, \
                theme=self.cmd_options.theme, \
                vtkb=self.spg.get_virtual_keyboard(), \
                fullscr=self.cmd_options.fullscreen)# returns when user hits login button
            username = g.get_loginname()
        else:
            self.logger.debug("Username passed as cmdline option, no login screen")
            username = self.current_user
        self.logger.debug("Got login: %s" % username)
        if not username:
            # we run in anonymous mode
            self.anonymous = True
            self.current_user = None
            self.logger.debug("No login, running in anonymous mode")
        else:
            # we have a name so we first check if it already exists
            # get the users table
            users = sqla.select([self.tables['users']])
            # specify a match for the "login_name" column
            result = users.select(users.c.login_name == username).execute()
            row = result.fetchone()
            if row:
                self.logger.debug("found %s" % row.login_name)
            else:
                # insert just user_name, NULL for others
                # will auto-populate primary key columns if they are configured
                # to do so
                self.tables['users'].insert(values={'login_name':username}).execute()
                self.logger.debug("inserted %s" % username)
                result = users.select(users.c.login_name == username).execute()
                row = result.fetchone()
                self.logger.debug("%s has user id %s" % (username, row.user_id))
            self.current_user_id = row.user_id
            self.current_user = username
            # make sure we run in non-anonymousmode
            self.anonymous = False
            
    def _replace_dbase(self):
        """Backs up the existing dbase and replace it with a current one.
        This is done when there's a problem in the dbase.
        Most of the time this is due to a new database used by a new schoolsplay
        version."""
        self.logger.info("backing up the existing database %s and replacing it with a new one" % DBASEPATH)
        # backup the existing dbase file
        dst = DBASEPATH + '_back'
        try:
            shutil.copyfile(DBASEPATH, dst)
            os.remove(DBASEPATH)
        except (IOError, OSError), info:
            self.logger.exception("Trouble backing up the dbase file")
            raise MyError, info
        else:
            self.logger.debug("(re)starting dbase, %s" % DBASEPATH)
            self.engine = sqla.create_engine('sqlite:///%s' % DBASEPATH)
            self.metadata = sqla.BoundMetaData(self.engine)
            sqltb = SQLTables.SqlTables(self.metadata)
            self.tables = sqltb._create_tables(self.metadata)
        self.spg.tellcore_info_dialog(_(SPHelpText.DataManager._replace_dbase))
        
    def export_dbase(self, path):
        """Dumps the entire dbase into a csv file"""
        writer = csv.writer(open(path, 'wb'), dialect=csv.excel)
        for t in self.metadata.table_iterator():
            writer.writerow(('%s' % t.name,))
            select = t.select()
            rows = select.execute()
            for row in rows.fetchall():
                writer.writerow(row.values())
                
    def get_username(self):
        """Returns the current user or None if in anonymousmode"""
        self.logger.debug("get_username returns:%s" % self.current_user)
        if not self.current_user:
            return ''
        return self.current_user
    
    def get_user_id_by_loginname(self, username):
        """Returns the user_id.
        @username must be the users login name"""
        try:
            users = sqla.select([self.tables['users']])
            result = users.select().execute(login_name=username)
            row = result.fetchone()
        except (sqla.exceptions.SQLError, sqla.exceptions.NoSuchColumnError), info:
            self.logger.error("Error trying to fetch activity options row %s" % name)
            self.logger.error("%s" % info)
            self._replace_dbase()
            self.get_user_id_by_loginname(username)
        return row.user_id
    
    def get_table_names(self):
        """Returns a list with the names (strings) of the SQL tables currently in use."""
        tl = self.metadata.tables.keys()
        return tl
    
    def get_table(self, tablename):
        try:
            t = self.tables[tablename]
        except KeyError:
            self.logger.error("No such table: %s" % tablename)
        else:
            return t
    
    def get_table_data(self, table):
        t = self.get_table(table)
        s = t.select().execute()
        rows = s.fetchall()
        return rows
    
    def get_mu_sigma(self, name):
        t = self.get_table('activity_options')
        row = None
        try:
            c = t.select(t.c.activity == name).execute()
            row = c.fetchone()
            if row:
                m, s = row['mu'], row['sigma']
        except (sqla.exceptions.SQLError, sqla.exceptions.NoSuchColumnError, TypeError), info:
            self.logger.error("Error trying to fetch activity options row %s" % name)
            self.logger.error("%s" % info)
            m, s = 5, 50# default values
            row = None
        if not row:
            # Not found activity name, set name with default values
            # make sure we don't set the users and options tables.
            if name in [u'users', u'options', u'activity_options']:
                return (None, None)
            t.insert().execute(activity=name, mu=5, sigma=50)
            m, s = 5, 50
        return (m, s)
    

    def get_mapper(self, activity):
        self.logger.debug("get_mapper called with activity:%s" % activity)
        if self.anonymous or not activity:
            self.logger.debug("anonymous or no activity, returning bogus")
            return BogusMapper()
        try:
            mclass = RowMapper(self.tables[activity], self.current_user_id)
        except (sqla.exceptions.SQLError, KeyError):
            self.logger.exception("Failed to get mapper: %s, returning bogus mapper" % activity)
            return BogusMapper()
        else:
            return mclass

class RowMapper:
    """DB object used by the core and activity to store data in the dbase
    table and row beloging to the current activity.
    Don't use this class directly, use the DataManagers get_mapper method."""
    def __init__(self, table, user_id=None):
        self.logger = logging.getLogger("schoolsplay.SPDataManager.RowMapper")
        # get the table
        self.user_id = user_id
        self.table = table
        self.rowdata = {}
    def set_user_id(self, uid):
        """set the user_id. 
        Used by the unittest in Test_DMmanager, and the GUI (not sure if we do:-)"""
        self.user_id = uid
    def insert(self, col, data):
        """collects all the data which should go into a row.
        You must call 'commit' to actually store it into the dbase."""
        self.logger.debug("insert in %s: %s" % (col, data))
        self.rowdata[col] = data
    
    def update(self, rowdata):
        """insert a row in to the current table.
        @rowdata must be a dictionary with column keys and data values.
        You must call 'commit' to actually store it into the dbase."""
        self.rowdata.update(rowdata)
    
    def insert_row(self, rowdata):
        """insert a new row into the current table.
        @rowdata must be a tuple with field values in the correct order.
        Use update to insert partial rows.
        You don't have to call commit as this method inserts the row directly
        into the database."""
        self.table.insert(values=rowdata).execute()
    
    def commit(self):
        """Flush dbase data to disk.
        Returns None on success and True on faillure."""
        self.logger.debug("commit data to dbase")
        if self.table.name != 'users':
            self.rowdata['user_id'] = self.user_id
        try:
            self.table.insert().execute(self.rowdata)
        except sqla.exceptions.SQLError:
            self.logger.exception("Failed to insert data into db")
            return True
            
    def get_table_column_names(self):
        """Returns the column names from the current table"""
        return self.table.columns.keys()
    
    def get_table_data(self):
        """returns all the table cols in a list of tuples with strings.
        The list contain the whole table, the tuples contain the rows and the
        strings are the collumn data."""
        self.logger.debug("getting data from %s" % self.table.name)
        try:
            rows = self.table.select().execute()
            datalist = [tuple(row.values()) for row in rows.fetchall()]
        except sqla.exceptions.SQLError:
            self.logger.exception("Failed to get table data")
        else:
            return datalist    
    
    def delete_row(self, row_id):
        """delete a row from the current table.
        You must call 'commit' to delete the row from the dbase."""
        try:
            self.table.delete(self.table.c.table_id == row_id).execute()
        except (sqla.exceptions.SQLError, AttributeError):
            self.logger.exception("Failed to delete table row")
            return True
    
    def _delete_user_row(self, row_id):
        """Internal method, don't use this directly"""
        try:
            self.table.delete(self.table.c.user_id == row_id).execute()
        except (sqla.exceptions.SQLError, AttributeError):
            self.logger.exception("Failed to delete table row")
            return True
    
    def replace_me_with(self, newrowslist):
        """Replace this table rows with new rows defined in @newrowslist.
        This will remove all the existing rows and then add the new rows.
        This replacement can't be undone so use with care.
        Returns True on faillure"""
        oldrows = self.get_table_data()
        if self.table.name == 'users':
            func = self._delete_user_row
        else:
            func = self.delete_row
        for row in oldrows:
            if func(row[0]):
                self.logger.critical("error while deleting old rows, stopping")
                break
        else:
            for row in newrowslist:
                self.insert_row(row)
            return 
        return "Error while deleting old rows, stopping"
        
    def get_all_by_user_id(self, uid):
        """Return all rows that match the user_id, @uid"""
        rows = self.table.select(sqla.and_(self.table.c.user_id == uid)).execute()
        datalist = [tuple(row.values()) for row in rows.fetchall()]
        return datalist

    def _get_level_data(self, levelnum=1):
        """Used by maincore"""
        result = self.table.select(sqla.and_(self.table.c.level == levelnum, \
            self.table.c.user_id == self.user_id)).execute()
        rows = result.fetchall()
        return rows
        
    def _get_start_time(self):
        """Used by the maincore"""
        try:
            st = self.rowdata['start_time']
        except:
            self.logger.error("No start time available")
            st = None
        return st
    def _get_end_time(self):
        """Used by the maincore"""
        try:
            et = self.rowdata['end_time']
        except:
            self.logger.error("No end time available")
        return et


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

