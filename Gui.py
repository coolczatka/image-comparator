from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, \
    QVBoxLayout, QWidget, QLabel, QMenu, QFileDialog, QDialog, \
    QRadioButton, QLineEdit, QPushButton, QComboBox
from PyQt5.QtGui import QIcon, QPixmap
from globals import Config
from PIL import Image
from PIL.ImageQt import ImageQt
import logging
from actions import interpolationButtonAction, copyImageToSiblingAction, \
    compressImageAction, calculateMetricAction, addGaussNoiceAction, \
    addSaltAndPepperNoiceAction
import functools
from io import BytesIO

class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle(Config.appname)

        self.leftImageLabel = ImageLabel()
        self.rightImageLabel = ImageLabel()
        self.triggerButton = QPushButton('Oblicz')
        self.metricSelect = QComboBox()
        self.leftImageLabel.setSibling(self.rightImageLabel)
        self.rightImageLabel.setSibling(self.leftImageLabel)

    def buildLeyout(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        mainLayout = QVBoxLayout(centralWidget)

        placeholder1 = QLabel('Placeholder1')

        mainLayout.addWidget(placeholder1)
        mainLayout.addWidget(self.buildMainHolizontalWidget(centralWidget))
        mainLayout.addWidget(self.buildMetricCalculatorWrapper(centralWidget))
        self.connectEvents()
        self.setLayout(mainLayout)

    def buildMainHolizontalWidget(self, parent):
        widget = QWidget(parent)
        mainHorizontal = QHBoxLayout(widget)
        mainHorizontal.addWidget(self.leftImageLabel)
        mainHorizontal.addWidget(self.rightImageLabel)
        widget.setLayout(mainHorizontal)
        return widget

    def buildMetricCalculatorWrapper(self, parent):
        widget = QWidget(parent)
        metricCalculatorWrapper = QHBoxLayout()
        for item in Config.availableMetrics.keys():
            self.metricSelect.addItem(item)
        metricCalculatorWrapper.addWidget(self.metricSelect)
        metricCalculatorWrapper.addWidget(self.triggerButton)
        widget.setLayout(metricCalculatorWrapper)
        return widget

    def connectEvents(self):
        self.triggerButton.clicked.connect(functools.partial(calculateMetricAction, self))

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

        noicesmenu = QMenu(menu)
        noicesmenu.setTitle('Dodaj szum')
        gaussNoiceAction = noicesmenu.addAction(Config.availableNoices['gauss'])
        saltandPepperNoiceAction = noicesmenu.addAction(Config.availableNoices['saltandpepper'])

        loadImageAction = menu.addAction('Wczytaj obraz')
        resizeAction = menu.addAction('Przeskaluj obraz')
        copyAction = menu.addAction('Skopiuj obok')
        compressAction = menu.addAction('Skompresuj')
        imageInfo = menu.addAction('Info')
        menu.addMenu(noicesmenu)
        action = menu.exec_(gp)

        if action == loadImageAction:
            newPath, _ = QFileDialog.getOpenFileName(self)
            self.setupImage(newPath)
        elif action == resizeAction:
            rd = ResizeDialog(self)
            rd.exec_()
        elif action == gaussNoiceAction:
            logging.debug('noice')
            logging.debug(Config.availableNoices['gauss'])
            nd = NoiseDialog(self, Config.availableNoices['gauss'])
            nd.exec_()
        elif action == saltandPepperNoiceAction:
            nd = NoiseDialog(self, Config.availableNoices['saltandpepper'])
            nd.exec_()
        elif action == copyAction:
            copyImageToSiblingAction(self)
        elif action == compressAction:
            cd = CompressionDialog(self)
            cd.exec_()
        elif action == imageInfo:
            id = InfoDialog(self)
            id.exec_()
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
    def __init__(self, parent, type):
        super(QDialog, self).__init__()
        self.setWindowTitle('Zaszumienie')
        self.parent = parent
        self.type = type

        self.acceptButton = QPushButton('Wykonaj')
        self.mi = QLineEdit()
        self.mi.setPlaceholderText("Mi")
        self.sigma = QLineEdit()
        self.sigma.setPlaceholderText("Sigma")
        self.noicedPercent = QLineEdit()
        self.noicedPercent.setPlaceholderText("Procent zaszumienia")

        if(self.type == Config.availableNoices['gauss']):
            self.addGaussNoiceInputs()
        elif(self.type == Config.availableNoices['saltandpepper']):
            self.addSaltAndPepperInputs()
        self.connectEvents()

    def refreshFields(self):

        self.acceptButton = QPushButton('Wykonaj')

        self.mi = QLineEdit()
        self.mi.setPlaceholderText("Mi")
        self.sigma = QLineEdit()
        self.sigma.setPlaceholderText("Sigma")
        self.noicedPercent = QLineEdit()
        self.noicedPercent.setPlaceholderText("Procent zaszumienia")

    def addGaussNoiceInputs(self):
        self.refreshFields()
        widget = QWidget(self)
        vertical = QVBoxLayout(widget)
        vertical.addWidget(self.mi)
        vertical.addWidget(self.sigma)
        vertical.addWidget(self.acceptButton)
        self.setLayout(vertical)
        return widget

    def addSaltAndPepperInputs(self):
        self.refreshFields()
        widget = QWidget(self)
        vertical = QVBoxLayout(widget)
        vertical.addWidget(self.noicedPercent)
        vertical.addWidget(self.acceptButton)
        self.setLayout(vertical)
        return widget

    def connectEvents(self):
        if (self.type == Config.availableNoices['gauss']):
            self.acceptButton.clicked.connect(functools.partial(addGaussNoiceAction, self.parent, self))
        elif (self.type == Config.availableNoices['saltandpepper']):
            self.acceptButton.clicked.connect(functools.partial(addSaltAndPepperNoiceAction, self.parent, self))


class CompressionDialog(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()
        self.setWindowTitle('Kompresja')
        self.parent = parent

        self.quality = QLineEdit('1')
        
        self.acceptButton = QPushButton('Wykonaj')

        self.buildLayout()
        self.connectEvents()

    def buildLayout(self):
        widget = QWidget(self.parent)
        vertical = QVBoxLayout(widget)
        vertical.addWidget(self.quality)
        vertical.addWidget(self.acceptButton)
        self.setLayout(vertical)

        return widget

    def connectEvents(self):
        self.acceptButton.clicked.connect(functools.partial(compressImageAction, self.parent, self))

class InfoDialog(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()
        self.setWindowTitle('Informacje o obrazie')
        self.parent = parent

        self.sizeInfo = QLabel('Rozmiar: '+str(self.parent.image.size))
        buffer = BytesIO()
        self.parent.image.save(buffer, "JPEG")
        filesize = buffer.tell()
        self.wageInfo = QLabel('Waga: '+str(filesize) + " B")

        self.buildLayout()

    def buildLayout(self):
        widget = QWidget(self.parent)
        vertical = QVBoxLayout(widget)
        vertical.addWidget(self.sizeInfo)
        vertical.addWidget(self.wageInfo)
        self.setLayout(vertical)

        return widget

class MeticDialog(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()
        self.setWindowTitle('Wynik')
        self.parent = parent

        logging.debug(parent)