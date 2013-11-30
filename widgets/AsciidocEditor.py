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
                           QUrl)

if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('..')
    sys.path.append(lib_path)

from  core.Mixin import mixin
from  core.MqEdit import (WithHighlight,
                          WithFixedFont,
                          WithLineNumbers)

from core.Completion import (WithWordCompletion)


class AsciidocEditor(QWidget):
    """Asciidoc editor
    """

    def __init__(self, parent=None):
        super(AsciidocEditor, self).__init__(parent)

        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        # create widgets
        self.editor = mixin(
                       WithHighlight,
                       WithFixedFont,
                       WithLineNumbers,
                       WithWordCompletion,
                       QPlainTextEdit)(self)
        self.webview = QWebView(self)
        self.webview.load(QUrl("/home/maiquel/develop/developing/main/qt/qadoc/bin/__builds/documents.html"))
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.webview)
        self.splitter.setSizes([self.size().width(), self.size().width()])

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)
        layout.setMargin(0)
        self.setLayout(layout)

    def focusInEvent(self, focus_event):
        super(AsciidocEditor, self).focusInEvent(focus_event)
        self.editor.setFocus()


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = AsciidocEditor()
        widget.show()
        app.exec_()
    test()
