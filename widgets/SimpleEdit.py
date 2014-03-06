# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 11:03:22 2013

@author: maiquel
"""


from  PyQt4.QtGui import(QPlainTextEdit)

if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('..')
    sys.path.append(lib_path)

from  core.MqEdit import (WithHighlight,
                          WithFixedFont,
                          WithViewPortMargins,
                          WithLineNumbers)

from core.MqEditIO import WithMqEditIO
from core.Completion import (WithCompletion,
                             WithWordCompletion)

from core.SingleIO import WithSingleIO


class SimpleEdit(WithSingleIO,
                 WithMqEditIO,
                 WithFixedFont,
                 WithHighlight,
                 WithLineNumbers,
                 WithViewPortMargins,
                 WithWordCompletion,
                 WithCompletion,
                 QPlainTextEdit,
                 ):
    """SimpleEdit to test
    """

    def __init__(self, params, parent=None):
        self._editor_widget = self
        QPlainTextEdit.__init__(self, parent)
        WithSingleIO.__init__(self, params)
        WithCompletion.__init__(self, parent)
        WithWordCompletion.__init__(self, parent)
        WithFixedFont.__init__(self, parent)
        WithViewPortMargins.__init__(self, parent)
        WithLineNumbers.__init__(self, parent)
        WithHighlight.__init__(self, parent)
        WithMqEditIO.__init__(self, params)

    def bw_lock_command_window(self):
        return self.completer.popup().isVisible()


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = SimpleEdit(None)

        widget.show()
        app.exec_()
    test()
