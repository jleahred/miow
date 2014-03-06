"""Support to line highlight, line numbering...
"""

from PyQt4.QtCore import Qt, QRect

from PyQt4.QtGui import (QPlainTextEdit, QColor, QWidget,
                         QTextFormat, QTextCursor, QFont,
                         QPainter, QFrame, QLineEdit, QHBoxLayout)
                         
from MqEdit import  (WithHighlight, WithFixedFont, 
                    WithViewPortMargins, WithLineNumbers)


import re


class WithFind(QPlainTextEdit):
    """Mixin to add find command
    It requieres WithViewPortMargins"""

    class FindLine(QFrame):

        def __init__(self, edit):
            QWidget.__init__(self, edit)

            self.edit = edit
            
            layout = QHBoxLayout(self)

            self.find1 = QLineEdit(self)
            layout.addWidget(self.find1)
            self.find2 = QLineEdit(self)
            layout.addWidget(self.find2)
            
            layout.setMargin(0)
            layout.setSpacing(0)
            layout.setContentsMargins(0,0,0,0)
            self.setLayout(layout)
            self.find1.setFocus()
            self.setBackgroundRole


        def paintEvent(self, event):
            painter = QPainter(self)
            painter.fillRect(event.rect(), QColor(230, 230, 255))
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
        self.layout.addWidget(self.find_line)
        self.setFrameStyle(QFrame.NoFrame)
        self.updateRequest.connect(self.find_line.updateContents)
        self.__adjust_height()

    def __adjust_height(self):
        height = self.find_line.adjustHeight()
        super(WithFind, self).set_viewport_margins("WithFind", 
                                (0, 0, 0, self.find_line.find1.height()))


    def resizeEvent(self, resize_event):
        pass
        super(WithFind, self).resizeEvent(resize_event)
        super(WithFind, self).get_viewport_margins()
        #self.find_line.setGeometry(QRect(self.viewport().width()/3, 
        #                               0, #self.viewport().height(), 
        #                               self.viewport().width()*2/3, 
        #                               self.find_line.find1.height()-4))
        self.find_line.setGeometry(QRect(0, 
                                       self.viewport().height(), 
                                       self.viewport().width(), 
                                       self.find_line.find1.height()-8))




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
