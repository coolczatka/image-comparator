import logging


class Config:

    appname = 'Image Comarator'

    defaultImg = 'static/qwe.jpg'

    logfile = 'debug.log'
    logtarget = 'stdout'

    availableMetrics = {
        'pearson': 'Korelacja Pearsona',
        'tanimoto': 'Miara Tanimoto',
        'stochastic_sign_change': 'Stochastyczna zmiana znaku',
        'deterministic_sign_change': 'Deterministyczna zmiana znaku',
        'minimum_ratio': 'Stosunek minimów',
        #'spearman_rho': 'Współczynnik Spearmana',
        'kandell_tau': 'Współczynnik Kandalla',
        #'greatest_deviation': 'Największe odchylenie',
        #'ordinal_measure': 'Miara porządkowa',
        #'correlation_ratio': 'Stosunek korelacji',
        #'eojpd': 'Energia wspólnego rozkładu prawdopodobieństwa',
        #'material_similarity': 'Podobieństwo materiałów',
        #'shannon_mutual_info': 'Obustronna informacja Shannona',
        #'renyi_mutual_info': 'Obustronna informacja Renyi',
        #'tsallis_mutual_info': 'Obustronna informacja Tsallis',
        #'f_info_measures': 'Miara f informacji',
    }
    slowMetrics = ['kandell_tau']
    availableModifiers = {
        'gauss': 'Szum gaussa',
        'saltandpepper': 'Sól i pieprz',
        'gassianblur': 'Rozmycie gaussa'
    }