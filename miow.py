# -*- coding: utf-8 -*-
"""MY OWn...
"""

import os
from string import Template

from  PyQt4.QtGui import(QWidget,
                         QSplitter,
                         QVBoxLayout,
                         QTabWidget)

from  PyQt4.QtCore import Qt

import core.CommandEditor
from  core.CommandEditor import CommandEditor


# These will be readed at starting
# if nothing defined, this is de default configuration
INIT_FOLDERS = ['.']
REGISTERED_WIDGETS = []
#-----------------------------------------------------


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
        self._run_init_miows()
        self._auto_register_widgets()

    def _auto_register_widgets(self):
        for reg_widget in REGISTERED_WIDGETS:
            reg = Template("""\
def _new_widget(self):
    _self = self
    def __new_widget(caption):
        from $module import $widget
        _self._add_widget($widget, caption)
    return __new_widget

self.new_widget_$widget = _new_widget(self)
""").substitute(module=reg_widget["module"], widget=reg_widget["widget"])
            exec(reg)

    def _add_widget(self, widget_class, label="???"):
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

    @property
    def init_folders(self):
        return INIT_FOLDERS

    @property
    def available_widgets(self):
        return REGISTERED_WIDGETS
        #return [(base, f)
        #                for folder in self.init_folders
        #                for base, _, files in os.walk(folder)
        #                for f in files if (f.endswith(".py")
        #                                    and not f.startswith("_"))]

    def _run_init_miows(self):
        miows_inits = [(base, f)
                        for folder in self.init_folders
                        for base, _, files in os.walk(folder)
                        for f in files if (f == "init.miow")]
        for folder, fname in miows_inits:
            execfile(os.path.join(folder, fname))


if __name__ == '__main__':
    from PyQt4.QtGui import QApplication

    #register_components = "from widgets.SimpleEdit import SimpleEdit"
    #exec(register_components)

    def main():
        """execute miow"""

        app = QApplication([])
        mainw = MainWindow()
        core.CommandEditor.MAIN_WINDOW = mainw
        mainw.showMaximized()
        #mainw.add_widget(SimpleEdit, "test1")
        #mainw.add_widget(SimpleEdit, "test2")

        app.exec_()
    main()
