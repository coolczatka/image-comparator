from PyQt5.QtWidgets import QApplication
from Gui import MainWindow
import sys
if __name__ == '__main__':
    application = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.buildLeyout()
    mainwindow.show()
    sys.exit(application.exec_())