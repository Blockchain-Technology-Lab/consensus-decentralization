import sys

def compute_nc(blocks_per_entity):
    nc = [0, 0]
    for (name, blocks) in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
        if nc[1] < 50:
            nc[0] += 1
            nc[1] += 100 * blocks / sum([i[1] for i in blocks_per_entity.items()])
        else:
            return nc


if __name__ == '__main__':
    filename = sys.argv[1]
    blocks_per_entity = {}
    with open(filename) as f:
        for idx, line in enumerate(f.readlines()):
            if idx > 0:
                row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                blocks_per_entity[row[0]] = int(row[1])

    print('Nakamoto Coefficient:', compute_nc(blocks_per_entity))
