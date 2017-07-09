# AUTO-GENERATED MODULE, DON'T EDIT
# This module holds all the paths needed for schoolsplay.
#DOCDIR = 'C:\test\doc\schoolsplay'
#LOCALEDIR = 'C:\test\locale\schoolsplay'
#BASEDIR = 'C:\test\schoolsplay'
#SHARELIBDATADIR = 'C:\test\schoolsplay\lib'
import os,sys, imp, distutils.sysconfig

def get_rootdir():
    if (hasattr(sys, "frozen") or # new py2exe
        hasattr(sys, "importers") or # old py2exe
        imp.is_frozen("__main__")): # tools/freeze
        return os.path.abspath(sys.path[0])
    else:
        return os.path.dirname(sys.path[0])

def get_packagesdir():
    if (hasattr(sys, "frozen") or # new py2exe
        hasattr(sys, "importers") or # old py2exe
        imp.is_frozen("__main__")): # tools/freeze
        return os.path.abspath(sys.path[0])
    else:
        return distutils.sysconfig.get_python_lib()    

BASEPATH= get_rootdir()        
DOCDIR = os.path.join(BASEPATH, 'share', 'doc', 'childsplay_sp')
LOCALEDIR = os.path.join(BASEPATH, 'share','locale')
BASEDIR = os.path.join(BASEPATH, 'childsplay_sp')
SHARELIBDATADIR = os.path.join(BASEPATH, 'share', 'childsplay_sp')
ALPHABETDIR = os.path.join(BASEPATH,'share','sp_alphabetsounds')
PYTHONCPDIR = os.path.join(get_packagesdir(), 'childsplay_sp')