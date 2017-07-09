# This module holds all the paths needed for schoolsplay.
import sys,os
try:
    import sugar.env
except ImportError:
    # were not on a xo
    XO=False
else:
    XO=True
    
def get_rootdir():
    if XO:
        return os.environ['SUGAR_BUNDLE_PATH']
    else:
        return os.getcwd()# use this on GNU/Linux and probably on win32
    
BASEPATH= get_rootdir()        
DOCDIR = os.path.join(BASEPATH, 'doc', 'schoolsplay')
LOCALEDIR = os.path.join(BASEPATH, 'locale', 'schoolsplay')
BASEDIR = os.path.join(BASEPATH)
SHARELIBDATADIR = os.path.join(BASEPATH,'lib')
HOME_DIR_NAME = '.schoolsplay.rc'

if XO:
    HOMEDIR = sugar.env.get_profile_path()
else:
    # Check if there's a schoolsplay dir in the home directory
    if sys.platform == 'win32':
        try:
          HOMEDIR = os.path.join(os.environ['HOMEDRIVE'],os.environ['HOMEPATH'],HOME_DIR_NAME)
        except:
            # for win 98 ??
            HOMEDIR = os.path.join(BASEDIR,HOME_DIR_NAME)
            if not os.path.exists(HOMEDIR):
                os.makedirs(HOMEDIR) 
    else:
        try:
            HOMEDIR = os.path.join(os.environ['HOME'],HOME_DIR_NAME)
        except KeyError,info:
            print info
            HOMEDIR = os.path.abspath(sys.path[0])

