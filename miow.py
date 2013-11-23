# -*- coding: utf-8 -*-
"""MY OWn...
"""

import os
from string import Template

from  PyQt4.QtGui import(QApplication,
                         QWidget,
                         QSplitter,
                         QVBoxLayout,
                         QTabWidget,
                         QKeyEvent)

import PyQt4.QtCore
from  PyQt4.QtCore import (Qt,
                           QEvent)

import core.CommandEditor
from  core.CommandEditor import CommandEditor

from core.keys import(get_key_event_from_dict_simpl,
                      get_dict_from_key_event_simpl)


MAIN_WINDOW = None

# These will be readed at starting
# if nothing defined, this is de default configuration
INIT_FOLDERS = ['.']
APP_KEY_MAPS = []
REGISTERED_WIDGETS = []
KEY_START_RECORDING = {#'count': 1,
                       'text': PyQt4.QtCore.QString(u''),
                       #'autorepeat': False,
                       'modifiers': 0,
                       'key': 16777266}

KEY_STOP_RECORDING = {#'count': 1,
                      'text': PyQt4.QtCore.QString(u''),
                      #'autorepeat': False,
                      'modifiers': 0,
                      'key': 16777267}

#-----------------------------------------------------


class MainWindow(QWidget):
    """Miow main window
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        # create widgets
        self._main_tab = QTabWidget(self)
        self._command_editor = CommandEditor(self)
        self.v_splitter = QSplitter(Qt.Vertical, self)
        self.v_splitter.addWidget(self._main_tab)
        self.v_splitter.addWidget(self._command_editor)
        layout = QVBoxLayout(self)
        layout.addWidget(self.v_splitter)
        layout.setMargin(0)
        self.setLayout(layout)
        self._command_editor.setFocus()
        self._run_init_miows()
        self._auto_register_widgets()

    @property
    def command_editor(self):
        return self._command_editor

    @property
    def main_tab(self):
        return self._main_tab

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


class MiowApplication(QApplication):

    def __init__(self, args):
        super(MiowApplication, self).__init__(args)
        self.recording = False
        self._keys_recorded = []

    @property
    def keys_recorded(self):
        return self._keys_recorded

    @property
    def keys_map(self):
        return APP_KEY_MAPS

    def reproduce_keys(self, keys):
        for key_dict in self._keys_recorded:
            super(MiowApplication, self).notify(QApplication.focusWidget(),
                              get_key_event_from_dict_simpl(key_dict))

    def notify(self, receiver, event):
        if event.type() == QEvent.KeyPress:
            key_dict = get_dict_from_key_event_simpl(QKeyEvent(event))

            if key_dict == KEY_STOP_RECORDING and not self.recording:
                self.reproduce_keys(self._keys_recorded)
            elif key_dict == KEY_STOP_RECORDING and self.recording:
                self.recording = False
            elif self.recording:
                self._keys_recorded.append(key_dict)

            if key_dict == KEY_START_RECORDING:
                self.recording = True
                self._keys_recorded = []

#==============================================================================
#             key = {
#                 "key": key_event.key(),
#                 "modifiers": int(key_event.modifiers()),
#                 "text": key_event.text(),
#                 "autorepeat": key_event.isAutoRepeat(),
#                 "autorepeat": key_event.isAutoRepeat(),
#                 "count": key_event.count()
#             }
#             print key
#==============================================================================
#==============================================================================
#         if event.type() == QEvent.KeyPress:
#             key_event = QKeyEvent(event)
#             ker = QKeyEvent(QEvent.KeyPress,
#                             key_event.key(),
#                             key_event.modifiers(),
#                             key_event.text(),
#                             key_event.isAutoRepeat(),
#                             key_event.count())
#             super(MiowApplication, self).notify(receiver, ker)
#==============================================================================
            for method, key in self.keys_map:
                if key == key_dict:
                    method()
                    return True
        return super(MiowApplication, self).notify(receiver, event)


if __name__ == '__main__':

    def main():
        """execute miow"""
        app = MiowApplication([])
        core.CommandEditor.APP = app
        global MAIN_WINDOW
        MAIN_WINDOW = MainWindow()
        core.CommandEditor.MAIN_WINDOW = MAIN_WINDOW
        MAIN_WINDOW.showMaximized()
        #mainw.add_widget(SimpleEdit, "test1")
        #mainw.add_widget(SimpleEdit, "test2")

        app.exec_()

    main()
