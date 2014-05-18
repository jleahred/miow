# -*- coding: utf-8 -*-


if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('../..')
    sys.path.append(lib_path)


from PyQt4.QtGui import QApplication, QMainWindow


from widgets.console.pyqterm import TerminalWidget
#from pyqterm.procinfo import ProcessInfo


if __name__ == "__main__":
    def on_mouse_down(line, col, row):
        print line, col, row
        
    def test():
        app = QApplication(sys.argv)
        mw = QMainWindow()
        mw.setGeometry(0, 0, 900, 300)
        term = TerminalWidget(mw)
        mw.setCentralWidget(term)
        mw.show()
        #term.send("""ls ~""")
        term.signal_mouse_down.connect(on_mouse_down)
        app.exec_()
    test()
    
    
