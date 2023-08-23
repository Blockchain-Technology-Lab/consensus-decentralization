# Metrics

A metric gets the mapped data (see above `Mapping`) and outputs a relevant value.
The metrics that have been implemented so far are the following:

1. **Nakamoto coefficient**: The Nakamoto coefficient represents the minimum number of entities that
collectively produce more than 50% of the total blocks within a given timeframe. The output of the metric is an
integer.
2. **Gini coefficient**: The Gini coefficient represents the degree of inequality in block production. The
output of the metric is a decimal number in [0,1]. Values close to 0 indicate equality (all entities in
the system produce the same number of blocks) and values close to 1 indicate inequality (one entity
produces most or all blocks).
3. **Entropy**: Entropy represents the expected amount of information in the distribution of blocks across entities.
The output of the metric is a real number. Typically, a higher value of entropy indicates higher decentralization
(lower predictability). Entropy is parameterized by a base rate α, which defines different types of entropy:
    - α = -1: min entropy
    - α = 0: Hartley entropy
    - α = 1: Shannon entropy (this is used by default)
    - α = 2: collision entropy
4. **HHI**: The Herfindahl-Hirschman Index (HHI) is a measure of market concentration. It is defined as the sum of the
squares of the market shares (as whole numbers, e.g. 40 for 40%) of the entities in the system. The output of the metric
is a real number in (0, 10000]. Values close to 0 indicate low concentration (many entities produce a similar number of
blocks) and values close to 1 indicate high concentration (one entity produces most or all blocks). 
The U.S. Department of Justice has set the following thresholds for interpreting HHI values (in traditional markets):
    - (0, 1500): Competitive market
    - [1500, 2500]: Moderately concentrated market
    - (2500, 10000]: Highly concentrated market

Each metric is implemented in a separate Python script in the folder `metrics`. Each script defines a function named `compute_<metric_name>`, which takes as input a dictionary of the form `{'<entity name>': <number of resources>}` (and possibly other relevant arguments) and outputs the corresponding metric values.
