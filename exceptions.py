import logging

def debugactionwrapper(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(str(e))
    return inner


class DifferentSizeException(Exception):
    def __init__(self):
        super(DifferentSizeException, self).__init__()
        self.message = 'Rozny rozmiar obrazow'