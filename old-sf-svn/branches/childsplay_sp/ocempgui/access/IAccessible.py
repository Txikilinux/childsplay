# $Id: IAccessible.py,v 1.2 2006/04/25 13:54:52 marcusva Exp $
#
# Copyright (c) 2004-2005, Marcus von Appen
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

"""Basic accessibility interface class. It enables inheriting classes to
provide accessibility information and makes them ready to be recognized
and used by accessibility technologies."""

class IAccessible (object):
    """IAccessible () -> IAccessible

    An abstract interface class for accessibility implementations.

    The IAccessible class provides a single get_accessible() method
    definition, which can can be used by accessibility toolkit bindings
    to get necessary acessibility information from an python
    object. Those can contain information such as the object its current
    state, presentation information and interaction possibilities, for
    example.

    Accessibility information are especially needed by, but not limited
    to, people with disabilities, so they can gather needed information
    from objects to clearly recognize them.
    """
    def get_accessible (self):
        """I.get_accessible () -> Accessible

        Gets the Accessible from the object.

        Gets the Accessible from the object, which contains further
        infomormation about its state, presentation, interaction
        possibilities and more.

        This method has to be implemented by inheriting classes.
        """
        raise NotImplementedError
