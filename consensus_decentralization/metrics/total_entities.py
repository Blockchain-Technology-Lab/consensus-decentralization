def compute_total_entities(block_distribution):
    """
    Computes the number of entities that have produced blocks in the given timeframe.
    :param block_distribution: list of integers, each being the blocks that an entity has produced
    :returns: an integer that represents the number of entities that have produced blocks
    """
    return len([v for v in block_distribution if v > 0])
