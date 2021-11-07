import logging
from PIL import Image as ImageModule


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

def noicetypeChangedAction(dialogWindow):
    logging.debug("Zmiana typu szumu")
    pass