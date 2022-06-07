from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, \
    QVBoxLayout, QWidget, QLabel, QMenu, QFileDialog, QDialog, \
    QRadioButton, QLineEdit, QPushButton, QComboBox, QMessageBox, QAction
from PyQt5.QtGui import QIcon, QPixmap, QActionEvent
from globals import Config
from PIL import Image
from PIL.ImageQt import ImageQt
import logging
from actions import interpolationButtonAction, copyImageToSiblingAction, \
    compressImageAction, calculateMetricAction, addGaussNoiceAction, \
    addSaltAndPepperNoiceAction, calculateAllMetricsButton, addGaussianBlurAction, \
    translationButtonAction, rotationAction, cuttingAction
import functools
from io import BytesIO

class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        # self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle(Config.appname)

        menubar = self.menuBar()
        aboutProgramMenu = menubar.addMenu('&Pomoc')
        extractAction = QAction('&O programie', self)
        aboutProgramMenu.triggered.connect(functools.partial(startAPD, self))
        aboutProgramMenu.addAction(extractAction)
        self.leftImageLabel = ImageLabel()
        self.rightImageLabel = ImageLabel()
        self.resultImage = None

        self.allmetricsButton = QPushButton('Oblicz wszystkie dostępne metryki')
        self.triggerButton = QPushButton('Oblicz')
        self.metricSelect = QComboBox()
        self.resultLabel = QLabel('Wynik: \nCzas: ')
        self.leftImageLabel.setSibling(self.rightImageLabel)
        self.rightImageLabel.setSibling(self.leftImageLabel)

    def buildLeyout(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        mainLayout = QVBoxLayout(centralWidget)

        self.allmetricsButton.clicked.connect(functools.partial(calculateAllMetricsButton, self))

        mainLayout.addWidget(self.allmetricsButton)
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
        for _,item in Config.availableMetrics.items():
            self.metricSelect.addItem(item)
        metricCalculatorWrapper.addWidget(self.metricSelect)
        metricCalculatorWrapper.addWidget(self.triggerButton)
        metricCalculatorWrapper.addWidget(self.resultLabel)
        widget.setLayout(metricCalculatorWrapper)
        return widget

    def connectEvents(self):
        self.triggerButton.clicked.connect(functools.partial(calculateMetricAction, self))

    def showResult(self, resultText):
        QMessageBox.about(self, "Wynik", resultText)

    def showNearestPart(self, image):
        self.resultImage = image
        imagedialog = ImageDialog(self)
        imagedialog.exec_()


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
        gaussNoiceAction = noicesmenu.addAction(Config.availableModifiers['gauss'])
        saltandPepperNoiceAction = noicesmenu.addAction(Config.availableModifiers['saltandpepper'])
        gaussianBlurAction = noicesmenu.addAction(Config.availableModifiers['gassianblur'])

        transformMenu = QMenu(menu)
        transformMenu.setTitle('Transformuj obraz')
        resizeAction = transformMenu.addAction('Przeskaluj obraz')
        translationAction = transformMenu.addAction('Translacja')
        rotationAction = transformMenu.addAction('Rotacja')
        cutingAction = transformMenu.addAction('Przytnij')

        loadImageAction = menu.addAction('Wczytaj obraz')
        transformMenu = menu.addMenu(transformMenu)
        copyAction = menu.addAction('Skopiuj obok')
        compressAction = menu.addAction('Skompresuj')
        imageInfo = menu.addAction('Info')
        menu.addMenu(noicesmenu)
        action = menu.exec_(gp)

        if action == loadImageAction:
            try:
                newPath, _ = QFileDialog.getOpenFileName(self)
                self.setupImage(newPath)
            except Exception:
                pass
        elif action == resizeAction:
            rd = ResizeDialog(self)
            rd.exec_()
        elif action == translationAction:
            rd = TranslationDialog(self)
            rd.exec_()
        elif action == rotationAction:
            rd = RotationDialog(self)
            rd.exec_()
        elif action == cutingAction:
            rd = CuttingDialog(self)
            rd.exec_()
        elif action == gaussNoiceAction:
            logging.debug('noice')
            logging.debug(Config.availableModifiers['gauss'])
            nd = NoiseDialog(self, Config.availableModifiers['gauss'])
            nd.exec_()
        elif action == saltandPepperNoiceAction:
            nd = NoiseDialog(self, Config.availableModifiers['saltandpepper'])
            nd.exec_()
        elif action == gaussianBlurAction:
            nd = NoiseDialog(self, Config.availableModifiers['gassianblur'])
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
        self.radioNearest.setChecked(True)
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

class TranslationDialog(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()
        self.setWindowTitle('Translacja')
        self.parent = parent

        self.sizeInput = QLineEdit('0,0')
        self.acceptButton = QPushButton('Wykonaj')

        self.buildLayout()
        self.connectEvents()

class AboutProgramDialog(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()
        self.setWindowTitle('O programmie')
        self.parent = parent

        label1 = QLabel('Program do pracy dyplomowej 2022')
        label2 = QLabel('Autor: Karol Baran')

        widget = QWidget(self.parent)
        vertical = QVBoxLayout(widget)

        vertical.addWidget(label1)
        vertical.addWidget(label2)
        self.setLayout(vertical)
def startAPD(parent):
    AboutProgramDialog(parent).exec_()
class RotationDialog(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()
        self.setWindowTitle('Rotatcja')
        self.parent = parent

        self.sizeInput = QLineEdit('0')
        self.acceptButton = QPushButton('Wykonaj')

        self.buildLayout()
        self.connectEvents()

    def buildLayout(self):
        widget = QWidget(self.parent)
        vertical = QVBoxLayout(widget)

        vertical.addWidget(self.sizeInput)
        vertical.addWidget(self.acceptButton)
        self.setLayout(vertical)

        return widget

    def connectEvents(self):
        self.acceptButton.clicked.connect(functools.partial(rotationAction, self.parent, self))

class CuttingDialog(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()
        self.setWindowTitle('Przycinanie')
        self.parent = parent

        self.sizeInput = QLineEdit(f'(0, 0) ({self.parent.image.size[0]},{self.parent.image.size[1]})')
        self.acceptButton = QPushButton('Wykonaj')

        self.buildLayout()
        self.connectEvents()

    def buildLayout(self):
        widget = QWidget(self.parent)
        vertical = QVBoxLayout(widget)

        vertical.addWidget(self.sizeInput)
        vertical.addWidget(self.acceptButton)
        self.setLayout(vertical)

        return widget

    def connectEvents(self):
        self.acceptButton.clicked.connect(functools.partial(cuttingAction, self.parent, self))


class NoiseDialog(QDialog):
    def __init__(self, parent, type):
        super(QDialog, self).__init__()
        self.setWindowTitle('Zaszumienie')
        self.parent = parent
        self.type = type

        self.acceptButton = QPushButton('Wykonaj')
        # szum gaussa
        self.mi = QLineEdit()
        self.mi.setPlaceholderText("Mi")
        self.sigma = QLineEdit()
        self.sigma.setPlaceholderText("Sigma")
        # sól i pieprz
        self.noicedPercent = QLineEdit()
        self.noicedPercent.setPlaceholderText("Procent zaszumienia")
        # rozmycie gaussa
        self.masksize = QLineEdit()
        self.masksize.setPlaceholderText("Wielkosc maski")

        if(self.type == Config.availableModifiers['gauss']):
            self.addGaussNoiceInputs()
        elif(self.type == Config.availableModifiers['saltandpepper']):
            self.addSaltAndPepperInputs()
        elif (self.type == Config.availableModifiers['gassianblur']):
            self.addGaussianBlurInputs()
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

    def addGaussianBlurInputs(self):
        self.refreshFields()
        widget = QWidget(self)
        vertical = QVBoxLayout(widget)
        vertical.addWidget(self.masksize)
        vertical.addWidget(self.acceptButton)
        self.setLayout(vertical)
        return widget

    def connectEvents(self):
        if (self.type == Config.availableModifiers['gauss']):
            self.acceptButton.clicked.connect(functools.partial(addGaussNoiceAction, self.parent, self))
        elif (self.type == Config.availableModifiers['saltandpepper']):
            self.acceptButton.clicked.connect(functools.partial(addSaltAndPepperNoiceAction, self.parent, self))
        elif (self.type == Config.availableModifiers['gassianblur']):
            self.acceptButton.clicked.connect(functools.partial(addGaussianBlurAction, self.parent, self))


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

class ImageDialog(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()
        self.setWindowTitle('Wynik')
        self.parent = parent
        self.image = QLabel()

        imageQt = ImageQt(parent.resultImage).rgbSwapped().rgbSwapped()
        pixmap = QPixmap.fromImage(imageQt)
        self.image.setPixmap(pixmap)

        self.buildLayout()

    def buildLayout(self):
        widget = QWidget(self.parent)
        vertical = QVBoxLayout(widget)
        vertical.addWidget(self.image)
        self.setLayout(vertical)

        return widget