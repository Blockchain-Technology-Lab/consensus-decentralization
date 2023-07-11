import sys
import src.helpers.helper as hlp

def compute_mining_power_ratio(blocks_per_entity):
    """
    Calculates the mining power ratio of a distribution of blocks to entities
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :returns: maxer: an integer which is the maximum value of mining power ratio of all participants
    """
    mpr = {}
    total_blocks = sum(blocks_per_entity.values())
    for (name, blocks) in blocks_per_entity.items():
        current_mpr = (blocks/total_blocks)
        mpr[name] = current_mpr
    maxer = max(mpr.values())
    return maxer

if __name__ == '__main__':
    filename = sys.argv[1]
    blocks_per_entity = hlp.get_blocks_per_entity_from(filename)
    print(f'Mining Power Ratio: {compute_mining_power_ratio(blocks_per_entity)}')