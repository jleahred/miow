# -*- coding: utf-8 -*-
"""Command editor component

TODO: control-enter to add new lines without sending command
TODO: multiexecution with several selected lines
TODO: if partial command, add identation on editor???
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
from MqEdit import(WithHighlight,
                   WithFixedFont,
                   WithBasicIdentationManager)

#WidthLineEnterEvent
from PyQt4.QtGui import (QTextCursor)

# Interpreter
import code
import sys
from cStringIO import StringIO


def h():
    print """\
This is the help
kkkkkkk"""


class Interpreter():
    def __init__(self):
        self.ii = code.InteractiveConsole()

    def process_command(self, command, result, partial):
        if command == '.reset':
            self.ii = code.InteractiveConsole()
        else:
            backup_out = sys.stdout
            sys.stdout = StringIO()      # capture output
            backup_error = sys.stderr
            sys.stderr = StringIO()

            out = ""
            error = ""
            try:
                partial.append(
                                    self.ii.push(command)
                              )
                out = sys.stdout.getvalue()
                error = sys.stderr.getvalue()
            except Exception as _error:
                result.append(str(_error))
            sys.stdout = backup_out          # restore original stdout
            sys.stderr = backup_error
            result.append(out)
            if(error):
                result.append(error)


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
            if self.textCursor().atBlockEnd():
                super(WidthLineEnterEvent, self).keyPressEvent(event)
            self.on_line_event(line)
        else:
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
                               WithBasicIdentationManager,
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

        self.interpreter = Interpreter()
        self.previous_partial = False

    def focusInEvent(self, focus_event):
        super(CommandEditor, self).focusInEvent(focus_event)
        self.command_editor.setFocus()

    def _on_line_event(self, line):
        results = []
        partials = []
        self.interpreter.process_command(line, results, partials)

        if not partials[0] or not self.previous_partial:
            self.command_result.appendPlainText(
                                "__________________________________________")
            self.command_result.appendPlainText(">>> " + line)
            for lines in results:
                for line in lines.splitlines():
                    self.command_result.appendPlainText(unicode(line))
            if not partials[0]:
                self.command_result.appendPlainText("")
        else:
            self.command_result.appendPlainText("... " + line)
#==============================================================================
#         if(partials[0] and not self.previous_partial
#                         and self.command_editor.textCursor().atBlockStart()):
#             self.command_editor.insert_tab()
#==============================================================================
        self.previous_partial = partials[0]


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = CommandEditor()
        widget.show()
        app.exec_()
    test()
