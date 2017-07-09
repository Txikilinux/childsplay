# $Id: Image.py,v 1.12.2.1 2006/08/16 09:30:31 marcusva Exp $
#
# Copyright (c) 2004-2006, Marcus von Appen
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Image loading, drawing and manipulation functions."""

from pygame import image

def load_image (filename, alpha=False, colorkey=None):
    """load_image (...) -> Surface

    Loads and returns an image.

    Tries to load an image from the passed 'filename' argument and
    automatically converts it to the display pixel format for faster
    blit operations.

    The 'alpha' argument will enforce alpha transparency on the image by
    invoking Surface.convert_alpha(). If the surface contains alpha
    transparency, it will be enabled automatically.

    The 'colorkey' argument can be used to add color based transparency
    using Surface.set_colorkey().

    The following example will load an image using both, alpha
    transparency and a colorkey:

    load_image ('image.png', True, (255, 0, 0))
    """
    surface = image.load (filename)
    if colorkey:
        surface.set_colorkey (colorkey)
    if alpha or surface.get_alpha ():
        return surface.convert_alpha ()
    return surface.convert ()
