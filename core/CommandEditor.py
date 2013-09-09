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


CURRENT_WIDGET = None

START_COMMANDS = """\
from core.CommandEditorCommands import (h, clear, reset)

h()
"""

WELLCOME_MESSAGE = """\
Wellcome to myow... CommandEditor
=================================


"""


class CommandEditor(QWidget):
    """Command editor component
    """

    class Interpreter():
        def __init__(self):
            self.ii = code.InteractiveConsole()

        def _process_commands(self, commands):
            def process_command(self, command):
                result = []
                partial = False
                backup_out = sys.stdout
                sys.stdout = StringIO()      # capture output
                backup_error = sys.stderr
                sys.stderr = StringIO()

                out = ""
                error = ""
                try:
                    partial = self.ii.push(command)
                    out = sys.stdout.getvalue()
                    error = sys.stderr.getvalue()
                except Exception as _error:
                    result.append(str(_error))
                sys.stdout = backup_out          # restore original stdout
                sys.stderr = backup_error
                result.append(out)
                if(error):
                    result.append(error)
                return result, partial

            results = []
            partial = False
            for command in commands.splitlines():
                c_result, partial = process_command(self, command)
                results += c_result
            return results, partial

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
                    super(CommandEditor.WidthLineEnterEvent,
                                              self).keyPressEvent(event)
                self.on_line_event(line)
            else:
                super(CommandEditor.WidthLineEnterEvent,
                                              self).keyPressEvent(event)

    def __init__(self, parent=None):
        super(CommandEditor, self).__init__(parent)
        import core.CommandEditorCommands
        core.CommandEditorCommands.EVENT_COMMAND_CLEAR += self.clear
        core.CommandEditorCommands.EVENT_COMMAND_RESET += self.reset

        self.setMinimumWidth(400)
        self.setMinimumHeight(100)

        # create widgets
        self.command_editor = mixin(
                               WithBasicIdentationManager,
                               CommandEditor.WidthLineEnterEvent,
                               WithHighlight,
                               WithFixedFont,
                               QPlainTextEdit)(self)
        self.command_editor.on_line_event += self._on_line_event
        self.command_result = mixin(WithFixedFont, QPlainTextEdit)(self)
        self.command_result.appendPlainText(WELLCOME_MESSAGE)

        # create a horizontal splitter
        v_splitter = QSplitter(Qt.Horizontal, self)
        v_splitter.addWidget(self.command_editor)
        v_splitter.addWidget(self.command_result)

        layout = QVBoxLayout(self)
        layout.addWidget(v_splitter)
        layout.setMargin(0)
        self.setLayout(layout)

        self.interpreter = CommandEditor.Interpreter()
        self.previous_partial = False
        self._on_line_event(START_COMMANDS)
        global CURRENT_WIDGET
        CURRENT_WIDGET = self

    def clear(self):
        """\
It will delete the result console"""
        self.command_result.clear()

    def reset(self):
        self.interpreter = CommandEditor.Interpreter()

    def focusInEvent(self, focus_event):
        super(CommandEditor, self).focusInEvent(focus_event)
        self.command_editor.setFocus()

    def _on_line_event(self, line):
        results, partials = self.interpreter._process_commands(line)

        if not partials or not self.previous_partial:
            self.command_result.appendPlainText(
                                "__________________________________________")
            self.command_result.appendPlainText(">>> " + line)
            for lines in results:
                for line in lines.splitlines():
                    self.command_result.appendPlainText(unicode(line))
            if not partials:
                self.command_result.appendPlainText("")
        else:
            self.command_result.appendPlainText("... " + line)
#==============================================================================
#         if(partials and not self.previous_partial
#                         and self.command_editor.textCursor().atBlockStart()):
#             self.command_editor.insert_tab()
#==============================================================================
        self.previous_partial = partials


if(__name__ == '__main__'):
    def test_gui():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = CommandEditor()
        widget.show()
        app.exec_()

    test_gui()
