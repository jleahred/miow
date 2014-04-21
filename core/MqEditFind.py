"""Support to line highlight, line numbering...
"""


if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('..')
    sys.path.append(lib_path)


import time

from PyQt4.QtCore import Qt, QRect, QRegExp, QTimer

from PyQt4.QtGui import (QPlainTextEdit, QColor, QWidget,
                         QTextFormat, QTextCursor, QFont,
                         QPainter, QFrame, QLineEdit, QHBoxLayout,
                         QKeyEvent, QSyntaxHighlighter, QTextCharFormat)

from  core.BaseWidget import BaseWidget

from core.MqEdit import  (WithLineHighlight, WithFixedFont, 
                    WithViewPortMargins, WithLineNumbers)


import re

from core.highlighters.MqHighlight import WidthMqHighlighter



class Highlighter_find(object):
    
    def __init__(self, highlighter):
        super(Highlighter_find, self).__init__()
        self.words = dict() # word, format
        self.highlighter = highlighter

        self.current_rehighlight_block = -1
        self.finish_rehighlight_block = -1
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_highlight)

    def update_word(self, index, word, _format):
        self.words[index] = (word, _format)

    def mq_highlightBlock(self, text):
        for index_words, pattern_format in self.words.items():
            pattern, _format = pattern_format
            if len(pattern)>0:
                expression = QRegExp(pattern)
                expression.setCaseSensitivity(False)
                index = expression.indexIn(text);
                while index >= 0:
                    length = expression.matchedLength()
                    if length == 0:
                        length = 1
                    self.highlighter.setFormat(index, length, _format)
                    index = expression.indexIn(text, index + length)

    def _check_highlight(self):
        t0 = time.clock()
        if self.current_rehighlight_block >= 0:
            counter = 0
            #for l in xrange(self.current_rehighlight_block, self.highlighter.document().blockCount()):
            while True:
                self.highlighter.rehighlightBlock(self.highlighter.document().findBlockByNumber(self.current_rehighlight_block))
                self.current_rehighlight_block += 1
                self.current_rehighlight_block %= self.highlighter.document().blockCount()

                if self.current_rehighlight_block == self.finish_rehighlight_block:
                    self.current_rehighlight_block = -1
                    self.timer.stop()
                    break
                
                counter += 1
                if counter > 20:
                    if time.clock() - t0 > 0.002:
                        break
                    else:
                        counter = 10
            
    def mq_rehighlight_all(self, current_block):
        current_block -= 100
        if current_block < 0:
            current_block = 0
        self.current_rehighlight_block = current_block
        self.finish_rehighlight_block = current_block
        if self.timer.isActive() == False:
            self.timer.start(10)
                    

