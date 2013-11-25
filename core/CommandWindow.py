# -*- coding: utf-8 -*-
"""CommandWindow component


"""

if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('..')
    sys.path.append(lib_path)


from PyQt4 import QtCore
from PyQt4.QtCore import (Qt,
                          QEvent)
from PyQt4.QtGui import (QWidget, QFrame, QVBoxLayout, QLineEdit, 
                         QFont, QListWidget, QKeyEvent)





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
        
        self.line_edit.textChanged.connect(self.text_changed)
        self.line_edit.editingFinished.connect(self.editing_finished)
        

    def showEvent(self, event):
        geom = self.frameGeometry()
        #parent_widget = self.parentWidget()
        if self.parent:
            geom.moveCenter(QtCore.QPoint(self.parent.pos().x()+self.parent.width()/2, 
                                          self.parent.pos().y()+self.parent.height()/3))
            self.setGeometry(geom)
            self.command_list = self.parent.get_command_list()
            for command, tags in self.command_list:
                self.list_widget.addItem(command)
            super(QFrame, self).showEvent(event)

    def keyPressEvent(self, event):
        if event.type() == QEvent.KeyPress:
            key_event = QKeyEvent(event)
            if(key_event.key() == Qt.Key_Down
              or key_event.key() == Qt.Key_Up):
                return self.list_widget.keyPressEvent(event)
        return super(CommandWindow, self).keyPressEvent(event)

    def text_changed(self, text):
        print text

    def editing_finished(self):
        print "edited"



if(__name__ == '__main__'):
    from PyQt4.QtGui import QPushButton
    
    class MainWindow(QWidget):
        def __init__(self, parent=None):
            super(MainWindow, self).__init__(parent)
            self.button = QPushButton(self)
            self.setMinimumWidth(400)
            self.setMinimumHeight(300)
            self.setGeometry(100, 100, 600, 300)
            self.cw = CommandWindow(self)
            self.button.clicked.connect(self.on_click)
        def on_click(self):
            self.cw.show()
        
        def get_command_list(self):
            return [("command", ""),
                    ("do something", "great"),
                    ("boring", ""),
                    ("just", "an example"),
                    ]

    def test_gui():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        main = MainWindow()
        main.show()
        app.exec_()

    test_gui()
