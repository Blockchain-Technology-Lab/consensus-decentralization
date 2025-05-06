def compute_concentration_ratio(block_distribution, topn):
    """
    Calculates the n-concentration ratio of a distribution of balances
    :param block_distribution: a list of integers, each being the blocks that an entity has produced, sorted in descending order
    :param topn: the number of top block producers to consider
    :returns: float that represents the ratio of blocks produced by the top n block producers (0 if there weren't any)
    """
    total_blocks = sum(block_distribution)
    return sum(block_distribution[:topn]) / total_blocks if total_blocks else 0
