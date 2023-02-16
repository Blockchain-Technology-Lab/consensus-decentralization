# Metrics

A metric gets the mapped data (see above `Mapping`) and outputs a relevant value.
The metrics that we currently track are the following (note that more metrics may be added in the future):

1. **Nakamoto coefficient**: The Nakamoto coefficient in this context represents the minimum number of entities that 
collectively produce more than 50% of the system's total blocks. The output of the metric is a tuple of the Nakamoto 
coefficient and the power percentage that these entities (that form the coefficient) control.
2. **Gini coefficient**: The Gini coefficient represents the degree of inequality when it comes to block production. The 
output of the metric a decimal number in [0,1], where values close to 0 are an indicator of perfect equality (all entities in 
the system produce the same number of blocks) and values close to 1 are an indicator of perfect inequality (one entity 
produces most or all blocks).
3. **Shannon entropy**: The Shannon entropy represents the expected amount of information that one will gain by 
determining which entity produced some block. The output of the metric is a real number; typically, a high number of 
different involved entities will yield high entropy.

Each metric is implemented in a separate Python script in the folder `metrics`. Each script defines a function named `
compute_<metric_name>`, which takes as input a dictionary of the form `{'<entity name>': <number of resources>}` (and 
possibly other relevant arguments) and outputs the corresponding metric values.