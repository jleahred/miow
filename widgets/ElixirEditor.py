# -*- coding: utf-8 -*-
"""
@author: maiquel
"""


if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('..')
    sys.path.append(lib_path)

import os

from  PyQt4.QtGui import(QWidget,
                         QPlainTextEdit,
                         QVBoxLayout,
                         QSplitter,
                         QTabWidget)

from  PyQt4.QtCore import (Qt,
                           QString)
                           
from core.console.pyqterm import TerminalWidget
                           


from  core.Mixin import mixin


from  core.MqEdit import (WithLineHighlight,
                          WithFixedFont,
                          WithLineNumbers,
                          WithViewPortMargins,
                          WithBasicIdentationManager)

from core.Completion import (WithCompletion,
                             WithWordCompletionMulty_)
from core.MqEditIO import WithMqEditIO
from core.BaseWidget import BaseWidget
from core.SingleIO import WithSingleIO

from core.highlighters.MqHighlight import  WidthMqHighlighter
from core.MqEditFind import WithFind




class ElixirEditor(BaseWidget, QWidget):
    """Elixir editor
    """

    def __init__(self, params, parent=None):
        self.base_dir = os.path.dirname(__file__)
        QWidget.__init__(self, parent)

        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        # create widgets
        self.terminal_a = TerminalWidget(self)
        self.terminal_b = TerminalWidget(self)
        self.terminal_a.set_font_size(15)
        self.terminal_b.set_font_size(15)
        
        self.splitter_main = QSplitter(Qt.Horizontal)
        self._tab_editor = QTabWidget(self)
        self._tab_editor.setTabPosition(QTabWidget.South)
        self._tab_editor.setMovable(True)
        self.splitter_main.addWidget(self._tab_editor)

        self.splitter_terminal = QSplitter(Qt.Vertical)
        self.splitter_terminal.addWidget(self.terminal_a)
        self.splitter_terminal.addWidget(self.terminal_b)
        
        self.splitter_main.addWidget(self.splitter_terminal)
        self.splitter_main.setSizes([self.width()/2, self.width()/2])

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter_main)
        layout.setMargin(0)
        self.setLayout(layout)

        #WithSingleIO.__init__(self, params)
        self.go_file("pr.ex")


    def bw_add_command_list(self, command_list):
        super(ElixirEditor, self).bw_add_command_list(command_list)
        if self._tab_editor.currentWidget()>=0:
            self._tab_editor.currentWidget().bw_add_command_list(command_list)
        command_list += [
                    ("focus editor",     "fe fe", 0.5, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.focus_editor()"),
                    ("focus console a",    "fc", 1.5, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.terminal_a.setFocus();"),
                    ("focus console b",    "fcb", 1, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.terminal_b.setFocus();"),

                    ("increase font console",    "ifc", 0.7, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.terminal_a.set_font_size("+ str(self.terminal_a.get_font_size()+2) +");"
                     "_self.terminal_b.set_font_size("+ str(self.terminal_b.get_font_size()+2) +");"
                     ),
                    ("decrease font console",    "dfc", 0.7, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.terminal_a.set_font_size("+ str(self.terminal_a.get_font_size()-2) +");"
                     "_self.terminal_b.set_font_size("+ str(self.terminal_b.get_font_size()-2) +");"
                     ),
            ]
        try:
            self.focus().bw_add_command_list(self, command_list)
        except:
            pass


    def focus_editor(self):
        if self._tab_editor.currentIndex >=0:
            self._tab_editor.currentWidget().setFocus()

    def bw_lock_command_window(self):
        if self._tab_editor.currentIndex() >=0:
            return self._tab_editor.currentWidget().completer.popup().isVisible()
        else:
            return False

    def log(self, text):
        self.log_widget.appendPlainText(unicode(text))
        
    def go_file(self, file_name):
        _editor_widget = mixin(
                        WithFind,
                        WidthMqHighlighter,
                        WithMqEditIO,
                        WithBasicIdentationManager,
                        WithLineHighlight,
                        WithFixedFont,
                        WithLineNumbers,
                        WithViewPortMargins,
                        WithWordCompletionMulty_,
                        WithCompletion,
                        QPlainTextEdit)(self._tab_editor)
        self._tab_editor.addTab(_editor_widget, file_name)
        


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        elixir_editor = ElixirEditor(None)
        elixir_editor.go_file("pr.ex")
        elixir_editor.go_file("pr.ex")
        elixir_editor.show()
        app.exec_()
    test()
