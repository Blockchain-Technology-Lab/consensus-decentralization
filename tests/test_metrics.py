from consensus_decentralization.metrics import (entropy, gini, nakamoto_coefficient, herfindahl_hirschman_index,
                                                theil_index, max_power_ratio, tau_index, total_entities)
import numpy as np


def test_entropy():
    """
    Ensure that the results of the compute_entropy function are consistent with online calculators.
    Shannon entropy: https://www.omnicalculator.com/statistics/shannon-entropy
    Renyi entropy: https://github.com/dit/dit
    """
    shannon_entropy = entropy.compute_entropy([3, 2, 1], 1)
    assert round(shannon_entropy, 3) == 1.459

    min_entropy = entropy.compute_entropy([3, 2, 1], -1)
    assert round(min_entropy, 3) == 1.0

    hartley_entropy = entropy.compute_entropy([432, 288, 216, 64], 0)
    assert round(hartley_entropy, 3) == 2.0

    collision_entropy = entropy.compute_entropy([432, 288, 216, 64], 2)
    assert round(collision_entropy, 3) == 1.642

    no_entropy = entropy.compute_entropy([], 1)
    assert no_entropy is None

    no_entropy = entropy.compute_entropy([0, 0], 1)
    assert no_entropy is None


def test_max_entropy():
    max_shannon_entropy = entropy.compute_max_entropy(num_entities=len([3, 2, 1]), alpha=1)
    assert round(max_shannon_entropy, 3) == 1.585

    no_max_entropy = entropy.compute_max_entropy(num_entities=0, alpha=1)
    assert no_max_entropy is None


def test_entropy_percentage():
    entropy_percentage = entropy.compute_entropy_percentage([3, 2, 1], 1)
    assert round(entropy_percentage, 3) == 0.921

    no_entropy_percentage = entropy.compute_entropy_percentage([], 1)
    assert no_entropy_percentage is None

    no_entropy_percentage = entropy.compute_entropy_percentage([0, 0], 1)
    assert no_entropy_percentage is None


def test_gini():
    """
    Ensure that the results of the compute_entropy function are consistent with online calculators,
    such as https://goodcalculators.com/gini-coefficient-calculator/ (5 decimal accuracy)
    """
    decimals = 5

    g1 = gini.compute_gini([5, 4, 3, 2, 1])
    assert round(g1, decimals) == 0.26667

    g2 = gini.gini(array=np.array([368, 156, 20, 7, 10, 49, 22, 1]))
    assert round(g2, decimals) == 0.67792

    g3 = gini.gini(array=np.array([11, 2, -1]))
    assert round(g3, decimals) == 0.53333

    g4 = gini.gini(array=np.array([1, 1, 3, 0, 0]))
    assert round(g4, decimals) == 0.56000

    g5 = gini.compute_gini([])
    assert g5 is None

    g6 = gini.compute_gini([0, 0])
    assert g6 is None


def test_nc():
    nc1 = nakamoto_coefficient.compute_nakamoto_coefficient([3, 2, 1])
    assert nc1 == 1

    nc2 = nakamoto_coefficient.compute_nakamoto_coefficient([3, 2, 1, 1, 1, 1])
    assert nc2 == 2

    nc3 = nakamoto_coefficient.compute_nakamoto_coefficient([1])
    assert nc3 == 1

    nc4 = nakamoto_coefficient.compute_nakamoto_coefficient([])
    assert nc4 is None

    nc5 = nakamoto_coefficient.compute_nakamoto_coefficient([0, 0])
    assert nc5 is None


def test_hhi():
    # each participant produced 10% of the total blocks
    hhi1 = herfindahl_hirschman_index.compute_hhi([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    assert hhi1 == 1000

    # 'a', 'b', 'c' and 'd' produced 40%, 30%, 15% and 15% respectively of the total blocks
    hhi2 = herfindahl_hirschman_index.compute_hhi([8, 6, 3, 3])
    assert hhi2 == 2950

    # 'a' and 'b' each produced 50% of the total blocks
    hhi3 = herfindahl_hirschman_index.compute_hhi([2, 2])
    assert hhi3 == 5000

    # 'a' produced 100% of the blocks
    hhi4 = herfindahl_hirschman_index.compute_hhi([1])
    assert hhi4 == 10000

    hhi5 = herfindahl_hirschman_index.compute_hhi([])
    assert hhi5 is None

    hhi5 = herfindahl_hirschman_index.compute_hhi([0, 0])
    assert hhi5 is None


def test_compute_theil_index():
    """
    Ensure that the results of the compute_theil_index function are consistent with online calculators,
    such as: http://www.poorcity.richcity.org/calculator/
    """
    decimals = 3

    theil_t = theil_index.compute_theil_index([3, 2, 1])
    assert round(theil_t, decimals) == 0.087

    theil_t = theil_index.compute_theil_index([3, 2, 1, 1, 1, 1])
    assert round(theil_t, decimals) == 0.115

    theil_t = theil_index.compute_theil_index([432, 0, 0, 0])
    assert round(theil_t, decimals) == 1.386

    theil_t = theil_index.compute_theil_index([432])
    assert round(theil_t, decimals) == 0

    theil_t = theil_index.compute_theil_index([])
    assert theil_t == 0


def test_compute_max_power_ratio():
    max_mpr = max_power_ratio.compute_max_power_ratio([3, 2, 1])
    assert max_mpr == 0.5

    max_mpr = max_power_ratio.compute_max_power_ratio([3, 2, 1, 1, 1, 1])
    assert max_mpr == 1 / 3

    max_mpr = max_power_ratio.compute_max_power_ratio([1])
    assert max_mpr == 1

    max_mpr = max_power_ratio.compute_max_power_ratio([1, 1, 1])
    assert max_mpr == 1 / 3

    max_mpr = max_power_ratio.compute_max_power_ratio([])
    assert max_mpr == 0


def test_tau_33():
    tau_idx = tau_index.compute_tau_index([3, 2, 1], threshold=0.33)
    assert tau_idx == 1

    tau_idx = tau_index.compute_tau_index([3, 2, 1, 1, 1, 1], threshold=0.33)
    assert tau_idx == 1

    tau_idx = tau_index.compute_tau_index([1], threshold=0.33)
    assert tau_idx == 1

    tau_idx = tau_index.compute_tau_index([], threshold=0.33)
    assert tau_idx is None


def test_tau_66():
    tau_idx = tau_index.compute_tau_index([3, 2, 1], threshold=0.66)
    assert tau_idx == 2

    tau_idx = tau_index.compute_tau_index([3, 2, 1, 1, 1, 1], threshold=0.66)
    assert tau_idx == 3

    tau_idx = tau_index.compute_tau_index([1], threshold=0.66)
    assert tau_idx == 1


def test_total_entities():
    entity_count = total_entities.compute_total_entities(block_distribution=[1, 2, 3])
    assert entity_count == 3

    entity_count = total_entities.compute_total_entities(block_distribution=[0])
    assert entity_count == 0

    entity_count = total_entities.compute_total_entities(block_distribution=[5, 0, 0])
    assert entity_count == 1
