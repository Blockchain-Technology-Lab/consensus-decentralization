from src.metrics import entropy, gini, nakamoto_coefficient, herfindahl_hirschman_index, theil_index, centralization_level, parties, mining_power_ratio
import numpy as np


def test_entropy():
    """
    Ensure that the results of the compute_entropy function are consistent with online calculators.
    Shannon entropy: https://www.omnicalculator.com/statistics/shannon-entropy
    Renyi entropy: https://github.com/dit/dit
    """
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}

    shannon_entropy = entropy.compute_entropy(blocks_per_entity, 1)
    assert round(shannon_entropy, 3) == 1.459

    min_entropy = entropy.compute_entropy(blocks_per_entity, -1)
    assert round(min_entropy, 3) == 1.0

    blocks_per_entity = {'a': 216, 'b': 432, 'c': 288, 'd': 64}

    hartley_entropy = entropy.compute_entropy(blocks_per_entity, 0)
    assert round(hartley_entropy, 3) == 2.0

    collision_entropy = entropy.compute_entropy(blocks_per_entity, 2)
    assert round(collision_entropy, 3) == 1.642


def test_max_entropy():
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}

    max_shannon_entropy = entropy.compute_max_entropy(len(blocks_per_entity), 1)
    assert round(max_shannon_entropy, 3) == 1.585


def test_entropy_percentage():
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}

    entropy_percentage = entropy.compute_entropy_percentage(blocks_per_entity, 1)
    assert round(entropy_percentage, 3) == 0.921


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
    coeff = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity)
    assert coeff == 1

    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3, 'd': 1, 'e': 1, 'f': 1}
    coeff = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity)
    assert coeff == 2

    blocks_per_entity = {'a': 1}
    coeff = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity)
    assert coeff == 1


def test_hhi():
    # each participant produced 10% of the total blocks
    blocks_per_entity = {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'h': 1, 'i': 1, 'j': 1}
    hhi = herfindahl_hirschman_index.compute_hhi(blocks_per_entity)
    assert hhi == 1000

    # 'a', 'b', 'c' and 'd' produced 40%, 30%, 15% and 15% respectively of the total blocks
    blocks_per_entity = {'a': 8, 'b': 6, 'c': 3, 'd': 3}
    hhi = herfindahl_hirschman_index.compute_hhi(blocks_per_entity)
    assert hhi == 2950

    blocks_per_entity = {'a': 2, 'b': 2}  # 'a' and 'b' each produced 50% of the total blocks
    hhi = herfindahl_hirschman_index.compute_hhi(blocks_per_entity)
    assert hhi == 5000

    blocks_per_entity = {'a': 1}  # 'a' produced 100% of the blocks
    hhi = herfindahl_hirschman_index.compute_hhi(blocks_per_entity)
    assert hhi == 10000

def test_theil():
    """
    Ensure that the results of the compute_theil function are consistent with the definition (5 decimal accuracy).
    """
    decimals = 5

    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}
    theil_t = theil_index.compute_theil(blocks_per_entity, 1)
    assert round(theil_t, decimals) == 0.08721
    theil_l = theil_index.compute_theil(blocks_per_entity, 0)
    assert round(theil_l, decimals) == 0.09589

    blocks_per_entity = {'a': 0, 'b': 0, 'c': 12, 'd': 432}
    theil_t = theil_index.compute_theil(blocks_per_entity, 1)
    assert round(theil_t, decimals) == 0.5689
    theil_l = theil_index.compute_theil(blocks_per_entity, 0)
    assert round(theil_l, decimals) == 1.12601

def test_cl():
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}
    cl = centralization_level.compute_centralization_level(blocks_per_entity, 0.5)
    assert cl == 1
    cl = centralization_level.compute_centralization_level(blocks_per_entity, 0.33)
    assert cl == 2

    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3, 'd': 1, 'e': 1, 'f': 1}
    cl = centralization_level.compute_centralization_level(blocks_per_entity, 0.5)
    assert cl == 2
    cl = centralization_level.compute_centralization_level(blocks_per_entity, 0.33)
    assert cl == 4

    blocks_per_entity = {'a': 1}
    cl = centralization_level.compute_centralization_level(blocks_per_entity, 0.5)
    assert cl == 1
    cl = centralization_level.compute_centralization_level(blocks_per_entity, 0.33)
    assert cl == 1

def test_parties():
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}
    numpart = parties.compute_num_parties(blocks_per_entity)
    assert numpart == 3

    blocks_per_entity = {'a': 0, 'b': 2, 'c': 3, 'd': 0, 'e': 1, 'f': 1}
    numpart = parties.compute_num_parties(blocks_per_entity)
    assert numpart == 4

def test_mpr():
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}
    mpr = mining_power_ratio.compute_mining_power_ratio(blocks_per_entity)
    assert mpr == 0.5

    blocks_per_entity = {'a': 3, 'b': 3, 'c': 0}
    mpr = mining_power_ratio.compute_mining_power_ratio(blocks_per_entity)
    assert mpr == 0.5
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}
    decimals = 5

    theil_t = theil.compute_theil(blocks_per_entity, 1)
    assert round(theil_t, decimals) == 0.08721

    theil_l = theil.compute_theil(blocks_per_entity, 0)
    assert round(theil_l, decimals) == 0.09589

    blocks_per_entity = {'a': 0, 'b': 0, 'c': 0, 'd': 432}

    theil_t = theil.compute_theil(blocks_per_entity, 1)
    assert round(theil_t, decimals) == 1.38629
