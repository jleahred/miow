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
from  core.MqEdit import (WithLineHighlight,
                          WithFixedFont,
                          WithLineNumbers,
                          WithViewPortMargins,
                          WithBasicIdentationManager)

from core.Completion import (WithCompletion,
                             WithWordCompletionMulty_)
from core.MqEditIO import WithMqEditIO

from core.SingleIO import WithSingleIO
from core.highlighters.MqHighlight import  WidthMqHighlighter
from core.MqEditFind import WithFind


import os

TEMP_DIR= '/tmp/miow/'


class AsciidocEditor(WithSingleIO, QWidget):
    """Asciidoc editor
    """

    def __init__(self, params, parent=None):
        self.base_dir = os.path.dirname(__file__)
        QWidget.__init__(self, parent)

        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        # create widgets
        self._editor_widget = mixin(
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
                ("generate preview asciidoc",    "pp", 1.0, "self.get_current_widget().command_generate_preview('asciidoc -a data-uri -a icons  -a iconsdir="+self.base_dir+"/adoc/icons/')"),
                ("generate preview asciidoc style_sheet no images embeded",    "pp", 1.0, "self.get_current_widget().command_generate_preview('asciidoc --attribute  stylesheet="+self.base_dir+"/adoc/mq_red.css  -a icons  -a iconsdir="+self.base_dir+"/adoc/icons/')"),
                ("generate preview asciidoc style_sheet",    "pp", 1.2, "self.get_current_widget().command_generate_preview('asciidoc --attribute  stylesheet="+self.base_dir+"/adoc/mq_red.css    -a data-uri -a icons  -a iconsdir="+self.base_dir+"/adoc/icons/')"),
                ("generate preview slidy", "pp slides", 0.8, "self.get_current_widget().command_generate_preview('asciidoc  -b slidy    -a data-uri -a icons')"),
                ("generate preview slidy2", "pp slides", 0.9, "self.get_current_widget().command_generate_preview('asciidoc  -b slidy2    -a data-uri -a icons')"),
                ("generate preview asciidoctor", "pp", 0.7, "self.get_current_widget().command_generate_preview('asciidoctor  -a data-uri -a icons')"),
                ("generate preview deck.js", "pp slides", 0.7, "self.get_current_widget().command_generate_preview('asciidoc  -b deckjs    -a data-uri -a icons')"),

                ("generate pdf small", "", 0., """self.get_current_widget().command_generate_document('a2x --verbose -d article --icons --dblatex-opts "-T native -P doc.pdfcreator.show=0 -P doc.collab.show=0 -P latex.output.revhistory=0 -P doc.toc.show=1 -P table.title.top" -f pdf  -D /tmp/adoc/ ')"""),
                ("generate pdf book", "", 0., """self.get_current_widget().command_generate_document('a2x --verbose -d book --icons --dblatex-opts "-T native -P doc.pdfcreator.show=0 -P doc.collab.show=0 -P latex.output.revhistory=0 -P doc.toc.show=1 -P table.title.top" -f pdf  -D /tmp/adoc/ ')"""),
               ]
        super(AsciidocEditor, self).bw_add_command_list(command_list)
        self._editor_widget.bw_add_command_list(command_list)
        command_list += [
                    ("focus editor",    "fe", 0.5, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self._editor_widget.setFocus();"),
                    ("focus preview",    "fp", 0.5, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.webview.setFocus();"),

                    ("increase font webview",    "if if", 0.7, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.webview.setTextSizeMultiplier(_self.webview.textSizeMultiplier()+0.1);"),
                    ("decrease font webview",    "df df", 0.7, 
                     "import ctypes; _self = ctypes.cast(" + str(id(self)) + ", ctypes.py_object).value;"
                     "_self.webview.setTextSizeMultiplier(_self.webview.textSizeMultiplier()-0.1);"),
            ]


    def command_generate_preview(self, adoc_command):
        self.command_save_file()
        if not os.path.exists(TEMP_DIR):
            os.mkdir(TEMP_DIR)
        temp_source_file = open(TEMP_DIR + 'pr.adoc','wt')
        temp_source_file.write(self._editor_widget.toPlainText().toUtf8())
        temp_source_file.close()
        #self.compile(backend + " -b deckjs  -o " + self.get_html_output() + "  " + TEMP_DIR + "pr.adoc")
        #asciidoc --verbose -a data-uri -a icons -a toc -a max-width=55em -o __builds/index.html /home/maiquel/Documents/qadoc/adoc/index.adoc
        #self.compile(adoc_command + " --attribute  stylesheet=/home/maiquel/inet.prj/miow/widgets/adoc/mq_red.css    -a data-uri -a icons  -o " + self.get_html_output() + "  " + TEMP_DIR + "pr.adoc")
        self.compile(adoc_command + ' -o ' +self.get_html_output() + "  " + TEMP_DIR + "pr.adoc")
        if self.webview.url() != QUrl("file://" + self.get_html_output()):
            self.webview.load(QUrl(self.get_html_output()))

    def command_generate_document(self, adoc_command):
        self.command_save_file()
        if not os.path.exists(TEMP_DIR):
            os.mkdir(TEMP_DIR)
        temp_source_file = open(TEMP_DIR + 'pr.adoc','wt')
        temp_source_file.write(self._editor_widget.toPlainText().toUtf8())
        temp_source_file.close()
        self.compile(adoc_command + "  " + TEMP_DIR + "pr.adoc")
        if self.webview.url() != QUrl("file://" + self.get_html_output()):
            self.webview.load(QUrl(self.get_html_output()))

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
        self.log(result)

    def proc_compile_readyReadStandardError(self):
        result = str(self.proc_compile.readAllStandardError())
        self.log(result)

    def log(self, text):
        self.log_widget.appendPlainText(unicode(text))


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = AsciidocEditor(None)
        widget._editor_widget.setPlainText("""\
deck.js Support for Asciidoc
=============================
:author: Foo Bar
:email: <foo@bar.org>
:description: just a template file.
:revdate: 2011-12-16
:revnumber: 0.1
///////////////////////
	Themes that you can choose includes:
	web-2.0, swiss, neon beamer
///////////////////////
:deckjs_theme: swiss
///////////////////////
	Transitions that you can choose includes:
	fade, horizontal-slide, vertical-slide
///////////////////////
:deckjs_transition: vertical-slide
///////////////////////
	AsciiDoc use `source-highlight` as default highlighter.

	Styles available for pygment highlighter:
	monokai, manni, perldoc, borland, colorful, default, murphy, vs, trac,
	tango, fruity, autumn, bw, emacs, vim, pastie, friendly, native,

	Uncomment following two lines if you want to highlight your code
	with `Pygments`.
///////////////////////
//:pygments:
//:pygments_style: native
///////////////////////
	Uncomment following line if you want to scroll inside slides
	with {down,up} arrow keys.
///////////////////////
:scrollable:
///////////////////////
	Uncomment following line if you want to link css and js file 
	from outside instead of embedding them into the output file.
///////////////////////
//:linkcss:
///////////////////////
	Uncomment following line if you want to count each incremental
	bullet as a new slide
///////////////////////
//:count_nested:

== Slide One

[incremental="true"]
 * item 1
 * item 2

== Slide Two

That's all.
""")
        widget.show()
        widget.command_generate_preview("asciidoc")
        app.exec_()
    test()
