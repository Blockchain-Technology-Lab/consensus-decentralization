from math import log


def compute_theil_index(block_distribution):
    """
    Calculates the Thiel index of a distribution of blocks to entities
    :param block_distribution: a list of integers, each being the blocks that an entity has produced, sorted in descending order
    :returns: float that represents the Thiel index of the given distribution
    """
    n = len(block_distribution)
    if n == 0:
        return 0
    total_blocks = sum(block_distribution)
    mu = total_blocks / n
    theil = 0
    for nblocks in block_distribution:
        x = nblocks / mu
        if x > 0:
            theil += x * log(x)
    theil /= n
    return theil
