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

from Mixin import mixin
from Event import Event
from MqEdit import WithHighlight, WithFixedFont

#WidthLineEnterEvent
from PyQt4.QtGui import (QTextCursor)


class WidthLineEnterEvent(QPlainTextEdit):
    """Mixin to add LineEnterEvent to QPlainTextEdit"""

    def __init__(self, *args):
        self.on_line_event = Event()

    def keyPressEvent(self, event):
        if((event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return)
                and (not event.modifiers()
                            or event.modifiers() == Qt.KeypadModifier)):
            tc = self.textCursor()
            tc.select(QTextCursor.BlockUnderCursor)
            line = ''.join(unicode(tc.selectedText()).splitlines())
            self.on_line_event(line)
        super(WidthLineEnterEvent, self).keyPressEvent(event)


class CommandEditor(QWidget):
    """Command editor component
    """
    def __init__(self, parent=None):
        super(CommandEditor, self).__init__(parent)

        self.setMinimumWidth(400)
        self.setMinimumHeight(100)

        # create widgets
        self.command_editor = mixin(QPlainTextEdit,
                               WithHighlight,
                               WithFixedFont,
                               WidthLineEnterEvent)(self)
        self.command_editor.on_line_event += self._on_line_event
        self.command_result = mixin(QPlainTextEdit, WithFixedFont)(self)

        # create a horizontal splitter
        v_splitter = QSplitter(Qt.Horizontal, self)
        v_splitter.addWidget(self.command_editor)
        v_splitter.addWidget(self.command_result)

        layout = QVBoxLayout(self)
        layout.addWidget(v_splitter)
        layout.setMargin(0)
        self.setLayout(layout)

    def _on_line_event(self, line):
        self.command_result.appendPlainText(">>> " + line)


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = CommandEditor()
        widget.show()
        app.exec_()
    test()
