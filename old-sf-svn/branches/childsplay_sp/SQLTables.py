# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SQLTables.py
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

# Put all the tables that are used in the dbase here

# ACTIVITY DEVELOPERS, BE SURE YOU UNDERSTAND WHAT YOU MUST ADD HERE TO GET YOUR
# ACTIVITY UP AND RUNNING.
# PLEASE CONTACT THE AUTHOR OF THIS FILE OR THE SCHOOLSPLAY MAILINGLIST FOR
# ADDITIONAL INFO OR HELP.

# PLEASE DON'T CHANGE ANYTHING IN THIS MODULE WITHOUT DISCUSSING IT WITH THE
# SCHOOLSPLAY MAILINGLIST.
# THE CreateTemplate SCRIPT DEPENDS ON CERTAIN SYNTAX TO BE PRESENT IN HERE.

from sqlalchemy import *

class SqlTables:
    """Class that holds the dbase table definitions"""
    def _create_tables(self, metadata, engine):
        """Called by the datamanager to setup the dbase tables"""
        tables = {}
        for table in self.tableslist:
            tables[table.name] = table
            self._appendcolumns(table)
        metadata.create_all(engine)
        return tables
    def _appendcolumns(self, t):
        if t.name in ['users', 'options', 'activity_options']:
            return 
        t.append_column(Column('table_id', Integer, primary_key=True))
        t.append_column(Column('user_id', Integer, ForeignKey('users.user_id')))
        t.append_column(Column('timespend', String(4)))
        t.append_column(Column('start_time', String(17)))
        t.append_column(Column('end_time', String(17)))
        t.append_column(Column('level', Integer))
        t.append_column(Column('score', Integer))
        
    def __init__(self, metadata):
        # table to hold user data, mandatory for any sp dbase.
        # All other tables are regarded as activity tables.
        # Used by the core, don't change it
        self.users = Table('users', metadata, \
            Column('user_id', Integer, primary_key=True), \
            Column('login_name', String(20)), \
            Column('first_name', String(20)), \
            Column('last_name', String(40)), \
            Column('birthdata', String(11)), \
            Column('class', String(6)), \
            Column('profile', String(200)), \
            Column('passwrd', String(10)), \
            Column('activities', String(250))\
            )
        # table to hold the configuration stuff, not really suitable stuff to put
        # inside a dbase but I don't want to setup a different framework for 
        # configuration files. This way we only use a dbase for our data storage.
        # Used by the core, don't change it
        self.options = Table('options', metadata, \
            Column('table_id', Integer, primary_key=True), \
            Column('admin_login_name', String(20)), \
            Column('admin_first_name', String(20)), \
            Column('admin_last_name', String(40)), \
            Column('passwrd', String(40)), \
            Column('fullscreen', Integer)\
            )
        # The graph image needs two values:
        # average (greek: mu-value) and the standard deviation (greek: sigma-value)
        # mu is a integer between 1-10 and sigma is an integer between 0-100 which
        # stand for the percentage deviation. (Probably always 50%)
        self.activity_options = Table('activity_options', metadata, \
            Column('table_id', Integer, primary_key=True), \
            Column('activity', String(20)), \
            Column('mu', Integer), \
            Column('sigma', Integer)\
            )
        
        ################ Activity tables ########################## 
        # Every activity *must* have a sql table set.
        # The name of the table must be the same as the activity modules name
        # The following cols are mandatory for any activity table.
        # 'table_id' to hold the id
        # 'user_id' to hold the user id (set by DM)
        # 'timespend' to hold the time it took to complete the level. (set by core)
        # 'start_time' to hold the time the level is started (set by core)
        # 'end_time' to hold the time the level is finished (set by core)
        # 'level' to hold the level number (set by core)
        # 'score' to hold the score value.
        # The mandatory columns are provided by the BaseTable class, 
        # the reporter tool expect them to be present so please extend the BaseTable
        # instead of creating your own.
        # The rest of the cols are set/used by the activity.
        
        self.memory = Table('memory', metadata, \
            Column('cards', Integer), \
            Column('knowncards', Integer))

        self.memorylower = Table('memorylower', metadata, \
            Column('cards', Integer), \
            Column('knowncards', Integer))
                    
        self.memoryupper = Table('memoryupper', metadata, \
            Column('cards', Integer), \
            Column('knowncards', Integer))
                    
        self.memorynumbers = Table('memorynumbers', metadata, \
            Column('cards', Integer), \
            Column('knowncards', Integer))
                    
        self.fishtank = Table('fishtank', metadata, \
            Column('fish', Integer), \
            Column('clearfish', Integer))
                    
        #self.CR_math_add1 = BaseTable('CR_math_add1',metadata)
        
        self.CP_find_char_sound = Table('CP_find_char_sound', metadata, \
            Column('chars', Integer), \
            Column('kind', String(20)), \
            Column('missedchars', Integer))

        # LEAVE THESE COMMENTS IN HERE, THE CreateTemplate SCRIPT NEEDS THEM.
        # @splitpoint@
        self.completion = Table('completion',metadata)
        self.flashcards = Table('flashcards', metadata)
        self.pong = Table('pong', metadata)
        
        self.packid = Table('packid', metadata, \
            Column('word', String(20)), \
            Column('wrong', Integer), \
                )
        self.billiard = Table('billiard', metadata, \
            Column('tries', Integer), \
            Column('maxpoints', Integer), \
            Column('points', Integer), \
            Column('balls', Integer),
            )
        self.findsound = Table('findsound', metadata, \
            Column('wrong', Integer), \
                )
        
        self.puzzle = Table('puzzle', metadata, \
            Column('pieces', Integer), \
            Column('wrongpieces', Integer), \
                )
        
        self.soundmemory = Table('soundmemory', metadata, \
            Column('sounds', Integer), \
            Column('knownsounds', Integer), \
                )
        self.fallingletters = Table('fallingletters', metadata, \
            Column('missedletters', Integer), \
            Column('wrongletters', Integer), \
            Column('totaltime', Integer), \
                )
        
        ############ Setup an activity list #################################
        # Now we put all the tables we have into this list.
        # The Datamanager uses this list to setup the dbase tables.
        self.tableslist = [self.users, self.options, self.activity_options, \
            self.memory, self.memorylower, self.memoryupper, \
            self.memorynumbers, self.fishtank, \
            self.CP_find_char_sound, \
        self.fallingletters, \
            self.soundmemory, \
            self.puzzle, \
            self.findsound, \
            self.billiard, \
            self.pong, \
            self.packid, \
            self.flashcards,\
                        self.completion]



if __name__ == '__main__':
    # test code
    from SPConstants import DBASEPATH
    import sqlalchemy as sqla
    
    engine = sqla.create_engine('sqlite:///%s' % DBASEPATH)
    metadata = sqla.MetaData(engine)
    
    #metadata.engine.echo = True
    sqltb = SqlTables(metadata)
    tables = sqltb._create_tables(metadata)
    
    
