import sys
import src.helpers.helper as hlp

def compute_centralization_level(blocks_per_entity, epsilon):
    """Calculates the Centralization Level (Chu et al., 2018) of a distribution of blocks to entities
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :param epsilon: a specification which indicates a chain is N_ε centralized if the top N nodes performed more than 1 − ε fraction of transactions.
    :returns: (cl, power) where cl is an int that represents the Centralization level of the given
    distribution and power, a float that represents the fraction of blocks that these cl entities controlled
    """
    cl, power = 0,0
    target = 1-epsilon
    total_blocks = sum(blocks_per_entity.values())
    for (name, blocks) in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
        if power < target:
            cl += 1
            power += (blocks/ total_blocks)
    return cl

if __name__ == '__main__':
    filename = sys.argv[1]
    cl_epsilon = sys.argv[2] if len(sys.argv) > 2 else 0.33
    blocks_per_entity = hlp.get_blocks_per_entity_from_file(filename)
    print(f'Centralization Level: {compute_centralization_level(blocks_per_entity, cl_epsilon)}')
