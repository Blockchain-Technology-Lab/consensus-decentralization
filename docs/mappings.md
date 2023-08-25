# Mappings

A mapping obtains the parsed data of a ledger (from `output/<project_name>/parsed_data.json`) and outputs one or more 
`csv` files that map blocks to entities, structured as follows:

```
Entity,Resources
<name of entity>,<(int) number of blocks>
```

Specifically, if the `timeframe` argument is provided during execution, then the mapping outputs a single `csv` 
file that corresponds to that timeframe. Otherwise, it outputs a `csv` file for each month contained in the default 
time range (as specified in the [config file](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/config.yaml)). 
It also outputs a `csv` file for each year contained in the relevant time frames.

Each `csv` file is named after the timeframe over which the mapping was executed (e.g., `2021-04.csv`) and is
stored in a dedicated folder in the project's output directory (`output/<project_name>/mapped_data`).

The logic of the mapping depends on the type of clustering we want to achieve. So, different mappings will output
different results, even if applied on the same data. An exception to this is the "no-cluster" mapping (DummyMapping
in the code), which maps blocks to reward addresses, so it doesn't perform any extra processing on the raw data.

## Mapping Information

To assist the mapping process, the directory `mapping_information/` contains
mapping information about the supported projects.

There exist three subdirectories and two additional files. In each subdirectory there exists a file for
the corresponding ledger data, if such data exists.

#### Identifiers

The files under `identifiers` define information about block creators. Each key
corresponds to a tag or ticker, by which the pool is identifiable in its
produced blocks. The value for each key is a dictionary of pool-related
information, specifically its name, a URL to its homepage, etc. Each file's
structure is as follows:
```
{
  "P1": {
      "name": "Pool P1",
      "homepage": "example.com/p1"
  },
  "--P2--": {
      "name": "Pool P2",
      "homepage": "example.com/p2"
  }
}
```

#### Clusters

The files under `clusters` define information about pool clusters. This information is
organized per cluster. For each cluster, an array of pool-related information is
defined. Each item in the array defines the pool's name, the time window during
which the pool belonged to the cluster (from the beginning of `from` until the
beginning of `to` _excluding_), and the _publicly available_ source of
information, via which the link between the pool and the cluster is established.
Each file's structure is as follows:
```
{
  "cluster A": [
      {"name": "P1", "from": "", "to": "2023", "source": "example.com/link1"}
  ],
  "cluster B": [
      {"name": "--P2--", "from": "", "to": "", "source": "example.com/link2"}
  ]
}
```

#### Addresses
The files under `addresses` define ownership information about addresses. As with
clusters, for each address the pool ownership information defines the pool's
name and a public source of information about the ownership.  Each file's
structure is as follows:
```
{
  "address1": {"name": "Pool P2", "source": "example.com"},
}
```

#### Legal links

The file `legal_links.json` defines legal links between pools and companies, based on off-chain information.
For example, it defines ownership information of a pool by a company.
The structure of the file is as follows:

```
{
  "<parent company>": [
      {"name": "<pool name>", "from": "<start date>", "to": "<end date>", "source": "<source of information>"}
  ]
}
```

The values for each entry are the same as `clusters` in the above pool information.

#### Special addresses

The file `special_addresses.json` defines per-project information about addresses that are not related to some entity 
but are used for protocol-specific reasons (e.g. treasury address). The format of the file is the following:
```
{
  "Project A": [
      {"address": "A special address 1", "source": "some.public.source"},
      {"address": "A special address 2", "source": "some.public.source"}
  ],
  "Project B": [
      {"address": "B special address", "source": "some.public.source"}
  ]
}
```

## Mapping process implementation

In our implementation, the mapping of a block uses the auxiliary information as follows.

First, it iterates over all known tags and compares each one with the block's identifiers. If the tag is a
substring of the parameter, then we have a match.

Second, if the first step fails, we compare the block's reward addresses with known pool addresses and again look for
a match.

In both cases, if there is a match, then: (i) we map the block to the matched pool; (ii) we associate all of the block's
reward addresses (that is, the addresses that receive fees from the block) with the matched pool.

In essence, the identifiers are the principal element for mapping a block to an entity and the known addresses are
the fallback mechanism.

If there is a match, we also parse the auxiliary information, such as pool ownership or clusters, in order to assign the
block to the top level entity, e.g., the pool's parent company or cluster.

If both mechanisms fail, then no match is found. In this case, we assign the reward addresses as the block's entity.
