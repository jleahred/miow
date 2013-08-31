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


class SimpleEdit(QWidget):
    """SimpleEdit to test
    """

    def __init__(self, parent=None):
        super(SimpleEdit, self).__init__(parent)

        self.setMinimumWidth(100)
        self.setMinimumHeight(100)

        # create widgets
        self.editor = mixin(QPlainTextEdit,
                       WithHighlight,
                       WithFixedFont,
                       WithLineNumbers)(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.editor)
        layout.setMargin(0)
        self.setLayout(layout)

    def focusInEvent(self, focus_event):
        super(SimpleEdit, self).focusInEvent(focus_event)
        self.editor.setFocus()


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = SimpleEdit()
        widget.show()
        app.exec_()
    test()
