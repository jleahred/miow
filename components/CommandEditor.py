# -*- coding: utf-8 -*-
"""Command editor component
"""

if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('..')
    sys.path.append(lib_path)


from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QSplitter, QVBoxLayout, QPlainTextEdit

from misc.Mixin import mixin
from components.edit.MqEdit import WithHighlight, WithFixedFont


class CommandEditor(QWidget):
    """Command editor component
    """
    def __init__(self, parent=None):
        super(CommandEditor, self).__init__(parent)

        self.setMinimumWidth(400)
        self.setMinimumHeight(100)

        # create widgets
        command_editor = mixin(QPlainTextEdit,
                               WithHighlight,
                               WithFixedFont)(self)
        command_result = mixin(QPlainTextEdit, WithFixedFont)(self)

        # create a horizontal splitter
        v_splitter = QSplitter(Qt.Horizontal, self)
        v_splitter.addWidget(command_editor)
        v_splitter.addWidget(command_result)

        layout = QVBoxLayout(self)
        layout.addWidget(v_splitter)
        layout.setMargin(0)
        self.setLayout(layout)


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = CommandEditor()
        widget.show()
        app.exec_()
    test()
