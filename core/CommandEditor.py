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

from Completion import WithCompletion


#WidthLineEnterEvent
from PyQt4.QtGui import (QTextCursor)

# Interpreter
import code
import sys
from cStringIO import StringIO

# completer
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import core.jedi
sys.path.pop(0)

MAIN_WINDOW = None
CURRENT_WIDGET = None
APP = None


START_COMMANDS = """\
from pprint import pprint

import core.CommandEditor
cw = core.CommandEditor.get_current_widget()
mw = core.CommandEditor.get_main_window()
app = core.CommandEditor.get_app()

from core.CommandEditorCommands import (h, clear, reset)
h()

"""

WELLCOME_MESSAGE = """\
Wellcome to myow... CommandEditor
=================================

    clear() to delete the result window
    reset() to restart the interpreter


    cw  gets the working widget on miow
    mw  gets the miow window
    app gets the QApplication


"""


def get_current_widget():
    return CURRENT_WIDGET


def get_main_window():
    return MAIN_WINDOW

def get_app():
    return APP


class CommandEditor(QWidget):
    """Command editor component
    """

    class Interpreter():
        def __init__(self):
            self.ii = code.InteractiveConsole(globals())

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
            for command in commands.splitlines() or ['']:
                c_result, partial = process_command(self, command)
                results += c_result
            return results, partial

    class WidthLineEnterEvent(QPlainTextEdit):
        """Mixin to add LineEnterEvent to QPlainTextEdit"""

        def __init__(self, *args):
            self.on_lines_event = Event()

        def keyPressEvent(self, event):
            if((event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return)
                    and (not event.modifiers()
                                or event.modifiers() == Qt.KeypadModifier)):
                tc = self.textCursor()
                tc.select(QTextCursor.BlockUnderCursor)
                lines = ''.join(unicode(tc.selectedText()).splitlines())
                if self.textCursor().atBlockEnd():
                    super(CommandEditor.WidthLineEnterEvent,
                                              self).keyPressEvent(event)
                self.on_lines_event(lines)
            else:
                super(CommandEditor.WidthLineEnterEvent,
                                              self).keyPressEvent(event)

    class WithInterpreterCompletion(QPlainTextEdit):
        """\
Mixin to add interpreter word completion to WithCompletion
"""
        def __init__(self, *args):
            pass

        event_wicompl_send_command_interpreter = Event()

        def get_text_completion_list(self):
            namespace = globals()
            QTextCursor.beginEditBlock
            cursor = self.textCursor()
            cursor.movePosition(cursor.StartOfBlock, QTextCursor.KeepAnchor)
            line_till_cursor = str(cursor.selectedText())

            script = core.jedi.api.Interpreter(line_till_cursor, [namespace])

            completion_list = []
            for completion in script.completions():
                completion_list.append(completion.name)

            return completion_list

    def clear(self):
        """\
It will delete the result console"""
        self.command_result.clear()

    def reset(self):
        self.interpreter = CommandEditor.Interpreter()
        self.command_editor.event_wicompl_send_command_interpreter \
                                += self.interpreter._process_commands
        self.clear()
        #self.command_result.appendPlainText(WELLCOME_MESSAGE)
        self.previous_partial = False
        self._process_lines(START_COMMANDS)

    def __init__(self, parent=None):
        super(CommandEditor, self).__init__(parent)
        import core.CommandEditorCommands
        core.CommandEditorCommands.EVENT_COMMAND_CLEAR += self.clear
        core.CommandEditorCommands.EVENT_COMMAND_RESET += self.reset

        self.setMinimumWidth(400)
        self.setMinimumHeight(100)

        # create widgets
        self.command_editor = mixin(
                               CommandEditor.WithInterpreterCompletion,
                               WithCompletion,
                               WithBasicIdentationManager,
                               CommandEditor.WidthLineEnterEvent,
                               WithHighlight,
                               WithFixedFont,
                               QPlainTextEdit)(self)
        self.command_editor.on_lines_event += self._process_lines
        self.command_result = mixin(WithFixedFont, QPlainTextEdit)(self)

        # create a horizontal splitter
        v_splitter = QSplitter(Qt.Horizontal, self)
        v_splitter.addWidget(self.command_editor)
        v_splitter.addWidget(self.command_result)

        layout = QVBoxLayout(self)
        layout.addWidget(v_splitter)
        layout.setMargin(0)
        self.setLayout(layout)
        self.reset()

    def focusInEvent(self, focus_event):
        super(CommandEditor, self).focusInEvent(focus_event)
        self.command_editor.setFocus()

    def _process_lines(self, lines):
        def process_line(line):
            results, partials = self.interpreter._process_commands(line)

            if len(line) or self.previous_partial:
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

        for line in lines.splitlines() or ['']:
            process_line(line)


if(__name__ == '__main__'):
    def test_gui():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = CommandEditor()
        widget.show()
        app.exec_()

    test_gui()
