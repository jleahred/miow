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
        self.terminal = TerminalWidget(self)
        self.terminal.set_font_size(14)
        self.splitter = QSplitter(Qt.Horizontal)
        self._main_tab = QTabWidget(self)
        self._main_tab.setMovable(True)
        self.splitter.addWidget(self._main_tab)

        self.splitter.addWidget(self.terminal)
        self.splitter.setSizes([self.size().width(), self.size().width()])

        self.splitterv = QSplitter(Qt.Vertical)
        self.splitterv.addWidget(self.splitter)
        self.log_widget = QPlainTextEdit()
        self.splitterv.addWidget(self.log_widget)

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitterv)
        layout.setMargin(0)
        self.setLayout(layout)

        #WithSingleIO.__init__(self, params)
        self.open_file("pr.ex")


    def bw_add_command_list(self, command_list):
        #command_list += [
        #        ("generate preview asciidoc",    "pp", 1.0, "self.get_current_widget().command_generate_preview('asciidoc -a data-uri -a icons  -a iconsdir="+self.base_dir+"/adoc/icons/')"),
        #        ("generate preview asciidoc style_sheet no images embeded",    "pp", 1.0, "self.get_current_widget().command_generate_preview('asciidoc --attribute  stylesheet="+self.base_dir+"/adoc/mq_red.css  -a icons  -a iconsdir="+self.base_dir+"/adoc/icons/')"),
        #        ("generate preview asciidoc style_sheet",    "pp", 1.2, "self.get_current_widget().command_generate_preview('asciidoc --attribute  stylesheet="+self.base_dir+"/adoc/mq_red.css    -a data-uri -a icons  -a iconsdir="+self.base_dir+"/adoc/icons/')"),
        #        ("generate preview slidy", "pp slides", 0.8, "self.get_current_widget().command_generate_preview('asciidoc  -b slidy    -a data-uri -a icons')"),
        #        ("generate preview slidy2", "pp slides", 0.9, "self.get_current_widget().command_generate_preview('asciidoc  -b slidy2    -a data-uri -a icons')"),
        #        ("generate preview asciidoctor", "pp", 0.7, "self.get_current_widget().command_generate_preview('asciidoctor  -a data-uri -a icons')"),
        #        ("generate preview deck.js", "pp slides", 0.7, "self.get_current_widget().command_generate_preview('asciidoc  -b deckjs    -a data-uri -a icons')"),
#
        #        ("generate pdf small", "", 0., """self.get_current_widget().command_generate_document('a2x --verbose -d article --icons --dblatex-opts "-T native -P doc.pdfcreator.show=0 -P doc.collab.show=0 -P latex.output.revhistory=0 -P doc.toc.show=1 -P table.title.top" -f pdf  -D /tmp/adoc/ ')"""),
        #        ("generate pdf book", "", 0., """self.get_current_widget().command_generate_document('a2x --verbose -d book --icons --dblatex-opts "-T native -P doc.pdfcreator.show=0 -P doc.collab.show=0 -P latex.output.revhistory=0 -P doc.toc.show=1 -P table.title.top" -f pdf  -D /tmp/adoc/ ')"""),
        #       ]
        super(ElixirEditor, self).bw_add_command_list(command_list)
        if self._main_tab.currentWidget()>=0:
            self._main_tab.currentWidget().bw_add_command_list(command_list)
        command_list += [
                    ("focus editor",     "fe fe", 0.5, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.focus_editor()"),
                    ("focus console",    "fc fc fc", 0.5, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.terminal.setFocus();"),

                    ("increase font console",    "ifc ifc", 0.7, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.terminal.zoom_in();"),
                    ("decrease font console",    "dfc dfc", 0.7, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.terminal.zoom_out();"),
            ]


    def focus_editor(self):
        if self._main_tab.currentIndex >=0:
            self._main_tab.currentWidget().setFocus()

    def bw_lock_command_window(self):
        if self._main_tab.currentIndex() >=0:
            return self._main_tab.currentWidget().completer.popup().isVisible()
        else:
            return False

    #def focusInEvent(self, focus_event):
    #    super(ElixirEditor, self).focusInEvent(focus_event)
    #    if self._main_tab.currentIndex >= 0:
    #        self._main_tab.currentWidget().setFocus()

    def log(self, text):
        self.log_widget.appendPlainText(unicode(text))
        
    def open_file(self, file_name):
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
                        QPlainTextEdit)(self._main_tab)
        self._main_tab.addTab(_editor_widget, file_name)
        


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        elixir_editor = ElixirEditor(None)
        elixir_editor.open_file("pr.ex")
        elixir_editor.open_file("pr.ex")
        elixir_editor.show()
        app.exec_()
    test()
