# -*- coding: utf-8 -*-
"""This Is Not An Editor
"""

from  PyQt4.QtGui import    QWidget, QSplitter, QVBoxLayout, QPlainTextEdit,\
                            QTabWidget
from  PyQt4.QtCore import Qt

from  components.CommandEditor import CommandEditor
from  components.edit.MqEdit import (WithHighlight,
                                     WithFixedFont,
                                     WithLineNumbers)
from  misc.Mixin import mixin


class MainWindow(QWidget):
    """Miow main window
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        # create widgets
        main_tab = QTabWidget(self)
        editor = mixin(QPlainTextEdit,
                       WithHighlight,
                       WithFixedFont,
                       WithLineNumbers)(main_tab)
        main_tab.addTab(editor, "testing")
        ce = CommandEditor(self)

        # create vertical splitter
        v_splitter = QSplitter(Qt.Vertical, self)
        v_splitter.addWidget(main_tab)
        v_splitter.addWidget(ce)
        v_splitter.setStretchFactor(0, 10)
        v_splitter.setStretchFactor(1, 3)

        layout = QVBoxLayout(self)
        layout.addWidget(v_splitter)
        layout.setMargin(0)
        self.setLayout(layout)
        main_tab.widget(0).setFocus()


if(__name__ == '__main__'):
    from PyQt4.QtGui import QApplication

    def main():
        """execute miow"""
        app = QApplication([])
        widget = MainWindow()
        widget.show()
        app.exec_()
    main()
