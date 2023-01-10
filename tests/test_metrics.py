from src.metrics import entropy, gini, nakamoto_coefficient
import numpy as np


def test_entropy():
    """
    Ensure that the results of the compute_entropy function are consistent with online calculators,
    such as https://www.omnicalculator.com/statistics/shannon-entropy
    """
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}
    ntrp = entropy.compute_entropy(blocks_per_entity)
    assert round(ntrp, 3) == 1.459


def test_gini():
    """
    Ensure that the results of the compute_entropy function are consistent with online calculators,
    such as https://goodcalculators.com/gini-coefficient-calculator/ (5 decimal accuracy)
    """
    decimals = 5

    x1 = np.array([1, 2, 3, 4, 5])
    g1 = gini.gini(x1)
    assert round(g1, decimals) == 0.26667

    x2 = np.array([368, 156, 20, 7, 10, 49, 22, 1])
    g2 = gini.gini(x2)
    assert round(g2, decimals) == 0.67792

    x3 = np.array([11, 2, 1])
    g3 = gini.gini(x3)
    assert round(g3, decimals) == 0.47619

    x5 = np.array([1, 1, 3, 0, 0])
    g5 = gini.gini(x5)
    assert round(g5, decimals) == 0.56000


def test_nc():
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}
    coeff, power_percentage = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity)
    assert coeff == 1

    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3, 'd': 1, 'e': 1, 'f': 1}
    coeff, power_percentage = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity)
    assert coeff == 2
