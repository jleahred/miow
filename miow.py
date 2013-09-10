# -*- coding: utf-8 -*-
"""MY OWn...
"""

from  PyQt4.QtGui import(QWidget,
                         QSplitter,
                         QVBoxLayout,
                         QTabWidget)

from  PyQt4.QtCore import Qt

import core.CommandEditor
from  core.CommandEditor import CommandEditor


class MainWindow(QWidget):
    """Miow main window
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        # create widgets
        self.main_tab = QTabWidget(self)
        ce = CommandEditor(self)
        self.v_splitter = QSplitter(Qt.Vertical, self)
        self.v_splitter.addWidget(self.main_tab)
        self.v_splitter.addWidget(ce)
        layout = QVBoxLayout(self)
        layout.addWidget(self.v_splitter)
        layout.setMargin(0)
        self.setLayout(layout)
        ce.setFocus()

    def add_widget(self, widget_class, label="???"):
        """Add any kind of widget"""
        widget = widget_class(self.main_tab)
        self.main_tab.addTab(widget, label)
        if self.main_tab.count() == 1:
            #self.v_splitter.setStretchFactor(0, 10)
            #self.v_splitter.setStretchFactor(1, 3)
            total_size = sum(self.v_splitter.sizes())
            self.v_splitter.setSizes([total_size / 100 * 70,
                                      total_size / 100 * 30])
        widget.setFocus()
        core.CommandEditor.CURRENT_WIDGET = widget


if(__name__ == '__main__'):
    from PyQt4.QtGui import QApplication

    register_components = "from widgets.SimpleEdit import SimpleEdit"
    exec(register_components)

    def main():
        """execute miow"""

        import core.CommandEditor

        app = QApplication([])
        mainw = MainWindow()
        core.CommandEditor.MAIN_WINDOW = mainw
        mainw.show()
        #mainw.add_widget(SimpleEdit, "test1")
        #mainw.add_widget(SimpleEdit, "test2")

        app.exec_()
    main()
