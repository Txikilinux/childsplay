
# Schooldsplay goodies
# SPGoodies is a class that is passed on to the activity constructor
# It contains references to useful stuff, callback functions from the core
# and observers from the core.
import SPConstants

from BorgSingleton import Borg 

class SPGoodies(Borg):
    """This class is a singleton because we want that the core and
    activity always uses the same object"""
    def __init__(self,parent,lang,lock,topbar,cb_level_end,cb_level_restart,\
                cb_game_end,cb_stop_gui,cmd_options):
        Borg.__init__(self)
        # references to stuff, use the methods to get them
        self.parent = parent
        self.topbar = topbar
        self.level_end = cb_level_end
        self.restart_level = cb_level_restart
        self.game_end = cb_game_end
        self.localesetting = lang
        self.lock = lock
        self.stop_gui = cb_stop_gui
        self.cmd_options = cmd_options
        
    # these methods are the observers that an activity can use to signal the core
    def tellcore_level_end(self,store_db=None):
        """Use this to notify the core that the level is ended.
        The core will call next_level on the activity."""
        apply(self.level_end,(store_db,))
    def tellcore_restart_level(self,store_db):
        """Use this to notify the core that the current level needs to be
        restarted. This is the case when the user changes the numbersrange."""
        apply(self.restart_level,(store_db,)) 
    def tellcore_game_end(self,store_db=None):
        """Use this to notify the core that the game is ended.
        The core will start the menu and delete the activity."""
        apply(self.game_end,(store_db,))
    def tellcore_stop_gui(self):
        """Stops the GUI. This will quit the program.
        This should not be called by activities."""
        # Reminder stop_gui == schoolsplay.py>Observer>stop_gui
        apply(self.stop_gui)
    # these methods provide stuff needed by the activity.
    def get_parent(self):
        """get a references to the gtk frame"""
        return self.parent
    def are_we_sugar(self):
        """Returns True if we are running on the sugar desktop.
        Sugar is the XO desktop."""
        return self.cmd_options.bundle_id
    def get_localesetting(self):
        """Returns the current locale as set by schoolsplay.
        The value is a tuple with the language code and a bool signalling if
        were in a RTL environment (Hebrew and Arabic)"""
        return self.localesetting
    def get_topbar(self):
        """Returns the topbar object which is set by the core.
        The topbar exposes a number of methods activities can use to query the
        users choices.
        It also provides a method to register an observer to listen for 'check solution'
        button events.
        See the docs for the TopbarContainer class in the sp_cr module for additional info."""
        return self.topbar
    def get_thread_lock(self):
        """Returns a reference to the thread lock setup by the core.
        This lock MUST be used when dealing with the timer object from
        the SP Timer module.
        """
        return self.lock
    def get_theme(self):
        """Returns the theme name or None for the default theme.
        """
        return self._theme
    
    # paths related to the place where SP is currently installed
    def get_libdir_path(self):
        """path to the 'lib' directory were activities store there stuff"""
        return SPConstants.ACTIVITYDATADIR
    def get_absdir_path(self):
        """path to the 'alphabetsounds directory"""
        return SPConstants.ALPHABETDIR
    # Not sure we will implement these
    def get_virtual_keyboard(self):
        return None
