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
                          WithBasicIdentationManager)

from core.Completion import (WithCompletion,
                             WithWordCompletion)
from core.MqEditIO import WithMqEditIO

from core.SingleIO import WithSingleIO


import os

TEMP_DIR= '/tmp/miow/'


class AsciidocEditor(WithSingleIO, QWidget):
    """Asciidoc editor
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
                        WithWordCompletion,
                        WithCompletion,
                        QPlainTextEdit)(self)
        self.webview = QWebView(self)
        self.webview.load(QUrl("/home/maiquel/develop/developing/main/qt/qadoc/bin/__builds/documents.html"))
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
                ("generate preview asciidoc",    "", 0.0, "self.get_current_widget().command_generate_preview('asciidoc')"),
                ("generate preview asciidoctor", "", 0.0, "self.get_current_widget().command_generate_preview('asciidoctor')"),
               ]
        super(AsciidocEditor, self).bw_add_command_list(command_list)


    def command_generate_preview(self, backend):
        if not os.path.exists(TEMP_DIR):
            os.mkdir(TEMP_DIR)
        temp_source_file = open(TEMP_DIR + 'pr.adoc','wt')
        temp_source_file.write(str(self._editor_widget.toPlainText()))
        temp_source_file.close()
        self.compile(backend + "  -o " + self.get_html_output() + "  " + TEMP_DIR + "pr.adoc")

    def compile(self, command):
        self.log(command)
        self.proc_compile.start(command)


    def bw_lock_command_window(self):
        return self._editor_widget.completer.popup().isVisible()

    def focusInEvent(self, focus_event):
        super(AsciidocEditor, self).focusInEvent(focus_event)
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
        print(q_process_error)
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
        widget = AsciidocEditor(None)
        widget._editor_widget.setPlainText("""\
= Header
 * Testing
        """)
        widget.show()
        widget.command_generate_preview("asciidoc")
        app.exec_()
    test()
