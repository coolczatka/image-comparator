import copy
import datetime
import logging

import numpy as np
from PIL import Image as ImageModule, ImageDraw
from io import BytesIO

from globals import Config
from imagemodifiers import NoiceHelper, ImageTransformer
from metrics import MetricCalculator
import time
import re

import os
from xml.etree import ElementTree
from exceptions import logerror

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
    it = ImageTransformer(imageLabel.image)
    resized = it.resize(size, type)
    imageLabel.setupImageFromMemory(resized)

def translationButtonAction(imageLabel, dialogWindow):
    logging.debug("Akcja translacji")
    vectorText = dialogWindow.sizeInput.text()
    left, up = vectorText.split(',')
    vector = (1, 0, -int(left), 0, 1, -int(up))
    logging.debug(vector)
    it = ImageTransformer(imageLabel.image)
    changed = it.move(vector)
    imageLabel.setupImageFromMemory(changed)

def rotationAction(imageLabel, dialogWindow):
    logging.debug("Akcja rotacji")
    angleText = dialogWindow.sizeInput.text()
    angle = float(angleText)
    it = ImageTransformer(imageLabel.image)
    changed = it.rotate(angle)
    imageLabel.setupImageFromMemory(changed)

def cuttingAction(imageLabel, dialogWindow):
    logging.debug("Akcja ciecia")
    try:
        pointsText = dialogWindow.sizeInput.text().replace(' ', '')
        pointsRegex = re.compile('\(\d+,\d+\)')
        regexResult = pointsRegex.findall(pointsText)
        points = list(
            map(lambda x: (int(x.replace('(', '').replace(')', '').split(',')[0]),
                           int(x.replace('(', '').replace(')', '').split(',')[1])), regexResult))
        it = ImageTransformer(imageLabel.image)
        changed = it.crop(points)
        imageLabel.setupImageFromMemory(changed)

    except Exception as e:
        print(logging.debug(str(e)))
    #
    # it = ImageTransformer(imageLabel.image)
    # changed = it.rotate(angle)
    # imageLabel.setupImageFromMemory(changed)
    #
def copyImageToSiblingAction(imageLabel):
    logging.debug("Skopiowanie obrazu")
    imageLabel.siblingImageLabel.setupImageFromMemory(imageLabel.image)

def addGaussNoiceAction(imageLabel, dialogWindow):
    logging.debug('Szum gaussa')
    mi = float(dialogWindow.mi.text())
    sigma = float(dialogWindow.sigma.text())
    nh = NoiceHelper(imageLabel.image)
    imageLabel.setupImageFromMemory(nh.gauss(mi, sigma))

def addSaltAndPepperNoiceAction(imageLabel, dialogWindow):
    logging.debug('Sol i pieprz')
    percent = float(dialogWindow.noicedPercent.text())
    nh = NoiceHelper(imageLabel.image)
    imageLabel.setupImageFromMemory(nh.saltandpepper(percent))

