# needed for version numbers
import pygame
import Version
version=Version.version

### don't make changes below this line ################
spversion = "Schoolsplay version: %s" % version
pgversion = "Pygame version: %s" % pygame.version.ver
sdlversion = "SDL version: %s.%s.%s" % pygame.get_sdl_version()

# Needed for the option parser
optversion = '\n'.join(['-'*60,spversion,pgversion,sdlversion,'-'*60])
