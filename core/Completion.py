# -*- coding: utf-8 -*-
"""
Adding completion


Created on Mon Sep 16 23:00:23 2013

@author: maiquel
"""


from PyQt4.QtCore import Qt, QRegExp

try:  
    from PyQt4.QtCore import QString  
except ImportError:  
    # we are using Python3 so QString is not defined  
    QString = str  

from PyQt4.QtGui import (QPlainTextEdit, QTextCursor,
                         QCompleter, QStringListModel,
                         QKeySequence,
                         QApplication, QCursor,
                         QFont)
import re


WORD_SYMBOLS = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZabcdefghijklmnñopqrstuvwxyz0123456789_ÁÉÍÓÚáéíóú'

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
        return []

    def __init__(self, *args):
        self.model_completer = QStringListModel()
        self.completer = QCompleter(self)
        self.completer.popup().setFont(QFont("Monospace", 11))
        #self.completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWrapAround(False)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setModel(self.model_completer)
        self.completer.activated.connect(self.insert_completion)

    def keyPressEvent(self, event):
        event_key = event.key()
        if (self.completer.popup().isVisible()):
            #The following keys are forwarded by the completer to the widget
            if(event_key in [Qt.Key_Enter,
                             Qt.Key_Return,
                             Qt.Key_Escape,
                             Qt.Key_Tab,
                             Qt.Key_Backtab]):
                if self.completer.popup().currentIndex().row() >= 0:
                    event.ignore()
                    return  # let the completer do default behavior
                else:
                    self.completer.popup().hide()

        super(WithCompletion, self).keyPressEvent(event)

        if((event.modifiers() | event.key()) == QKeySequence("Ctrl+Space")):
            self.show_completer(True)

        elif(event_key in [Qt.Key_Enter,
                             Qt.Key_Return,
                             Qt.Key_Escape,
                             Qt.Key_Tab,
                             Qt.Key_Backtab]):
            pass
        else:
            pressed_key_as_string = QKeySequence(event.key()).toString()
            word_till_cursor = self.word_till_cursor()
            if((len(word_till_cursor) > 2  or
                    (self.completer.popup().isVisible() and word_till_cursor.size() > 0))
                    and
                    ((event.text() != ""
                    and re.match("^[A-Za-z0-9_-]*$", pressed_key_as_string[0]))
                    or  self.completer.popup().isVisible())):
                self.show_completer(self.completer.popup()
                                                .currentIndex().row() >= 0)
            else:
                self.completer.popup().setCurrentIndex(
                            self.completer.completionModel().index(-1, 0))
                self.completer.popup().hide()

    def show_completer(self, select_first):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            completion_words = self.get_text_completion_list()
        except:
            completion_words = []
        print(completion_words)
        QApplication.restoreOverrideCursor()

        if not completion_words or len(completion_words) < 1:
            self.completer.popup().hide()
            return

        self.model_completer.setStringList(completion_words)

        cr = self.cursorRect()
        width = (self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        cr.setWidth(width if width < 300 else 300)
        self.completer.complete(cr)
        if select_first:
            self.completer.popup().setCurrentIndex(
                            self.completer.completionModel().index(0, 0))

    def word_under_cursor(self):
        result = ""
        for i in range(self.current_pos_init_of_word(), self.current_pos_end_of_word()):
            result = result + self.document().characterAt(i)
        return QString(result)

    def word_till_cursor(self):
        result = ""
        for i in range(self.current_pos_init_of_word(), self.textCursor().position()):
            result = result + self.document().characterAt(i)
        return QString(result)

    def current_pos_init_of_word(self):
        pos = self.textCursor().position()-1
        while True:
            char = self.document().characterAt(pos)
            if not char in WORD_SYMBOLS  or  pos<0:
            #if char=='\n' or re.match("^[A-Za-z0-9_-ñÑ]*$", unicode(char)) == None  or pos==0:
                break
            pos = pos - 1
        return pos+1

    def current_pos_end_of_word(self):
        pos = self.textCursor().position()
        while True:
            char = self.document().characterAt(pos)
            if not char in WORD_SYMBOLS  or pos==self.document().characterCount():
            #if char.isSpace() or re.match("^[A-Za-z0-9_-ñÑ]*$", unicode(char)) == None:
                break
            pos = pos + 1
        return pos

    def insert_completion(self, completion_text):
        if (self.completer.widget() != self):
            return
        tc = self.textCursor()
        till_pos = tc.position()
        tc.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, self.textCursor().position()-self.current_pos_init_of_word())
        #tc.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, self.current_pos_end_of_word()-self.current_pos_init_of_word())
        tc.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, till_pos - self.current_pos_init_of_word())
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
        word_till_cursor = self.word_till_cursor()
        word_under_cursor = self.word_under_cursor()
        words.removeDuplicates()
        words.sort()
        completion_list = []
        completion_list_not_start_with = []
        for word in words:
            if(word != word_till_cursor  and  word != word_under_cursor  and
                    word.toUpper().indexOf(word_till_cursor.toUpper()) == 0):
                completion_list.append(word)
            elif(word != word_till_cursor  and
                    word.toUpper().indexOf(word_till_cursor.toUpper()) > 0):
                completion_list_not_start_with.append(word)
        return (super(WithWordCompletion, self).get_text_completion_list()
                     + completion_list + completion_list_not_start_with)

class WithWordCompletionMulty_(QPlainTextEdit):
    """\
Mixin to add simple word completion multyword separated by _ to WithCompletion

It will propose completion with words from current document
"""
    def __init__(self, *args):
        pass

    def get_text_completion_list(self):
        print("----------------1")
        #words = self.toPlainText().split(QRegExp("[^a-zA-Z0-9_]"),
        #                         QString.SkipEmptyParts)
        print("----------------2")
        word_till_cursor = self.word_till_cursor()
        print("----------------3")
        word_under_cursor = self.word_under_cursor()
        print("----------------4")
        words.removeDuplicates()
        print("----------------5")
        words.sort()
        print("----------------6")
        completion_list = []
        completion_list_not_start_with = []
        print("----------------7")
        for word in words:
            print(word)
            if(word != word_till_cursor  and  word != word_under_cursor  and
                    word.toUpper().indexOf(word_till_cursor.toUpper()) == 0):
                completion_list.append(word)
            elif (word != word_till_cursor  and
                        len(word) > len(word_till_cursor)):
                words_till_cursor = [x for x in word_till_cursor.split("_")
                                if x!=""  and  len(x)>=2]
                matches = 0
                for word_tc in words_till_cursor:
                    if word.toUpper().find(word_tc.upper())>=0:
                        matches += 1
                if matches == len(words_till_cursor):
                    completion_list.append(word)
                elif matches*1.20 >= len(words_till_cursor):
                    completion_list_not_start_with.append(word)
        print(completion_list)
        return (super(WithWordCompletionMulty_, self).get_text_completion_list()
                     + completion_list + completion_list_not_start_with)



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

    def test_word_completion_multy():
        """simple test"""
        from PyQt4.QtGui import QApplication
        from Mixin import mixin

        app = QApplication([])
        widget = mixin(
                       WithWordCompletionMulty_,
                       WithCompletion,
                       QPlainTextEdit)()
        widget.show()
        app.exec_()

    #test_word_completion()
    test_word_completion_multy()