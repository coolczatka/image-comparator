from PIL import Image
from exceptions import DifferentSizeException
class MetricCalculator:
    def __init__(self, image1, image2):
        self.image1 = image1
        self.image2 = image2

        if(self.image1.size[0] != self.image2.size[0]) or (self.image1.size[1] != self.image2.size[1]):
            raise DifferentSizeException()

    def pearson(self):
        image1arr = self.image1.toArray()
        print(image1arr)