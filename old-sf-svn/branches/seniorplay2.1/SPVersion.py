# needed for version numbers
import pygame, sys
import sqlalchemy as sqla
import Version
version=Version.version

### don't make changes below this line ################
spversion = "Childsplay version: %s" % version
plat = "Platform :%s" % sys.platform
pyversion = "Python version: %s" % sys.version.split('\n')[0]
pgversion = "Pygame version: %s" % pygame.version.ver
sdlversion = "SDL version: %s.%s.%s" % pygame.get_sdl_version()
sqlaversion = "Sqlalchemy version: %s" % sqla.__version__
# Needed for the option parser
optversion = '\n'.join(['-'*60,spversion,plat, pyversion, pgversion,\
                        sdlversion,sqlaversion,'-'*60])
