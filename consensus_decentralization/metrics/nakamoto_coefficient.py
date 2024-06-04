from consensus_decentralization.metrics.tau_index import compute_tau_index


def compute_nakamoto_coefficient(block_distribution):
    """
    Calculates the Nakamoto coefficient of a distribution of blocks to entities
    :param block_distribution: a list of integers, each being the blocks that an entity has produced, sorted in descending order
    :returns: int that represents the Nakamoto coefficient of the given distribution, or None if the data is empty
    """
    return compute_tau_index(block_distribution, 0.5)
