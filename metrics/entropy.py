from math import e
import numpy as np

def compute_entropy(blocks_per_entity):  # https://stackoverflow.com/a/45091961
    labels = []
    for (key, value) in blocks_per_entity.items():
        labels += [key] * value

    value,counts = np.unique(labels, return_counts=True)
    norm_counts = counts / counts.sum()
    return -(norm_counts * np.log(norm_counts)/np.log(e)).sum()
