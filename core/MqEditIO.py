"""Especific mixings to integrate with miow
"""


from PyQt4.QtGui import (QPlainTextEdit,)
from MqEdit import WithLineHighlight, WithFixedFont

class WithMqEditIO(QPlainTextEdit):
    """"""

    def __init__(self, *args):
        pass

    def load_file(self, file_name):
        self.file_name = file_name
        f = open(self.file_name, 'r')
        self.setPlainText(unicode(f.read().decode('utf-8')))
        self.update()

    def save_file(self, file_name):
        f = open(self.file_name, 'w')
        f.write(unicode(self.toPlainText()).encode('utf-8'))



if(__name__ == '__main__'):
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
