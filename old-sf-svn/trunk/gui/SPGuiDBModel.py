# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPGuiDBModel.py
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

""" This module provides an communication layer between a GUI and the SP dbase.
 GUI's should use this an not access the SP dbase stuff directly.
 This module assumes the GUI is used independant of SP.
 Use the 'get_datamanager' function to get a mapper object.
"""

# first parse commandline options, it's fake ofcourse as we are run from inside
# a python module but we need the options object
try:
    from childsplay_sp.SPOptionParser import OParser
except ImportError:
    # try to import from cwd in case we are started from sources
    from SPOptionParser import OParser
    
op = OParser()
# this will return a class object with the options as attributes  
CMD_Options = op.get_options()

class SPGoodiesWrapper:
    """Wrapper class, needed to run the datamanager"""
    _cmd_options = CMD_Options  

#create logger, logger was configured in SPLogging
import logging
module_logger = logging.getLogger("schoolsplay.SPGuiDBModel")

import atexit
import sqlalchemy as sqla
try:
    import schoolsplay.SPDataManager as SPDataManager
    import schoolsplay.SQLTables as SQLTables
    from schoolsplay.SPConstants import DBASEPATH
    import schoolsplay.utils as utils
except ImportError:
    # import from cwd
    import SPDataManager
    import SQLTables
    from SPConstants import DBASEPATH
    import utils

# get a datamanager
def get_datamanager():
    """use this to get a datamanager instance which could be used by a GUI.
    Typical usage would be:
        import SPGuiDBModel
        dm = SPGuiDBModel.get_datamanager()
        tablemapper = dm.get_mapper('<table name>')
        tabledata = tablemapper.get_table_data()
        # inserting is related to the table design
        newrow = [{id:<int>,'logon':<string>,'name':<string>}]
        tablemapper.update_row(data)
        """
    return DataManagerWrapper(SPGoodiesWrapper())

class DataManagerWrapper(SPDataManager.DataManager):
    """Wrapper class to set up a DataManager which can be used as a standalone.
    This is meant for GUI's that want to interface with the SP dbase.
    Don't use this class directly, use the 'get_datamanager' function."""
    def __init__(self,spgoodies):
        self.logger = logging.getLogger("schoolsplay.SPGuiDBModel.DataManagerWrapper")
        self.logger.debug("Starting")
        self.current_user_id = None # needed for the testsuite
        self.spg = spgoodies
        self.cmd_options = self.spg._cmd_options
        atexit.register(self._cleanup)
        self.logger.debug("Starting dbase, %s" % DBASEPATH)
        self.engine = sqla.create_engine('sqlite:///%s' % DBASEPATH)
        #self.metadata = sqla.BoundMetaData('sqlite:///%s' % DBASEPATH)
        self.metadata = sqla.MetaData(self.engine)
        #print "metadata",dir(self.metadata)
        # uncomment this to echo the SQL commands to stdout, usefull for debugging
        #self.metadata.engine.echo = True
        
        sqltb = SQLTables.SqlTables(self.metadata)
        self.tables = {}
        # returns lookup table to get table objects by name and creates tables
        self.tables = sqltb._create_tables(self.metadata,self.engine)
                
    def get_mapper(self,activity):
        """Overrides the get_mapper from SPDataManager.
        We don't have or use user id's"""
        try:
            mclass = SPDataManager.RowMapper(self.tables[activity])
        except (sqla.exceptions.SQLError,KeyError):
            self.logger.exception("Failed to get mapper: %s" % activity)
            raise utils.NoSuchTable("Failed to get mapper: %s" % activity)
        else:
            return mclass
            
        
        
        
        
