"""Support to line highlight, line numbering...
"""

from PyQt4.QtCore import Qt, QRect
from PyQt4.QtGui import (QWidget, QPainter, QBrush, QFrame,
                         QTextEdit, QPlainTextEdit, QColor,
                         QTextFormat, QTextCursor, QFont)


class WithHighlight(QPlainTextEdit):
    """Mixin to add Highlight on current line to QPlainTextEdit"""

    color_focus = QColor(255, 220, 240)
    color_no_focus = QColor(255, 220, 240, 150)

    def __init__(self, *args):
        self.highlight()
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.cursorPositionChanged.connect(self.highlight)

    def highlight(self):
        """this method will hightlight current line"""
        if self.hasFocus():
            color = self.color_focus
        else:
            color = self.color_no_focus

        extra_selections = []

        if (self.isReadOnly() is False):
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(color)
            selection.format.setProperty(QTextFormat.FullWidthSelection,
                                         True)

            cursor = self.textCursor()
            last_selection_line = cursor.blockNumber()
            selection.cursor = cursor
            selection.cursor.movePosition(QTextCursor.EndOfBlock)
            extra_selections.append(QTextEdit.ExtraSelection(selection))

            selection.cursor.movePosition(QTextCursor.StartOfLine)
            selection.cursor.movePosition(QTextCursor.PreviousCharacter)
            while(last_selection_line == selection.cursor.blockNumber()):
                if(selection.cursor.atStart()):
                    break
                extra_selections.append(QTextEdit.ExtraSelection(selection))
                selection.cursor.movePosition(QTextCursor.StartOfLine)
                selection.cursor.movePosition(QTextCursor.PreviousCharacter)

        self.setExtraSelections(extra_selections)

    def focusInEvent(self, focus_event):
        super(WithHighlight, self).focusInEvent(focus_event)
        self.highlight()

    def focusOutEvent(self, focus_event):
        super(WithHighlight, self).focusOutEvent(focus_event)
        self.highlight()


class WithFixedFont(QPlainTextEdit):
    """Mixin to add Highlight on current line to QPlainTextEdit"""
    def __init__(self, *args):
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setFont(QFont("Monospace", 11))


class WithLineNumbers(QPlainTextEdit):
    """Mixin to add Highlight on current line to QPlainTextEdit"""

    class LineNumber(QWidget):

        def __init__(self, edit):
            QWidget.__init__(self, edit)

            self.edit = edit
            self.adjustWidth(1)

        def paintEvent(self, event):
            self.edit.number_bar_paint(self, event)
            QWidget.paintEvent(self, event)

        def adjustWidth(self, count):
            width = self.fontMetrics().width(unicode(count)) + 3
            if self.width() != width:
                self.setFixedWidth(width)

        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update()

    def __init__(self, *args):
        self.number_bar = self.LineNumber(self)
        self.contentOffset()
        #self.setViewportMargins(15,0,0,0)
        self.setFrameStyle(QFrame.NoFrame)
        self.blockCountChanged.connect(self.number_bar.adjustWidth)
        self.updateRequest.connect(self.number_bar.updateContents)

    def number_bar_paint(self, number_bar, event):
        font_metrics = self.fontMetrics()
        current_line = self.document().findBlock(self.textCursor().
                                            position()).blockNumber() + 1

        block = self.firstVisibleBlock()
        line_count = block.blockNumber()
        painter = QPainter(number_bar)
        #painter.fillRect(event.rect(), Qt.lightGray)#self.palette().base())
        painter.fillRect(event.rect(), QColor(230, 230, 230))

        # Iterate over all visible text blocks in the document.
        while block.isValid():
            line_count += 1
            block_top = self.blockBoundingGeometry(block).translated(
                                        self.contentOffset()).top()

            # Check if the position of the block is out side of the visible
            # area.
            if not block.isVisible() or block_top >= event.rect().bottom():
                break

            # We want the line number for the selected line to be bold.
            if line_count == current_line:
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)
                painter.setBrush(QBrush(Qt.red))
            else:
                font = painter.font()
                font.setBold(False)
                painter.setFont(font)

            # Draw the line number right justified at the position of the line.
            self.setViewportMargins(number_bar.width(), 0, 0, 0)
            paint_rect = QRect(0, block_top, number_bar.width(),
                                               font_metrics.height())
            painter.drawText(paint_rect, Qt.AlignRight, str(line_count))

            block = block.next()

        painter.end()

    def resizeEvent(self, resize_event):
        super(WithLineNumbers, self).resizeEvent(resize_event)
        self.number_bar.setGeometry(QRect(0, 0, 15, self.viewport().height()))


if(__name__ == '__main__'):
    def test_with_hightlight():
        """simple test"""
        import os
        import sys
        from PyQt4.QtGui import QApplication

        lib_path = os.path.abspath('../..')
        sys.path.append(lib_path)
        from misc.Mixin import mixin

        app = QApplication([])
        widget = mixin(QPlainTextEdit,
                       WithHighlight,
                       WithFixedFont)()
        widget.show()
        app.exec_()

    def test_with_linenumber():
        """simple test"""
        import os
        import sys
        from PyQt4.QtGui import QApplication

        lib_path = os.path.abspath('../..')
        sys.path.append(lib_path)
        from misc.Mixin import mixin

        app = QApplication([])
        widget = mixin(QPlainTextEdit,
                       WithHighlight,
                       WithFixedFont,
                       WithLineNumbers)()
        widget.show()
        app.exec_()

    test_with_hightlight()
    test_with_linenumber()
