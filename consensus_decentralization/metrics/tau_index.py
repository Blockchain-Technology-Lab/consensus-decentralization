def compute_tau_index(blocks_per_entity, threshold):
    """
    Calculates the tau-decentralization index of a distribution of blocks
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :param threshold: float, the parameter of the tau-decentralization index, i.e. the threshold for the power
    ratio that is captured by the index (e.g. 0.66 for 66%)
    :returns: int that corresponds to the tau index of the given distribution, or None if there were no blocks
    """
    total_blocks = sum(blocks_per_entity.values())
    if total_blocks == 0:
        return None
    tau_index, power_ratio_covered = 0, 0
    blocks_per_entity_copy = blocks_per_entity.copy()
    while power_ratio_covered < threshold:
        current_max_entity = max(blocks_per_entity_copy, key=blocks_per_entity_copy.get)
        tau_index += 1
        power_ratio_covered += blocks_per_entity_copy[current_max_entity] / total_blocks
        del blocks_per_entity_copy[current_max_entity]
    return tau_index
