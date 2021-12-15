import logging
from PIL import Image
from exceptions import DifferentSizeException
import numpy as np
from PIL import ImageOps
import copy
import traceback
from scipy import stats
import math

class MetricCalculator:
    def __init__(self, image1, image2):
        self.MODE_GRAYSCALE = 1
        self.MODE_CANAlAVG = 2

        self.image1 = image1
        self.image2 = image2

        self.image1Gray = ImageOps.grayscale(self.image1)
        self.image2Gray = ImageOps.grayscale(self.image2)

        self.image1Array = np.array(self.image1Gray)
        self.image2Array = np.array(self.image2Gray)

        self.n = len(self.image1Array.flat)

        if(self.image1Array.shape[0] != self.image2Array.shape[0]) or (self.image1Array.shape[1] != self.image2Array.shape[1]):
            raise DifferentSizeException()

    def refreshImages(self):
        self.image1Array = np.array(ImageOps.grayscale(self.image1))
        self.image2Array = np.array(ImageOps.grayscale(self.image2))

    def pearson(self):
        return stats.pearsonr(self.image1Array.flat, self.image2Array.flat)[0]

    def old_pearson(self):
        img1flatten = self.image1Array.flat
        img2flatten = self.image2Array.flat
        mi1 = np.mean(img1flatten)
        sigma1 = np.std(img1flatten)
        mi2 = np.mean(img2flatten)
        sigma2 = np.std(img2flatten)
        result = 0
        for i in range(self.n):
            result += ((img1flatten[i] - mi1)/sigma1)*((img2flatten[i] - mi2)/sigma2)
        return result / self.n

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
        return result / self.n

    def spearman_rho(self):
        return stats.spearmanr(self.image1Array.flat, self.image2Array.flat).correlation

    def old_spearman_rho(self):
        try:
            rankImage1 = ImageHelper.getRankArray(self.image1Array)
            rankImage2 = ImageHelper.getRankArray(self.image2Array)
            rankdiffsquared = 0
            for x, y in zip(rankImage1.flat, rankImage2.flat):
                rankdiffsquared += (x-y)*(x-y)
            return 6*rankdiffsquared / (self.n*(self.n*self.n-1))
        except Exception as e:
            print(traceback.format_exc())


    def kandell_tau(self):
        return stats.kendalltau(self.image1Array.flat, self.image2Array.flat).correlation

    def old_kandell_tau(self):
        img1flatten = self.image1Array.flatten().astype(np.float16)
        img2flatten = self.image2Array.flatten().astype(np.float16)
        Nc = 0 # ilosc concordance
        Nd = 0 # ilosc discordance
        n = self.n
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if (img1flatten[j] - img1flatten[i]) * (img2flatten[j] - img2flatten[i]) >= 0:
                    Nc+=1
                else:
                    Nd+=1
        return (Nc - Nd) / (n*(n-1)/2)

    def greatest_deviation(self):
        image1Ranks = stats.rankdata(self.image1Array.flat, method='ordinal')
        image2Ranks = stats.rankdata(self.image2Array.flat, method='ordinal')
        n = len(self.image1Array.flat)
        maxd = 0
        maxD = 0
        for i in range(len(image1Ranks)):
            di = 0
            Di = 0
            for j in range(i):
                di += 1 if (image1Ranks[i] <= i < image2Ranks[j]) else 0
                Di += 1 if (n + 1 - image1Ranks[i]) > image2Ranks[i] else 0
            if(di > maxd):
                maxd = di
            if(Di > maxD):
                maxD = Di
        return (maxD - maxd) / (n/2)

    def ordinal_measure(self):
        image1Ranks = stats.rankdata(self.image1Array.flat, method='ordinal')
        image2Ranks = stats.rankdata(self.image2Array.flat, method='ordinal')
        n = len(self.image1Array.flat)
        maxD = 0
        for i in range(len(image1Ranks)):
            Di = 0
            for j in range(i):
                Di += 1 if (n + 1 - image1Ranks[i]) > image2Ranks[j] else 0
            if(Di > maxD):
                maxD = Di
        return (maxD) / (n/2)

    def correlation_ratio(self):
        #konieczna modyfikacja bo często D2 > 1
        sigma2 = []
        ns = []
        image1flatten = self.image1Array.flatten() / 255
        image2flatten = self.image2Array.flatten() / 255
        for i in range(0, 255):
            wheree = np.argwhere(image1flatten == (i / 255))
            if len(wheree) == 0:
                sigma2.append(0)
                ns.append(0)
                continue
            mean = 0.0
            for j in wheree:
                mean += image2flatten[j[0]]
            mean = mean / len(wheree)
            s = 0
            for j in wheree:
                s += (image2flatten[j[0]] - mean)**2
            s = s / len(wheree)
            sigma2.append(s)
            ns.append(len(wheree))
        n = sum(ns)
        D2 = sum([ni * s2 for ni, s2 in zip(ns, sigma2)])/n
        return (1 - D2)**(1/2)

    def eojpd(self):
        im1hist = np.array(self.image1Gray.histogram()).astype('float64')
        im1hist = np.array(im1hist, ndmin=2).T / np.sum(im1hist).astype('float64')
        im2hist = self.image2Gray.histogram()
        im2hist = np.array(im2hist, ndmin=2) / np.sum(im2hist).astype('float64')

        jpd = np.dot(im1hist, im2hist)
        jpdsq = np.square(jpd)
        return np.sum(jpdsq)

    def shannon_mutual_info(self):
        im1hist = np.array(self.image1Gray.histogram())
        im1hist = np.array(im1hist, ndmin=2).T / np.sum(im1hist).astype('float64')
        im2hist = self.image2Gray.histogram()
        im2hist = np.array(im2hist, ndmin=2) / np.sum(im2hist).astype('float64')

        jpd = np.dot(im1hist, im2hist)

        shannon = []
        for i in range(jpd.shape[0]):
            for j in range(jpd.shape[1]):
                sumofint = (np.sum(jpd[i, :]) * np.sum(jpd[:, j]))
                if(sumofint == 0):
                    continue
                logthing = jpd[i, j] / sumofint
                print(logthing)
                if(logthing <=0):
                    continue
                shannon.append(jpd[i, j] * np.log2(logthing))
        return np.nansum(shannon)



class ImageHelper:
    @staticmethod
    def getRankArray(imageArray):
        countArr = np.zeros((1, 256))[0]
        for height in range(imageArray.shape[0]):
            for width in range(imageArray.shape[1]):
                countArr[imageArray[height, width]] += 1
        pixelNumber = 1
        resultImg = copy.deepcopy(imageArray).astype(np.float16)
        for i in range(len(countArr)):
            countInfo = countArr[i]
            rank = sum(np.arange(pixelNumber, int(pixelNumber+countInfo))) / countInfo
            np.where((resultImg == i), rank, resultImg)
            pixelNumber+=1
        print(resultImg)
        return resultImg
