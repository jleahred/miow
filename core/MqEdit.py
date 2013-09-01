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
    """Mixin to add simple word completion to QPlainTextEdit"""
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
                             Qt.Key_Backtab]):
                event.ignore()
                return  # let the completer do default behavior

        super(WithWordCompletion, self).keyPressEvent(event)
        if((event.modifiers() | event.key()) == QKeySequence("Ctrl+Space")):
            self.show_completer()
        else:
            pressed_key_as_string = QKeySequence(event.key()).toString()
            text_under_cursor = self.text_under_cursor()
            if(text_under_cursor.size() > 2  and
                    ((event.text() != ""
                    and re.match("^[A-Za-z0-9_-]*$", pressed_key_as_string[0]))
                    or  self.completer.popup().isVisible())):
                self.show_completer()
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

    def show_completer(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        completion_words = self.get_text_completion_list()

        QApplication.restoreOverrideCursor()

        self.model_completer.setStringList(completion_words)

        cr = self.cursorRect()
        width = (self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        cr.setWidth(width if width < 300 else 300)
        self.completer.complete(cr)
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
                       WithWordCompletion)()
        widget.show()
        app.exec_()

    #test_with_hightlight()
    test_with_linenumber_and_word_completion()
