# Mappings

A mapping is responsible for linking blocks to the entities that created them. While the parsed data contains 
information about the addresses that received rewards for producing some block or identifiers that are related to them,
it does not contain information about the entities that control these addresses, which is where the mapping comes in. 

The mapping takes as input the parsed data (from `output/<project_name>/parsed_data.json`) and outputs a file
(`output/<project_name>/mapped_data.json`), which is structured as follows:

```
[
    {
        "number": "<block's number>",
        "timestamp": "<block's timestamp of the form: yyyy-mm-dd hh:mm:ss UTC>",
        "reward_addresses": "<address1>,<address2>"
        "creator": <entity that created the block>,
        "mapping_method": <method used to map the block to its creator>
    }
]
```


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
substring of the parameter, then a match is found.

If the first step fails, we compare the block's reward addresses with known pool addresses (including special 
addresses that exist for some blockchains) and again look for a match. 

In both cases, if there is a match, then:

1. We map the block to the matched pool.
2. We associate all of the block's reward addresses (that is, the addresses that receive fees from the block) with 
the matched pool.
3. We record the mapping method that was used to obtain the mapping (`known_identifiers` for the first case or 
   `known_addresses` for the second.

In essence, the identifiers are the principal element for mapping a block to an entity and the known addresses are
the fallback mechanism.

If there is a match, we also parse the auxiliary information, such as pool ownership or clusters, in order to assign the
block to the top level entity, e.g., the pool's parent company or cluster. If a match is found this way, we update 
the mapping method to `known_pool_links`.

If all mechanisms fail, then no match is found. In this case, we assign the reward addresses as the block's entity.
