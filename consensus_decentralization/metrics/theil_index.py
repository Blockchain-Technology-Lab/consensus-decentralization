from math import log


def compute_theil_index(blocks_per_entity):
    """
    Calculates the Thiel index of a distribution of blocks to entities
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :returns: float that represents the Thiel index of the given distribution
    """
    n = len(blocks_per_entity)
    if n == 0:
        return 0
    total_blocks = sum(blocks_per_entity.values())
    mu = total_blocks / n
    theil = 0
    for nblocks in blocks_per_entity.values():
        x = nblocks / mu
        if x > 0:
            theil += x * log(x)
    theil /= n
    return theil
