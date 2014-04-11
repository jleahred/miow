"""
Python highlighter
"""


if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('../..')
    sys.path.append(lib_path)


from PyQt4.QtGui import *
from PyQt4.QtCore import *


from core.Event import Event


class  WidthMqHighlighter(QPlainTextEdit):
    def __init__(self, *args):
        super(WidthMqHighlighter, self).__init__(*args)
        self.highlighter = MqHighlighter(self.document())


class MqHighlighter( QSyntaxHighlighter ):

    def __init__( self, parent):
        super(MqHighlighter, self).__init__( parent )
        #QSyntaxHighlighter.__init__( self, parent )
        self.parent = parent
        self._event = Event()

    def highlightBlock( self, text ):
        self._event(text)
