"""Support to line highlight, line numbering...
"""

from PyQt4.QtCore import Qt, QRect

from PyQt4.QtGui import (QPlainTextEdit, QColor, QWidget,
                         QTextFormat, QTextCursor, QFont,
                         QPainter, QFrame, QLineEdit, QHBoxLayout,
                         QKeyEvent)

from  BaseWidget import BaseWidget

from MqEdit import  (WithHighlight, WithFixedFont, 
                    WithViewPortMargins, WithLineNumbers)


import re


class WithFind(BaseWidget):
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

        def __init__(self, edit):
            QWidget.__init__(self, edit)

            self.edit = edit
            
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
        self.find_line.setVisible(False)
        self.layout.addWidget(self.find_line)
        self.setFrameStyle(QFrame.NoFrame)
        self.updateRequest.connect(self.find_line.updateContents)
        self.updateRequest.connect(self.updateContents)
        self.__adjust_height()
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

    def show_find(self, show):
        self.find_line.setVisible(show)
        if self.find_line.isVisible():
            self.find_line.find1.setFocus()
        else:
            self.setFocus()
        self.__adjust_height()


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
        widget.setFocus()
        widget.show_find(True)
        #widget.show_find(False)
        app.exec_()


    test_with_find()