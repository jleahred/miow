"""
Python highlighter
"""


if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('../..')
    sys.path.append(lib_path)


from PyQt4.QtGui import *
from PyQt4.QtCore import *


from core.Event import Event

from core.highlighters.MqHighlight import  WidthMqHighlighter


class  WidthPythonHighlighter(WidthMqHighlighter):
    def __init__(self, *args):
        super(WidthPythonHighlighter, self).__init__(*args)
        #self.python_highlighter = PythonHighlighter(self.document())
        self.python_highlighter = PythonHighlighter(self.highlighter)
        self.highlighter._event += self.python_highlighter.mq_highlightBlock




class PythonHighlighter(object):

    def __init__(self, highlighter):
        #super(PythonHighlighter, self).__init__(parent)
        self.highlightingRules = []
        self.highlighter = highlighter

        self.list_limiters = []

        # coments and strings
        format_string = QTextCharFormat()
        format_string.setForeground(QColor(0, 150, 0))

        format_string_ml = QTextCharFormat()
        format_string_ml .setForeground(QColor(190, 150, 50))
        format_string_ml.setFontWeight( QFont.Bold )

        format_comment = QTextCharFormat()
        format_comment.setForeground(QColor(150, 50, 20))
        format_comment.setFontItalic(True)

        # magic words
        format_ = QTextCharFormat()
        brush = QBrush( Qt.black, Qt.SolidPattern )
        format_.setForeground( brush )
        format_.setFontWeight( QFont.Bold )


        #  start, end, format, multiline?
        self.multiline_delimiters = [0]
        self.list_limiters = [('"""',  '"""',  format_string_ml),
                              ("'",  "'",  format_string),
                              ('"',  '"',  format_string),
                              ('\#', '$',  format_comment),
                              ("\\b__\w+__\\b", "\\b", format_)
                        ]



        # upper case words
        class_def_name =  QTextCharFormat()
        pattern = QRegExp( "\\b[A-Z][A-Za-z0-9_]+\\b" )
        pattern.setMinimal( True )
        class_def_name.setForeground( QColor(80, 80, 180) )
        rule = HighlightingRule( pattern, class_def_name)
        self.highlightingRules.append( rule )

        # class and function names
        class_def_name =  QTextCharFormat()
        class_def_name.setFontWeight( QFont.Bold )
        pattern = QRegExp( " *(class|def) +[A-Za-z_][A-Za-z0-9_]*\\b" )
        pattern.setMinimal( True )
        brush = QBrush( Qt.black, Qt.SolidPattern )
        class_def_name.setForeground( brush )
        rule = HighlightingRule( pattern, class_def_name)
        self.highlightingRules.append( rule )
        
        # keyword
        keyword_rule = QTextCharFormat()
        brush = QBrush( Qt.blue, Qt.SolidPattern )
        keyword_rule.setForeground( brush )
        keyword_rule.setFontWeight( QFont.Bold )
        keywords = QStringList( [ 
        "and",       "del",     "from",     "not",     "while",
        "as",        "elif",    "global",   "or",      "with",
        "assert",    "else",    "if",       "pass",    "yield",
        "break",     "except",  "import",   "print",
        "class",     "exec",    "in",       "raise",
        "continue",  "finally", "is",       "return",
        "def",       "for",     "lambda",   "try",
           ] )
        for word in keywords:
            pattern = QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule( pattern, keyword_rule )
            self.highlightingRules.append( rule )

        # keyword2
        keyword2_rule = QTextCharFormat()
        brush = QBrush( Qt.darkMagenta, Qt.SolidPattern )
        keyword2_rule.setForeground( brush )
        #keyword2_rule.setFontItalic(True)
        #keyword2_rule.setFontWeight( QFont.Bold )
        keywords = QStringList( [ 
        "self",       "len",  "True",  "False",   "print",  "open",
           ] )
        for word in keywords:
            pattern = QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule( pattern, keyword2_rule )
            self.highlightingRules.append( rule )

        # number
        number_rule =  QTextCharFormat()
        pattern = QRegExp( "\\b[\-\+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\\b" )
        pattern.setMinimal( False )
        brush = QBrush( Qt.darkRed, Qt.SolidPattern )
        number_rule.setForeground( brush )
        #number_rule.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, number_rule )
        self.highlightingRules.append( rule )

        # symbols
        symbol_rule =  QTextCharFormat()
        pattern = QRegExp( "[=\+\-\*\/\:\,\>\<]" )
        pattern.setMinimal( True )
        symbol_rule.setForeground( Qt.darkRed )
        symbol_rule.setFontWeight( QFont.Bold )
        rule = HighlightingRule( pattern, symbol_rule )
        self.highlightingRules.append( rule )





    def mq_highlightBlock( self, text ):
        def find_first_begining(text, current_pos):
            found_end = ""
            found_status = 0
            min_found = len(text)+1
            found_len = 0
            status_index = -1
            found_format = None
            for start, end, format_r in self.list_limiters:
                status_index += 1
                expr_start = QRegExp(start)
                f_pos = expr_start.indexIn(text, current_pos)
                f_len = expr_start.matchedLength()
                if f_pos >= 0  and  f_pos<min_found:
                    found_end = end
                    found_status = status_index
                    min_found = f_pos
                    found_len = f_len
                    found_format = format_r

            return found_end, found_status, min_found, found_len, found_format


        for rule in self.highlightingRules:
            expression = QRegExp( rule.pattern )
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.highlighter.setFormat( index, length, rule.format )
                index = expression.indexIn(text, index + length )
                self.highlighter.setCurrentBlockState( 0 )

        self.highlighter.setCurrentBlockState(-1);
        current_pos = 0
        if self.highlighter.previousBlockState() in self.multiline_delimiters:
            #  start, end, format, multiline?
            curent_config = self.list_limiters[self.highlighter.previousBlockState()]
            start_format = current_pos
            f_format = curent_config[2]
            expr_end = QRegExp(curent_config[1])
            f_pos = expr_end.indexIn(text, current_pos)
            f_len = expr_end.matchedLength()
            if f_pos >= 0:
                self.highlighter.setFormat(start_format, f_pos-start_format+f_len, f_format)
                current_pos = f_pos + f_len
            else:
                self.highlighter.setFormat(start_format, len(text)-start_format, f_format)
                self.highlighter.setCurrentBlockState(self.highlighter.previousBlockState())
                return
        
        while True:
            end_re, status, current_pos, f_len, f_format = find_first_begining(text, current_pos)
            start_format = current_pos
            if end_re != "":
                expr_end = QRegExp(end_re)
                f_pos = expr_end.indexIn(text, current_pos + f_len)
                f_len = expr_end.matchedLength()
                if f_pos >= 0:
                    self.highlighter.setFormat(start_format, f_pos-start_format+f_len, f_format)
                    current_pos = f_pos + f_len
                else:
                    self.highlighter.setFormat(start_format, len(text)-start_format, f_format)
                    self.highlighter.setCurrentBlockState(status)
                    break
            else:
                break

        return



class HighlightingRule():
  def __init__( self, pattern, format ):
    self.pattern = pattern
    self.format = format



if(__name__ == '__main__'):
    from core.MqEdit import  (WithLineHighlight, WithFixedFont,
                        WithViewPortMargins, WithLineNumbers)
    
    def test_python_highlight():
        """simple test"""
        from PyQt4.QtGui import QApplication
        from Mixin import mixin
        import os

        app = QApplication([])
        widget = mixin(
                       WidthPythonHighlighter,
                       WidthMqHighlighter,
                       WithLineNumbers,
                       WithViewPortMargins,
                       WithLineHighlight,
                       WithFixedFont,
                       QPlainTextEdit)()
        f = open(os.path.abspath(__file__), 'r')
        widget.setPlainText(unicode(f.read().decode('utf-8')))
        widget.setPlainText("""#'asd"fsdf'sadfasdf

"asdfasdf"
def
aaas"dfas"df"asdf"
""")
        widget.show()
        app.exec_()

    test_python_highlight()
