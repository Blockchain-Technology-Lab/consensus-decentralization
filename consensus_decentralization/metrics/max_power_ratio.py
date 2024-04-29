def compute_max_power_ratio(block_distribution):
    """
    Calculates the maximum power ratio of a distribution of balances
    :param block_distribution: a list of integers, each being the blocks that an entity has produced, sorted in descending order
    :returns: float that represents the maximum power ratio among all block producers (0 if there weren't any)
    """
    total_blocks = sum(block_distribution)
    return block_distribution[0] / total_blocks if total_blocks else 0
