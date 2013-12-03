# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
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

# PLEASE DON'T CHANGE ANYTHING IN THIS MODULE WITHOUT DISCUSSING IT ON THE
# SCHOOLSPLAY MAILINGLIST.
# THE CreateTemplate SCRIPT and Datamanager DEPENDS ON CERTAIN SYNTAX TO BE 
# PRESENT IN HERE.

# Make sure to add a ORM class to SPORMs.py if you add new sql tables.
import datetime
from sqlalchemy import *
import sqlalchemy.orm as sqlorm
    
import SPORMs as ORMS

def create_contentdb_orms(metadata):
    tables = {}
    for name in [k for k in ORMS.__dict__.keys() if k.startswith('game_')]:
        t = Table(name, metadata, autoload=True)
        orm = getattr(ORMS, name)
        orm._name = name
        sqlorm.mapper(orm, t)
        tables[name] = orm
    return tables

class SqlTables:
    """Class that holds the dbase table definitions and creates the tables for
    the content dbase and user dbase."""
    def _create_userdb_tables(self, metadata):
        """Called by the datamanager to setup the dbase tables.
        We also map the ORM classes to the dbase tables.
        Returns a dict with the keys set to the dbase table names and
        the values set to the ORM classes."""
        tables = {}
        sqlorm.clear_mappers()
        for table in self.tableslist:
            self._appendcolumns(table)
            if hasattr(ORMS, table.name):
                orm = getattr(ORMS, table.name)
                orm._name = table.name
                sqlorm.mapper(orm, table)
                tables[table.name] = orm
        
        metadata.create_all()
        return tables
    
    def _appendcolumns(self, t):
        # These are the skipped Tables for default columns
        if t.name in ['users', 'options', 'activity_options', 'menu', \
                    'served_content', 'group_names', 'change_pass', 'zorgenquete', \
                    'spconf',  'users_faces', 'dt_sequence', 'stats', 'stats_session']:
            return 
        # Columns added to all act tables
        t.append_column(Column('table_id', Integer, primary_key=True))
        t.append_column(Column('user_id', Integer, nullable=False))
        t.append_column(Column('timespend', Unicode(6)))
        t.append_column(Column('start_time', Unicode(17)))
        t.append_column(Column('end_time', Unicode(17)))
        t.append_column(Column('level', Integer))
        t.append_column(Column('score', Float))
                
    def __init__(self, metadata):
        # table to hold user data, mandatory for any sp dbase.
        # All other tables are regarded as activity tables.
        # Used by the core, don't change it
        self.users = Table('users', metadata,\
            Column('user_id', Integer, primary_key=True), \
            Column('login_name', Unicode(20), unique=True, nullable=False), \
            Column('title', Unicode(20)), \
            Column('first_name', Unicode(20)),\
            Column('last_name', Unicode(40)), \
            Column('birthdate', DateTime), \
            Column('group', Integer), \
            Column('profile', Unicode(200)), \
            Column('passwrd', Unicode(10)), \
            Column('activities', Unicode(250)), \
            Column('audio', Integer, default=50),\
            Column('dt_target', Unicode(250), default='default'),\
            Column('levelup_dlg', Unicode(4), default='true')\
            )
    
        # The graph image needs two values:
        # average (greek: mu-value) and the standard deviation (greek: sigma-value)
        # mu is a integer between 1-10 and sigma is an integer between 0-100 which
        # stand for the percentage deviation. (Probably always 50%)
        self.activity_options = Table('activity_options', metadata, \
            Column('table_id', Integer, primary_key=True), \
            Column('activity', Unicode(20)), \
            Column('mu', Float, default=6.5), \
            Column('sigma', Float, default=1.63)\
            )
        
        # served content table used by the acts to store content they serve so that
        # we can make sure we don't serve the same content twice.
        # This is meanly intended for the quizzes as the rest of the acts don't
        # have much content, yet ?
        self.served_content = Table('served_content', metadata, \
                Column('table_id', Integer, primary_key=True), \
                Column('user_id', Integer,nullable=False), \
                Column('CID', Integer, nullable=False),\
                Column('game_theme_id', Integer, nullable=False),\
                Column('module', Unicode(25)), \
                Column('start_time', DATETIME(timezone=True)), \
                Column('count_served', Integer, default=0), \
                Column('wrong', Integer, default=0)
                )

        # Table to convert group name to an id
        self.group_names = Table('group_names', metadata, \
                                 Column('group_id', Integer, primary_key=True), \
                                 Column('group_name', Unicode(50), unique=True, nullable=False))
        
        self.spconf = Table('spconf', metadata, \
                            Column('table_id', Integer, primary_key=True), \
                            Column('activity_name', Unicode(50)), \
                            Column('key', Unicode(20)), \
                            Column('value', Unicode(200)), \
                            Column('theme', Unicode(20), default='default'), \
                            Column('comment', Unicode(200)))        

        self.faces = Table('users_faces',  metadata, \
                           Column('face_id',  Integer, primary_key=True),  \
                           Column('user_id',  Integer),  \
                           Column('shape_diff', Float), \
                           Column('temp_diff', Float), \
                           Column('pic_name',  Unicode(10)),  \
                           Column('datetime', DATETIME))

        self.stats = Table('stats', metadata,\
                           Column('ID', Integer, primary_key=True),\
                           Column('datetime', DATETIME),\
                           Column('activity_name', Unicode(50)),\
                           Column('message', Unicode(255)),\
                           Column('game_start_called', Boolean, default=False),\
                           Column('game_nextlevel_called', Boolean, default=False),\
                           Column('game_end_called', Boolean, default=False),\
                           Column('is_cop', Boolean, default=False),\
                           Column('user_id', Integer),\
                           Column('final_score', Integer),\
                           Column('session', Integer))
        self.stats_session = Table('stats_session', metadata,\
                            Column('ID', Integer, primary_key=True),\
                            Column('datetime', DATETIME))


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
        self.BlockBreaker = Table('BlockBreaker',metadata)
        self.TicTacToe = Table('TicTacToe',metadata)
        
        self.fourrow = Table('fourrow',metadata,\
                Column('stonesplayed', Integer),\
                    )
        self.numbers_sp = Table('numbers_sp',metadata)
        
        
        self.test_act = Table('test_act',metadata)
        
        self.fishtank = Table('fishtank',metadata,\
                Column('fish', Integer),\
                Column('clearfish', Integer),\
                    )
        self.ichanger = Table('ichanger',metadata,\
                Column('wrongs', Integer),\
                Column('extra', Integer),\
                    )
        self.puzzle = Table('puzzle',metadata,\
                Column('total_pieces', Integer),\
                Column('wrongs', Integer),\
                    )
        
        self.simon_sp = Table('simon_sp',metadata,\
                Column('sounds', Integer))
        
        self.soundmemory = Table('soundmemory', metadata, \
            Column('sounds', Integer), \
            Column('knownsounds', Integer), \
                )
        
        self.memory_sp = Table('memory_sp',metadata,\
                Column('cards', Integer),\
                Column('knowncards', Integer),\
                    )
        self.quiz_royal = Table('quiz_royal',metadata,\
                Column('total_questions', Integer),\
                Column('total_wrongs', Integer),\
                    )
        self.quiz_history = Table('quiz_history',metadata,\
                Column('total_questions', Integer),\
                Column('total_wrongs', Integer),\
                    )
        self.quiz_picture = Table('quiz_picture',metadata,\
                Column('total_questions', Integer),\
                Column('total_wrongs', Integer),\
                    )
        self.quiz_math = Table('quiz_math',metadata,\
                Column('total_questions', Integer),\
                Column('total_wrongs', Integer),\
                    )
        self.quiz_text = Table('quiz_text',metadata,\
                Column('total_questions', Integer),\
                Column('total_wrongs', Integer),\
                    )
        self.quiz = Table('quiz',metadata,\
                Column('total_questions', Integer),\
                Column('total_wrongs', Integer),\
                    )
        self.quiz_general = Table('quiz_general',metadata,\
                Column('total_questions', Integer),\
                Column('total_wrongs', Integer),\
                    )
        self.quiz_melody = Table('quiz_melody',metadata,\
                Column('total_questions', Integer),\
                Column('total_wrongs', Integer),\
                    )
        self.quiz_sayings = Table('quiz_sayings',metadata,\
                Column('total_questions', Integer),\
                Column('total_wrongs', Integer),\
                    )
        self.findit_sp = Table('findit_sp',metadata,\
                Column('total_diffs', Integer),\
                Column('wrongs', Integer),\
                    )
                    
        self.electro_sp = Table('electro_sp', metadata, \
            Column('knowncards', Integer), \
            Column('cards', Integer))
            
        self.video = Table('video', metadata, \
            Column('movie', Unicode(20)), \
            Column('answer', Integer))
        
        self.dt_sequence = Table('dt_sequence',metadata,\
                 Column('fortune', Integer),\
                 Column('act_name', Unicode(255)),\
                 Column('group', Unicode(255)),\
                 Column('level', Integer),\
                 Column('cycles', Integer),\
                 Column('target', Unicode(255)),\
                 Column('table_id', Integer, primary_key=True),\
                 Column('order', Integer))
        
        #TODO: This table is not finished, as soon as the specs are known we must update this
        self.dltr = Table('dltr', metadata, \
            Column('activity', Unicode(20)), \
            Column('done', Integer), \
            Column('cycles', Integer), \
            Column('epoch', Numeric))
                        
        ############ Setup an activity list #################################
        # Now we put all the tables we have into this list.
        # The Datamanager uses this list to setup the dbase tables.
        self.tableslist = [self.users, self.activity_options,self.served_content, \
                           self.spconf, self.stats,self.stats_session,\
                           self.group_names, self.findit_sp, self.electro_sp,\
                        self.quiz_text, self.quiz_melody, self.quiz_math,\
                        self.quiz_picture, self.quiz_history, self.quiz_royal,\
                        self.quiz, self.quiz_general, self.quiz_sayings, \
                        self.memory_sp, self.simon_sp, self.puzzle,\
                        self.soundmemory, self.ichanger, self.fishtank,\
                        self.dltr, \
                        self.test_act,\
                        self.numbers_sp,\
                        self.fourrow, self.dt_sequence
                        ,\
                        self.TicTacToe,\
                        self.BlockBreaker]








if __name__ == '__main__':
    # test code
    from SPConstants import DBASEPATH
    import sqlalchemy as sqla
    engine = sqla.create_engine('sqlite:///%s' % DBASEPATH)
    metadata = sqla.MetaData(engine)
    #metadata.engine.echo = True
    sqltb = SqlTables(metadata)
    tables = sqltb._create_tables(metadata)
    print tables
    
