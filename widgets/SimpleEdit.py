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
                          WithLineNumbers)

from core.Completion import (WithCompletion,
                             WithWordCompletion)


class SimpleEdit(WithHighlight,
                 WithFixedFont,
                 WithLineNumbers,
                 WithWordCompletion,
                 WithCompletion,
                 QPlainTextEdit):
    """SimpleEdit to test
    """

    def __init__(self, parent=None):
        super(QPlainTextEdit, self).__init__(parent)
        super(WithCompletion, self).__init__(parent)
        super(WithWordCompletion, self).__init__(parent)
        super(WithLineNumbers, self).__init__(parent)
        super(WithFixedFont, self).__init__(parent)
        super(WithHighlight, self).__init__(parent)


if(__name__ == '__main__'):
    def test():
        """Isolated execution for testing"""
        from PyQt4.QtGui import QApplication

        app = QApplication([])
        widget = SimpleEdit()

        widget.show()
        app.exec_()
    test()
