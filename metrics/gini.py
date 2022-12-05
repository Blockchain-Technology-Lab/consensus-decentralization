import numpy as np
import sys


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


if __name__ == '__main__':
    filename = sys.argv[1]
    blocks_per_entity = {}
    with open(filename) as f:
        for idx, line in enumerate(f.readlines()):
            if idx > 0:
                row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                blocks_per_entity[row[0]] = int(row[1])

    print('Gini:', compute_gini(list(blocks_per_entity.values())))
