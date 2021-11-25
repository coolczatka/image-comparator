import logging
from PIL import Image
from exceptions import DifferentSizeException
import numpy as np
from PIL import ImageOps
import copy
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
        self.image1Array = self.image1Array.astype(np.int16)
        self.image2Array = self.image2Array.astype(np.int16)
        multiplied = np.sum(np.multiply(img1flatten, img2flatten))
        return multiplied / (np.linalg.norm(np.subtract(self.image1Array, self.image2Array))**2 + multiplied)

    def stochastic_sign_change(self):
        self.image1Array = self.image1Array.astype(np.int16)
        self.image2Array = self.image2Array.astype(np.int16)
        difference = np.subtract(self.image1Array, self.image2Array)
        steps = 0
        signChangeCounter = 0
        for height in range(difference.shape[0]):
            sign = 1
            for width in range(difference.shape[1]):
                currentSign = 1 if difference[height, width] >= 0 else -1
                if sign != currentSign:
                    signChangeCounter += 1
                steps+=1
                sign = currentSign
        return signChangeCounter / steps

    def deterministic_sign_change(self):
        q = 10
        for height in range(self.image2Array.shape[0]):
            for width in range(self.image2Array.shape[1]):
                self.image2Array[height, width] += q*((-1)**(height+width))
        return self.stochastic_sign_change()

    def minimum_ratio(self):
        result = 0
        for height in range(self.image1Array.shape[0]):
            for width in range(self.image1Array.shape[1]):
                try:
                    result += min(self.image1Array[height, width]/self.image2Array[height, width],
                                self.image2Array[height, width]/self.image1Array[height, width])
                except (ZeroDivisionError, RuntimeWarning):
                    pass
        return result / len(self.image1Array.flat)

    def spearman_rho(self):
        pass

    def kandell_tau(self):
        img1flatten = self.image1Array.flatten().astype(np.float16)
        img2flatten = self.image2Array.flatten().astype(np.float16)
        Nc = 0 # ilosc concordance
        Nd = 0 # ilosc discordance
        n = len(img1flatten)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if (img1flatten[j] - img1flatten[i]) * (img2flatten[j] - img2flatten[i]) >= 0:
                    Nc+=1
                else:
                    Nd+=1
        return (Nc - Nd) / (n*(n-1)/2)