import random
import numpy as np
from PIL import Image
from PIL import ImageFilter
from copy import deepcopy
import logging

class NoiceHelper():
    def __init__(self, image):
        self.image = image

    def gauss(self, mi, sigma):
        imageArray = np.array(self.image)
        for height in range(imageArray.shape[0]):
            for width in range(imageArray.shape[1]):
                noice = round(random.gauss(mi, sigma))
                val = deepcopy(imageArray[height, width])
                imageArray[height, width] = [
                    addIntegersWithBounds(value, noice) for value in imageArray[height, width]]
                # print('[',noice,']', val, ' -> ', imageArray[height, width])
        return Image.fromarray(imageArray)

    def saltandpepper(self,  percent):
        part = percent / 100
        imageArray = np.array(self.image)
        for height in range(imageArray.shape[0]):
            for width in range(imageArray.shape[1]):
                for canal in range(imageArray.shape[2]):
                    r = random.random()
                    if(r < part):
                        blackorwhite = 255 if random.random() > .5 else 0
                        imageArray[height, width, canal] = blackorwhite
        return Image.fromarray(imageArray)

    def gassianblur(self, masksize = 3):
        return self.image.filter(ImageFilter.GaussianBlur(radius=masksize))

class ImageTransformer:
    def __init__(self, image):
        self.image = image

    def move(self, vector):
        return self.image.transform(self.image.size, Image.AFFINE, vector)

    def rotate(self, angle):
        return self.image.rotate(angle)

    def resize(self, size ,method):
        return self.image.resize(size, method)

    def crop(self, points):
        sizes = points[0][0], points[0][1], points[1][0], points[1][1]
        return self.image.crop(sizes)

def addIntegersWithBounds(a, b, minval = 0, maxval = 255):
    return int(min(max(minval, a+b), maxval))