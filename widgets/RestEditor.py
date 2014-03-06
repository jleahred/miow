# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 09:43:28 2013

@author: maiquel
"""


from  PyQt4.QtGui import(QWidget,
                         QPlainTextEdit,
                         QVBoxLayout,
                         QSplitter)

from  PyQt4.QtWebKit import QWebView

from  PyQt4.QtCore import (Qt,
                           QUrl,
                           QProcess,
                           QString)

if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('..')
    sys.path.append(lib_path)

from  core.Mixin import mixin
from  core.MqEdit import (WithHighlight,
                          WithFixedFont,
                          WithLineNumbers,
                          WithViewPortMargins,
                          WithBasicIdentationManager)

from core.Completion import (WithCompletion,
                             WithWordCompletion)
from core.MqEditIO import WithMqEditIO

from core.SingleIO import WithSingleIO


import os

TEMP_DIR= '/tmp/miow/'


class RestEditor(WithSingleIO, QWidget):
    """Restructredtext editor
    """

    def __init__(self, params, parent=None):
        QWidget.__init__(self, parent)

        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        # create widgets
        self._editor_widget = mixin(
                        WithMqEditIO,
                        WithBasicIdentationManager,
                        WithHighlight,
                        WithFixedFont,
                        WithLineNumbers,
                        WithViewPortMargins,
                        WithWordCompletion,
                        WithCompletion,
                        QPlainTextEdit)(self)
        self.webview = QWebView(self)
        #self.webview.load(QUrl("/home/maiquel/develop/developing/main/qt/qadoc/bin/__builds/documents.html"))
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self._editor_widget)
        self.splitter.addWidget(self.webview)
        self.splitter.setSizes([self.size().width(), self.size().width()])

        self.splitterv = QSplitter(Qt.Vertical)
        self.splitterv.addWidget(self.splitter)
        self.log_widget = QPlainTextEdit()
        self.splitterv.addWidget(self.log_widget)

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitterv)
        layout.setMargin(0)
        self.setLayout(layout)

        # proc_compile
        self.proc_compile = QProcess()
        self.proc_compile.finished.connect(self.proc_compile_finished)
        self.proc_compile.error.connect(self.proc_compile_error)
        self.proc_compile.readyReadStandardOutput.connect(self.proc_compile_readyReadStandardOutput)
        self.proc_compile.readyReadStandardError.connect(self.proc_compile_readyReadStandardError)

        WithSingleIO.__init__(self, params)


    def bw_add_command_list(self, command_list):
        command_list += [
                ("generate preview restructuretext",    "pp", 1.0, "self.get_current_widget().command_generate_preview('rst2html')"),
               ]
        super(RestEditor, self).bw_add_command_list(command_list)


    def command_generate_preview(self, backend):
        self.command_save_file()
        if not os.path.exists(TEMP_DIR):
            os.mkdir(TEMP_DIR)
        temp_source_file = open(TEMP_DIR + 'pr.rst','wt')
        temp_source_file.write(self._editor_widget.toPlainText().toUtf8())
        temp_source_file.close()
        self.compile(backend + " --stylesheet=./widgets/rst2html.style " + TEMP_DIR + "pr.rst" + "   " + self.get_html_output())
        if self.webview.url() != QUrl("file://" + self.get_html_output()):
            self.webview.load(QUrl(self.get_html_output()))

    def compile(self, command):
        self.log(command)
        self.proc_compile.start(command)


    def bw_lock_command_window(self):
        return self._editor_widget.completer.popup().isVisible()

    def focusInEvent(self, focus_event):
        super(RestEditor, self).focusInEvent(focus_event)
        self._editor_widget.setFocus()

    def get_html_output(self):
        return TEMP_DIR + "pr.html"
    def proc_compile_finished(self, result, exit_status):
        self.log("compilation finished")
        if self.webview.url().toString() == "":
            self.webview.load(QUrl(self.get_html_output()))
        else:
            self.webview.reload()

    def proc_compile_error(self, q_process_error):
        self.log("compilation error")
        print q_process_error
    def proc_compile_readyReadStandardOutput(self):
        result = self.proc_compile.readAllStandardOutput();
        self.log(str(QString(result)))

    def proc_compile_readyReadStandardError(self):
        result = self.proc_compile.readAllStandardError();
        self.log(str(QString(result)))

    def log(self, text):
        self.log_widget.appendPlainText(text)


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = RestEditor(None)
        widget._editor_widget.setPlainText("""\
======
Header
======

* Testing
""")
        widget.show()
        widget.command_generate_preview("rst2html")
        app.exec_()
    test()
