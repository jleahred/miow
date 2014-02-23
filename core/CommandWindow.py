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

from Event import Event




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

        self.line_edit.textChanged.connect(self.on_text_changed)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.event_selected_command = Event()


    def show_hide(self, context):
        if self.isVisible() == False or context is not None:        
            self.command_list = self.parent.get_command_list(context)
            self.filter_commands("")
            self.show()
        else:
            self.hide()

    def showEvent(self, event):
        geom = self.frameGeometry()
        self.line_edit.setFocus()
        self.line_edit.clear()
        #parent_widget = self.parentWidget()
        if self.parent:
            geom.moveCenter(QtCore.QPoint(self.parent.pos().x()+self.parent.width()/2,
                                          self.parent.pos().y()+self.parent.height()/3))
            self.setGeometry(geom)
            super(QFrame, self).showEvent(event)

    def _get_command_from_text(self, text):
        for command_text, tags, weight, command in self.command_list:
            if command_text == text:
                return command
        return None
        
    def keyPressEvent(self, event):
        if event.type() == QEvent.KeyPress:
            key_event = QKeyEvent(event)
            if(key_event.key() == Qt.Key_Down
              or key_event.key() == Qt.Key_Up):
                return self.list_widget.keyPressEvent(event)
            elif((event.key() == Qt.Key_Enter  or  event.key() == Qt.Key_Return)
                    and self.list_widget.currentItem().text()):
                self.hide()
                #self.event_selected_command(str(self.list_widget.currentItem().text()))
                self.event_selected_command(self._get_command_from_text(
                            str(self.list_widget.currentItem().text())))
        return super(CommandWindow, self).keyPressEvent(event)

    def on_item_double_clicked(self, item):
        self.hide()
        self.event_selected_command(str(self.list_widget.currentItem().text()))



    def filter_commands(self, text):
        self.list_widget.clear()
        text = str(text).upper()

        def get_item_map_def0(_map, key):
            if(_map.has_key(key)):
                return _map[key]
            else:
                return 0.

        def get_command_matches(command_list, words):
            result_map = {}
            for command, tags, _, _ in command_list:
                for word in words:
                    located_command_weight = 1
                    located_tag_weight = 0.3
                    if word == '':
                        located_command_weight = 0.
                        located_tag_weight = 0.
                    if command.upper().find(word) != -1:
                        result_map[command] = (get_item_map_def0(result_map,
                                                    command)
                                                    - located_command_weight)
                    for tag in tags.split(" "):
                        if tag.upper().find(word) != -1:
                            result_map[command] = (get_item_map_def0(result_map,
                                                    command)
                                                    - located_tag_weight)
            for command, _, current_weight, _ in command_list:
                if result_map.has_key(command):
                    result_map[command] -= current_weight
            return sorted(result_map, key=result_map.get)


        words = str(text).strip().split(" ")
        matches_map = get_command_matches(self.command_list, words)
        for command in matches_map:
            self.list_widget.addItem(command)
        self.list_widget.setCurrentRow(0)


    def on_text_changed(self, text):
        self.filter_commands(text)




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
            self.cw.event_selected_command += self.on_selected_command
            self.button.clicked.connect(self.on_click)
        def on_click(self):
            self.cw.show()

        def on_selected_command(self, command):
            print command

        def get_command_list(self):
            return [("command", "", 0.0, ""),
                    ("COMMAND", "", 0.0, ""),
                    ("do something", "great", 0.01, ""),
                    ("boring", "", 0.0, ""),
                    ("just", "an example", 0.0, ""),
                    ]

    def test_gui():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        main = MainWindow()
        main.show()
        app.exec_()

    test_gui()
