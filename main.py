from PyQt5.QtWidgets import QApplication
from Gui import MainWindow
import sys
from globals import Config
import logging

if __name__ == '__main__':
    if Config.logtarget == 'stdout':
        logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.DEBUG)
    else:
        logging.basicConfig(filename=sys.stdout, encoding='utf-8', level=logging.DEBUG)
    application = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.buildLeyout()
    mainwindow.show()
    sys.exit(application.exec_())