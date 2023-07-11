import sys
import src.helpers.helper as hlp

def compute_num_parties(blocks_per_entity):
    """
    Calculates the number of parties within a distribution
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :returns: a float that represents the total number of parties within the distribution
    """
    num=0
    filtered_vals = [v for _, v in blocks_per_entity.items() if v != 0]
    num= len(filtered_vals)
    return num

if __name__ == '__main__':
    filename = sys.argv[1]
    blocks_per_entity = hlp.get_blocks_per_entity_from_file(filename)
    print(f'# Parties: {compute_num_parties(blocks_per_entity)}')