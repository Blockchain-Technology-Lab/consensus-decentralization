from consensus_decentralization.metrics import entropy, gini, nakamoto_coefficient, herfindahl_hirschman_index
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

    no_entropy = entropy.compute_entropy({}, 1)
    assert no_entropy is None


def test_max_entropy():
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}

    max_shannon_entropy = entropy.compute_max_entropy(len(blocks_per_entity), 1)
    assert round(max_shannon_entropy, 3) == 1.585

    no_max_entropy = entropy.compute_max_entropy(0, 1)
    assert no_max_entropy is None


def test_entropy_percentage():
    blocks_per_entity = {'a': 1, 'b': 2, 'c': 3}

    entropy_percentage = entropy.compute_entropy_percentage(blocks_per_entity, 1)
    assert round(entropy_percentage, 3) == 0.921

    no_entropy_percentage = entropy.compute_entropy_percentage({}, 1)
    assert no_entropy_percentage is None


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

    no_g = gini.compute_gini({})
    assert no_g is None


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

    no_coeff = nakamoto_coefficient.compute_nakamoto_coefficient({})
    assert no_coeff is None


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

    no_hhi = herfindahl_hirschman_index.compute_hhi({})
    assert no_hhi is None
