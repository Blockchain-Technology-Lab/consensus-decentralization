import logging
from math import log
import sys
import src.helper as hlp


def compute_entropy(blocks_per_entity, alpha):
    """
    Calculates the entropy of a distribution of blocks to entities
    Pi is the relative frequency of each entity.
    Renyi entropy: 1/(1-alpha) * log2 (sum (Pi**alpha))
    Shannon entropy (alpha=1): −sum P(Si) log2 (Pi)
    Min entropy (alpha=-1): -log max Pi
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :param alpha: the entropy parameter (depending on its value the corresponding entropy measure is used)
    :returns: a float that represents the entropy of the data
    """
    block_distribution = blocks_per_entity.values()
    all_blocks = sum(block_distribution)
    if alpha == 1:
        entropy = 0
        for value in block_distribution:
            rel_freq = value / all_blocks
            if rel_freq > 0:
                entropy -= rel_freq * log(rel_freq, 2)
    else:
        probs = [blocks / all_blocks for blocks in block_distribution]
        if alpha == -1:
            entropy = - log(max(probs), 2)
        else:
            sum_freqs = sum([
                prob ** alpha for prob in probs
            ])
            entropy = log(sum_freqs, 2) / (1 - alpha)

    return entropy


def compute_max_entropy(num_entities, alpha):
    return compute_entropy({i: 1 for i in range(num_entities)}, alpha)


def compute_entropy_percentage(blocks_per_entity, alpha):
    try:
        return compute_entropy(blocks_per_entity, alpha) / compute_max_entropy(len(blocks_per_entity), alpha)
    except ZeroDivisionError:
        return 0


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)
    filename = sys.argv[1]
    entropy_alpha = sys.argv[2] if len(sys.argv) > 2 else 1
    blocks_per_entity = hlp.get_blocks_per_entity_from_file(filename)
    logging.info(f'Entropy: {compute_entropy(blocks_per_entity, entropy_alpha)}')
