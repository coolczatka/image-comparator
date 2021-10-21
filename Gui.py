from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from Config import Config


class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle(Config.appname)

    def buildLeyout(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        mainLayout = QVBoxLayout(centralWidget)

        placeholder1 = QLabel('Placeholder1')
        placeholder2 = QLabel('Placeholder2')

        mainLayout.addWidget(placeholder1)
        mainLayout.addWidget(self.buildMainHolizontalWidget(centralWidget))
        mainLayout.addWidget(placeholder2)
        self.setLayout(mainLayout)

    def buildMainHolizontalWidget(self, parent):
        widget = QWidget(parent)
        mainHorizontal = QHBoxLayout(widget)
        dP = QPixmap(Config.defaultImg)
        leftImageLabel = QLabel()
        leftImageLabel.setPixmap(dP)
        rightImageLabel = QLabel()
        rightImageLabel.setPixmap(dP)
        mainHorizontal.addWidget(leftImageLabel)
        mainHorizontal.addWidget(rightImageLabel)
        widget.setLayout(mainHorizontal)
        return widget


class ImageLabel(QLabel):
    def __init__(self, path):
        self.setPixmap(path)

    def contextMenuEvent(self, event):
        pass