# -*- coding: utf-8 -*-
"""This Is Not An Editor
"""

from  PyQt4.QtGui import(QWidget,
                         QSplitter,
                         QVBoxLayout,
                         QTabWidget)

from  PyQt4.QtCore import Qt

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
        """Add any kind of components"""
        widget = widget_class(self.main_tab)
        self.main_tab.addTab(widget, label)
        if self.main_tab.count() == 1:
            #self.v_splitter.setStretchFactor(0, 10)
            #self.v_splitter.setStretchFactor(1, 3)
            total_size = sum(self.v_splitter.sizes())
            self.v_splitter.setSizes([total_size / 100 * 85,
                                      total_size / 100 * 15])
        widget.setFocus()


if(__name__ == '__main__'):
    from PyQt4.QtGui import QApplication

    register_components = "from components.SimpleEdit import SimpleEdit"
    exec(register_components)

    def main():
        """execute miow"""
        app = QApplication([])
        mainw = MainWindow()
        mainw.show()
        #mainw.add_widget(SimpleEdit, "test1")
        #mainw.add_widget(SimpleEdit, "test2")

        app.exec_()
    main()
