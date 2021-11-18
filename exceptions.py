
class DifferentSizeException(Exception):
    def __init__(self):
        super(DifferentSizeException, self).__init__()
        self.message = 'Rozny rozmiar obrazow'