# -*- coding: utf-8 -*-
"""InterpreterEditor component

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

from Completion import WithCompletion, WithWordCompletion

from BaseWidget import BaseWidget



#WidthLineEnterEvent
from PyQt4.QtGui import (QTextCursor)

# InterpreterEditor
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


START_COMMANDS_GLOBAL = """\
from pprint import pprint

import core.InterpreterEditor
cw = CURRENT_WIDGET
mw = MAIN_WINDOW
app = APP

from core.InterpreterEditorCommands import (h, clear, reset)
h()

"""

START_COMMANDS_LOCAL = """\
from pprint import pprint

import core.InterpreterEditor

from core.InterpreterEditorCommands import (h, clear, reset)
h()

"""


START_COMMANDS_GLOBAL = """\
from pprint import pprint

import core.InterpreterEditor
cw = CURRENT_WIDGET
mw = MAIN_WINDOW
app = APP

from core.InterpreterEditorCommands import (h, clear, reset)
h()

"""



WELLCOME_MESSAGE = """\
Wellcome to myow... InterpreterEditor
=================================

    clear() to delete the result window
    reset() to restart the interpreter


    [enter]         to send a command (current "block")
    [ctrl+enter]    to create a new block
    [shift+enter]   to insert new line in same block



    only on global configuration
    --------------------------------
    CURRENT_WIDGET  is the working widget on miow
    MAIN_WINDOW     is the miow window
    APP             is the application
    --------------------------------


"""





class InterpreterEditor(BaseWidget, QWidget):
    """InterpreterEditor component
    """

    class Interpreter():
        def __init__(self, is_gobal):
            if is_gobal:
                self.ii = code.InteractiveConsole(globals())
            else:
                self.ii = code.InteractiveConsole(locals())

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
        """Mixin to add LineEnterEvent to QPlainTextEdit
           This method can cancel event propagation.
           Therefore, would be interesting have it at first position on
           mixing string
        """

        def __init__(self, *args):
            self.on_lines_event = Event()

        def keyPressEvent(self, event):
            if((event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return)
                    and (not event.modifiers()
                                or event.modifiers() == Qt.KeypadModifier)):
                tc = self.textCursor()
                cancel_key = False
                if len(tc.selectedText())==0:
                    tc.select(QTextCursor.BlockUnderCursor)
                else:
                    cancel_key = True

                if (len(tc.selectedText())>1 and
                            ord(unicode(tc.selectedText()[0])) == 8233):
                    lines = ''.join(unicode(tc.selectedText()[1:]).splitlines(True))
                else:
                    lines = ''.join(unicode(tc.selectedText()).splitlines(True))
                if(not cancel_key and self.textCursor().atBlockEnd()
                                                and  len(lines)>1):
                    super(InterpreterEditor.WidthLineEnterEvent,
                                              self).keyPressEvent(event)
                self.on_lines_event(lines)
            elif((event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return)
                    and (event.modifiers() == Qt.ControlModifier)):
                self.textCursor().insertBlock()
            else:
                super(InterpreterEditor.WidthLineEnterEvent,
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

            return (super(InterpreterEditor.WithInterpreterCompletion, self)
                        .get_text_completion_list()
                     + completion_list)

    def clear(self):
        """\
It will delete the result console"""
        self._result_widget.clear()

    def reset(self):
        self.interpreter = InterpreterEditor.Interpreter(self.is_global)
        self._editor_widget.event_wicompl_send_command_interpreter \
                                += self.interpreter._process_commands
        self.clear()
        #self._result_widget.appendPlainText(WELLCOME_MESSAGE)
        self.previous_partial = False
        if self.is_global:
            self._process_lines(START_COMMANDS_GLOBAL)
        else:
            self._process_lines(START_COMMANDS_LOCAL)

    def __init__(self, params, parent=None):
        super(InterpreterEditor, self).__init__(parent)

        self.is_global = False
        if not params is None:
            self.is_global = params["global"]
        import core.InterpreterEditorCommands
        core.InterpreterEditorCommands.EVENT_COMMAND_CLEAR += self.clear
        core.InterpreterEditorCommands.EVENT_COMMAND_RESET += self.reset

        self.setMinimumWidth(400)
        self.setMinimumHeight(100)

        # create widgets
        self._editor_widget = mixin(
                               InterpreterEditor.WithInterpreterCompletion,
                               WithWordCompletion,
                               WithCompletion,
                               InterpreterEditor.WidthLineEnterEvent,
                               WithBasicIdentationManager,
                               WithHighlight,
                               WithFixedFont,
                               QPlainTextEdit)(self)
        self._editor_widget.on_lines_event += self._process_lines
        self._result_widget = mixin(WithFixedFont, QPlainTextEdit)(self)

        # create a horizontal splitter
        v_splitter = QSplitter(Qt.Horizontal, self)
        v_splitter.addWidget(self._editor_widget)
        v_splitter.addWidget(self._result_widget)

        layout = QVBoxLayout(self)
        layout.addWidget(v_splitter)
        layout.setMargin(0)
        self.setLayout(layout)
        self.reset()

    def focusInEvent(self, focus_event):
        super(InterpreterEditor, self).focusInEvent(focus_event)
        self._editor_widget.setFocus()

    def _process_lines(self, lines):
        def process_line(line):
            results, partials = self.interpreter._process_commands(line)

            if len(line) or self.previous_partial:
                if not partials or not self.previous_partial:
                    self._result_widget.appendPlainText(
                                 "__________________________________________")
                    self._result_widget.appendPlainText(">>> " + unicode(line))
                    for lines in results:
                        for line in lines.splitlines():
                            self._result_widget.appendPlainText(unicode(line))
                    if not partials:
                        self._result_widget.appendPlainText("")
                else:
                    self._result_widget.appendPlainText("... " + unicode(line))
                self._result_widget.ensureCursorVisible()
#==============================================================================
#         if(partials and not self.previous_partial
#                        and self._editor_widget.textCursor().atBlockStart()):
#             self._editor_widget.insert_tab()
#==============================================================================
            self.previous_partial = partials

        for line in lines.splitlines() or ['']:
            process_line(line)

    @property
    def editor_widget(self):
        return self._editor_widget

    @property
    def result_widget(self):
        return self._result_widget

if(__name__ == '__main__'):
    def test_gui(params):
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = InterpreterEditor(params)
        widget.show()
        app.exec_()

    test_gui({"global": True})
    test_gui({"global": False})
