from math import log
import sys
import src.helpers.helper as hlp


def compute_entropy(blocks_per_entity, alpha):
    """
        Pi is the relative frequency of each entity.
        Renyi entropy: 1/(1-alpha) * log2 (sum (Pi**alpha))
        Shannon entropy (alpha=1): −sum P(Si) log2 (Pi)
        Min entropy (alpha=-1): -log max Pi
    """
    if alpha == 1:
        entropy = 0
        all_blocks = sum(blocks_per_entity.values())
        for entity in blocks_per_entity.keys():
            rel_freq = blocks_per_entity[entity] / all_blocks
            if rel_freq > 0:
                entropy -= rel_freq * log(rel_freq, 2)
    else:
        all_blocks = sum(blocks_per_entity.values())
        probs = [
            blocks / all_blocks for blocks in blocks_per_entity.values()
        ]
        if alpha == -1:
            entropy = - log(max(probs), 2)
        else:
            sum_freqs = sum([
                prob ** alpha for prob in probs
            ])
            entropy = log(sum_freqs, 2) / (1 - alpha)

    return entropy


if __name__ == '__main__':
    filename = sys.argv[1]
    entropy_alpha = sys.argv[2] if len(sys.argv) > 2 else 1
    blocks_per_entity = hlp.get_blocks_per_entity_from_file(filename)
    print(f'Entropy: {compute_entropy(blocks_per_entity, entropy_alpha)}')
