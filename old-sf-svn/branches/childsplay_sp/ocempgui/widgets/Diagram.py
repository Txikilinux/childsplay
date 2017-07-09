# $Id: Diagram.py,v 1.7 2006/07/02 13:08:53 marcusva Exp $
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

"""An abstract widget for diagram and graph implementations."""

from BaseWidget import BaseWidget
from Constants import *
import base

class Diagram (BaseWidget):
    """Diagram () -> Diagram

    An abstract widget class for diagram and graph implementations.

    The Diagram class contains the minimum set of attributes and methods
    needed to visualize diagrams or graphs from arbitrary data.

    Diagrams can have different resolutions, dependant on the value
    range, that should be displayed. Inheritors thus have to implement
    the 'units' attribute and its related methods get_units() and
    set_units(), which define, how many pixels between each full unit
    have to be left. Greater values usually result in a higher
    resolution, resp. pixel amount between the values.

    To allow the user to know about the kind of data, that is evaluated
    and displayed, the 'scale_units' attribute and its related methods
    get_scale_units() and set_scale_units() must be implemented. Those
    define the concrete type of data, that is displayed on each axis of
    the diagram (e.g. cm, inch, kg...).

    The 'axes' attribute and its related methods get_axes() and
    set_axes(), which have to be implemented. denote the axes, which are
    used to set the data and its results into relation. A typical
    cartesian coordinate plane for example will have two axes (x and y).

    The 'orientation' attribute should be respected by inheritors to
    allow displaying data in a vertical or horizontal align.

    diagram.orientation = ORIENTATION_HORIZONTAL
    diagram.set_orientation (ORIENTATION_VERTICAL)

    The Diagram contains a 'negative' attribute and set_negative()
    method, which indicate, whether negative values should be shown or
    not.

    diagram.negative = True
    diagram.set_negative = False
    
    The 'origin' attribute and set_origin() method set the point of
    origin of the diagram on its widget surface and denote a tuple of an
    x and y value. Inheritors should use this to set the point of origin
    of their diagram type. Most diagram implementors usually would use
    this as a relative coordinate to the bottom left corner of the
    widget surface.
    Note, that this is different from a real relative position on the
    widget surface, as those are related to the topleft corner

    diagram.origin = 10, 10
    diagram.set_origin (20, 20)

    The 'data' attribute and set_data() method set the data to be
    evaluated by the diagram inheritor using the evaluate() method. It
    is up to the inheritor to perform additional sanity checks.

    diagram.data = mydata
    diagram.set_data (mydata)

    An evaluation function, which processes the set data can be set
    using the 'eval_func' attribute or set_eval_func() method. If set,
    the evaluate() method will process the set data using the eval_func
    and store the return values in its 'values' attribute. Otherwise, the
    values will be set to the data.

    def power_1 (x):
        return x**2 - x

    diagram.eval_func = power_1
    
    The evaluate() method of the widget distinguishes between the type
    of data and will act differently, dependant on whether it is a
    sequence or not. Lists and tuples will be passed to the eval_func
    using the python map() function, else the complete data will be
    passed to the eval_func:

    # Data is list or tuple:
    self.values = map (self.eval_func, data)

    # Any other type of data:
    self.values = self.eval_func (data)

    The result values can also be set manually without any processing
    using the 'values' attribute and set_values() method. This can be
    useful for inheritors like a bar chart for example.

    self.values = myvalues
    self.set_values (myvalues)

    A concrete implementation of the Diagram class can be found as
    Graph2D widget within this module.

    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None
    
    Attributes:
    scale_units - The scale unit(s) to set for the axes.
    units       - Pixels per unit to set.
    axes        - The axes to show.
    negative    - Indicates, that negative vaues should be taken into
                  account.
    orientation - The orientation mapping of the axes.
    origin      - The position of the point of origin on the widget.
    data        - Data to evaluate.
    values      - Result values of the set data after evaluation.
    eval_func   - Evaluation function to calculate the values.
    """
    def __init__ (self):
        BaseWidget.__init__ (self)

        # Negative values. Influences the axes.
        self._negative = False

        # Horizontal or vertical mapping of the axes.
        self._orientation = ORIENTATION_HORIZONTAL

        # Coordinates of the point of origin on the widget.
        self._origin = (0, 0)

        # The data to evaluate and the return values.
        self._data = None
        self._values = None

        # The eval func.
        self._evalfunc = None

    def get_scale_units (self):
        """D.get_scale_units (...) -> None

        Gets the scale units of the axes.

        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError

    def set_scale_units (self, units):
        """D.set_scale_units (...) -> None

        Sets the scale units of the axes.

        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError

    def get_units (self):
        """D.set_units (...) -> None

        Gets the pixels per unit for dimensioning.

        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError

    def set_units (self, units):
        """D.set_units (...) -> None

        Sets the pixels per unit for dimensioning.

        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError

    def get_axes (self):
        """D.get_axes (...) -> None

        Gets the amount and names of the axes.

        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError

    def set_axes (self, axes):
        """D.set_axes (...) -> None

        Sets the amount and names of the axes.

        This method has to be implemented by inherited widgets.
        """
        raise NotImplementedError

    def set_negative (self, negative=True):
        """D.set_negative (...) -> None

        Sets the indicator, whether negative values should be shown.
        """
        self._negative = negative
        self.dirty = True

    def set_orientation (self, orientation=ORIENTATION_HORIZONTAL):
        """D.set_orientation (...) -> None

        Sets the orientation of the axes.

        Raises a ValueError, if the passed argument is not a value of
        the ORIENTATION_TYPES tuple.
        """
        if orientation not in ORIENTATION_TYPES:
            raise ValueError("orientation must be a value of ORIENATION_TYPES")
        self._orientation = orientation
        self.dirty = True

    def set_origin (self, x, y):
        """D.set_origin (...) -> None

        Sets the coordinates of the point of origin on the widget.

        Raises a TypeError, if the passed arguments are not integers.
        """
        if (type (x) != int) or (type (y) != int):
            raise TypeError ("x and y must be integers")
        self._origin = (x, y)
        self.dirty = True

    def set_data (self, data):
        """D.set_data (...) -> None

        Sets the data to evaluate.

        This method does not perform any consistency checking or
        whatsoever.
        """
        self._data = data
        if self.data != None:
            self.evaluate ()
        else:
            self.values = None

    def set_values (self, values):
        """D.set_values (...) -> None

        Sets the values without processing the data.
        """
        self._values = values
        self.dirty = True
    
    def set_eval_func (self, func):
        """D.set_eval_func (...) -> None

        Sets the evaluation function for the data.

        Raises a TypeError, if func is not callable.
        """
        if not callable (func):
            raise TypeError ("func must be callable")
        self._evalfunc = func
        if self.data != None:
            self.evaluate ()
        else:
            self.dirty = True

    def evaluate (self):
        """D.evaluate () -> None

        Calulates the result values from the set data.
        
        Calculates the result values from the set the data using the set
        evaluation function.

        If the set data is a sequence, eval_func will be applied to each
        item of it (using map()) to build the return values:

        values = map (eval_func, data)

        If the set data is not a list or tuple, the data will be passed
        in it entirety to eval_func in order to calculate the return
        values:

        values = eval_func (data)

        The 'negative' attribute neither does affect the data nor the
        return values.
        """
        if self.eval_func != None:
            if self.data != None:
                if type (self.data) in (list, tuple):
                    self.values = map (self.eval_func, self.data)
                else:
                    self.values = self.eval_func (self.data)
                return
        self.values = self.data

    scale_units = property (lambda self: self.get_scale_units (),
                            lambda self, var: self.set_scale_units (var),
                            doc = "The scale units of the axes.")
    units = property (lambda self: self.get_units (),
                      lambda self, var: self.set_units (var),
                      doc = "The pixels per unit to set.")
    axes = property (lambda self: self.get_axes (),
                     lambda self, var: self.set_axes (var),
                     doc = "The axes to show.")
    negative = property (lambda self: self._negative,
                         lambda self, var: self.set_negative (var),
                         doc = "Indicates, whether negative values are shown.")
    orientation = property (lambda self: self._orientation,
                            lambda self, var: self.set_orientation (var),
                            doc = "The orientation of the axes.")
    origin = property (lambda self: self._origin,
                       lambda self, (x, y): self.set_origin (x, y),
                       doc = "Coordinates of the point of origin on the " \
                       "widget")
    data = property (lambda self: self._data,
                     lambda self, var: self.set_data (var),
                     doc = "The data to evaluate.")
    values = property (lambda self: self._values,
                       lambda self, var: self.set_values (var),
                       doc = "The calculated values of the set data.")
    eval_func = property (lambda self: self._evalfunc,
                          lambda self, var: self.set_eval_func (var),
                          doc = "The evaluation function for calculation.")
