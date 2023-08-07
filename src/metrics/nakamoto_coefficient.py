import logging
import sys
import src.helpers.helper as hlp


def compute_nakamoto_coefficient(blocks_per_entity):
    """
    Calculates the Nakamoto coefficient of a distribution of blocks to entities
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :returns: int that represents the Nakamoto coefficient of the given distribution
    """
    nc, power_percentage = 0, 0
    total_blocks = sum(blocks_per_entity.values())
    for (name, blocks) in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
        if power_percentage < 50:
            nc += 1
            power_percentage += 100 * blocks / total_blocks
        else:
            return nc
    return nc


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)
    filename = sys.argv[1]
    blocks_per_entity = hlp.get_blocks_per_entity_from_file(filename)
    logging.info(f'Nakamoto Coefficient: {compute_nakamoto_coefficient(blocks_per_entity)}')
