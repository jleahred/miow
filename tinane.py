# -*- coding: utf-8 -*-
"""This Is Not An Editor
"""

from  components.CommandEditor import CommandEditor


if(__name__ == '__main__'):
    from PyQt4.QtGui import QApplication

    def test():
        """Isolated execution for testing"""
        app = QApplication([])
        widget = CommandEditor()
        widget.show()
        app.exec_()
    test()
