import logging


class Config:

    appname = 'Image Comarator'

    defaultImg = 'static/qwe.jpg'

    logfile = 'debug.log'
    logtarget = 'stdout'

    availableMetrics = {
        'pearson': 'Korelacja Pearsona',
        'tanimoto': 'Miara Tanimoto',
        'stochastic_sign_change': 'Stochastyczna zmiana znaku'
    }

    availableModifiers = {
        'gauss': 'Szum gaussa',
        'saltandpepper': 'Sól i pieprz',
        'gassianblur': 'Rozmycie gaussa'
    }