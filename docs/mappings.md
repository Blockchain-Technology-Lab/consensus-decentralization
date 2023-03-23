# Mappings

A mapping obtains the parsed data (from `output/<project_name>/parsed_data.json`) and outputs a `csv` file that maps
blocks to entities, structured as follows:

```
Entity,Resources
<name of entity>,<(int) number of blocks>
```

The name of the `csv` file is the timeframe, over which the mapping was executed (e.g., `2021-04.csv`). The file is stored in the
project's output directory (`output/<project_name>/`).

The logic of the mapping depends on the type of clustering we want to achieve. So, different mappings will output
different results, even if applied on the same data.

## Pool Information

To assist the mapping process, the directory `helpers/pool_information/` contains files named `<project_name>.json`, with
relevant pool information, structured as follows:

```
{
  "clusters": {
    "<cluster name>": [
      {"name": "<pool name>", "from": "<from>", "to": "<to>", "source": "<source of information>"}
    ]
  },
  "coinbase_tags": {
    "<pool tag>": {
      "name": "<pool name>",
      "link": "<pool website>"
    }
  },
  "pool_addresses": {
    "<address>": {"name": "<pool name>", "from": "<from>", "to": "<to>", "source": "<source of information>"},
  }
}
```

In this file:

- `clusters` refers to pools that share infrastructure:
- for each pool in a cluster, the following values should be defined:
  - `<from>` sets the beginning of the control of the pool by the cluster; the first
    day of the timeframe is chosen; for example, if `2022`, then the beginning is set
    to `2022-01-01`); if `<from>` is empty, then the control existed since the
    pool's inception.
  - `<to>` sets the end of the control of the pool by the cluster; the end is
    exclusive, i.e., it defines the beginning of the control transition; for
    example, if `2022`, the end of the control is `31-12-2021`
    if `<to>` is empty, then the control is still active.
  - `<source of information>` should be either (i) comma-separated keywords or (ii) a url with the clustering information; this information should be publicly-available and reproducible (for example, a link to a community or company, with information that cannot be verified independently, is not acceptable);
    - keywords: for Cardano, `homepage` can be used for pools that define the
      same `homepage` in their metadata json file (published on0chain)
- `<pool tag>` is the tag that a pool inserts in a block's coinbase parameter, in order to claim a block as being mined by the pool; in projects that do not rely on the coinbase parameter (e.g., Cardano, Tezos) the tag is just the name of the pool (Tezos) or its ticker (Cardano).
- `pool_addresses` define control of an address by a pool; the structure is the same as `clusters`.

#### Pool Ownership

The file `helpers/legal_links.json` defines legal links between pools and companies, based on off-chain information.
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
