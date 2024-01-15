from consensus_decentralization.metrics.tau_index import compute_tau_index


def compute_nakamoto_coefficient(blocks_per_entity):
    """
    Calculates the Nakamoto coefficient of a distribution of blocks to entities
    :param blocks_per_entity: a dictionary with entities and the blocks they have produced
    :returns: int that represents the Nakamoto coefficient of the given distribution, or None if the data is empty
    """
    return compute_tau_index(blocks_per_entity=blocks_per_entity, threshold=0.5)
