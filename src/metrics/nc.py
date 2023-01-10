import sys
import src.helpers.helper as hlp


def compute_nc(blocks_per_entity):
    nc, power_percentage = 0, 0
    total_blocks = sum(blocks_per_entity.values())
    for (name, blocks) in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
        if power_percentage < 50:
            nc += 1
            power_percentage += 100 * blocks / total_blocks
        else:
            return nc, power_percentage


if __name__ == '__main__':
    filename = sys.argv[1]
    blocks_per_entity = hlp.get_blocks_per_entity_from_file(filename)
    print(f'Nakamoto Coefficient: {compute_nc(blocks_per_entity)}')
