"""Support to line highlight, line numbering...
"""

from PyQt4.QtCore import Qt, QRect

from PyQt4.QtGui import (QWidget, QPainter, QFrame,
                         QTextEdit, QPlainTextEdit, QColor,
                         QTextFormat, QTextCursor, QFont, QPen)

import re


class WithLineHighlight(QPlainTextEdit):
    """Mixin to add Highlight on current line to QPlainTextEdit"""

    color_focus = QColor(255, 210, 255)
    color_no_focus = QColor(255, 210, 255, 120)

    def __init__(self, *args):
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.cursorPositionChanged.connect(self.highlight)
        self.extra_selections_dict = {}
        self.highlight()

    def get_extra_selections(self, key):
        return self.extra_selections_dict.get(key, [])
    def set_extra_selections(self, key, extra_selections):
        self.extra_selections_dict[key] = extra_selections
        
    def update_extra_selections(self):
        extra_selections = []
        for key, extra in list(self.extra_selections_dict.items()):
            if key == 'current_line':
                # Python 3 compatibility (weird): current line has to be 
                # highlighted first
                extra_selections = extra + extra_selections
            else:
                extra_selections += extra
        self.setExtraSelections(extra_selections)
    def highlight(self):
        """Highlight current line"""
        selection = QTextEdit.ExtraSelection()
        selection.format.setProperty(QTextFormat.FullWidthSelection,
                                     True)
        selection.format.setBackground(self.color_focus)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.set_extra_selections('current_line', [selection])
        self.update_extra_selections()
    """def highlight(self):
        " ""this method will hightlight current line" ""
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

        self.setExtraSelections(extra_selections)"""

    def focusInEvent(self, focus_event):
        super(WithLineHighlight, self).focusInEvent(focus_event)
        self.highlight()

    def focusOutEvent(self, focus_event):
        super(WithLineHighlight, self).focusOutEvent(focus_event)
        self.highlight()


class WithFixedFont(QPlainTextEdit):
    """Mixin to add Highlight on current line to QPlainTextEdit"""
    def __init__(self, *args):
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setFont(QFont("Monospace", 11))


class WithViewPortMargins(QPlainTextEdit):
    """Mixin to add ViewPortMargins to QPlainTextEdit"""

    def __init__(self, *args):
        """tupple left, top, right. bottom"""
        self.dict_margins = {}
        self.catched_margins = (0, 0, 0, 0)

    def get_viewport_margins(self):
        return self.catched_margins

    
    def __update_viewport_margins(self):
        left, top, right, bottom = 0,0,0,0
        for _n, margins in self.dict_margins.items():
            left += margins[0]
            top += margins[1]
            right += margins[2]
            bottom += margins[3]
        
        self.catched_margins = left, top, right, bottom
        self.setViewportMargins(left, top, right, bottom)

           

    def set_viewport_margins(self, name, margins):
        
        if name in self.dict_margins:
            if margins == (0, 0) :
                del self.dict_margins[name]
                self.__update_viewport_margins()
            elif self.dict_margins[name] != margins:
                self.dict_margins[name] = margins
                self.__update_viewport_margins()
            else:  # no change
                pass
        else:
            if margins != (0,0):
                self.dict_margins[name] = margins
                self.__update_viewport_margins()
            else:
                pass                


