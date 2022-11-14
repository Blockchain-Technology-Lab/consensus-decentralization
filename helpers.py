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


def compute_nc(blocks_per_pool):
    nc = [0, 0]
    for (name, blocks) in sorted(blocks_per_pool.items(), key=lambda x: x[1], reverse=True):
        if nc[1] < 50:
            nc[0] += 1
            nc[1] += 100 * blocks / sum([i[1] for i in blocks_per_pool.items()])
        else:
            return nc
