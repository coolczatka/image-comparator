from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, \
    QVBoxLayout, QWidget, QLabel, QMenu, QFileDialog, QDialog, \
    QRadioButton, QLineEdit, QPushButton, QComboBox
from PyQt5.QtGui import QIcon, QPixmap
from globals import Config
from PIL import Image
from PIL.ImageQt import ImageQt
import logging
from actions import interpolationButtonAction, noicetypeChangedAction, copyImageToSiblingAction, compressImageAction
import functools

class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle(Config.appname)

        self.leftImageLabel = ImageLabel()
        self.rightImageLabel = ImageLabel()

        self.leftImageLabel.setSibling(self.rightImageLabel)
        self.rightImageLabel.setSibling(self.leftImageLabel)

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
        mainHorizontal.addWidget(self.leftImageLabel)
        mainHorizontal.addWidget(self.rightImageLabel)
        widget.setLayout(mainHorizontal)
        return widget

class ImageLabel(QLabel):
    def __init__(self):
        super(QLabel, self).__init__()
        self.image = None
        self.siblingImageLabel = None
        self.setupImage(Config.defaultImg)

    def setupImage(self, path):
        image = Image.open(path)
        self.setupImageFromMemory(image)

    def setupImageFromMemory(self, image):
        self.image = image
        imageQt = ImageQt(self.image).rgbSwapped().rgbSwapped()
        pixmap = QPixmap.fromImage(imageQt)
        self.setPixmap(pixmap)

    def contextMenuEvent(self, event):
        gp = event.globalPos()
        menu = QMenu(self)

        loadImageAction = menu.addAction('Wczytaj obraz')
        resizeAction = menu.addAction('Przeskaluj obraz')
        noiceAction = menu.addAction('Dodaj szum')
        copyAction = menu.addAction('Skopiuj obok')
        compressAction = menu.addAction('Skompresuj')

        action = menu.exec_(gp)

        if action == loadImageAction:
            newPath, _ = QFileDialog.getOpenFileName(self)
            self.setupImage(newPath)
        elif action == resizeAction:
            rd = ResizeDialog(self)
            rd.exec_()
        elif action == noiceAction:
            nd = NoiseDialog(self)
            nd.exec_()
        elif action == copyAction:
            copyImageToSiblingAction(self)
        elif action == compressAction:
            cd = CompressionDialog(self)
            cd.exec_()
        else:
            pass

    def setSibling(self, siblingImageLabel):
        self.siblingImageLabel = siblingImageLabel

class ResizeDialog(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()
        self.setWindowTitle('Przeskalowanie')
        self.parent = parent

        self.interpolation = 'NEAREST'

        self.sizeInput = QLineEdit('0,0')
        self.radioNearest = QRadioButton('NEAREST')
        self.radioBilinear = QRadioButton('BILINEAR')
        self.radioBicubic = QRadioButton('BICUBIC')
        self.radioBox = QRadioButton('BOX')
        self.acceptButton = QPushButton('Wykonaj')

        self.buildLayout()
        self.connectEvents()

    def buildLayout(self):
        widget = QWidget(self.parent)
        vertical = QVBoxLayout(widget)

        vertical.addWidget(self.sizeInput)
        vertical.addWidget(self.radioNearest)
        vertical.addWidget(self.radioBilinear)
        vertical.addWidget(self.radioBicubic)
        vertical.addWidget(self.radioBox)
        vertical.addWidget(self.acceptButton)
        self.setLayout(vertical)

        return widget

    def connectEvents(self):
        self.acceptButton.clicked.connect(functools.partial(interpolationButtonAction, self.parent, self))


class NoiseDialog(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()
        self.setWindowTitle('Zaszumienie')
        self.parent = parent

        self.noicetypeCombobox = QComboBox()
        self.noicetypeCombobox.addItem('Gaussa')
        self.noicetypeCombobox.addItem('Sól i pieprz')

        self.acceptButton = QPushButton('Wykonaj')

        self.buildLayout()
        self.connectEvents()

    def buildLayout(self):
        widget = QWidget(self.parent)
        vertical = QVBoxLayout(widget)
        vertical.addWidget(self.noicetypeCombobox)
        vertical.addWidget(self.acceptButton)
        self.setLayout(vertical)

        return widget

    def connectEvents(self):
        self.noicetypeCombobox.currentTextChanged.connect(functools.partial(noicetypeChangedAction, self))
        self.acceptButton.clicked.connect(functools.partial(interpolationButtonAction, self.parent, self))


class CompressionDialog(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()
        self.setWindowTitle('Kompresja')
        self.parent = parent

        self.compressionRate = QLineEdit('1')
        self.acceptButton = QPushButton('Wykonaj')

        self.buildLayout()
        self.connectEvents()

    def buildLayout(self):
        widget = QWidget(self.parent)
        vertical = QVBoxLayout(widget)
        vertical.addWidget(self.compressionRate)
        vertical.addWidget(self.acceptButton)
        self.setLayout(vertical)

        return widget

    def connectEvents(self):
        self.acceptButton.clicked.connect(functools.partial(compressImageAction, self.parent, self))