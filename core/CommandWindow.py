# -*- coding: utf-8 -*-
"""CommandWindow component


"""

if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('..')
    sys.path.append(lib_path)


from PyQt4 import QtCore
from PyQt4.QtGui import (QFrame, QVBoxLayout, QLineEdit, 
                         QFont, QListWidget)





class CommandWindow(QFrame):
    """Miow main window
    """

    def __init__(self, parent=None):
        super(CommandWindow, self).__init__(parent)
        
        self.parent = parent
        self.setWindowFlags(QtCore.Qt.Popup)

        self.setFont(QFont("Monospace", 14))
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.setGeometry(0, 0, 600, 300)
        

        # create widgets
        layout = QVBoxLayout(self)
        self.line_edit = QLineEdit(self)
        layout.addWidget(self.line_edit)
        
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        layout.setMargin(0)
        self.setLayout(layout)
        self.line_edit.setFocus()

    def showEvent(self, event):
        geom = self.frameGeometry()
        #parent_widget = self.parentWidget()
        if self.parent:
            geom.moveCenter(QtCore.QPoint(self.parent.width()/2, 
                                                  self.parent.height()/3))
        self.setGeometry(geom)
        super(QFrame, self).showEvent(event)



if(__name__ == '__main__'):
    def test_gui():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = CommandWindow()
        widget.show()
        app.exec_()

    test_gui()
