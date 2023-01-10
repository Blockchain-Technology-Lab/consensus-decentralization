from math import e
import numpy as np
import sys
import src.helpers.helper as hlp


# todo failing test so look more into it
def compute_entropy(blocks_per_entity):  # https://stackoverflow.com/a/45091961
    labels = []
    for (key, value) in blocks_per_entity.items():
        labels += [key] * value

    value, counts = np.unique(labels, return_counts=True)
    norm_counts = counts / counts.sum()
    return -(norm_counts * np.log(norm_counts)/np.log(e)).sum()


if __name__ == '__main__':
    filename = sys.argv[1]
    blocks_per_entity = hlp.get_blocks_per_entity_from_file(filename)
    print(f'Entropy: {compute_entropy(blocks_per_entity)}')
