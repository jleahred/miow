"""Support to line highlight, line numbering...
"""

from PyQt4.QtCore import Qt, QRect

from PyQt4.QtGui import (QPlainTextEdit, QColor, QWidget,
                         QTextFormat, QTextCursor, QFont,
                         QPainter, QFrame, QLineEdit)
                         
from MqEdit import  (WithHighlight, WithFixedFont, 
                    WithViewPortMargins, WithLineNumbers)


import re


class WithFind(QPlainTextEdit):
    """Mixin to add find command
    It requieres WithViewPortMargins"""

    class FindLine(QWidget):

        def __init__(self, edit):
            QWidget.__init__(self, edit)

            self.edit = edit
            self.find1 = QLineEdit(self)


        def paintEvent(self, event):
            self.find_line_paint(self, event)
            QWidget.paintEvent(self, event)

        def adjustHeight(self):
            height = self.fontMetrics().height()
            if self.height() != height:
                self.setFixedHeight(height)
                #self.find1.setFixedHeight(height)
            return self.height()

        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update()

        def find_line_paint(self, number_bar, event):
            painter = QPainter(number_bar)
            painter.fillRect(event.rect(), QColor(230, 230, 255))
            painter.end()

    def __init__(self, *args):
        self.find_line = self.FindLine(self)
        self.setFrameStyle(QFrame.NoFrame)
        self.updateRequest.connect(self.find_line.updateContents)
        self.__adjust_height()

    def __adjust_height(self):
        #height = self.find_line.adjustHeight()
        #height = self.find_line.find1.height()
        super(WithFind, self).set_viewport_margins("WithFind", 
                                (0, 0, 0, self.find_line.find1.height()-4))


    def resizeEvent(self, resize_event):
        super(WithFind, self).resizeEvent(resize_event)
        self.find_line.setGeometry(QRect(0, 
                                       self.height()-self.find_line.find1.height(), 
                                       self.width(), self.find_line.find1.height()))





if(__name__ == '__main__'):
    def test_with_find():
        """simple test"""
        from PyQt4.QtGui import QApplication
        from Mixin import mixin

        app = QApplication([])
        widget = mixin(
                       WithFind,
                       WithLineNumbers,
                       WithViewPortMargins,
                       WithHighlight,
                       WithFixedFont,
                       QPlainTextEdit)()
        widget.show()
        app.exec_()


    test_with_find()
