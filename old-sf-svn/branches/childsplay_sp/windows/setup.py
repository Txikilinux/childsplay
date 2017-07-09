# Copyright (c) 2007 Chris Van Bael <chris.van.bael@gmail.com>
#
#           setup.py
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.



# Bootstrap setuptools, will install if isn't installed yet
#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup
from childsplay_sp import SPVersion
import sys, os, shutil, string
import pygame
import glob

# Minimum requirements
PYTHON_MINIMUM = (2, 4)
PYGAME_MINIMUM = (1, 7, 1)


# Stuff that can change regurarly
PATCH_VERSION = ""
# nothing when you release a main version, eg '' gives 0.85.1
# '_x' when you release a patch version, eg 0.85.1_1 needs '_1'
DATA_DIRS = ['share']
SP_MODULES = []


def run_checks ():
    # Python version check.
    if sys.version_info < PYTHON_MINIMUM: # major, minor check
        raise Exception ("You should have at least Python >= %d.%d.x installed." % PYTHON_MINIMUM)

    # Pygame versioning checks.
    pygame_version = None
    try:
        import pygame
        if pygame.version.vernum < PYGAME_MINIMUM:
            raise Exception ("You should have at least Pygame >= %d.%d.%d installed" % PYGAME_MINIMUM)
        pygame_version = pygame.version.ver
    except ImportError:
        pass


def get_data_files():

    # 1st get PyGame font and icon files
    pygamedir = os.path.split(pygame.base.__file__)[0]
    pygamefiles = [os.path.join(pygamedir, pygame.font.get_default_font()), os.path.join(pygamedir, 'pygame_icon.bmp')]
    datafiles = [('./pygame', pygamefiles)]

    # 2nd add files in Schoolsplay dir made & needed by Schoolsplay
    datafiles.append(('.', SP_MODULES))
    
    # 3rd add OCempGui data files (themes) and now change temporarily the path
    from childsplay_sp.ocempgui.widgets.Constants import DEFAULTDATADIR
    datafiles.append(('./childsplay_sp/ocempgui/widgets/themes/default', [os.path.join(DEFAULTDATADIR, 'themes', 'default', 'default.rc.py')]))
       
    # 4th add all files in all subdirectories for DATA_DIRS
    for directory in DATA_DIRS:
        for dirpath, dirnames, filenames in os.walk(directory):
            for name in filenames:
                datafiles.append((dirpath, [os.path.join(dirpath, name)]))
                
    # 5th add the rest of the files that are not copied automatically
    datafiles.append(('./gtk', [os.path.join(os.environ['PYTHONPATH'], 'Lib', 'site-packages', 'gtk-2.0', 'gtk', 'glade.pyd')]))
    datafiles.append(('./gtk', [os.path.join(os.environ['PYTHONPATH'], 'Lib', 'site-packages', 'gtk-2.0', 'gtk', '_gtk.pyd')]))
                
    return datafiles
    
    
