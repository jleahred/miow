# -*- coding: utf-8 -*-
"""
Adding completion


Created on Mon Sep 16 23:00:23 2013

@author: maiquel
"""


from PyQt4.QtCore import Qt, QString, QRegExp

from PyQt4.QtGui import (QPlainTextEdit, QTextCursor,
                         QCompleter, QStringListModel,
                         QKeySequence,
                         QApplication, QCursor)
import re


class WithCompletion(QPlainTextEdit):
    """\
Mixin to add base completion funtionallity to QPlainTextEdit

It will propose completion with words from current file

When the word you are writting is bigger than two, it will request for
possible completions but with no default selection.

If you press Ctrl-Space, the proposal will choose the first one as default

Specific mixings will have to implement the get_text_completion_list method
"""

    def get_text_completion_list(self):
        pass

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

        super(WithCompletion, self).keyPressEvent(event)
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


class WithWordCompletion(QPlainTextEdit):
    """\
Mixin to add simple word completion to WithCompletion

It will propose completion with words from current file
"""
    def __init__(self, *args):
        pass

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


if(__name__ == '__main__'):
    def test_word_completion():
        """simple test"""
        from PyQt4.QtGui import QApplication
        from Mixin import mixin

        app = QApplication([])
        widget = mixin(
                       WithWordCompletion,
                       WithCompletion,
                       QPlainTextEdit)()
        widget.show()
        app.exec_()

    test_word_completion()