def addGaussianBlurAction(imageLabel, dialogWindow):
    logging.debug('Rozmycie gaussa')
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
    logging.debug('Obliczanie metryki '+selected)
    reversed = {v: k for k, v in Config.availableMetrics.items()}

    im1 = copy.deepcopy(window.leftImageLabel.image)
    im2 = copy.deepcopy(window.rightImageLabel.image)
    try:
        if(im1.size[0] == im2.size[0] and im1.size[1] == im2.size[1]):
            file = Xmlfile(Config.resultfile)
            resultChild = file.addChild(file.getRoot(), 'result')

            mc = MetricCalculator(window.leftImageLabel.image, window.rightImageLabel.image)
            method = getattr(mc, reversed[selected])
            starttime = time.time()
            value = method()
            stoptime = time.time()

            file.addElement(resultChild, 'datetime', datetime.datetime.now().isoformat())
            file.addElement(resultChild, 'value', round(value, 5),
                            [('type', reversed[selected]),('time', round(stoptime-starttime, 5))])

            window.resultLabel.setText(f'Wynik: {value}\nCzas: {stoptime - starttime}s')

            file.save()
        elif (im1.size[0] <= im2.size[0] and im1.size[1] <= im2.size[1]) or (im1.size[0] >= im2.size[0] and im1.size[1] >= im2.size[1]):
            if (im1.size[0] >= im2.size[0] and im1.size[1] >= im2.size[1]):
                im1, im2 = im2, im1

            file = Xmlfile(Config.resultseriesfile)
            resultChild = file.addChild(file.getRoot(), 'result')

            it = ImageTransformer(im2)
            starttime = time.time()
            n = 0
            results = []
            coordinates = []
            for i in range(im2.size[0] - im1.size[0] + 1):
                for j in range(im2.size[1] - im1.size[1] + 1):
                    mc = MetricCalculator(im1, it.crop([(i, j), (im1.size[0]+i, im1.size[1]+j)]))
                    method = getattr(mc, reversed[selected])
                    value = method()
                    n+=1
                    if not np.isnan(value):
                        results.append(value)
                        coordinates.append((i, j))

            maxvalue = Config.metricsProperties[reversed[selected]]['maxsim'](results)
            maxvalueCoordinates = coordinates[results.index(maxvalue)]

            stoptime = time.time()
            logging.debug(maxvalueCoordinates)
            file.addElement(resultChild, 'datetime', datetime.datetime.now().isoformat())
            file.addElement(resultChild, 'value', round(maxvalue, 5),
                            [('type', reversed[selected]),
                             ('time', round(stoptime - starttime, 5)),
                             ('coordinates', maxvalueCoordinates),
                             ('n_operations', n)])
            file.save()
            window.resultLabel.setText(f'Wynik: {maxvalue}\nCzas: {stoptime - starttime}s'
                                       f'\nLiczba operacji: {n}\nLewy górny piksel wzorca: {maxvalueCoordinates}')
            id = ImageDraw.Draw(im2)
            id.rectangle([maxvalueCoordinates, (maxvalueCoordinates[0]+im1.size[0], maxvalueCoordinates[1]+im1.size[1])],
                         outline='violet', width=3)
            window.showNearestPart(im2)
    except Exception as e:
        logerror()
def calculateAllMetricsButton(window):
    logging.debug("Wszystkie metryki")

    file = Xmlfile(Config.resultallfile)
    resultChild = file.addChild(file.getRoot(), 'result')

    file.addElement(resultChild, 'datetime', datetime.datetime.now().isoformat())
    text = ''
    mc = MetricCalculator(window.leftImageLabel.image, window.rightImageLabel.image)
    for metric, metricName in Config.availableMetrics.items():
        if(metric in Config.slowMetrics):
            continue
        mc.refreshImages()
        method = getattr(mc, metric)
        starttime = time.time()
        metricvalue = method()
        stoptime = time.time()
        file.addElement(resultChild, metric, round(metricvalue, 5), [('time',round(stoptime-starttime, 5))])
        text += f"{metricName}: {metricvalue:.3f} {Config.metricsProperties[metric]['range']}\n"

    file.save()
    window.showResult(text)


class Xmlfile:
    def __init__(self, path):
        if not os.path.exists(path):
            file = open(path, 'w')
            file.write('<?xml version="1.0" encoding="UTF-8"?><results></results>')
            file.close()

        self.path = path
        self.tree = ElementTree.parse(path)
        self.root = self.tree.getroot()

    def getRoot(self):
        return self.root

    def addChild(self, parent, name):
        child = ElementTree.SubElement(parent, name)
        return child

    def addElement(self, parent, tag, value, attributes = list()):
        el = ElementTree.SubElement(parent, tag)
        for key, val in attributes:
            el.set(key, str(val))
        el.text = str(value)

    def save(self):
        ElementTree.indent(self.root, space='\t', level=0)
        self.tree.write(self.path)