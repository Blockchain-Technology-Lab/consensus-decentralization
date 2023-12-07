def compute_nakamoto_coefficient(blocks_per_entity):
    """
    Calculates the Nakamoto coefficient of a distribution of blocks to entities
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :returns: int that represents the Nakamoto coefficient of the given distribution or None if the data is empty
    """
    total_blocks = sum(blocks_per_entity.values())
    if total_blocks == 0:
        return None
    nc, power_percentage, top_entities = 0, 0, set()
    while power_percentage < 50:
        current_max_name = None
        for (name, blocks) in blocks_per_entity.items():
            if current_max_name is None or (blocks >= blocks_per_entity[current_max_name] and name not in top_entities):
                current_max_name = name
        nc += 1
        power_percentage += 100 * blocks_per_entity[current_max_name] / total_blocks
        top_entities.add(current_max_name)
    return nc
