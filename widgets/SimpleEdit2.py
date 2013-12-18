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
                          WithLineNumbers)

from core.Completion import (WithCompletion, WithWordCompletion)
from core.BaseWidget import BaseWidget


class SimpleEdit2(BaseWidget, QWidget):
    """SimpleEdit2 to test
    """

    def __init__(self, params, parent=None):
        super(SimpleEdit2, self).__init__(parent)

        self.setMinimumWidth(100)
        self.setMinimumHeight(100)

        # create widgets
        self.editor = mixin(
                       WithFixedFont,
                       WithHighlight,
                       WithLineNumbers,
                       WithWordCompletion,
                       WithCompletion,
                       QPlainTextEdit)(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.editor)
        layout.setMargin(0)
        self.setLayout(layout)

    def lock_command_window(self):
        return self.editor.completer.popup().isVisible()

    def focusInEvent(self, focus_event):
        super(SimpleEdit2, self).focusInEvent(focus_event)
        self.editor.setFocus()


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = SimpleEdit2(None)
        widget.show()
        app.exec_()
    test()
