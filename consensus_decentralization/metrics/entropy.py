from math import log
from consensus_decentralization.metrics.total_entities import compute_total_entities


def compute_entropy(block_distribution, alpha):
    """
    Calculates the entropy of a distribution of blocks to entities
    Pi is the relative frequency of each entity.
    Renyi entropy: 1/(1-alpha) * log2 (sum (Pi**alpha))
    Shannon entropy (alpha=1): −sum P(Si) log2 (Pi)
    Min entropy (alpha=-1): -log max Pi
    :param block_distribution: a list of integers, each being the blocks that an entity has produced, sorted in descending order
    :param alpha: the entropy parameter (depending on its value the corresponding entropy measure is used)
    :returns: a float that represents the entropy of the data or None if the data is empty
    """
    all_blocks = sum(block_distribution)
    if all_blocks == 0:
        return None
    if alpha == 1:
        entropy = 0
        for value in block_distribution:
            rel_freq = value / all_blocks
            if rel_freq > 0:
                entropy -= rel_freq * log(rel_freq, 2)
    else:
        if alpha == -1:
            entropy = - log(max(block_distribution)/all_blocks, 2)
        else:
            sum_freqs = 0
            for entry in block_distribution:
                sum_freqs += pow(entry/all_blocks, alpha)
            entropy = log(sum_freqs, 2) / (1 - alpha)

    return entropy


def compute_max_entropy(num_entities, alpha):
    return compute_entropy([1 for i in range(num_entities)], alpha)


def compute_entropy_percentage(block_distribution, alpha):
    if sum(block_distribution) == 0:
        return None
    try:
        total_entities = compute_total_entities(block_distribution)
        return compute_entropy(block_distribution, alpha) / compute_max_entropy(total_entities, alpha)
    except ZeroDivisionError:
        return 0
