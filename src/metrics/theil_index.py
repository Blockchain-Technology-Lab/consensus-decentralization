from math import log
import sys
import src.helpers.helper as hlp


def compute_theil(blocks_per_entity, alpha):
    """
    Calculates the Theil index of a distribution of blocks to entities
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :param alpha: a value of alpha which determines the type of Theil index (i.e. alpha = 1: Theil-T, alpha = 0: Theil-L, alpha = 2: Coefficient of Variation)
    :returns: a float that represents the Theil index of the given distribution
    """
    filtered_vals = [v for _, v in blocks_per_entity.items() if v != 0]
    N = len(filtered_vals)
    mu = sum(filtered_vals) / len(filtered_vals)
    summation = 0
    if alpha == 1:
        for entity in blocks_per_entity.keys():
            prop = (blocks_per_entity[entity]) / mu
            if prop > 0:
                summation += (prop * log(prop))
    if alpha == 0:
        for entity in blocks_per_entity.keys():
            if blocks_per_entity[entity] > 0:
                prop = mu / blocks_per_entity[entity]
                summation += (log(prop))
    theil = (1 / N) * summation
    return theil


if __name__ == '__main__':
    filename = sys.argv[1]
    theil_alpha = sys.argv[2] if len(sys.argv) > 2 else 1
    blocks_per_entity = hlp.get_blocks_per_entity_from_file(filename)
    print(f'Theil Index: {compute_theil(blocks_per_entity, theil_alpha)}')
