from src.metrics import entropy, gini, nakamoto_coefficient
import numpy as np


def test_entropy():
    """
    Ensure that the results of the compute_entropy function are consistent with online calculators,
    such as https://www.omnicalculator.com/statistics/shannon-entropy

    TODO: add tests for other entropies (alpha = {0, 2, -1}
    """
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}
    shannon_ntrp = entropy.compute_entropy(blocks_per_entity, 1)
    assert round(shannon_ntrp, 3) == 1.459


def test_gini():
    """
    Ensure that the results of the compute_entropy function are consistent with online calculators,
    such as https://goodcalculators.com/gini-coefficient-calculator/ (5 decimal accuracy)
    """
    decimals = 5

    x1 = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
    g1 = gini.compute_gini(x1)
    assert round(g1, decimals) == 0.26667

    x2 = np.array([368, 156, 20, 7, 10, 49, 22, 1])
    g2 = gini.gini(x2)
    assert round(g2, decimals) == 0.67792

    x3 = np.array([11, 2, -1])
    g3 = gini.gini(x3)
    assert round(g3, decimals) == 0.53333

    x4 = np.array([1, 1, 3, 0, 0])
    g4 = gini.gini(x4)
    assert round(g4, decimals) == 0.56000


def test_nc():
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}
    coeff, power_percentage = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity)
    assert coeff == 1

    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3, 'd': 1, 'e': 1, 'f': 1}
    coeff, power_percentage = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity)
    assert coeff == 2

    blocks_per_entity = {'a': 1}
    coeff, power_percentage = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity)
    assert coeff == 1
