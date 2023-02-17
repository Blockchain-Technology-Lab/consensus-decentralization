# Mappings

The mapping obtains the parsed data (from `output/<project_name>/parsed_data.json`) and outputs a `csv` file that maps 
blocks to entities. Specifically, the `csv` file is structured as follows:
```
Entity,Resources
<name of entity>,<(int) number of blocks>
```

The `csv` file is named as the timeframe over which the mapping was executed (e.g., `2021-04.csv`) and is stored in the 
project's output directory (i.e., `output/<project_name>`).

The logic of the mapping depends on the type of clustering we want to achieve. So, different mappings will output 
different results, even if applied on the same data. 

## Pool Information

To assist the mapping process, the directory `helpers/pool_information` contains files named `<project_name>.json`, with 
relevant pool information, structured as follows:

```
{
  "clusters": {
    "<year>": {
      "<cluster name>": [
        ["<pool name>", "<source of information>"]
      ]
    }
  },
  "coinbase_tags": {
    "<pool tag>": {
      "name": "<pool name>",
      "link": "<pool website>"
    }
  },
  "pool_addresses: {
      "<year>" {
          "<address>": "<pool name>"
      }
  }
}
```

In this file:

- `clusters` refers to pools with shared coinbase addresses:
  - instead of `<year>`, use the keyword `all` for clusters across years
  - in projects other than Cardano, such links appear when an address appears in two blocks that are attributed to 
different pools
  - in Cardano, such links exist when two pools share the same metadata
  - the `<source of information>` should be comma-separated keywords (e.g., "homepage", "shared block", etc) or a url with the clustering information; this information should be reprodusible (a link to a community or company with information that cannot be verified independently is not acceptable)
- `<pool tag>` is the tag that a pool inserts in a block's coinbase parameter, in order to claim a block as being mined 
by the pool
  - in projects that do not rely on the coinbase parameter (e.g., Cardano, Tezos) the tag is just the name of the pool

#### Pool Ownership

The file `helpers/legal_links.json` defines legal links between pools and companies, based on off-chain information 
(e.g., when a company is the major stakeholder in a pool).
