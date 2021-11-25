import random
import numpy as np
from PIL import Image
from PIL import ImageFilter
import logging

class NoiceHelper():
    def __init__(self, image):
        self.image = image

    def gauss(self, mi, sigma):
        imageArray = np.array(self.image)
        for height in range(imageArray.shape[0]):
            for width in range(imageArray.shape[1]):
                noice = random.gauss(mi, sigma)
                for canal in range(imageArray.shape[2]):
                    imageArray[height, width, canal] += noice
                    if(imageArray[height, width, canal] < 0):
                        imageArray[height, width, canal] = 0
                    elif(imageArray[height, width, canal] >= 255):
                        imageArray[height, width, canal] = 255
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