import logging
from PIL import Image
from exceptions import DifferentSizeException
import numpy as np
from PIL import ImageOps

class MetricCalculator:
    def __init__(self, image1, image2):
        self.MODE_GRAYSCALE = 1
        self.MODE_CANAlAVG = 2

        self.image1 = image1
        self.image2 = image2

        self.image1Array = np.array(ImageOps.grayscale(self.image1))
        self.image2Array = np.array(ImageOps.grayscale(self.image2))

        if(self.image1Array.shape[0] != self.image2Array.shape[0]) or (self.image1Array.shape[1] != self.image2Array.shape[1]):
            raise DifferentSizeException()

    def pearson(self):
        img1flatten = self.image1Array.flat
        img2flatten = self.image2Array.flat
        mi1 = np.mean(img1flatten)
        sigma1 = np.std(img1flatten)
        mi2 = np.mean(img2flatten)
        sigma2 = np.std(img2flatten)
        result = 0
        for i in range(len(img1flatten)):
            result += ((img1flatten[i] - mi1)/sigma1)*((img2flatten[i] - mi2)/sigma2)
        return result / len(img1flatten)

    def tanimoto(self):
        img1flatten = self.image1Array.flat
        img2flatten = self.image2Array.flat
        multiplied = np.sum(np.multiply(img1flatten, img2flatten))
        return multiplied / (np.linalg.norm(np.subtract(self.image1Array, self.image2Array))**2 + multiplied)

    def stochastic_sign_change(self):
        difference = np.subtract(self.image1Array, self.image2Array)
        steps = 0
        signChangeCounter = 0
        for height in range(difference.shape[0]):
            sign = 0
            for width in range(difference.shape[1]):
                currentSing = 1 if difference[height, width] > 0 else -1
                if sign != currentSing:
                    signChangeCounter += 1
                steps+=1
                sign = currentSing
        return signChangeCounter / steps
