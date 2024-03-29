"""Especific mixings to integrate with miow a single MqEdit with IO
"""


from PyQt4.QtGui import (QWidget, QPlainTextEdit,)

from core.Mixin import mixin

from core.BaseWidget import BaseWidget

from core.MqEdit import(WithLineHighlight,
                   WithFixedFont,
                   WithBasicIdentationManager)
                   
from core.Completion import WithCompletion, WithWordCompletionMulty_



class WithSingleIO(BaseWidget):
    """"""

    def __init__(self, params):
        self.file_name = None
        if params is not None  and  "file" in params:
            self.command_load_file(params["file"])

    def bw_add_command_list(self, command_list):
        super(WithSingleIO, self).bw_add_command_list(command_list)
        if self.file_name:
            command_list += [
                    #("load examples/pyinterpreter.ipy",    "", 0.0, "self.get_current_widget().command_load_file('examples/pyinterpreter.ipy')"),
                    ("save file",    "ss", 0.5, "self.get_current_widget().command_save_file()"),
                   ]

    def command_load_file(self, file_name):
        self.file_name = file_name
        self._editor_widget.load_file(self.file_name)

    def command_save_file(self):
        if self.file_name:
            self._editor_widget.save_file(self.file_name)



if(__name__ == '__main__'):
    from MqEditIO import WithMqEditIO
    class TestClass(QWidget):
        def __init__(self, params, parent=None):
            super(TestClass, self).__init__(parent)
    
            self.file_name=None
            # create widgets
            self._editor_widget = mixin(
                                   WithBasicIdentationManager,
                                   WithWordCompletionMulty_,
                                   WithCompletion,
                                   WithLineHighlight,
                                   WithFixedFont,
                                   WithMqEditIO,
                                   QPlainTextEdit)(self)

    def test_mqedit_load_save():
        """simple test"""
        from PyQt4.QtGui import QApplication
        from Mixin import mixin

        app = QApplication([])
        widget = mixin(
                        WithLineHighlight, 
                        WithFixedFont,
                        WithMqEditIO,
                        QPlainTextEdit)()
        widget.show()
        widget.load_file('MqEditIO.py')
        app.exec_()

    test_mqedit_load_save()
