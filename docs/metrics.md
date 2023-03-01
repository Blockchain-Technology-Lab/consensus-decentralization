# Metrics

A metric gets the mapped data (see above `Mapping`) and outputs a relevant value.
The implemented metrics are the following (with more to be added in the future):

1. **Nakamoto coefficient**: The Nakamoto coefficient is the minimum number of entities that
collectively produce more than 50% of the produced blocks within a given timeframe. The output of the metric is a tuple of the Nakamoto
coefficient and the power percentage that these entities control.
2. **Gini coefficient**: The Gini coefficient represents the degree of inequality in block production. The
output of the metric a decimal number in [0,1]. Values close to 0 indicate equality (all entities in
the system produce the same number of blocks) and values close to 1 indicate inequality (one entity
produces most or all blocks).
3. **Entropy**: Entropy represents the expected amount of information in the distribution of blocks across entities.
Entropy is parameterized by a base rate α, which defines different types of
entropy: (a) -1: min; (b) 0: Hartley; (c) 1: Shannon; (d) 2: collision.
The output of the metric is a real number. Typically, a high number of
different involved entities, each with approximately equal power, should yield high entropy.

Each metric is implemented in a separate Python script in the folder `metrics`. Each script defines a function named `compute_<metric_name>`, which takes as input a dictionary of the form `{'<entity name>': <number of resources>}` (and possibly other relevant arguments) and outputs the corresponding metric values.