class WithLineNumbers(WithViewPortMargins):
    """Mixin to add line numbers to QPlainTextEdit
    It requieres WithViewPortMargins"""

    class LineNumber(QWidget):

        def __init__(self, edit):
            QWidget.__init__(self, edit)

            self.edit = edit
            self.adjustWidth(1)

        def paintEvent(self, event):
            self.edit.number_bar_paint(self, event)
            QWidget.paintEvent(self, event)

        def adjustWidth(self, count):
            width = self.fontMetrics().width("A", count) + 8
            if self.width() != width:
                self.setFixedWidth(width)

        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update()

    def __init__(self, *args):
        self.number_bar = self.LineNumber(self)
        #self.contentOffset()
        #self.setViewportMargins(15,0,0,0)
        self.setFrameStyle(QFrame.NoFrame)
        self.blockCountChanged.connect(self.number_bar.adjustWidth)
        self.updateRequest.connect(self.number_bar.updateContents)
        self.number_bar.adjustWidth(self.blockCount())

    def number_bar_paint(self, number_bar, event):
        font_metrics = self.fontMetrics()
        current_line = self.document().findBlock(self.textCursor().
                                            position()).blockNumber() + 1

        block = self.firstVisibleBlock()
        line_count = block.blockNumber()
        painter = QPainter(number_bar)
        #painter.fillRect(event.rect(), Qt.lightGray)#self.palette().base())
        painter.fillRect(event.rect(), QColor(230, 230, 230))
        painter.setPen(QPen(QColor(180, 180, 180)))
        painter.drawLine(event.rect().width()-1, 0, event.rect().width()-1, 
                                         event.rect().height()-1)
        
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
                painter.setPen(QColor(160, 100, 160))
            else:
                font = painter.font()
                font.setBold(False)
                painter.setFont(font)
                painter.setPen(QColor(160, 160, 160))

            # Draw the line number right justified at the position of the line.
            #left, top, right, bottom = super(WithLineNumbers, self).get_viewport_margins()
            left = number_bar.width()
            super(WithLineNumbers, self).set_viewport_margins("line_number", 
                                                (left, 0, 0, 0))
            paint_rect = QRect(0, block_top, number_bar.width()-3,
                                               font_metrics.height())
            painter.drawText(paint_rect, Qt.AlignRight, str(line_count))

            block = block.next()

        painter.end()

    def resizeEvent(self, resize_event):
        super(WithLineNumbers, self).resizeEvent(resize_event)
        self.number_bar.setGeometry(QRect(0, 0, 15, self.viewport().height()))


