# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 11:03:22 2013

@author: maiquel
"""


from  PyQt4.QtGui import(QWidget,
                         QPlainTextEdit,
                         QVBoxLayout)

if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('..')
    sys.path.append(lib_path)

from  core.Mixin import mixin
from  core.MqEdit import (WithHighlight,
                          WithFixedFont,
                          WithViewPortMargins,
                          WithLineNumbers)
from core.MqEditIO import WithMqEditIO

from core.Completion import (WithCompletion, WithWordCompletion)
from core.SingleIO import WithSingleIO


class SimpleEdit2(WithSingleIO, QWidget):
    """SimpleEdit2 to test
    """

    def __init__(self, params, parent=None):
        super(QWidget, self).__init__(parent)

        self.setMinimumWidth(100)
        self.setMinimumHeight(100)

        # create widgets
        self._editor_widget = mixin(
                       WithMqEditIO,
                       WithFixedFont,
                       WithHighlight,
                       WithLineNumbers,
                       WithViewPortMargins,
                       WithWordCompletion,
                       WithCompletion,
                       QPlainTextEdit)(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self._editor_widget)
        layout.setMargin(0)
        self.setLayout(layout)

        WithSingleIO.__init__(self, params)

    def bw_lock_command_window(self):
        return self._editor_widget.completer.popup().isVisible()

    def focusInEvent(self, focus_event):
        super(SimpleEdit2, self).focusInEvent(focus_event)
        self._editor_widget.setFocus()


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = SimpleEdit2(None)
        widget.show()
        app.exec_()
    test()
