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

from sqlalchemy import *

class SqlTables:
    """Class that holds the dbase table definitions"""
    def _create_tables(self,metadata,engine):
        """Called by the datamanager to setup the dbase tables"""
        tables = {}
        for table in self.tableslist:
            tables[table.name] = table
            self._appendcolumns(table)
        metadata.create_all(engine)
        return tables
        
    def _appendcolumns(self,t):
        if t.name in ['users','options', 'activity_options']:
            return
        if t.name == 'user_activities_options':
            for act in self.tableslist:
                if act.name not in ['users','options', 'activity_options',\
                                    'user_activities_options']:
                    t.append_column(Column(act.name, BOOLEAN))  
        else:
            t.append_column(Column('table_id', Integer,primary_key=True))
            t.append_column(Column('user_id', Integer, ForeignKey('users.user_id')))
            t.append_column(Column('timespend', String(4)))
            t.append_column(Column('start_time',String(17)))
            t.append_column(Column('end_time',String(17)))
            t.append_column(Column('level', Integer))
            t.append_column(Column('score', Integer)) 
            t.append_column(Column('wrong', Integer)) 
    
    def __init__(self,metadata):
        # table to hold user data, mandatory for any sp dbase.
        # Used by the core, don't change it
        self.users = Table('users', metadata,\
                    Column('user_id', Integer, primary_key=True, unique=True),\
                    Column('login_name', String(20)),\
                    Column('first_name', String(20)), \
                    Column('last_name', String(40)),\
                    Column('birthdata', String(11)),\
                    Column('class', String(6)),\
                    Column('profile', String(200)),\
                    Column('passwrd', String(10)),\
                    Column('activities',String(250))\
                    )
        # This table is extended with extra columns in _append_uao_columns.
        # Eache activity gets a column with a Bool value signaling if
        # the user may (1) or may not (0) use that activity. 
        self.user_activities_options = Table('user_activities_options', metadata, \
                        Column('table_id', Integer, primary_key=True),\
                        Column('user_id', Integer, ForeignKey('users.user_id'), unique=True))
                        
        # table to hold the configuration stuff, not really suitable stuff to put
        # inside a dbase but I don't want to setup a different framework for 
        # configuration files. This way we only use a dbase for our data storage.
        # Used by the core, don't change it
        self.options = Table('options', metadata,\
                    Column('table_id', Integer, primary_key=True),\
                    Column('admin_login_name', String(20)),\
                    Column('admin_first_name', String(20)), \
                    Column('admin_last_name', String(40)),\
                    Column('passwrd', String(40)),\
                    Column('fullscreen', Integer)\
                    )
        # The graph image needs two values:
        # average (greek: mu-value) and the standard deviation (greek: sigma-value)
        # mu is a integer between 1-10 and sigma is an integer between 0-100 which
        # stand for the percentage deviation. (Probably always 50%)
        self.activity_options = Table('activity_options', metadata,\
                    Column('table_id', Integer, primary_key=True),\
                    Column('activity', String(20)),\
                    Column('sigma', Integer),\
                    Column('mu',Integer), \
                    Column('user_id', Integer, ForeignKey('users.user_id')),\
                    Column('level', Integer), \
                    Column('range', Integer), \
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
        
        # LEAVE THESE COMMENTS IN HERE, THE CreateTemplate SCRIPT NEEDS THEM.
        # @splitpoint@
        self.act_div_1 = Table('act_div_1',metadata)
        self.act_sub_1 = Table('act_sub_1',metadata)
        self.act_add_1 = Table('act_add_1',metadata)
        self.letterflash1 = Table('act_letterflash1',metadata,\
                Column('wrong_letters', String(78)),\
                    )
        self.multitables = Table('act_multitables',metadata,\
                Column('x1', String(4)),\
                Column('x2', String(4)),\
                Column('x3', String(4)),\
                Column('x4', String(4)),\
                Column('x5', String(4)),\
                Column('x6', String(4)),\
                Column('x7', String(4)),\
                Column('x8', String(4)),\
                Column('x9', String(4)),\
                Column('x10', String(4)),\
                Column('exam_1_10', Integer),\
                Column('x11', String(4)),\
                Column('x12', String(4)),\
                Column('x13', String(4)),\
                Column('x14', String(4)),\
                Column('x15', String(4)),\
                Column('x16', String(4)),\
                Column('x17', String(4)),\
                Column('x18', String(4)),\
                Column('x19', String(4)),\
                Column('x20', String(4)),\
                Column('exam_10_20', Integer),\
                Column('examexercises_1_10', Integer),\
                Column('examtime_1_10', String(4)),\
                Column('examexercises_10_20', Integer),\
                Column('examtime_10_20', String(4)))
                
        self.stack1 = Table('act_stack1',metadata,\
                                                )
        self.stack2 = Table('act_stack2',metadata,\
                                                )
        self.row1 = Table('act_row1',metadata,\
                                                )
        self.row2 = Table('act_row2',metadata,\
                                                )
        ############ Setup an activity list #################################
        # Now we put all the tables we have into this list.
        # The Datamanager uses this list to setup the dbase tables.
        self.tableslist = [self.users,self.options,self.activity_options,\
                           self.user_activities_options, \
                            self.stack1,\
                            self.stack2,\
                            self.row1,\
                            self.row2,\
                        self.multitables,\
                        self.letterflash1,\
                        self.act_add_1,\
                        self.act_sub_1,\
                        self.act_div_1]





        
        
    
