import numpy as np
import sys
import src.helpers.helper as hlp


def compute_gini(blocks_per_entity):
    """
    Calculate the Gini coefficient of a distribution
    param blocks_per_entity must be a dictionary
    """
    array = np.array(list(blocks_per_entity.values()))
    return gini(array)

def gini(array):
    """
    Calculate the Gini coefficient of a numpy array
    Source: https://github.com/oliviaguest/gini
    """
    array = array.flatten()
    if np.amin(array) < 0:
        # Values cannot be negative:
        array -= np.amin(array)
    array = np.sort(array)
    index = np.arange(1, array.shape[0] + 1)
    n = array.shape[0]
    return (np.sum((2 * index - n - 1) * array)) / (n * np.sum(array))


if __name__ == '__main__':
    filename = sys.argv[1]
    blocks_per_entity = hlp.get_blocks_per_entity_from_file(filename)
    print(f'Gini: {compute_gini(blocks_per_entity)}')