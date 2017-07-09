# needed for version numbers
#import pygame
import Version
version=Version.version
from gtk import gtk_version, pygtk_version
from sqlalchemy import __version__ as sversion

### don't make changes below this line ################
spversion = "Schoolsplay version: %s" % version
gtkversion = "GTK version: %s.%s.%s" % gtk_version
pygtkversion = "PyGTK version: %s.%s.%s" % pygtk_version
sqlversion = "SqlAlchemy version: %s" % sversion
#pgversion = "Pygame version: %s" % pygame.version.ver
#sdlversion = "SDL version: %s.%s.%s" % pygame.get_sdl_version()

# Needed for the option parser
optversion = '\n'.join(['-'*60,spversion,gtkversion, pygtkversion, sqlversion,'-'*60])
