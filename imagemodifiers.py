import random
import numpy as np
from PIL import Image

import logging

class NoiceHelper():
    def __init__(self, image):
        self.image = image

    def gauss(self, mi, sigma):
        imageArray = np.array(self.image)
        for height in range(imageArray.shape[0]):
            for width in range(imageArray.shape[1]):
                for canal in range(imageArray.shape[2]):
                    imageArray[height, width, canal] += random.gauss(mi, sigma)
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
