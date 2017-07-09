# $Id: Table.py,v 1.26.2.8 2007/03/23 11:57:14 marcusva Exp $
#
# Copyright (c) 2004-2007, Marcus von Appen
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

"""Widget class, which places its children in a table grid"""

from Container import Container
from Constants import *
import base

class Table (Container):
    """Table (rows, cols) -> Table

    A container widget, which packs its children in a table like manner.

    The Table class is a layout container, which packs it children in a
    regular, table like manner and allows each widget to be aligned
    within its table cell. The table uses a 0-based (Null-based)
    indexing, which means, that if 4 rows are created, they can be
    accessed using a row value ranging from 0 to 3. The same applies to
    the columns.

    The Table provides read-only 'columns' and 'rows' attributes, which
    are the amount of columns and rows within that Table.
    
    totalr = table.rows
    totalc = table.columns

    To access the children of the Table the 'grid' attribute can be
    used. It is a dictionary containing the widgets as values. To access
    a widget, a tuple containing the row and column is used as the
    dictionary key.

    widget = table.grid[(0, 3)]
    widget = table.grid[(7, 0)]

    The above examples will get the widget located at the first row,
    fourth column (0, 3) and the eighth row, first column (7, 0).

    The layout for each widget within the table can be set individually
    using the set_align() method. Alignments can be combined, which
    means, that a ALIGN_TOP | ALIGN_LEFT would align the widget at the
    topleft corner of its cell.

    However, not every alignment make sense, so a ALIGN_TOP | ALIGN_BOTTOM
    would cause the widget to be placed at the top. The priority
    order for the alignment follows. The lower the value, the higher the
    priority.

    Alignment      Priority
    -----------------------
    ALIGN_TOP         0
    ALIGN_BOTTOM      1
    ALIGN_LEFT        0
    ALIGN_RIGHT       1
    ALIGN_NONE        2
    
    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None
    
    Attributes:
    columns  - The column amount of the Table.
    rows     - The row amount of the Table.
    grid     - Grid to hold the children of the Table.
    """
    def __init__ (self, rows, cols):
        Container.__init__ (self)
        if (type (rows) != int) or (type (cols) != int):
            raise TypeError ("Arguments must be positive integers")
        if (rows <= 0) or (cols <= 0):
            raise ValueError ("Arguments must be positive integers")
        self._cols = cols
        self._rows = rows

        # The grid for the children.
        self._grid = {}
        for i in xrange (self._rows):
            for j in xrange (self._cols):
                self._grid[(i, j)] = None # None means unused, !None is used.

        # Grid for the layout.
        self._layout = {}
        for i in xrange (self._rows):
            for j in xrange (self._cols):
                self._layout[(i, j)] = ALIGN_NONE

        # Width and height grids.
        self._colwidth = {}
        self._rowheight = {}
        for i in xrange (self._cols):
            self._colwidth[i] = 0
        for i in xrange (self._rows):
            self._rowheight[i] = 0

        self.dirty = True # Enforce creation of the internals.

    def add_child (self, row, col, widget):
        """T.add_child (...) -> None

        Adds a widget into the cell located at (row, col) of the Table.

        Raises a ValueError, if the passed row and col arguments are not
        within the cell range of the Table.
        Raises an Exception, if the cell at the passed row and col
        coordinates is already occupied.
        """
        if (row, col) not in self.grid:
            raise ValueError ("Cell (%d, %d) out of range" % (row, col))
        if self.grid[(row, col)] != None:
            raise Exception ("Cell (%d, %d) already occupied" % (row, col))

        self.grid[(row, col)] = widget
        Container.add_child (self, widget)

    def remove_child (self, widget):
        """T.remove_widget (...) -> None

        Removes a widget from the Table.
        """
        Container.remove_child (self, widget)
        for i in xrange (self._rows):
            for j in xrange (self._cols):
                if self.grid[(i, j)] == widget:
                    self.grid[(i, j)] = None

    def set_children (self, children):
        """T.set_children (...) -> None

        Sets the children of the Table.

        When setting the children of the Table, keep in mind, that the
        children will be added row for row, causing the Table to fill
        the first row of itself, then the second and so on.

        Raises a ValueError, if the passed amount of children exceeds
        the cell amount of the Table.
        """
        if children != None:
            if len (children) > (self.columns * self.rows):
                raise ValueError ("children exceed the Table size.")

        # Remove all children first.
        for i in xrange (self._rows):
            for j in xrange (self._cols):
                self.grid[(i, j)] = None
        Container.set_children (self, children)
        if children == None:
            return
        
        cells = len (children)
        for i in xrange (self._rows):
            for j in xrange (self._cols):
                self.grid[(i, j)] = children[-cells]
                cells -= 1
                if cells == 0:
                    return

    def insert_child (self, pos, *children):
        """C.insert_child (...) -> None

        Inserts one or more children at the desired position.

        Raises a NotImplementedError, as this method cannot be applied
        to the Table.
        """
        raise NotImplementedError
    
    def set_focus (self, focus=True):
        """T.set_focus (focus=True) -> None

        Overrides the set_focus() behaviour for the Table.

        The Table class is not focusable by default. It is a layout
        class for other widgets, so it does not need to get the input
        focus and thus it will return false without doing anything.
        """
        return False

    def set_align (self, row, col, align=ALIGN_NONE):
        """T.set_align (...) -> None

        Sets the alignment for a specific cell.

        Raises a ValueError, if the passed row and col arguments are not
        within the rows and columns of the Table.
        Raises a TypeError, if the passed align argument is not a value
        from ALIGN_TYPES.
        """
        if (row, col) not in self._layout:
            raise ValueError ("Cell (%d, %d) out of range" % (row, col))
        if not constants_is_align (align):
            raise TypeError ("align must be a value from ALIGN_TYPES")

        self._layout[(row, col)] = align
        self.dirty = True

    def set_column_align (self, col, align=ALIGN_NONE):
        """T.set_column_align (...) -> None

        Sets the alignment for a whole column range.

        Raises a ValueError, if the passed col argument is not within
        the column range of the Table.
        Raises a TypeError, if the passed align argument is not a value from
        ALIGN_TYPES.
        """
        if (0, col) not in self._layout:
            raise ValueError ("Column %d out of range" % col)
        if not constants_is_align (align):
            raise TypeError ("align must be a value from ALIGN_TYPES")

        for i in xrange (self.rows):
            self._layout[(i, col)] = align
        self.dirty = True

    def set_row_align (self, row, align=ALIGN_NONE):
        """T.set_row_align (...) -> None

        Sets the alignment for a whole row.

        Raises a ValueError, if the passed row argument is not within
        the row range of the Table.
        Raises a TypeError, if the passed align argument is not a value
        from ALIGN_TYPES.
        """
        if (row, 0) not in self._layout:
            raise ValueError ("Row %d out of range" % row)
        if not constants_is_align (align):
            raise TypeError ("align must be a value from ALIGN_TYPES")

        for i in xrange (self.columns):
            self._layout[(row, i)] = align
        self.dirty = True
    
    def destroy (self):
        """T.destroy () -> None

        Destroys the Table and all its children and shedules them for
        deletion by the renderer.
        """
        Container.destroy (self)
        del self._grid
        del self._layout
        del self._colwidth
        del self._rowheight
        
    def calculate_size (self):
        """T.calculate_size () -> int, int

        Calculates the size needed by the children.

        Calculates the size needed by the children and returns the
        resulting width and height.
        """
        for i in xrange (self._cols):
            self._colwidth[i] = 0
        for i in xrange (self._rows):
            self._rowheight[i] = 0

        spacing = self.spacing
        
        # Fill the width and height grids with correct values.
        for row in xrange (self._rows):
            actheight = 0
            for col in xrange (self._cols):
                widget = self.grid[(row, col)]
                if not widget: # No child here.
                    continue
                cw = widget.width + spacing
                ch = widget.height + spacing
                if self._colwidth[col] < cw:
                    self._colwidth[col] = cw
                if actheight < ch:
                    actheight = ch

            if self._rowheight[row] < actheight:
                self._rowheight[row] = actheight
        
        height = reduce (lambda x, y: x + y, self._rowheight.values (), 0)
        height += 2 * self.padding - spacing
        width = reduce (lambda x, y: x + y, self._colwidth.values (), 0)
        width += 2 * self.padding - spacing
        return max (width, 0), max (height, 0)
    
    def dispose_widgets (self):
        """T.dispose_widgets (...) -> None

        Sets the children to their correct positions within the Table.
        """
        # Move all widgets to their correct position.
        spacing = self.spacing
        padding = self.padding
        x = padding
        y = padding
        
        for row in xrange (self._rows):
            for col in xrange (self._cols):
                widget = self.grid[(row, col)]
                if not widget: # no child here
                    x += self._colwidth[col]
                    continue

                # Dependant on the cell layout, move the widget to the
                # desired position.
                align = self._layout[(row, col)]
                # Default align is centered.
                posx = x + (self._colwidth[col] - widget.width - spacing) / 2
                posy = y + (self._rowheight[row] - widget.height - spacing) / 2
                if align & ALIGN_LEFT == ALIGN_LEFT:
                    posx = x
                elif align & ALIGN_RIGHT == ALIGN_RIGHT:
                    posx = x + self._colwidth[col] - widget.width - spacing

                if align & ALIGN_TOP == ALIGN_TOP:
                    posy = y
                elif align & ALIGN_BOTTOM  == ALIGN_BOTTOM:
                    posy = y + self._rowheight[row] - widget.height - spacing
                widget.topleft = (posx, posy)
                x += self._colwidth[col]

            y += self._rowheight[row]
            x = padding

    def draw_bg (self):
        """T.draw_bg () -> Surface

        Draws the background surface of the Table and returns it.

        Creates the visible surface of the Table and returns it to the
        caller.
        """
        return base.GlobalStyle.engine.draw_table (self)

    def draw (self):
        """T.draw () -> None

        Draws the Table surface and places its children on it.
        """
        Container.draw (self)

        # Draw all children.
        self.dispose_widgets ()
        blit = self.image.blit
        for widget in self.children:
            blit (widget.image, widget.rect)

    columns = property (lambda self: self._cols,
                        doc = "The column amount of the Table.")
    rows = property (lambda self: self._rows,
                     doc = "The row amount of the Table.")
    grid = property (lambda self: self._grid, doc = "The grid of the Table.")
