from math import log
import sys
import src.helpers.helper as hlp


def compute_entropy(blocks_per_entity):
    """
        Source: https://gist.github.com/yacineMahdid/55041c3bdcc70d1fa3300478a43f153b
        Custom implementation of shannon entropy with a full non-binarized sequence
        Formula looks like this: H(S) = −Σ P(Si) log2 (P(Si))
        P(Si) here is the relative frequency of each itme
    """
    entropy = 0
    all_blocks = sum(blocks_per_entity.values())
    for entity in blocks_per_entity.keys():
        rel_freq = blocks_per_entity[entity] / all_blocks
        if rel_freq > 0:
            entropy = entropy + -(rel_freq * log(rel_freq, 2))

    return entropy


if __name__ == '__main__':
    filename = sys.argv[1]
    blocks_per_entity = hlp.get_blocks_per_entity_from_file(filename)
    print(f'Entropy: {compute_entropy(blocks_per_entity)}')
