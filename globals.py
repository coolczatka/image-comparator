import logging

import numpy as np


class Config:

    appname = ''

    defaultImg = 'static/entropy.png'

    logfile = 'debug.log'
    logtarget = 'stdout'

    resultfile = 'result.xml'
    resultallfile = 'resultall.xml'
    resultseriesfile = 'resultseries.xml'

    availableMetrics = {
        'pearson': 'Korelacja Pearsona',
        'tanimoto': 'Miara Tanimoto',
        'stochastic_sign_change': 'Stochastyczna zmiana znaku',
        'deterministic_sign_change': 'Deterministyczna zmiana znaku',
        'minimum_ratio': 'Stosunek minimów',
        'spearman_rho': 'Współczynnik Spearmana',
        'kandell_tau': 'Współczynnik Kandalla',
        # 'greatest_deviation': 'Największe odchylenie',
        # 'ordinal_measure': 'Miara porządkowa',
        # 'correlation_ratio': 'Stosunek korelacji',
        'eojpd': 'Energia wspólnego rozkładu prawdopodobieństwa', # brak górnego zakresu - im wyższe tym bardziej podobne
        #'material_similarity': 'Podobieństwo materiałów',
        'shannon_mutual_info': 'Informacja wzajemna Shannona',
        # 'renyi_mutual_info': 'Obustronna informacja Renyi',
        # 'tsallis_mutual_info': 'Obustronna informacja Tsallis',
        #'f_info_measures': 'Miara f informacji',
    }
    metricsProperties = {
        'pearson': {
            'range': (0, 1),
            'maxsim': lambda x : max(np.abs(x)),
        },
        'tanimoto': {
            'range': (0, 1),
            'maxsim': lambda x : max(np.abs(x)),
        },
        'stochastic_sign_change': {
            'range': (0, 1),
            'maxsim': max,
        },
        'deterministic_sign_change': {
            'range': (0, 1),
            'maxsim': max,
        },
         'minimum_ratio': {
            'range': (0, 1),
            'maxsim': max,
        },
        'spearman_rho': {
            'range': (0, 1),
            'maxsim': lambda x : max(np.abs(x)),
        },
        'kandell_tau': {
            'range': (0, 1),
            'maxsim': lambda x : max(np.abs(x)),
        },
        'eojpd': {
            'range': (0, np.inf),
            'maxsim': min,
        },
        'shannon_mutual_info': {
            'range': (0, 1),
            'maxsim': max,
        }
    }
    slowMetrics = ['greatest_deviation', 'ordinal_measure']
    availableModifiers = {
        'gauss': 'Szum gaussa',
        'saltandpepper': 'Sól i pieprz',
        'gassianblur': 'Rozmycie gaussa'
    }

