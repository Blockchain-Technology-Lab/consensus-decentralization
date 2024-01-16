def compute_max_power_ratio(blocks_per_entity):
    """
    Calculates the maximum power ratio of a distribution of balances
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :returns: float that represents the maximum power ratio among all block producers (0 if there weren't any)
    """
    if len(blocks_per_entity) == 0:
        return 0
    max_nblocks = max(blocks_per_entity.values())
    total_blocks = sum(blocks_per_entity.values())
    return max_nblocks / total_blocks if total_blocks > 0 else 0