if __name__ == "__main__":
    run_checks ()
    
    # Delete output directories
    try:
        shutil.rmtree('build')
        shutil.rmtree('dist')
        print('Output directories deleted')
    except:
        print('ERROR: Could not delete output directories')
    
    # Standard distutils.core arguments
    generic_data = {
        "name": "Childsplay",
        "version": SPVersion.version,
        "description": "Collection of educational activities",
        "author": "Stas Zykiewicz",
        "author_email": "stas.zytkiewicz@gmail.com",
        "maintainer": "Chris Van Bael - Windows/Mac versions",
        "maintainer_email": "chris.van.bael@gmail.com",
        "license": "GPL v3",
        "url": "http://Schoolsplay.sourceforge.net",
        "packages": [],
        "data_files": get_data_files(),
        }
       # "cmdclass": { "install_data" : InstallData },
       # }
    
    
    if sys.argv[1] == 'py2exe':
        # Making Windows executable and installer
        import py2exe
        
        # Extra keywords related to py2exe
        extra_data = {
            "windows": [{ "script": "./bin/Childsplay",
                          "icon_resources": [(1, "./share/childsplay_sp/SPData/menu/default/Childsplay.ico")]
                       }],
            "options": {"py2exe": { 
                            "optimize": 0,
                            "bundle_files": 3,
                            "excludes": ['dotblas', 'email', 'Tkinter'],
                            "includes": ['pygame.*', 'shlex', 'encodings', 'encodings.*', 
                                         'pysqlite2.dbapi2', 'numpy',
                                         'childsplay_sp.lib.*', 'childsplay_sp.Timer', 
                                         'childsplay_sp.SPDataManager', 'childsplay_sp.SPHelpText',
                                         'childsplay_sp.SQLTables',
                                         'sqlalchemy', 'sqlalchemy.*', 'sqlalchemy.mods.*',
                                         'sqlalchemy.databases.*', 'sqlalchemy.engine.*', 
                                         'sqlalchemy.ext.*', 'sqlalchemy.orm.',
                                         'weakref', 'pygtk', 'gtk', 'cairo', 
                                         'pango', 'pangocairo', 'atk', 'gobject'],}
            },
        }        
        
        setup_data = {}
        setup_data.update(generic_data)
        setup_data.update(extra_data)
        
        # Now make the executable
        sys.argv += ["--skip-archive"]
        setup(**setup_data)
        
        # Here I presume you have set you GTKPATH variable
        print "Copying necessary GTK files..."
        shutil.copy(os.path.join(os.environ['GTKPATH'], 'bin', 'libglade-2.0-0.dll'), './dist/')
        shutil.copytree(os.path.join(os.environ['GTKPATH'], 'etc'), './dist/etc')
        shutil.copytree(os.path.join(os.environ['GTKPATH'], 'lib'), './dist/lib')
        shutil.copytree(os.path.join(os.environ['GTKPATH'], 'share', 'gtk-2.0'), './dist/share/gtk-2.0')
        shutil.copytree(os.path.join(os.environ['GTKPATH'], 'share', 'gtkthemeselector'), './dist/share/gtkthemeselector')
        # Here we copy the contents of the GTKPATH/share/locale dir. We must copy each file
        # as the locale directory already exists in /dist/share/locale.
        # glob.glob is used to get the full path names
        for file in glob.glob(os.path.join(os.environ['GTKPATH'], 'share', 'locale','*.mo')):
            shutil.copy(file, './dist/share/locale')
        #shutil.copytree(os.path.join(os.environ['GTKPATH'], 'share', 'locale'), './dist/share/locale')
        shutil.copytree(os.path.join(os.environ['GTKPATH'], 'share', 'themes'), './dist/share/themes')
        shutil.copytree(os.path.join(os.environ['GTKPATH'], 'share', 'xml'), './dist/share/xml')
        
        # Make InnoSetup script setup.iss from generic.iss
        print "Adapting the InnoSetup script: generic.iss..."
        setupfile =  os.path.join(os.path.dirname(os.path.abspath (sys.argv[0])), 'dist', 'setup.iss')
        
        fpin = open('generic.iss', 'r').read()
        fpin = fpin.replace('$AppVerName$', 'Childsplay ' + SPVersion.version + PATCH_VERSION)
        fpin = fpin.replace('$AppVersion$', SPVersion.version)
        fpin = fpin.replace('$VersionInfoVersion$', SPVersion.version)
        fpin = fpin.replace('$OutputBaseFilename$', 'Childsplay-' + SPVersion.version + PATCH_VERSION + '_win32')
        fpin = fpin.replace('$BaseDir$', os.path.join(os.path.dirname(os.path.abspath (sys.argv[0]))))
        fpout = open(setupfile, 'w')
        fpout.write(fpin)        
        fpout.close()
        
        # Launch InnoSetup
        print "Running Innosetup with setup.iss, please wait..."
        cmd = "C:\Programs\Innose~1\Compil32.exe /cc " + setupfile
        print cmd
        os.system(cmd)
        
        print "Finished!"
        
        
#***************************************************************************
# current problems:
# **************************************************************************        
        
        
    
    elif sys.argv[1] == 'py2app':
        # Making Mac OSX executable and disk image
        from setuptools import setup

        # Extra keywords related to py2app
        extra_data = {
            "app": ['/bin/childsplay'],
            "setup_requires": ['py2app'],
            "options": {"argv_emulation": True,
                        "iconfile": os.path.join(os.path.dirname(os.path.abspath (sys.argv[0])), "data","Childsplay.icns")},
        }
        
        setup_data = {}
        setup_data.update(generic_data)
        setup_data.update(extra_data)
        
        # Now make the application
        setup(**setup_data)          
        
        # Adapt the Disc iMaGe and let ??? make it

#***************************************************************************
# current problems:
# Timer.py not included -> maybe solved by data_files???
# others?
# **************************************************************************          
        
   
    elif sys.argv[1] == 'install':
        # Install in existing Python environment
        print get_data_files()
        shutil.copyfile(ocemp_copy, ocemp_orig)        
        pass
    
    else: 
        print "What do you want to do?"
        print "python setup.py py2exe  -> makes Windows exe"
        print "python setup.py py2app  -> makes Mac OSX exe"
        print "python setup.py install -> installs in Python"
