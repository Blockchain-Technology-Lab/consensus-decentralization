def compute_tau_index(block_distribution, threshold):
    """
    Calculates the tau-decentralization index of a distribution of blocks
    :param block_distribution: a list of integers, each being the blocks that an entity has produced, sorted in descending order
    :param threshold: float, the parameter of the tau-decentralization index, i.e. the threshold for the power
    ratio that is captured by the index (e.g. 0.66 for 66%)
    :returns: int that corresponds to the tau index of the given distribution, or None if there were no blocks
    """
    total_blocks = sum(block_distribution)
    if total_blocks == 0:
        return None
    tau_index, power_ratio_covered = 0, 0
    for block_amount in block_distribution:
        if power_ratio_covered >= threshold:
            break
        tau_index += 1
        power_ratio_covered += block_amount / total_blocks
    return tau_index
