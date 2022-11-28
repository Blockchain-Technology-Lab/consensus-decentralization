import numpy as np


def compute_gini(lst):
    array = np.array(lst)

    """
    Calculate the Gini coefficient of a numpy array.
    Source: https://github.com/oliviaguest/gini
    """
    array = array.flatten()
    if np.amin(array) < 0:
        # Values cannot be negative:
        array -= np.amin(array)
    array = np.sort(array)
    index = np.arange(1,array.shape[0]+1)
    n = array.shape[0]
    return ((np.sum((2 * index - n  - 1) * array)) / (n * np.sum(array)))
