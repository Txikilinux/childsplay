# $Id: Complex.py,v 1.8.2.2 2006/12/25 13:05:45 marcusva Exp $
#
# Copyright (c) 2006, Marcus von Appen
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

"""Complex drawing objects."""

from pygame import Surface, SRCALPHA, surfarray
    
class FaderSurface (Surface):
    """FaderSurface (width, height, alpha=255) -> FaderSurface

    A pygame.Surface class, that supports alpha fading.

    The FaderSurface is an enhanced 32-bit pygame.Surface, that supports
    alpha blending and fading the surface in or out. It uses pixel-based
    alpha values for transparency.

    The 'alpha' attribute indicates the currently set alpha value for
    the Surface and can be adjusted by either reassigning it directly or
    using the set_alpha() method. Its value range is limited from 0
    (transparent) to 255 (opaque) as supported by the pygame library.

    fader.alpha = 155
    fader.set_alpha (24)

    Note that the set_alpha() method overrides the original set_alpha()
    method from pygame.Surface.

    The stepping value for fading operations can be read and set through
    the 'step' attribute or set_step() method. Each call of the update()
    method will increase (or decrease) the alpha value by the set step.

    fader.step = 10
    fader.set_step (5)

    To in- or decrease the alpha channel so that you will receive a fade
    in or fade out effect, you can use the update() method in a loop,
    which constantly blits the surface.

    while fader.update ():
        screen.blit (fader, (10, 10))
        pygame.display.update (fader_rect)

    The update() method returns True as long as the alpha value has not
    reached its upper or lower boundary.
        
    Attributes:
    alpha - The currently set alpha value.
    step  - The step range for increasing or decreasing the alpha value.
    """
    def __init__ (self, width, height, alpha=255):
        Surface.__init__ (self, (width, height), SRCALPHA, 32)
        self._alpha = 255
        self._step = -1
        self.set_alpha (alpha)

    def set_alpha (self, alpha=255):
        """F.set_alpha (...) -> None

        Sets the alpha transparency value.

        Raises a TypeError, if the passed argument is not an integer.
        Raises a ValueError, if the passed argument is not in the range
        0 <= alpha <= 255
        """
        if type (alpha) != int:
            raise TypeError ("alpha must be a positive integer")
        if (alpha < 0) or (alpha > 255):
            raise ValueError ("alpha must be in the range 0 <= alpha <= 255")

        self._alpha = alpha
        # Apply the alpha.
        array = surfarray.pixels_alpha (self)
        array[:] = alpha
        del array
        
    def set_step (self, step=-1):
        """F.set_step (...) -> None

        Sets the step range to use for in- or decreasing the alpha value.

        Raises a TypeError, if the passed argument is not an integer.
        """
        if type (step) != int:
            raise TypeError ("step must be an integer")
        self._step = step
        
    def update (self):
        """F.update () -> bool

        Updates the alpha channel of the surface.

        Updates the alpha channel of the surface and returns True, if
        the alpha channel was modified or False, if not.
        """
        val = self._alpha + self._step

        if val < 0:
            val = 0
        if val > 255:
            val = 255

        array = surfarray.pixels_alpha (self)
        array[:] = val
        del array
        self._alpha = val

        return not (val == 0) and not (val == 255)
    
    alpha = property (lambda self: self._alpha,
                      lambda self, var: self.set_alpha (var),
                      doc = "The currently set alpha value.")
    step = property (lambda self: self._step,
                     lambda self, var: self.set_step (var),
                     doc = "The step range for increasing or decreasing the" \
                     "alpha value.")
