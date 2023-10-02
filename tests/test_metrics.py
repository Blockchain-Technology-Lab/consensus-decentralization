from consensus_decentralization.metrics import entropy, gini, nakamoto_coefficient, herfindahl_hirschman_index
import numpy as np


def test_entropy():
    """
    Ensure that the results of the compute_entropy function are consistent with online calculators.
    Shannon entropy: https://www.omnicalculator.com/statistics/shannon-entropy
    Renyi entropy: https://github.com/dit/dit
    """
    shannon_entropy = entropy.compute_entropy(blocks_per_entity={'a': 1, 'b': 2, 'c': 3}, alpha=1)
    assert round(shannon_entropy, 3) == 1.459

    min_entropy = entropy.compute_entropy(blocks_per_entity={'a': 1, 'b': 2, 'c': 3}, alpha=-1)
    assert round(min_entropy, 3) == 1.0

    hartley_entropy = entropy.compute_entropy(blocks_per_entity={'a': 216, 'b': 432, 'c': 288, 'd': 64}, alpha=0)
    assert round(hartley_entropy, 3) == 2.0

    collision_entropy = entropy.compute_entropy(blocks_per_entity={'a': 216, 'b': 432, 'c': 288, 'd': 64}, alpha=2)
    assert round(collision_entropy, 3) == 1.642

    no_entropy = entropy.compute_entropy(blocks_per_entity={}, alpha=1)
    assert no_entropy is None

    no_entropy = entropy.compute_entropy(blocks_per_entity={'a': 0, 'b': 0}, alpha=1)
    assert no_entropy is None


def test_max_entropy():
    max_shannon_entropy = entropy.compute_max_entropy(num_entities=len({'a': 1, 'b': 2, 'c': 3}), alpha=1)
    assert round(max_shannon_entropy, 3) == 1.585

    no_max_entropy = entropy.compute_max_entropy(num_entities=0, alpha=1)
    assert no_max_entropy is None


def test_entropy_percentage():
    entropy_percentage = entropy.compute_entropy_percentage(blocks_per_entity={'a': 1, 'b': 2, 'c': 3}, alpha=1)
    assert round(entropy_percentage, 3) == 0.921

    no_entropy_percentage = entropy.compute_entropy_percentage(blocks_per_entity={}, alpha=1)
    assert no_entropy_percentage is None

    no_entropy_percentage = entropy.compute_entropy_percentage(blocks_per_entity={'a': 0, 'b': 0}, alpha=1)
    assert no_entropy_percentage is None


def test_gini():
    """
    Ensure that the results of the compute_entropy function are consistent with online calculators,
    such as https://goodcalculators.com/gini-coefficient-calculator/ (5 decimal accuracy)
    """
    decimals = 5

    g1 = gini.compute_gini(blocks_per_entity={'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5})
    assert round(g1, decimals) == 0.26667

    g2 = gini.gini(array=np.array([368, 156, 20, 7, 10, 49, 22, 1]))
    assert round(g2, decimals) == 0.67792

    g3 = gini.gini(array=np.array([11, 2, -1]))
    assert round(g3, decimals) == 0.53333

    g4 = gini.gini(array=np.array([1, 1, 3, 0, 0]))
    assert round(g4, decimals) == 0.56000

    g5 = gini.compute_gini(blocks_per_entity={})
    assert g5 is None

    g6 = gini.compute_gini(blocks_per_entity={'a': 0, 'b': 0})
    assert g6 is None


def test_nc():
    nc1 = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity={'a': 1, 'b': 2, 'c': 3})
    assert nc1 == 1

    nc2 = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity={'a': 1, 'b': 2, 'c': 3, 'd': 1, 'e': 1, 'f': 1})
    assert nc2 == 2

    nc3 = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity={'a': 1})
    assert nc3 == 1

    nc4 = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity={})
    assert nc4 is None

    nc5 = nakamoto_coefficient.compute_nakamoto_coefficient(blocks_per_entity={'a': 0, 'b': 0})
    assert nc5 is None


def test_hhi():
    # each participant produced 10% of the total blocks
    hhi1 = herfindahl_hirschman_index.compute_hhi(blocks_per_entity={'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'h': 1, 'i': 1, 'j': 1})
    assert hhi1 == 1000

    # 'a', 'b', 'c' and 'd' produced 40%, 30%, 15% and 15% respectively of the total blocks
    hhi2 = herfindahl_hirschman_index.compute_hhi(blocks_per_entity={'a': 8, 'b': 6, 'c': 3, 'd': 3})
    assert hhi2 == 2950

    # 'a' and 'b' each produced 50% of the total blocks
    hhi3 = herfindahl_hirschman_index.compute_hhi(blocks_per_entity={'a': 2, 'b': 2})
    assert hhi3 == 5000

    # 'a' produced 100% of the blocks
    hhi4 = herfindahl_hirschman_index.compute_hhi(blocks_per_entity={'a': 1})
    assert hhi4 == 10000

    hhi5 = herfindahl_hirschman_index.compute_hhi(blocks_per_entity={})
    assert hhi5 is None

    hhi5 = herfindahl_hirschman_index.compute_hhi(blocks_per_entity={'a': 0, 'b': 0})
    assert hhi5 is None
