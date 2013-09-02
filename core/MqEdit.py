"""Support to line highlight, line numbering...
"""

from PyQt4.QtCore import Qt, QRect, QString, QRegExp

from PyQt4.QtGui import (QWidget, QPainter, QFrame,
                         QTextEdit, QPlainTextEdit, QColor,
                         QTextFormat, QTextCursor, QFont,
                         QCompleter, QStringListModel,
                         QKeySequence,
                         QApplication, QCursor)
import re


class WithHighlight(QPlainTextEdit):
    """Mixin to add Highlight on current line to QPlainTextEdit"""

    color_focus = QColor(255, 210, 255)
    color_no_focus = QColor(255, 210, 255, 120)

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
    """Mixin to add line numbers to QPlainTextEdit"""

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
                painter.setPen(QColor(160, 100, 160))
            else:
                font = painter.font()
                font.setBold(False)
                painter.setFont(font)
                painter.setPen(QColor(160, 160, 160))

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


class WithWordCompletion(QPlainTextEdit):
    """\
Mixin to add simple word completion to QPlainTextEdit

It will propose completion with words from current file

When the word you are writting is bigger than two, it will propose completion
but with no default selection.

If you press Ctrl-Space, the proposal will choose the first one as default
"""
    def __init__(self, *args):
        self.model_completer = QStringListModel()
        self.completer = QCompleter(self)
        #self.completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWrapAround(False)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setModel(self.model_completer)
        self.completer.activated.connect(self.insert_completion)

    def keyPressEvent(self, event):
        if (self.completer.popup().isVisible()):
            #The following keys are forwarded by the completer to the widget
            event_key = event.key()
            if(event_key in [Qt.Key_Enter,
                             Qt.Key_Return,
                             Qt.Key_Escape,
                             Qt.Key_Tab,
                             Qt.Key_Backtab]
                         and self.completer.popup().currentIndex().row() >= 0):
                event.ignore()
                return  # let the completer do default behavior

        super(WithWordCompletion, self).keyPressEvent(event)
        if((event.modifiers() | event.key()) == QKeySequence("Ctrl+Space")):
            self.show_completer(True)
        else:
            pressed_key_as_string = QKeySequence(event.key()).toString()
            text_under_cursor = self.text_under_cursor()
            if(text_under_cursor.size() > 2  and
                    ((event.text() != ""
                    and re.match("^[A-Za-z0-9_-]*$", pressed_key_as_string[0]))
                    or  self.completer.popup().isVisible())):
                self.show_completer(False)
            else:
                self.completer.popup().hide()

    def get_text_completion_list(self):
        words = self.toPlainText().split(QRegExp("[^a-zA-Z0-9_]"),
                                 QString.SkipEmptyParts)
        text_under_cursor = self.text_under_cursor()
        words.removeDuplicates()
        words.sort()
        completion_list = []
        completion_list_not_start_with = []
        for str in words:
            if(str != text_under_cursor  and
                    str.toUpper().indexOf(text_under_cursor.toUpper()) == 0):
                completion_list.append(str)
            elif(str != text_under_cursor  and
                    str.toUpper().indexOf(text_under_cursor.toUpper()) > 0):
                completion_list_not_start_with.append(str)
        return completion_list + completion_list_not_start_with

    def show_completer(self, select_first):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        completion_words = self.get_text_completion_list()

        QApplication.restoreOverrideCursor()

        self.model_completer.setStringList(completion_words)

        cr = self.cursorRect()
        width = (self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        cr.setWidth(width if width < 300 else 300)
        self.completer.complete(cr)
        if select_first:
            self.completer.popup().setCurrentIndex(
                            self.completer.completionModel().index(0, 0))

    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def insert_completion(self, completion_text):
        if (self.completer.widget() != self):
            return
        tc = self.textCursor()
        tc.movePosition(QTextCursor.EndOfWord)
        tc.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor,
                        self.text_under_cursor().length())
        tc.removeSelectedText()
        tc.insertText(completion_text)
        self.setTextCursor(tc)


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
        else:
            cursor = self.textCursor()
            dist_prev_tab = cursor.positionInBlock() % 4
            if dist_prev_tab == 0:
                dist_prev_tab = 4
            cursor.setPosition(cursor.position() - dist_prev_tab,
                                       QTextCursor.KeepAnchor)
            if str(cursor.selectedText()).strip() == "":
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
            tc2.movePosition(QTextCursor.EndOfBlock)
            self.setTextCursor(tc2)


if(__name__ == '__main__'):
    def test_with_hightlight():
        """simple test"""
        from PyQt4.QtGui import QApplication
        from Mixin import mixin

        app = QApplication([])
        widget = mixin(QPlainTextEdit,
                       WithHighlight,
                       WithFixedFont)()
        widget.show()
        app.exec_()

    def test_with_linenumber_and_word_completion():
        """simple test"""
        from PyQt4.QtGui import QApplication
        from Mixin import mixin

        app = QApplication([])
        widget = mixin(QPlainTextEdit,
                       WithHighlight,
                       WithFixedFont,
                       WithLineNumbers,
                       WithWordCompletion,
                       WithBasicIdentationManager)()
        widget.show()
        app.exec_()

    #test_with_hightlight()
    test_with_linenumber_and_word_completion()
