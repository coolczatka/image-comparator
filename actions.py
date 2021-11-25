import logging
from PIL import Image as ImageModule
from PIL import ImageFilter
from io import BytesIO
from globals import Config
from imagemodifiers import NoiceHelper
from metrics import MetricCalculator

def interpolationButtonAction(imageLabel, dialogWindow):
    logging.debug("Akcja interpolacji")
    sizeText = dialogWindow.sizeInput.text()
    image = imageLabel.image
    size = (1, 1)
    if '%' in sizeText:
        sizePercent = float(sizeText.split('%')[0])
        size = (int(sizePercent*image.size[0]/100), int(sizePercent*image.size[1]/100))
    else:
        heightText, widthText = dialogWindow.sizeInput.text().split(',')
        size = (int(heightText), int(widthText))
    type = ''
    if dialogWindow.radioNearest.isChecked():
        type = ImageModule.NEAREST
    elif dialogWindow.radioBilinear.isChecked():
        type = ImageModule.BILINEAR
    elif dialogWindow.radioBicubic.isChecked():
        type = ImageModule.BICUBIC
    elif dialogWindow.radioBox.isChecked():
        type = ImageModule.BOX
    resized = imageLabel.image.resize(size, type)
    imageLabel.setupImageFromMemory(resized)

def copyImageToSiblingAction(imageLabel):
    logging.debug("Skopiowanie obrazu")
    imageLabel.siblingImageLabel.setupImageFromMemory(imageLabel.image)

def addGaussNoiceAction(imageLabel, dialogWindow):
    mi = float(dialogWindow.mi.text())
    sigma = float(dialogWindow.sigma.text())
    nh = NoiceHelper(imageLabel.image)
    imageLabel.setupImageFromMemory(nh.gauss(mi, sigma))

def addSaltAndPepperNoiceAction(imageLabel, dialogWindow):
    logging.debug('wbija')
    percent = float(dialogWindow.noicedPercent.text())
    nh = NoiceHelper(imageLabel.image)
    imageLabel.setupImageFromMemory(nh.saltandpepper(percent))

def addGaussianBlurAction(imageLabel, dialogWindow):
    logging.debug('wbija')
    masksize = float(dialogWindow.masksize.text())
    nh = NoiceHelper(imageLabel.image)
    imageLabel.setupImageFromMemory(nh.gassianblur(masksize))

def compressImageAction(imageLabel, dialogWindow):
    logging.debug("Kompresja")
    compressionRate = int(dialogWindow.quality.text())
    buffer = BytesIO()
    imageLabel.image.save(buffer, "JPEG", quality = compressionRate)
    imageLabel.setupImage(buffer)

def calculateMetricAction(window):
    selected = window.metricSelect.currentText()
    reversed = {v: k for k, v in Config.availableMetrics.items()}
    mc = MetricCalculator(window.leftImageLabel.image, window.rightImageLabel.image)
    method = getattr(mc, reversed[selected])
    value = method()
    window.resultLabel.setText('Wynik: '+str(value))

def calculateAllMetricsButton(window):
    logging.debug("Wszystkie metryki")
    resultFile = open('result.xml', 'w')
    text = ''
    xmltext = '<result>\n'
    mc = MetricCalculator(window.leftImageLabel.image, window.rightImageLabel.image)
    for metric, metricName in Config.availableMetrics.items():
        method = getattr(mc, metric)
        metricvalue = method()
        xmltext += f"<{metric}>{metricvalue}</{metric}>\n"
        text += f"{metricName}: {metricvalue}\n"
    xmltext += '</result>'
    resultFile.write(xmltext)
    resultFile.close()
    window.showResult(text)
