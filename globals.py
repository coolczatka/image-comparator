import logging


class Config:

    appname = 'Image Comarator'

    defaultImg = 'static/qwe.jpg'

    logfile = 'debug.log'
    logtarget = 'stdout'

    availableMetrics = {
        'pearson': 'Pearson'
    }

    availableNoices = {
        'gauss': 'Szum gaussa',
        'saltandpepper': 'Sól i pieprz'
    }