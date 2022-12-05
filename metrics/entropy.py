from math import e
import numpy as np
import sys

def compute_entropy(blocks_per_entity):  # https://stackoverflow.com/a/45091961
    labels = []
    for (key, value) in blocks_per_entity.items():
        labels += [key] * value

    value,counts = np.unique(labels, return_counts=True)
    norm_counts = counts / counts.sum()
    return -(norm_counts * np.log(norm_counts)/np.log(e)).sum()


if __name__ == '__main__':
    filename = sys.argv[1]
    blocks_per_entity = {}
    with open(filename) as f:
        for idx, line in enumerate(f.readlines()):
            if idx > 0:
                row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                blocks_per_entity[row[0]] = int(row[1])

    print('Entropy:', compute_entropy(blocks_per_entity))
