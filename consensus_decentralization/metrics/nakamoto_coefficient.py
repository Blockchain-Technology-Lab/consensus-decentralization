import logging
import sys
import consensus_decentralization.helper as hlp


def compute_nakamoto_coefficient(blocks_per_entity):
    """
    Calculates the Nakamoto coefficient of a distribution of blocks to entities
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :returns: int that represents the Nakamoto coefficient of the given distribution or None if the data is empty
    """
    if len(blocks_per_entity) == 0:
        return None
    nc, power_percentage = 0, 0
    total_blocks = sum(blocks_per_entity.values())
    for (name, blocks) in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
        if power_percentage < 50:
            nc += 1
            power_percentage += 100 * blocks / total_blocks
        else:
            return nc
    return nc
