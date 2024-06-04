import numpy as np


def compute_gini(block_distribution):
    """
    Calculates the Gini coefficient of a distribution of blocks to entities
    :param block_distribution: a list of integers, each being the blocks that an entity has produced, sorted in descending order
    :returns: a float that represents the Gini coefficient of the given distribution or None if the data is empty
    """
    if sum(block_distribution) == 0:
        return None
    array = np.array(block_distribution)
    return gini(array)


def gini(array):
    """
    Calculates the Gini coefficient of a distribution
    Source: https://github.com/oliviaguest/gini
    :param array: a numpy array with entities and the blocks they have produced
    :returns: a float that represents the Gini coefficient of the given distribution
    """
    array = array.flatten()
    if np.amin(array) < 0:
        # Values cannot be negative:
        array -= np.amin(array)
    array = np.sort(array)
    index = np.arange(1, array.shape[0] + 1)
    n = array.shape[0]
    return (np.sum((2 * index - n - 1) * array)) / (n * np.sum(array))
