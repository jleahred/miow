# -*- coding: utf-8 -*-
"""MY OWn...
"""

import os
from copy  import copy

from  PyQt4.QtGui import(QApplication,
                         QWidget,
                         QSplitter,
                         QVBoxLayout,
                         QTabWidget,
                         QKeyEvent)

import PyQt4.QtCore
from  PyQt4.QtCore import (Qt,
                           QEvent)

import core.InterpreterEditor

from core.CommandWindow import CommandWindow

from core.Event  import Event



MAIN_WINDOW = None



#-----------------------------------------------------
# These will be readed at starting
# if nothing defined, this is de default configuration
APP_KEY_MAPS = []
REGISTERED_WIDGETS = []        #defined in miow.init
COMMAND_LIST = []              #defined in miow.init
KEY_START_RECORDING = ("F4", "")
KEY_STOP_RECORDING = ("F5", "")
EVENT_REQUEST_COMMAND_CONTEXT = Event()
execfile('miow.init')
#-----------------------------------------------------


def get_keyevent__from_key_as_text(key_as_text, text):
    return QKeyEvent(QEvent.KeyPress,
        PyQt4.QtGui.QKeySequence(key_as_text),
        Qt.KeyboardModifiers(0),      # modifiers
        text,     # text
        False,  # autorepeat
        1       # count
    )


class MainWindow(QWidget):
    """Miow main window
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        # create widgets
        self._main_tab = QTabWidget(self)
        #self._main_tab.setTabsClosable(True)
        self._main_tab.setMovable(True)
        self.v_splitter = QSplitter(Qt.Vertical, self)
        self.v_splitter.addWidget(self._main_tab)
        layout = QVBoxLayout(self)
        layout.addWidget(self.v_splitter)
        layout.setMargin(0)
        self.setLayout(layout)

        self.command_window = CommandWindow(self)
        self.command_window.event_selected_command += self.cw_selected_command

        import shutil
        shutil.rmtree('/tmp/miow/', True)
        os.makedirs('/tmp/miow/')


    def cw_selected_command(self, command):
        exec(command)

    def get_current_widget(self):
        return self.main_tab.currentWidget()

    def show_command_window(self, context=None):
        self.command_window.show_hide(context)

    def get_command_list(self, context=None):
        if(context==None):
            command_list = copy(COMMAND_LIST)
            if self.get_current_widget():
                self.get_current_widget().bw_add_command_list(command_list)
        else:
            command_list = []
            EVENT_REQUEST_COMMAND_CONTEXT(context, command_list)
        return command_list



    @property
    def main_tab(self):
        return self._main_tab

    def _add_widget(self, widget_class, params):
        """Add any kind of widget"""
        widget = widget_class(params, self.main_tab)
        self.main_tab.addTab(widget, "?")
        self.main_tab.setCurrentIndex(self.main_tab.count()-1)
        if self.main_tab.count() == 1:
            #self.v_splitter.setStretchFactor(0, 10)
            #self.v_splitter.setStretchFactor(1, 3)
            total_size = sum(self.v_splitter.sizes())
            self.v_splitter.setSizes([total_size / 100 * 70,
                                      total_size / 100 * 30])
        widget.setFocus()
        core.InterpreterEditor.CURRENT_WIDGET = widget



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
        for key_text, text in self._keys_recorded:
            super(MiowApplication, self).notify(QApplication.focusWidget(),
                      get_keyevent__from_key_as_text(key_text, text))

    def notify(self, receiver, event):
        if event.type() == QEvent.KeyPress:
            key_event = QKeyEvent(event)
            key_text = PyQt4.QtGui.QKeySequence(key_event.key() |
                        key_event.modifiers().__int__()).toString()
            text = key_event.text()

            if (key_text, text) == KEY_STOP_RECORDING and not self.recording:
                self.reproduce_keys(self._keys_recorded)
            elif (key_text, text) == KEY_STOP_RECORDING and self.recording:
                self.recording = False
            elif self.recording:
                self._keys_recorded.append((key_text, unicode(text)))

            if (key_text, text) == KEY_START_RECORDING:
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
            for key_as_text, method in self.keys_map:
                if key_as_text == (key_text, text):
                    replace = method(key_event, key_as_text)
                    if replace == None:
                        return True
                    elif replace == False:
                        return super(MiowApplication, self).notify(receiver, event)
                    else:
                        return self.notify(receiver, replace)

        return super(MiowApplication, self).notify(receiver, event)


if __name__ == '__main__':

    def main():
        """execute miow"""
        app = MiowApplication([])
        core.InterpreterEditor.APP = app
        global MAIN_WINDOW
        MAIN_WINDOW = MainWindow()
        core.InterpreterEditor.MAIN_WINDOW = MAIN_WINDOW
        MAIN_WINDOW.showMaximized()
        #mainw.add_widget(SimpleEdit, "test1")
        #mainw.add_widget(SimpleEdit, "test2")

        app.exec_()

    main()
