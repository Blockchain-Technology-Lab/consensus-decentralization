# Aggregator

The aggregator obtains the mapped data of a ledger (from `processed_data/<project_name>/mapped_data.json`) and 
aggregates it over units of time that are determined based on the given `timeframe` and `aggregate_by` parameters.
It then outputs a `csv` file with the distribution of blocks to entities for each time unit under consideration.
This file is saved in the directory `processed_data/<project name>/blocks_per_entity/` and is named based on the 
`timeframe` and `aggregate_by` parameters.
For example, if the specified timeframe is from June 2023 to September 2023 and the aggregation is by month, then
the output file would be named `monthly_from_2023-06-01_to_2023-09-30.csv` and would be structured as follows:
```
Entity \ Time period,Jun-2023,Jul-2023,Aug-2023,Sep-2023
<name of entity 1>,<number of blocks produced by entity 1 in June 2023>,<number of blocks produced by entity 1 in July 2023>,<number of blocks produced by entity 1 in August 2023>,<number of blocks produced by entity 1 in September 2023>
<name of entity 2>,<number of blocks produced by entity 2 in June 2023>,<number of blocks produced by entity 2 in July 2023>,<number of blocks produced by entity 2 in August 2023>,<number of blocks produced by entity 2 in September 2023>
```

Therefore, the file will have as many rows as the number of entities that have produced blocks in the given
timeframe (+ 1 for the header) and as many columns as the number of time units in the given timeframe (+ 1 for the
entity names).