class WithBasicIdentationManager(QPlainTextEdit):
    """Mixin to add simple identation manager to QPlainTextEdit

TAB key will add spaces stopping on multiples of 4

When TAB is pressed with more than one line pressed, it will increase ident
for all lines. Opposite pressing Shift-TAB

Adding new lines with RETURN key, will keep previous line identation
"""
    def __init__(self, *args):
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backtab:
            anchor_pos_cursor = self.textCursor()
            anchor_pos_cursor.setPosition(self.textCursor().anchor())
            if(self.textCursor().blockNumber()
                                    != anchor_pos_cursor.blockNumber()):
                self.decrease_identation()

        elif event.key() == Qt.Key_Backspace:
            self.delete_back(event)

        elif event.key() == Qt.Key_Tab:
            anchor_pos_cursor = self.textCursor()
            anchor_pos_cursor.setPosition(self.textCursor().anchor())
            if(self.textCursor().blockNumber()
                                    != anchor_pos_cursor.blockNumber()):
                self.increase_identation()
            else:
                self.insert_tab()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            super(WithBasicIdentationManager, self).keyPressEvent(event)
            self.process_newline()
        else:
            super(WithBasicIdentationManager, self).keyPressEvent(event)

    def insert_tab(self):
        cursor = self.textCursor()
        num_spaces2add = 4 - cursor.positionInBlock() % 4
        if num_spaces2add == 0:
            num_spaces2add = 3
        spaces2add = ' ' * num_spaces2add
        cursor.insertText(spaces2add)

    def increase_identation(self):
        cursor = self.textCursor()
        first_block_selected = 0
        last_block_selected = 0
        min_pos = 0
        extra_line = 0
        if cursor.position() > cursor.anchor():
            last_block_selected = cursor.blockNumber()
            if cursor.atBlockStart() == False:
                extra_line = 1
            cursor.setPosition(cursor.anchor())
            first_block_selected = cursor.blockNumber()
            min_pos = cursor.position()
        else:
            first_block_selected = cursor.blockNumber()
            min_pos = cursor.position()
            cursor.setPosition(cursor.anchor())
            last_block_selected = cursor.blockNumber()
            if cursor.atBlockStart() == False:
                extra_line = 1
        if first_block_selected != last_block_selected:
            cursor.setPosition(min_pos)
            for i in range(first_block_selected,
                                       last_block_selected + extra_line):
                cursor.movePosition(QTextCursor.StartOfBlock)
                cursor.insertText("    ")
                cursor.movePosition(QTextCursor.NextBlock)
                if cursor.atEnd():
                    break

    def decrease_identation(self):
        cursor = self.textCursor()
        first_block_selected = 0
        last_block_selected = 0
        min_pos = 0
        extra_line = 0
        if cursor.position() > cursor.anchor():
            last_block_selected = cursor.blockNumber()
            if cursor.atBlockStart() == False:
                extra_line = 1
            cursor.setPosition(cursor.anchor())
            first_block_selected = cursor.blockNumber()
            min_pos = cursor.position()
        else:
            first_block_selected = cursor.blockNumber()
            min_pos = cursor.position()
            cursor.setPosition(cursor.anchor())
            last_block_selected = cursor.blockNumber()
            if cursor.atBlockStart() == False:
                extra_line = 1

        if first_block_selected != last_block_selected:
            cursor.setPosition(min_pos)
            cursor.movePosition(cursor.StartOfBlock)
            for i in range(first_block_selected,
                                    last_block_selected + extra_line):
                #  try to remove 4 spaces at the beginning
                for j in range(0, 4):
                    cursor.movePosition(QTextCursor.Right,
                                                        QTextCursor.KeepAnchor)
                    if cursor.selectedText() == " ":
                        cursor.removeSelectedText()
                    else:
                        break

                cursor.movePosition(QTextCursor.NextBlock)
                if cursor.atEnd():
                    break

    def delete_back(self, event):
        #  if spaces till previous tab point, remove all of them
        if self.textCursor().selectedText() != "":
            self.textCursor().removeSelectedText()
        elif self.textCursor().atBlockStart():
            super(WithBasicIdentationManager, self).keyPressEvent(event)
        else:
            cursor = self.textCursor()
            dist_prev_tab = cursor.positionInBlock() % 4
            if dist_prev_tab == 0:
                dist_prev_tab = 4
            cursor.setPosition(cursor.position() - dist_prev_tab,
                                       QTextCursor.KeepAnchor)
            if cursor.selectedText().strip() == "":
                cursor.removeSelectedText()
            else:
                super(WithBasicIdentationManager, self).keyPressEvent(event)

    def process_newline(self):
        def get_previous_line_spaces(self):
            tc = self.textCursor()
            #while tc.selectedText().size() == 0 and tc.blockNumber() > 1:
            for i in range(0, 1):
                tc.movePosition(QTextCursor.StartOfBlock)
                tc.movePosition(QTextCursor.PreviousBlock)
                tc.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)

            if tc.selectedText() < 2:
                return 0
            else:
                found_spaces = re.search('[^ ]', tc.selectedText() + '.')
                if found_spaces:
                    return found_spaces.start()
                else:
                    return 0

        tc = self.textCursor()
        if tc.atBlockStart():
            tc.insertText(' ' * get_previous_line_spaces(self))
            tc2 = self.textCursor()
            #tc2.movePosition(QTextCursor.EndOfBlock)
            self.setTextCursor(tc2)


if(__name__ == '__main__'):
    def test_with_hightlight():
        """simple test"""
        from PyQt4.QtGui import QApplication
        from Mixin import mixin

        app = QApplication([])
        widget = mixin(
                       WithLineHighlight,
                       WithFixedFont,
                       QPlainTextEdit)()
        widget.show()
        app.exec_()

    def test_with_linenumber_and_word_completion():
        """simple test"""
        from PyQt4.QtGui import QApplication
        from Mixin import mixin

        app = QApplication([])
        widget = mixin(
                       WithBasicIdentationManager,
                       WithLineNumbers,
                       WithViewPortMargins,
                       WithLineHighlight,
                       WithFixedFont,
                       QPlainTextEdit)()
        widget.show()
        app.exec_()

    #test_with_hightlight()
    test_with_linenumber_and_word_completion()
