# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
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

import atexit,sys
sys.path.insert(0, 'gui')
#create logger, logger was configured in SPLogging
import logging
module_logger = logging.getLogger("schoolsplay.SPGuiDBModel")

# first parse commandline options, it's fake ofcourse as we are run from inside
# a python module but we need the options object

from SPOptionParser import OParser

op = OParser()
# this will return a class object with the options as attributes  
CMD_Options = op.get_options()

class SPGoodiesWrapper:
    """Wrapper class, needed to run the datamanager"""
    _cmd_options = CMD_Options  

try:
    import sqlalchemy as sqla
except ImportError:
    module_logger.exception("No sqlalchemy package found")
    raise Exception
else:
    if sqla.__version__ < '0.4':
        module_logger.error("Found sqlalchemy version %s" % sqla.__version__ )
        module_logger.error("Your version of sqlalchemy is to old, please upgrade to version >= 0.4")
    module_logger.debug("using sqlalchemy %s" % sqla.__version__)

import SPDataManager
from SPDataManagerCreateDbase import DbaseMaker
DEBUG = False
import SQLTables
from SPConstants import DBASEPATH
import utils
import sqlalchemy.exceptions as sqlae
import sqlalchemy.orm as sqlorm
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
        
        try:
            dbm = DbaseMaker(self.cmd_options.theme, debug_sql=DEBUG)            
        except (AttributeError, sqlae.SQLAlchemyError, utils.MyError), info:
            self.logger.exception("Failed to start the DBase, %s" % info)
            raise MyError, info
        self.content_engine, self.user_engine = dbm.get_engines()
        self.metadata_contentdb, self.metadata_usersdb = dbm.get_metadatas()
        self.all_orms = dbm.get_all_orms()
        self.orms_content_db, self.orms_userdb = dbm.get_orms()
        self.UserSession = sqlorm.sessionmaker(bind=self.user_engine)
        self.ContentSession = sqlorm.sessionmaker(bind=self.content_engine)
        
               
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
            
        
        
        
        