class WithFind(WidthMqHighlighter, WithViewPortMargins, BaseWidget):
    """Mixin to add find command
    It requieres WithViewPortMargins"""

    class FindLine(QFrame):
        
        class QFind_line_edit(QLineEdit):
            def __init__(self, parent):
                super(WithFind.FindLine.QFind_line_edit, self).__init__(parent)
                self.next_widget = self
                self.prev_widget = self

            def keyPressEvent (self, event):  # QKeyEvent
                if event.key() == Qt.Key_Tab:
                    event.setAccepted(True)
                    self.next_widget.setFocus()
                    self.next_widget.selectAll()
                    return
                elif event.key() == Qt.Key_Backtab:
                    event.setAccepted(True)
                    self.prev_widget.setFocus()
                    self.prev_widget.selectAll()
                    return

                super(WithFind.FindLine.QFind_line_edit, 
                                          self).keyPressEvent(event)
                if not event.isAccepted():
                    event.setAccepted(True)
                    return
                    

        def __init__(self, edit):
            QWidget.__init__(self, edit)

            self.edit = edit
            self.find_highlighter = Highlighter_find(self.edit.highlighter)
            self.edit.highlighter._event += self.find_highlighter.mq_highlightBlock

            
            layout = QHBoxLayout(self)

            self.find1 = WithFind.FindLine.QFind_line_edit(self)
            layout.addWidget(self.find1)
            self.find2 = WithFind.FindLine.QFind_line_edit(self)
            layout.addWidget(self.find2)
            self.find3 = WithFind.FindLine.QFind_line_edit(self)
            layout.addWidget(self.find3)
            
            self.find1.next_widget = self.find2
            self.find2.next_widget = self.find3
            self.find3.next_widget = self.find1

            self.find1.prev_widget = self.find3
            self.find2.prev_widget = self.find1
            self.find3.prev_widget = self.find2
            
            self.find1.textChanged.connect(self.__text_changed)
            self.find2.textChanged.connect(self.__text_changed)
            self.find3.textChanged.connect(self.__text_changed)
            
            self.find1.setStyleSheet("background-color: rgb(255, 255, 220);")
            self.format1 = QTextCharFormat()
            self.format1.setBackground(QColor(255, 255, 180))
            
            self.find2.setStyleSheet("background-color: rgb(230, 255, 255);")
            self.format2 = QTextCharFormat()
            self.format2.setBackground(QColor(200, 255, 255))
            
            self.find3.setStyleSheet("background-color: rgb(230, 255, 230);")
            self.format3 = QTextCharFormat()
            self.format3.setBackground(QColor(200, 255, 200))

            self.format_selection = QTextCharFormat()
            self.format_selection.setBackground(QColor(200, 200, 250))
            
            layout.setMargin(0)
            layout.setSpacing(0)
            layout.setContentsMargins(0,0,0,0)
            self.setLayout(layout)
            self.find1.setFocus()
            

        def __text_changed(self, text):
            self.find_highlighter.update_word(3, self.find1.text(), self.format1)
            self.find_highlighter.update_word(2, self.find2.text(), self.format2)
            self.find_highlighter.update_word(1, self.find3.text(), self.format3)
            self.find_highlighter.mq_rehighlight_all(self.edit.textCursor().blockNumber())
            #self.edit.highlighter.rehighlight()
            #self.edit.find(text)
            #self.update_highlight()


        def paintEvent(self, event):
            painter = QPainter(self)
            painter.fillRect(event.rect(), QColor(230, 230, 230))
            painter.end()
            QFrame.paintEvent(self, event)
            
        def adjustHeight(self):
            height = self.fontMetrics().height()
            if self.height() != height:
                self.setFixedHeight(height)
                self.find1.setFixedHeight(height+3)
                self.setFixedHeight(self.find1.height())
                #self.find2.setFixedHeight(height+3)
            return self.height()

        def updateContents(self, rect, scroll):
            if scroll:
                #self.scroll(0, scroll)
                self.update()
            else:
                self.update()


    def __init__(self, *args):
        self.layout = QHBoxLayout(self)
        self.find_line = self.FindLine(self)
        self.find_line.setVisible(False)
        self.layout.addWidget(self.find_line)
        self.setFrameStyle(QFrame.NoFrame)
        self.updateRequest.connect(self.find_line.updateContents)
        self.updateRequest.connect(self.updateContents)
        self.__adjust_height()
        
        self.selectionChanged.connect(self.__on_selecction_changed)
        self.selection_highlight = True

        #BaseWidget.__init__(self, args)

    def __adjust_height(self):
        #height = self.find_line.adjustHeight()
        if self.find_line.isVisible():
            super(WithFind, self).set_viewport_margins("WithFind", 
                                    (0, 0, 0, self.find_line.find1.height()))
        else:
            super(WithFind, self).set_viewport_margins("WithFind", 
                                    (0, 0, 0, 0))


    def __adjust_geometry(self):
        margins = self.get_viewport_margins()
        geometry = QRect(margins[0], 
                                       self.viewport().height(), 
                                       self.viewport().width(), 
                                       self.find_line.find1.height())
        if geometry != self.find_line.geometry():
            self.find_line.setGeometry(geometry)

    def updateContents(self, rect, scroll):
        self.__adjust_geometry()
        
    def resizeEvent(self, resize_event):
        super(WithFind, self).resizeEvent(resize_event)
        self.__adjust_geometry()
        return
        self.find_line.setGeometry(QRect(0, 
                                       self.viewport().height(), 
                                       self.viewport().width(), 
                                       self.find_line.find1.height()))
        #super(WithFind, self).get_viewport_margins()
        #self.find_line.setGeometry(QRect(self.viewport().width()/3, 
        #                               0, #self.viewport().height(), 
        #                               self.viewport().width()*2/3, 
        #                               self.find_line.find1.height()-4))

    def bw_add_command_list(self, command_list):
        super(WithFind, self).bw_add_command_list(command_list)
        if self.hasFocus():
            command_list += [
                        ("find text",    "ff", 0.5, 
                         "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                         "_self.show_find(True);"),
                       ]
        if self.find_line.isVisible():
            command_list += [
                        ("hide find text",    "hf", 0.5, 
                         "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                         "_self.show_find(False);"),
                       ]
        command_list += [
                    ("clear finds",    "fc cf", 0.5, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.find_line.find1.setText('');"
                     "_self.find_line.find2.setText('');"
                     "_self.find_line.find3.setText('');"
                     ),
                   ]

    def show_find(self, show):
        self.find_line.setVisible(show)
        if self.find_line.isVisible():
            self.find_line.find1.setFocus()
        else:
            self.setFocus()
        self.__adjust_height()


    def __on_selecction_changed(self):
        selection = self.textCursor().selectedText()
        if len(selection) < 60  and  len(selection)>=1:
            self.find_line.find_highlighter.update_word(4, 
                                            self.textCursor().selectedText(), 
                                            self.find_line.format_selection)
            #self.highlighter.rehighlight()
            self.find_line.find_highlighter.mq_rehighlight_all(self.textCursor().blockNumber())
            self.selection_highlight = True
        elif self.selection_highlight == True:
            # remove selection
            self.find_line.find_highlighter.update_word(4, 
                                            "", 
                                            self.find_line.format_selection)
            self.selection_highlight = False
            #self.highlighter.rehighlight()
            self.find_line.find_highlighter.mq_rehighlight_all(self.textCursor().blockNumber())



if(__name__ == '__main__'):
    def test_with_find():
        """simple test"""
        from PyQt4.QtGui import QApplication
        from Mixin import mixin

        app = QApplication([])
        widget = mixin(
                       WithFind,
                       WidthMqHighlighter, 
                       WithLineNumbers,
                       WithViewPortMargins,
                       WithLineHighlight,
                       WithFixedFont,
                       QPlainTextEdit)()
        widget.show()
        widget.setFocus()
        widget.show_find(True)
        widget.setPlainText("""\
aaa bbb ccc ddd
bbb ccc ddd aaa
aaa.aaa
aaa aaa
aaaaaaaa""")
        widget.find_line.find1.setText("aaa")
        #widget.show_find(False)
        app.exec_()


    test_with_find()
