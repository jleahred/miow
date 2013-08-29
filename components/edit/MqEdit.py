"""Support to line highlight, line numbering...
"""

from PyQt4.QtGui import QTextEdit, QPlainTextEdit, QColor, \
                        QTextFormat, QTextCursor


class WithHighlight(QPlainTextEdit):
    """Mixin to add Highlight on current line to QPlainTextEdit"""
    def __init__(self, *args):
        self.highlight()
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.cursorPositionChanged.connect(self.highlight)

    def highlight(self):
        """this method will hightlight current line"""
        extra_selections = []

        if (self.isReadOnly() is False):
            line_color = QColor(255, 220, 240)
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)

            cursor = self.textCursor()
            last_selection_line = cursor.blockNumber()
            selection.cursor = cursor
            selection.cursor.movePosition(QTextCursor.EndOfBlock)
            extra_selections.append(QTextEdit.ExtraSelection(selection))

            selection.cursor.movePosition(QTextCursor.StartOfLine)
            selection.cursor.movePosition(QTextCursor.PreviousCharacter)
            while(last_selection_line == selection.cursor.blockNumber()):
                if(selection.cursor.atStart()):
                    break
                extra_selections.append(QTextEdit.ExtraSelection(selection))
                selection.cursor.movePosition(QTextCursor.StartOfLine)
                selection.cursor.movePosition(QTextCursor.PreviousCharacter)

        self.setExtraSelections(extra_selections)


if(__name__ == '__main__'):
    def test_with_hightlight():
        """simple test"""
        import os
        import sys
        from PyQt4.QtGui import QApplication

        lib_path = os.path.abspath('../../misc')
        sys.path.append(lib_path)
        from Mixin import mixin

        app = QApplication([])
        widget = mixin(QPlainTextEdit, WithHighlight)()
        widget.show()
        app.exec_()

    test_with_hightlight()
